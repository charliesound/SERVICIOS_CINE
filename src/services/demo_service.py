from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import random
import uuid
from sqlalchemy import select

from .user_service import user_store, User
from .workflow_preset_service import preset_service


class DemoService:
    RELEASE_DEMO_LABEL = "OFFICIAL DEMO"
    DEMO_USERS = {
        "demo_free": {
            "username": "demo_free",
            "email": "demo_free@servicios-cine.com",
            "password": "demo123",
            "plan": "free",
            "role": "user",
        },
        "demo_studio": {
            "username": "demo_studio",
            "email": "demo_studio@servicios-cine.com",
            "password": "demo123",
            "plan": "studio",
            "role": "user",
        },
        "demo_creator": {
            "username": "demo_creator",
            "email": "demo_creator@servicios-cine.com",
            "password": "demo123",
            "plan": "creator",
            "role": "user",
        },
        "demo_enterprise": {
            "username": "demo_enterprise",
            "email": "demo_enterprise@servicios-cine.com",
            "password": "demo123",
            "plan": "enterprise",
            "role": "user",
        },
        "demo_admin": {
            "username": "demo_admin",
            "email": "admin@servicios-cine.com",
            "password": "admin123",
            "plan": "enterprise",
            "role": "admin",
        },
    }

    DEMO_PROJECTS = [
        {
            "id": "proj_cine_robot",
            "name": "Cine: Robot en Atardecer",
            "description": "Proyecto demo con secuencias de un robot en diferentes escenarios",
            "workflow_key": "still_text_to_image_pro",
            "status": "active",
        },
        {
            "id": "proj_storyboard_01",
            "name": "Storyboard: Escena de Acción",
            "description": "Storyboarddemo con 6 frames para secuencia de acción",
            "workflow_key": "still_storyboard_frame",
            "status": "active",
        },
        {
            "id": "proj_video_demo",
            "name": "Video: Transición Paisaje",
            "description": "Generación de video con transiciones de paisaje",
            "workflow_key": "video_text_to_video_base",
            "status": "active",
        },
        {
            "id": "proj_dubbing_spanish",
            "name": "Doblaje: Narración Documental",
            "description": "Narración en español con voz clara",
            "workflow_key": "dubbing_tts_es_es",
            "status": "active",
        },
        {
            "id": "proj_character_set",
            "name": "Consistencia de Personaje",
            "description": "Generar mismo personaje en diferentes poses",
            "workflow_key": "still_character_consistency",
            "status": "active",
        },
    ]

    DEMO_PRESETS = [
        {
            "name": "Cinematic Portrait",
            "workflow_key": "still_img2img_cinematic",
            "description": "Retratos cinematográficos con iluminación dramática",
            "inputs": {
                "prompt": "cinematic portrait, dramatic lighting, film grain",
                "negative_prompt": "blurry, low quality",
                "strength": 0.7,
                "steps": 30,
            },
            "tags": ["portrait", "cinematic", "dramatic"],
            "is_public": True,
        },
        {
            "name": "Fast Storyboard",
            "workflow_key": "still_storyboard_frame",
            "description": "Generación rápida de frames para storyboard",
            "inputs": {
                "prompt": "professional storyboard frame",
                "aspect_ratio": "16:9",
                "steps": 20,
            },
            "tags": ["storyboard", "fast", "production"],
            "is_public": True,
        },
        {
            "name": "Voice Clone Basic",
            "workflow_key": "dubbing_voice_clone_single",
            "description": "Clonación de voz básica para doblaje",
            "inputs": {"similarity": 0.8, "stability": 0.7},
            "tags": ["voice", "clone", "dubbing"],
            "is_public": True,
        },
    ]

    DEMO_NARRATIVE_PROJECT = {
        "id": "demo-narrative-001",
        "name": "El Viaje de Ana",
        "description": "Cortometraje demo sobre una mujer que descubre su pasado en un lugar inesperado.",
        "status": "PRE-PRODUCTION",
    }

    DEMO_SEQUENCES = [
        {
            "sequence_number": 1,
            "title": "EL ENCUENTRO",
            "description": "Ana regresa a su hogar y discovers secretos.",
        },
        {
            "sequence_number": 2,
            "title": "LA REVELACIÓN",
            "description": "Ana descubre la verdad sobre su familia.",
        },
        {
            "sequence_number": 3,
            "title": "EL FINAL",
            "description": "Ana toma una decisión que cambia su vida.",
        },
    ]

    DEMO_SCENES = [
        {
            "scene_number": "1",
            "setting": "INT",
            "location": "SALÓN",
            "time_of_day": "DÍA",
            "action_text": "ANA entra en el salón donde ha vivido toda su vida. Mira por la ventana mientras la luz del sol entra.",
        },
        {
            "scene_number": "1A",
            "setting": "INT",
            "location": "PASILLO",
            "time_of_day": "DÍA",
            "action_text": "Ana camina por el pasillo hacia la cocina. Se detiene frente a una fotografía antigua.",
        },
        {
            "scene_number": "2",
            "setting": "EXT",
            "location": "PARQUE",
            "time_of_day": "ATARDECER",
            "action_text": "Ana camina por el parque donde solía jugar de niña. El atardecer ilumina su rostro pensativo.",
        },
        {
            "scene_number": "3",
            "setting": "INT",
            "location": "COCINA",
            "time_of_day": "NOCHE",
            "action_text": "Ana prepara la cena en la cocina. Mientras cocina, recibe una llamada telefónica inesperada.",
        },
        {
            "scene_number": "4",
            "setting": "INT",
            "location": "DORMITORIO",
            "time_of_day": "NOCHE",
            "action_text": "Ana se acuesta pensativa. Mira el techo mientras recuerdos del día pasan por su mente.",
        },
        {
            "scene_number": "5",
            "setting": "EXT",
            "location": "CALLE",
            "time_of_day": "AMANECER",
            "action_text": "Ana sale de casa al amanecer. Un nuevo día comienza con una decisión tomada.",
        },
    ]

    DEMO_CHARACTERS = [
        {
            "name": "ANA",
            "description": "Mujer de 30 años. Profesora de escuela. Soñadora y curiosa.",
            "line_count": 45,
        },
        {
            "name": "MARÍA",
            "description": "Madre de Ana.60 años.Misteriosa y reservada.",
            "line_count": 12,
        },
        {
            "name": "LUIS",
            "description": "Amigo de Ana.35 años.Fotógrafo.Viajero.",
            "line_count": 8,
        },
    ]

    DEMO_SHOTS = [
        {
            "scene_number": "1",
            "shot_number": 1,
            "shot_size": "WIDE",
            "camera_angle": "EYE-LEVEL",
            "status": "ready",
        },
        {
            "scene_number": "1",
            "shot_number": 2,
            "shot_size": "MEDIUM",
            "camera_angle": "LOW",
            "status": "ready",
        },
        {
            "scene_number": "1",
            "shot_number": 3,
            "shot_size": "CLOSE-UP",
            "camera_angle": "EYE-LEVEL",
            "status": "generating",
        },
        {
            "scene_number": "1A",
            "shot_number": 1,
            "shot_size": "MEDIUM",
            "camera_angle": "EYE-LEVEL",
            "status": "pending",
        },
        {
            "scene_number": "2",
            "shot_number": 1,
            "shot_size": "WIDE",
            "camera_angle": "HIGH",
            "status": "ready",
        },
        {
            "scene_number": "2",
            "shot_number": 2,
            "shot_size": "MEDIUM",
            "camera_angle": "EYE-LEVEL",
            "status": "pending",
        },
        {
            "scene_number": "3",
            "shot_number": 1,
            "shot_size": "CLOSE-UP",
            "camera_angle": "EYE-LEVEL",
            "status": "pending",
        },
        {
            "scene_number": "4",
            "shot_number": 1,
            "shot_size": "MEDIUM",
            "camera_angle": "HIGH",
            "status": "pending",
        },
        {
            "scene_number": "5",
            "shot_number": 1,
            "shot_size": "WIDE",
            "camera_angle": "EYE-LEVEL",
            "status": "pending",
        },
    ]

    DEMO_ASSETS = [
        {"shot_scene": "1", "shot_number": 1, "status": "ready", "is_approved": True},
        {"shot_scene": "1", "shot_number": 2, "status": "ready", "is_approved": False},
        {"shot_scene": "2", "shot_number": 1, "status": "ready", "is_approved": True},
    ]

    DEMO_CLIPS = [
        {"scene_number": "1", "duration": "00:02:15", "status": "ready"},
        {"scene_number": "1", "duration": "00:01:30", "status": "ready"},
        {"scene_number": "1A", "duration": "00:00:45", "status": "ready"},
        {"scene_number": "2", "duration": "00:03:00", "status": "ready"},
        {"scene_number": "3", "duration": "00:02:00", "status": "processing"},
        {"scene_number": "4", "duration": "00:01:45", "status": "ingested"},
    ]

    DEMO_ASSEMBLIES = [
        {
            "name": "Rough Cut v1",
            "description": "Primera versión del corte",
            "sequence_ledger": [
                {"scene_id": "scene-001", "clips": ["clip-001", "clip-002"]},
                {"scene_id": "scene-002", "clips": ["clip-004"]},
                {"scene_id": "scene-003", "clips": []},
            ],
            "status": "draft",
        },
    ]

    DEMO_REVIEWS = [
        {"target_type": "asset", "target_id": "asset-001", "status": "approved"},
        {"target_type": "asset", "target_id": "asset-003", "status": "approved"},
        {"target_type": "asset", "target_id": "asset-004", "status": "pending"},
        {
            "target_type": "assembly_cut",
            "target_id": "assembly-001",
            "status": "needs_work",
        },
    ]

    DEMO_DECISIONS = [
        {
            "review_index": 0,
            "status_applied": "approved",
            "rationale_note": "Excelente trabajo, aprobado para delivery",
        },
        {
            "review_index": 1,
            "status_applied": "approved",
            "rationale_note": "Colores correctos, aprobado",
        },
        {
            "review_index": 2,
            "status_applied": "needs_work",
            "rationale_note": "Necesita ajustes en iluminación",
        },
    ]

    DEMO_DELIVERABLES = [
        {"name": "Rough Cut v1 - FCPXML", "format_type": "FCPXML", "status": "ready"},
        {"name": "Asset Pack - Final", "format_type": "ZIP", "status": "draft"},
    ]

    def __init__(self):
        self._demo_jobs: Dict[str, List[Dict]] = {}
        self._seeded = False

    async def _get_or_create_demo_organization(
        self,
        session,
        *,
        slug: str = "demo",
        plan: str = "free",
        name: Optional[str] = None,
    ):
        from models.core import Organization

        org_name = name or f"{self.RELEASE_DEMO_LABEL} {slug.replace('_', ' ').title()}"
        org_result = await session.execute(
            select(Organization).where(Organization.name == org_name)
        )
        org = org_result.scalar_one_or_none()
        if org is None:
            org = Organization(name=org_name, billing_plan=plan)
            session.add(org)
            await session.flush()
        else:
            org.billing_plan = plan
        return org

    async def _upsert_demo_user_in_db(
        self,
        session,
        user: User,
        role: str,
        organization_id: str,
    ) -> None:
        from models.core import User as DBUser

        result = await session.execute(select(DBUser).where(DBUser.id == user.user_id))
        db_user = result.scalar_one_or_none()
        if db_user is None:
            result = await session.execute(
                select(DBUser).where(DBUser.email == user.email)
            )
            db_user = result.scalar_one_or_none()

        if db_user is None:
            session.add(
                DBUser(
                    id=user.user_id,
                    organization_id=organization_id,
                    username=user.username,
                    email=user.email,
                    hashed_password=user.hashed_password,
                    full_name=user.username,
                    role=role,
                    is_active=user.is_active,
                    billing_plan=user.plan,
                    program=(
                        user.plan
                        if user.plan in {"creator", "producer", "studio", "enterprise"}
                        else "demo"
                    ),
                    signup_type="cid_user",
                    account_status="active",
                    access_level="full"
                    if user.plan in {"studio", "enterprise"}
                    else "standard",
                    cid_enabled=True,
                    onboarding_completed=True,
                    company=self.RELEASE_DEMO_LABEL,
                    country="ES",
                )
            )
            return

        db_user.id = user.user_id
        db_user.organization_id = organization_id
        db_user.username = user.username
        db_user.email = user.email
        db_user.hashed_password = user.hashed_password
        db_user.full_name = user.username
        db_user.role = role
        db_user.is_active = user.is_active
        db_user.billing_plan = user.plan
        db_user.program = (
            user.plan
            if user.plan in {"creator", "producer", "studio", "enterprise"}
            else "demo"
        )
        db_user.signup_type = "cid_user"
        db_user.account_status = "active"
        db_user.access_level = (
            "full" if user.plan in {"studio", "enterprise"} else "standard"
        )
        db_user.cid_enabled = True
        db_user.onboarding_completed = True
        db_user.company = self.RELEASE_DEMO_LABEL
        db_user.country = "ES"

    async def _seed_projects_for_org(
        self,
        session,
        *,
        organization_id: str,
        owner_user_id: str,
        project_templates: List[Dict[str, Any]],
    ) -> int:
        from models.core import Project

        created = 0
        for index, template in enumerate(project_templates, start=1):
            project_name = template["name"]
            existing = await session.execute(
                select(Project).where(
                    Project.organization_id == organization_id,
                    Project.name == project_name,
                )
            )
            if existing.scalar_one_or_none():
                continue

            script_text = None
            if "Storyboard" in project_name or "Cine:" in project_name:
                script_text = (
                    "INT. SET PRINCIPAL - DAY\n\n"
                    "La protagonista cruza el espacio, observa el decorado y prepara la siguiente toma.\n\n"
                    "DIRECTOR\nNecesitamos un plano abierto y otro detalle para la demo comercial."
                )

            session.add(
                Project(
                    organization_id=organization_id,
                    name=project_name,
                    description=template.get("description"),
                    status=template.get("status", "active"),
                    script_text=script_text,
                )
            )
            created += 1

        return created

    async def seed_demo_data(self) -> Dict[str, Any]:
        from database import AsyncSessionLocal

        results = {
            "users_created": 0,
            "presets_created": 0,
            "projects_created": 0,
            "sequences_created": 0,
            "scenes_created": 0,
            "characters_created": 0,
            "jobs_created": 0,
        }

        async with AsyncSessionLocal() as session:
            project_map = {
                "demo_free": self.DEMO_PROJECTS[:1],
                "demo_creator": self.DEMO_PROJECTS[1:3],
                "demo_studio": self.DEMO_PROJECTS,
                "demo_enterprise": self.DEMO_PROJECTS[2:],
                "demo_admin": self.DEMO_PROJECTS[:2],
            }

            for user_id, user_data in self.DEMO_USERS.items():
                org = await self._get_or_create_demo_organization(
                    session,
                    slug=user_id,
                    plan=user_data["plan"],
                    name=f"{self.RELEASE_DEMO_LABEL} Org {user_data['username']}",
                )
                user = user_store.get_user_by_email(user_data["email"])
                if user is None:
                    user = user_store.create_user(
                        username=user_data["username"],
                        email=user_data["email"],
                        password=self._hash_password(user_data["password"]),
                        plan=user_data["plan"],
                        organization_id=org.id,
                    )
                    results["users_created"] += 1

                user.organization_id = org.id
                user.role = user_data["role"]
                user.is_active = True
                user.plan = user_data["plan"]
                user.username = user_data["username"]
                user.onboarding_completed = True
                user.cid_enabled = True
                user.account_status = "active"
                user.signup_type = "cid_user"
                user.access_level = (
                    "full"
                    if user_data["plan"] in {"studio", "enterprise"}
                    else "standard"
                )
                user.program = (
                    user_data["plan"]
                    if user_data["plan"]
                    in {"creator", "producer", "studio", "enterprise"}
                    else "demo"
                )
                user.company = self.RELEASE_DEMO_LABEL
                user.country = "ES"

                await self._upsert_demo_user_in_db(
                    session=session,
                    user=user,
                    role=user_data["role"],
                    organization_id=org.id,
                )

                results["projects_created"] += await self._seed_projects_for_org(
                    session,
                    organization_id=org.id,
                    owner_user_id=user.user_id,
                    project_templates=project_map.get(user_id, self.DEMO_PROJECTS[:1]),
                )

            await session.commit()

        for preset_data in self.DEMO_PRESETS:
            try:
                preset_service.create_preset(
                    name=preset_data["name"],
                    workflow_key=preset_data["workflow_key"],
                    inputs=preset_data["inputs"],
                    user_id="system",
                    description=preset_data["description"],
                    tags=preset_data["tags"],
                    is_public=preset_data["is_public"],
                )
                results["presets_created"] += 1
            except Exception:
                pass

        narrative_results = await self.seed_narrative_to_db()
        if narrative_results.get("status") != "already_seeded":
            results["projects_created"] += 1
            results["sequences_created"] = len(self.DEMO_SEQUENCES)
            results["scenes_created"] = len(self.DEMO_SCENES)
            results["characters_created"] = len(self.DEMO_CHARACTERS)

        self._seed_demo_jobs()
        results["jobs_created"] = len(self._demo_jobs.get("demo_studio", []))

        self._seeded = True

        return results

    async def seed_narrative_to_db(self) -> Dict[str, Any]:
        """Seed the narrative project to the database asynchronously (idempotent)."""
        from database import AsyncSessionLocal
        from models.core import Project
        from models.narrative import Sequence, Scene, Character
        from models.visual import Shot, VisualAsset
        from models.postproduction import Clip, AssemblyCut
        from models.delivery import Deliverable
        from models.review import Review, ApprovalDecision
        from sqlalchemy import select

        async with AsyncSessionLocal() as session:
            existing_project = await session.execute(
                select(Project).where(Project.id == self.DEMO_NARRATIVE_PROJECT["id"])
            )
            if existing_project.scalar_one_or_none():
                return {
                    "message": "Narrative project already exists",
                    "project_id": self.DEMO_NARRATIVE_PROJECT["id"],
                    "status": "already_seeded",
                }

            org = await self._get_or_create_demo_organization(
                session,
                slug="demo_studio",
                plan="studio",
                name=f"{self.RELEASE_DEMO_LABEL} Org demo_studio",
            )

            project = Project(
                id=self.DEMO_NARRATIVE_PROJECT["id"],
                organization_id=org.id,
                name=self.DEMO_NARRATIVE_PROJECT["name"],
                description=self.DEMO_NARRATIVE_PROJECT["description"],
                status=self.DEMO_NARRATIVE_PROJECT["status"],
            )
            session.add(project)
            await session.flush()

            sequence_ids = []
            for seq_data in self.DEMO_SEQUENCES:
                sequence = Sequence(
                    id=uuid.uuid4().hex,
                    project_id=project.id,
                    sequence_number=seq_data["sequence_number"],
                    name=seq_data["title"],
                    description=seq_data["description"],
                )
                session.add(sequence)
                await session.flush()
                sequence_ids.append(sequence.id)

            scene_ids = []
            scene_map = {}
            for idx, scene_data in enumerate(self.DEMO_SCENES):
                sequence_id = (
                    sequence_ids[idx % len(sequence_ids)]
                    if idx < len(sequence_ids)
                    else sequence_ids[0]
                )
                scene = Scene(
                    id=uuid.uuid4().hex,
                    project_id=project.id,
                    scene_number=scene_data["scene_number"],
                    name=f"Escena {scene_data['scene_number']}",
                    description=(
                        f"{scene_data['setting']} {scene_data['location']} - {scene_data['time_of_day']}. "
                        f"{scene_data['action_text']}"
                    ),
                )
                session.add(scene)
                await session.flush()
                scene_ids.append(scene.id)
                scene_map[scene.scene_number] = scene.id

            character_ids = []
            for char_data in self.DEMO_CHARACTERS:
                character = Character(
                    id=uuid.uuid4().hex,
                    project_id=project.id,
                    name=char_data["name"],
                    description=char_data["description"],
                )
                session.add(character)
                await session.flush()
                character_ids.append(character.id)

            shot_ids = []
            shot_map = {}
            for shot_data in self.DEMO_SHOTS:
                scene_id = scene_map.get(shot_data["scene_number"])
                if scene_id:
                    shot = Shot(
                        id=uuid.uuid4().hex,
                        project_id=project.id,
                        scene_id=scene_id,
                        shot_number=shot_data["shot_number"],
                        name=(
                            f"Shot {shot_data['scene_number']}-{shot_data['shot_number']}"
                        ),
                        description=(
                            f"{shot_data['shot_size']} / {shot_data['camera_angle']}"
                        ),
                        status=shot_data["status"],
                    )
                    session.add(shot)
                    await session.flush()
                    shot_ids.append(shot.id)
                    shot_map[(shot_data["scene_number"], shot_data["shot_number"])] = (
                        shot.id
                    )

            for asset_data in self.DEMO_ASSETS:
                shot_key = (asset_data["shot_scene"], asset_data["shot_number"])
                shot_id = shot_map.get(shot_key)
                if shot_id:
                    asset = VisualAsset(
                        id=uuid.uuid4().hex,
                        project_id=project.id,
                        name=(
                            f"Asset {asset_data['shot_scene']}-{asset_data['shot_number']}"
                        ),
                        asset_type="image",
                        file_path=f"/assets/demo/{asset_data['shot_scene']}_{asset_data['shot_number']}.jpg",
                        metadata_json=json.dumps(
                            {
                                "source": "demo_seed",
                                "shot_id": shot_id,
                                "status": asset_data["status"],
                                "approved": asset_data.get("is_approved", False),
                            },
                            ensure_ascii=False,
                        ),
                    )
                    session.add(asset)

            clip_ids = []
            clip_map = {}
            for idx, clip_data in enumerate(self.DEMO_CLIPS):
                scene_id = scene_map.get(clip_data["scene_number"])
                if scene_id:
                    clip = Clip(
                        id=uuid.uuid4().hex,
                        project_id=project.id,
                        scene_id=scene_id,
                        name=f"Clip {idx + 1}",
                        source_file=f"/clips/demo/clip_{idx + 1}.mp4",
                        duration_seconds=clip_data["duration"],
                    )
                    session.add(clip)
                    await session.flush()
                    clip_ids.append(clip.id)
                    clip_map[f"clip-{idx + 1}"] = clip.id

            for assembly_data in self.DEMO_ASSEMBLIES:
                assembly = AssemblyCut(
                    id=uuid.uuid4().hex,
                    project_id=project.id,
                    name=assembly_data["name"],
                    description=assembly_data.get("description"),
                    status=assembly_data.get("status", "draft"),
                )
                session.add(assembly)
                await session.flush()
                assembly_id = assembly.id

            latest_review_id = None
            for review_data in self.DEMO_REVIEWS:
                review = Review(
                    project_id=project.id,
                    target_id=review_data["target_id"],
                    target_type=review_data["target_type"],
                    status=review_data["status"],
                )
                session.add(review)
                await session.flush()
                latest_review_id = review.id

                for decision_data in self.DEMO_DECISIONS:
                    if decision_data["review_index"] == self.DEMO_REVIEWS.index(
                        review_data
                    ):
                        decision = ApprovalDecision(
                            review_id=latest_review_id,
                            author_name="Director",
                            status_applied=decision_data["status_applied"],
                            rationale_note=decision_data.get("rationale_note"),
                        )
                        session.add(decision)

            for index, deliverable_data in enumerate(self.DEMO_DELIVERABLES):
                deliverable = Deliverable(
                    project_id=project.id,
                    source_review_id=latest_review_id if index == 0 else None,
                    name=deliverable_data["name"],
                    format_type=deliverable_data["format_type"],
                    delivery_payload={"export": True, "version": "1.0"},
                    status=deliverable_data["status"],
                )
                session.add(deliverable)

            await session.commit()

            return {
                "project_id": project.id,
                "sequences": len(sequence_ids),
                "scenes": len(scene_ids),
                "characters": len(character_ids),
                "shots": len(shot_ids),
                "assets": len(self.DEMO_ASSETS),
                "clips": len(clip_ids),
                "assemblies": len(self.DEMO_ASSEMBLIES),
            }

    def _seed_narrative_project(self) -> None:
        pass

    def _seed_project(self, project: Dict) -> None:
        pass

    def _seed_demo_jobs(self) -> None:
        statuses = ["succeeded", "succeeded", "succeeded", "running", "queued"]
        base_time = datetime.utcnow()

        for user_id in ["demo_studio", "demo_creator"]:
            jobs = []
            for i, status in enumerate(statuses):
                job = {
                    "job_id": f"demo_{user_id}_{i + 1:03d}",
                    "task_type": random.choice(["still", "video", "dubbing"]),
                    "workflow_key": random.choice(
                        [
                            "still_text_to_image_pro",
                            "still_img2img_cinematic",
                            "video_text_to_video_base",
                            "dubbing_tts_es_es",
                        ]
                    ),
                    "status": status,
                    "backend": random.choice(["still", "video", "dubbing"]),
                    "created_at": (base_time - timedelta(hours=i * 2)).isoformat(),
                    "started_at": (base_time - timedelta(hours=i * 2 - 1)).isoformat()
                    if status != "queued"
                    else None,
                    "completed_at": (base_time - timedelta(hours=i * 2 - 2)).isoformat()
                    if status == "succeeded"
                    else None,
                    "error": None if status != "failed" else "Simulated error",
                }
                jobs.append(job)

            self._demo_jobs[user_id] = jobs

    def _hash_password(self, password: str) -> str:
        import bcrypt

        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    async def reset_demo_data(self) -> Dict[str, Any]:
        self._demo_jobs.clear()
        self._seeded = False
        results = await self.seed_demo_data()
        results["message"] = "Demo data reset successfully"
        return results

    def get_demo_users(self) -> List[Dict[str, Any]]:
        return [
            {
                "user_id": user_id,
                "username": data["username"],
                "email": data["email"],
                "plan": data["plan"],
                "role": data["role"],
                "password_hint": "Usar la contraseña: demo123 (admin: admin123)",
            }
            for user_id, data in self.DEMO_USERS.items()
        ]

    def get_demo_jobs(self, user_id: str) -> List[Dict[str, Any]]:
        return self._demo_jobs.get(user_id, [])

    def is_demo_user(self, user_id: str) -> bool:
        return user_id in self.DEMO_USERS or user_id.startswith("demo_")

    def is_seeded(self) -> bool:
        return self._seeded

    def get_demo_status(self) -> Dict[str, Any]:
        return {
            "seeded": self._seeded,
            "demo_users_count": len(self.DEMO_USERS),
            "demo_projects_count": len(self.DEMO_PROJECTS),
            "demo_presets_count": len(self.DEMO_PRESETS),
            "total_demo_jobs": sum(len(jobs) for jobs in self._demo_jobs.values()),
        }


demo_service = DemoService()
