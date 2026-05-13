import asyncio
from datetime import datetime, timezone
from sqlalchemy import select
from app.core.database import async_session
from app.models import DubbingJob, JobStep, JobStatus, Transcript, Translation, GeneratedVoiceAsset, LipsyncOutput
from app.services.contract_validation_service import validate_contract
from app.services.audit_service import log_audit
from app.core.config import settings


async def run_step(db, job_id: int, step_name: str, step_status: JobStatus, execute_fn):
    step = JobStep(dubbing_job_id=job_id, step_name=step_name, status="running")
    step.started_at = datetime.now(timezone.utc)
    db.add(step)
    result = await db.execute(select(DubbingJob).where(DubbingJob.id == job_id))
    job = result.scalar_one()
    job.status = step_status
    await db.commit()

    try:
        output = await execute_fn(job)
        step.status = "completed"
        step.completed_at = datetime.now(timezone.utc)
        await db.commit()
        await log_audit(db, dubbing_job_id=job_id, action=f"worker.{step_name}.completed")
        return output
    except Exception as e:
        step.status = "failed"
        step.error_message = str(e)
        job.status = JobStatus.failed
        await db.commit()
        await log_audit(db, dubbing_job_id=job_id, action=f"worker.{step_name}.failed", details={"error": str(e)})
        raise


async def process_job(job_id: int):
    async with async_session() as db:
        result = await db.execute(select(DubbingJob).where(DubbingJob.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            print(f"Job {job_id} no encontrado")
            return

        if job.mode.value == "voz_original_ia_autorizada" and job.contract_id:
            validation = await validate_contract(
                db, contract_id=job.contract_id,
                mode=job.mode.value, language=job.target_language,
                territory=job.territory, usage_type=job.usage_type,
            )
            if validation["blocked"]:
                job.legal_blocked = True
                job.legal_block_reason = validation["reason"]
                job.status = JobStatus.blocked_legal
                await db.commit()
                await log_audit(db, dubbing_job_id=job.id, action="worker.blocked_legal", details=validation)
                return

        audio_path = None
        try:
            # 1. Transcripción
            async def transcribe_fn(job):
                if settings.asr_provider == "comfyui":
                    from app.providers.comfyui_asr import ComfyUIASRProvider
                    provider = ComfyUIASRProvider()
                else:
                    from app.workers.steps.transcribe import transcribe
                    return await transcribe("", job.source_language)

                result_data = await provider.transcribe("", job.source_language)

                transcript = Transcript(
                    dubbing_job_id=job.id, language=job.source_language,
                    segments=str(result_data.get("segments", [])),
                    raw_text=result_data.get("raw_text", ""),
                    model_used=result_data.get("model_used"),
                )
                db.add(transcript)
                await db.commit()
                return result_data

            transcript_result = await run_step(db, job.id, "transcribing", JobStatus.transcribing, transcribe_fn)

            # 2. Traducción
            async def translate_fn(job):
                from app.workers.steps.translate import translate
                segments = transcript_result.get("segments", [])
                result_data = await translate(segments, job.source_language, job.target_language)

                translation = Translation(
                    dubbing_job_id=job.id,
                    source_language=job.source_language,
                    target_language=job.target_language,
                    segments=str(result_data.get("segments", [])),
                    raw_text=result_data.get("raw_text", ""),
                    model_used=result_data.get("model_used"),
                )
                db.add(translation)
                await db.commit()
                return result_data

            translate_result = await run_step(db, job.id, "translating", JobStatus.translating, translate_fn)

            # 3. Generación de voz
            async def voice_fn(job):
                text = translate_result.get("raw_text", "")
                voice_id = None
                if job.actor_id:
                    from app.models import Actor, VoiceContract
                    a_result = await db.execute(select(Actor).where(Actor.id == job.actor_id))
                    actor = a_result.scalar_one_or_none()
                    if actor and actor.email:
                        voice_id = actor.email

                if settings.tts_provider == "comfyui":
                    from app.providers.comfyui_tts import ComfyUITTSProvider, ComfyUIVoiceCloneProvider
                    if job.contract_id and voice_id:
                        provider = ComfyUIVoiceCloneProvider()
                    else:
                        provider = ComfyUITTSProvider()
                else:
                    from app.workers.steps.generate_voice import generate_voice
                    return await generate_voice(text, job.target_language, voice_id)

                from app.providers.base import TTSInput
                input_data = TTSInput(text=text, language=job.target_language, voice_id=voice_id)
                output = await provider.synthesize(input_data)

                asset = GeneratedVoiceAsset(
                    dubbing_job_id=job.id, file_path=output.audio_path,
                    duration_seconds=output.duration_seconds,
                    provider=output.provider, model_used=output.model_used,
                )
                db.add(asset)
                await db.commit()

                job.tts_provider_used = output.provider
                job.model_version = output.model_used
                return output

            voice_result = await run_step(db, job.id, "generating_voice", JobStatus.generating_voice, voice_fn)
            audio_path = voice_result.audio_path

            # 4. LipSync
            async def lipsync_fn(job):
                if settings.lipsync_provider == "comfyui":
                    from app.providers.comfyui_lipsync import ComfyUILipSyncProvider
                    provider = ComfyUILipSyncProvider()
                else:
                    from app.workers.steps.lipsync import lipsync
                    return await lipsync("", audio_path)

                from app.providers.base import LipSyncInput
                input_data = LipSyncInput(video_path="", audio_path=audio_path)
                output = await provider.process(input_data)

                ls_out = LipsyncOutput(
                    dubbing_job_id=job.id, file_path=output.video_path,
                    provider=output.provider, model_used=output.model_used,
                )
                db.add(ls_out)
                await db.commit()

                job.lipsync_provider_used = output.provider
                return output

            await run_step(db, job.id, "lipsyncing", JobStatus.lipsyncing, lipsync_fn)

            # 5. Mezcla
            async def mix_fn(job):
                from app.workers.steps.mix import mix_audio
                return await mix_audio([audio_path] if audio_path else [])

            await run_step(db, job.id, "mixing", JobStatus.mixing, mix_fn)

            # Marcar como esperando aprobación
            job.status = JobStatus.awaiting_approval
            await db.commit()
            await log_audit(db, dubbing_job_id=job.id, action="worker.completed")

        except Exception as e:
            job = (await db.execute(select(DubbingJob).where(DubbingJob.id == job_id))).scalar_one()
            job.status = JobStatus.failed
            await db.commit()
            await log_audit(db, dubbing_job_id=job.id, action="worker.failed", details={"error": str(e)})
            raise


if __name__ == "__main__":
    import sys
    job_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    asyncio.run(process_job(job_id))
