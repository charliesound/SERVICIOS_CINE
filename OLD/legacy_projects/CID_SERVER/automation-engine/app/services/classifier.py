from app.schemas.lead_event import LeadEvent
from app.schemas.script_event import ScriptEvent
from app.schemas.routing_result import LeadRoutingResult, ScriptRoutingResult


class Classifier:
    def classify_lead(self, event: LeadEvent) -> dict:
        payload = event.payload
        text = f"{payload.company or ''} {payload.message or ''} {payload.project_interest or ''} {payload.source_channel or ''}".lower()

        notes = []
        classification = "general"
        lead_type = "unknown"
        priority = "normal"
        recommended_campaign = "cid_general"
        recommended_target = "equipo_comercial"
        recommended_secondary_target = None
        next_action = "standard_followup"

        production_terms = [
            "productora", "studio", "estudio", "largometraje", "serie",
            "pitch", "fondos", "storyboard", "teaser", "trailer", "guion"
        ]

        if payload.company:
            notes.append("Empresa detectada en el lead.")

        if any(term in text for term in production_terms):
            lead_type = "productora"
            classification = "comercial"
            priority = "hot"
            recommended_campaign = "cid_enterprise"
            recommended_target = "equipo_ventas"
            recommended_secondary_target = "cine_ai_platform"
            next_action = "contact_within_24h"
            notes.append("Perfil productora o proyecto audiovisual detectado.")

        if "storyboard" in text or "pitch" in text or "demo" in text:
            classification = "storyboard_demo"
            recommended_campaign = "cid_storyboard_ia"
            recommended_secondary_target = "cine_ai_platform"
            notes.append("Interés claro en demo o storyboard IA.")

        if len((payload.message or "").strip()) > 180:
            priority = "hot"
            notes.append("Mensaje largo: mayor intención o necesidad detallada.")

        if not payload.company and len((payload.message or "").strip()) < 30:
            priority = "low"
            lead_type = "consulta_simple"
            recommended_campaign = "cid_low_touch"
            recommended_target = "web_followup"
            next_action = "email_auto_reply"
            notes.append("Lead poco detallado y sin empresa.")

        return LeadRoutingResult(
            classification=classification,
            lead_type=lead_type,
            priority=priority,
            recommended_campaign=recommended_campaign,
            recommended_target=recommended_target,
            recommended_secondary_target=recommended_secondary_target,
            next_action=next_action,
            notes=notes or ["Clasificación generada por reglas locales."],
        ).model_dump()

    def classify_script(self, event: ScriptEvent) -> dict:
        text = (event.payload.text or "").lower()
        goal = (event.payload.goal or "").lower()
        notes = []

        content_type = "text_brief"
        recommended_pipeline = "manual_review"
        priority = "normal"

        if "int." in text or "ext." in text or "escena" in text or "secuencia" in text:
            content_type = "scene_script"
            recommended_pipeline = "extract_sequence_render"
            notes.append("Formato compatible con escena o guion técnico.")

        if "storyboard" in goal or "demo" in goal:
            recommended_pipeline = "extract_sequence_render"
            notes.append("Objetivo orientado a storyboard demo.")

        if len(text) > 500:
            priority = "high"
            notes.append("Texto extenso: conviene pipeline estructurado.")

        if recommended_pipeline == "manual_review" and len(text) < 80:
            notes.append("Texto corto: mejor revisión manual o briefing.")

        return ScriptRoutingResult(
            content_type=content_type,
            recommended_pipeline=recommended_pipeline,
            priority=priority,
            notes=notes or ["Clasificación de script por reglas locales."],
        ).model_dump()
