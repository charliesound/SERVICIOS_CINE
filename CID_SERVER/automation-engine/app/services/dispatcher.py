import logging

from app.schemas.lead_event import LeadEvent
from app.schemas.script_event import ScriptEvent
from app.schemas.routing_result import RoutingResult, ScriptRoutingResult
from app.services.classifier import Classifier
from app.handlers.cid_handler import CIDHandler
from app.handlers.cine_handler import CineHandler
from app.handlers.web_handler import WebHandler

logger = logging.getLogger(__name__)


class Dispatcher:
    def __init__(self):
        self.classifier = Classifier()
        self.cid_handler = CIDHandler()
        self.cine_handler = CineHandler()
        self.web_handler = WebHandler()

    def _select_handlers(self, classification: str) -> list[str]:
        routing_map = {
            "storyboard_ia": ["cine_ai_platform", "web_ailink_cinema"],
            "voz_doblaje": ["cid", "cine_ai_platform"],
            "guion_ia": ["cid", "web_ailink_cinema"],
            "produccion_general": ["cid", "cine_ai_platform", "web_ailink_cinema"],
        }
        return routing_map.get(classification, ["cid"])

    async def route_lead(self, event: LeadEvent) -> RoutingResult:
        classification_data = self.classifier.classify_lead(event)

        classification = classification_data.get("classification", "produccion_general")
        priority = classification_data.get("priority", "medium")
        lead_type = classification_data.get("lead_type", "inbound_lead")

        targets = self._select_handlers(classification)
        primary = targets[0] if targets else "cid"
        secondary = targets[1] if len(targets) > 1 else ""

        campaign_map = {
            "storyboard_ia": "storyboard_ia_launch",
            "voz_doblaje": "voice_dubbing_campaign",
            "guion_ia": "script_ai_campaign",
            "produccion_general": "general_demo_campaign",
        }
        campaign = campaign_map.get(classification, "general_demo_campaign")

        action_map = {
            "high": "immediate_outreach",
            "medium": "schedule_demo",
            "low": "add_to_nurture",
        }
        next_action = action_map.get(priority, "review")

        notes = f"Routed via {classification_data.get('confidence', 'rule_based')}. "
        notes += f"Targets: {', '.join(targets)}"

        result = RoutingResult(
            ok=True,
            classification=classification,
            lead_type=lead_type,
            priority=priority,
            recommended_campaign=campaign,
            recommended_target=primary,
            recommended_secondary_target=secondary,
            next_action=next_action,
            notes=notes,
        )

        logger.info("Lead routed: %s -> %s (priority=%s)", event.payload.email or "unknown", classification, priority)
        return result

    async def route_script(self, event: ScriptEvent) -> ScriptRoutingResult:
        classification_data = self.classifier.classify_script(event)

        content_type = classification_data.get("content_type", "script_general")
        pipeline = classification_data.get("recommended_pipeline", "script_analysis_pipeline")
        priority = classification_data.get("priority", "medium")

        notes = f"Content: {content_type}. Pipeline: {pipeline}. "
        notes += f"Confidence: {classification_data.get('confidence', 'rule_based')}"

        result = ScriptRoutingResult(
            ok=True,
            content_type=content_type,
            recommended_pipeline=pipeline,
            priority=priority,
            notes=notes,
        )

        logger.info("Script routed: %s -> %s (priority=%s)", event.payload.title or "untitled", content_type, priority)
        return result
