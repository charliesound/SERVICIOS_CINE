from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from models.client_feedback import (
    CIDClientFeedback,
    CIDFeedbackMemoryEntry,
    CIDAnswerFeedbackEvent,
    CIDProjectLearningRule,
    CIDOrganizationLearningPreference,
    CIDFeedbackAudit,
    CID_FEEDBACK_TYPES,
    CID_FEEDBACK_SCOPES,
    CID_FEEDBACK_STATUSES,
    CID_FEEDBACK_AUDIT_ACTIONS,
    CID_LEARNING_RULE_TYPES,
)
from schemas.client_feedback_schema import (
    CIDClientFeedbackCreate,
    CIDClientFeedbackResponse,
    CIDClientFeedbackUpdate,
    CIDFeedbackListResponse,
    CIDFeedbackMemoryEntryCreate,
    CIDFeedbackMemoryEntryResponse,
    CIDAnswerFeedbackEventCreate,
    CIDAnswerFeedbackEventResponse,
    CIDProjectLearningRuleCreate,
    CIDProjectLearningRuleResponse,
    CIDProjectLearningRuleUpdate,
    CIDOrganizationLearningPreferenceCreate,
    CIDOrganizationLearningPreferenceResponse,
    CIDOrganizationLearningPreferenceUpdate,
    CIDFeedbackAuditResponse,
)


class TestCIDEnums:
    def test_feedback_types_defined(self) -> None:
        assert "answer_helpful" in CID_FEEDBACK_TYPES
        assert "answer_wrong" in CID_FEEDBACK_TYPES
        assert "source_blacklist" in CID_FEEDBACK_TYPES
        assert "prompt_failure_case" in CID_FEEDBACK_TYPES

    def test_feedback_scopes_defined(self) -> None:
        assert "project_feedback" in CID_FEEDBACK_SCOPES
        assert "organization_feedback" in CID_FEEDBACK_SCOPES
        assert "answer_feedback" in CID_FEEDBACK_SCOPES

    def test_feedback_statuses_defined(self) -> None:
        assert "pending" in CID_FEEDBACK_STATUSES
        assert "approved" in CID_FEEDBACK_STATUSES
        assert "rejected" in CID_FEEDBACK_STATUSES
        assert "archived" in CID_FEEDBACK_STATUSES

    def test_audit_actions_defined(self) -> None:
        assert "created" in CID_FEEDBACK_AUDIT_ACTIONS
        assert "approved" in CID_FEEDBACK_AUDIT_ACTIONS
        assert "indexed" in CID_FEEDBACK_AUDIT_ACTIONS
        assert "deindexed" in CID_FEEDBACK_AUDIT_ACTIONS

    def test_learning_rule_types_defined(self) -> None:
        assert "style_preference" in CID_LEARNING_RULE_TYPES
        assert "project_rule" in CID_LEARNING_RULE_TYPES
        assert "source_blacklist" in CID_LEARNING_RULE_TYPES


class TestCIDClientFeedbackModel:
    def test_table_name(self) -> None:
        assert CIDClientFeedback.__tablename__ == "cid_client_feedback"

    def test_primary_key_column(self) -> None:
        col = CIDClientFeedback.__table__.c["id"]
        assert col.primary_key

    def test_required_columns_not_nullable(self) -> None:
        for name in ("organization_id", "project_id", "user_id", "feedback_type"):
            assert not CIDClientFeedback.__table__.c[name].nullable

    def test_optional_columns_nullable(self) -> None:
        for name in ("original_question", "original_answer", "corrected_answer", "feedback_text"):
            assert CIDClientFeedback.__table__.c[name].nullable

    def test_has_check_constraints(self) -> None:
        cks = [
            c for c in CIDClientFeedback.__table__.constraints
            if hasattr(c, "name") and c.name and c.name.startswith("ck_cf_")
        ]
        assert len(cks) >= 3

    def test_has_indexes(self) -> None:
        idx_names = {i.name for i in CIDClientFeedback.__table__.indexes}
        assert "ix_cf_org_project" in idx_names
        assert "ix_cf_user_id" in idx_names
        assert "ix_cf_created_at" in idx_names


class TestCIDFeedbackMemoryEntryModel:
    def test_table_name(self) -> None:
        assert CIDFeedbackMemoryEntry.__tablename__ == "cid_feedback_memory_entries"

    def test_foreign_key_to_feedback(self) -> None:
        fks = CIDFeedbackMemoryEntry.__table__.foreign_keys
        fk_cols = {fk.parent.name for fk in fks}
        assert "feedback_id" in fk_cols

    def test_required_columns(self) -> None:
        for name in ("organization_id", "project_id", "source_type", "source_id"):
            assert not CIDFeedbackMemoryEntry.__table__.c[name].nullable


class TestCIDAnswerFeedbackEventModel:
    def test_table_name(self) -> None:
        assert CIDAnswerFeedbackEvent.__tablename__ == "cid_answer_feedback_events"

    def test_foreign_key_to_feedback(self) -> None:
        fks = CIDAnswerFeedbackEvent.__table__.foreign_keys
        fk_cols = {fk.parent.name for fk in fks}
        assert "feedback_id" in fk_cols

    def test_required_columns(self) -> None:
        for name in ("organization_id", "project_id", "answer_id", "action"):
            assert not CIDAnswerFeedbackEvent.__table__.c[name].nullable


class TestCIDProjectLearningRuleModel:
    def test_table_name(self) -> None:
        assert CIDProjectLearningRule.__tablename__ == "cid_project_learning_rules"

    def test_required_columns(self) -> None:
        for name in ("organization_id", "project_id", "rule_type", "rule_value"):
            assert not CIDProjectLearningRule.__table__.c[name].nullable

    def test_has_check_constraint(self) -> None:
        cks = [
            c for c in CIDProjectLearningRule.__table__.constraints
            if hasattr(c, "name") and c.name == "ck_cplr_rule_type"
        ]
        assert len(cks) == 1


class TestCIDOrganizationLearningPreferenceModel:
    def test_table_name(self) -> None:
        assert CIDOrganizationLearningPreference.__tablename__ == "cid_organization_learning_preferences"

    def test_required_columns(self) -> None:
        for name in ("organization_id", "preference_type", "preference_value"):
            assert not CIDOrganizationLearningPreference.__table__.c[name].nullable


class TestCIDFeedbackAuditModel:
    def test_table_name(self) -> None:
        assert CIDFeedbackAudit.__tablename__ == "cid_feedback_audit"

    def test_foreign_key_to_feedback(self) -> None:
        fks = CIDFeedbackAudit.__table__.foreign_keys
        fk_cols = {fk.parent.name for fk in fks}
        assert "feedback_id" in fk_cols

    def test_required_columns(self) -> None:
        for name in ("organization_id", "project_id", "user_id", "action"):
            assert not CIDFeedbackAudit.__table__.c[name].nullable

    def test_column_nullable(self) -> None:
        assert CIDFeedbackAudit.__table__.c["previous_status"].nullable
        assert CIDFeedbackAudit.__table__.c["new_status"].nullable


class TestCIDClientFeedbackSchemaCreate:
    def test_create_with_required_fields(self) -> None:
        data = CIDClientFeedbackCreate(
            project_id="proj-1",
            feedback_type="answer_helpful",
        )
        assert data.project_id == "proj-1"
        assert data.feedback_type == "answer_helpful"
        assert data.feedback_scope == "project_feedback"
        assert data.approved_for_memory is False

    def test_create_with_all_fields(self) -> None:
        data = CIDClientFeedbackCreate(
            project_id="proj-1",
            feedback_type="approved_correction",
            feedback_scope="answer_feedback",
            original_question="What happens?",
            original_answer="Nothing.",
            corrected_answer="Something happens.",
            feedback_text="The answer was wrong.",
            source_ids=["src-1", "src-2"],
            source_types=["script_text", "storyboard_shot"],
            approved_for_memory=True,
            confidence=0.95,
            model_used="qwen2.5:14B",
            metadata_json={"key": "value"},
        )
        assert data.source_ids == ["src-1", "src-2"]
        assert data.confidence == 0.95
        assert data.metadata_json == {"key": "value"}


class TestCIDClientFeedbackSchemaUpdate:
    def test_update_partial(self) -> None:
        data = CIDClientFeedbackUpdate(status="approved")
        assert data.status == "approved"
        assert data.feedback_text is None
        assert data.corrected_answer is None

    def test_update_empty(self) -> None:
        data = CIDClientFeedbackUpdate()
        assert data.status is None


class TestCIDClientFeedbackSchemaResponse:
    def test_response_from_attributes(self) -> None:
        data = CIDClientFeedbackResponse(
            id="fb-1",
            organization_id="org-1",
            project_id="proj-1",
            user_id="user-1",
            feedback_type="answer_helpful",
            feedback_scope="project_feedback",
            status="pending",
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
        )
        assert data.id == "fb-1"
        assert data.organization_id == "org-1"
        assert data.status == "pending"

    def test_response_optional_fields_default(self) -> None:
        data = CIDClientFeedbackResponse(
            id="fb-1",
            organization_id="org-1",
            project_id="proj-1",
            user_id="user-1",
            feedback_type="answer_helpful",
            feedback_scope="project_feedback",
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
        )
        assert data.approved_for_memory is False
        assert data.status == "pending"
        assert data.feedback_text is None


class TestCIDFeedbackListResponse:
    def test_list_response(self) -> None:
        fb = CIDClientFeedbackResponse(
            id="fb-1",
            organization_id="org-1",
            project_id="proj-1",
            user_id="user-1",
            feedback_type="answer_helpful",
            feedback_scope="project_feedback",
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
        )
        data = CIDFeedbackListResponse(
            feedbacks=[fb],
            total_count=1,
            limit=10,
            offset=0,
        )
        assert len(data.feedbacks) == 1
        assert data.total_count == 1


class TestCIDFeedbackMemoryEntrySchema:
    def test_create_memory_entry(self) -> None:
        data = CIDFeedbackMemoryEntryCreate(
            feedback_id="fb-1",
            project_id="proj-1",
            source_type="approved_correction",
            source_id="src-1",
            source_text="Corrected text",
        )
        assert data.feedback_id == "fb-1"
        assert data.source_type == "approved_correction"

    def test_memory_entry_response(self) -> None:
        data = CIDFeedbackMemoryEntryResponse(
            id="mem-1",
            feedback_id="fb-1",
            organization_id="org-1",
            project_id="proj-1",
            source_type="approved_correction",
            source_id="src-1",
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
        )
        assert data.qdrant_point_id is None
        assert data.indexed_at is None


class TestCIDAnswerFeedbackEventSchema:
    def test_create_event(self) -> None:
        data = CIDAnswerFeedbackEventCreate(
            feedback_id="fb-1",
            project_id="proj-1",
            answer_id="ans-1",
            action="approved",
        )
        assert data.action == "approved"

    def test_event_response(self) -> None:
        data = CIDAnswerFeedbackEventResponse(
            id="evt-1",
            feedback_id="fb-1",
            organization_id="org-1",
            project_id="proj-1",
            answer_id="ans-1",
            action="approved",
            created_at="2026-01-01T00:00:00",
        )
        assert data.action == "approved"


class TestCIDProjectLearningRuleSchema:
    def test_create_rule(self) -> None:
        data = CIDProjectLearningRuleCreate(
            project_id="proj-1",
            rule_type="style_preference",
            rule_value="dark tones",
        )
        assert data.rule_type == "style_preference"
        assert data.active is True
        assert data.priority == 0

    def test_update_rule(self) -> None:
        data = CIDProjectLearningRuleUpdate(active=False)
        assert data.active is False
        assert data.rule_value is None

    def test_rule_response(self) -> None:
        data = CIDProjectLearningRuleResponse(
            id="rule-1",
            organization_id="org-1",
            project_id="proj-1",
            rule_type="style_preference",
            rule_value="dark tones",
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
        )
        assert data.active is True


class TestCIDOrganizationLearningPreferenceSchema:
    def test_create_preference(self) -> None:
        data = CIDOrganizationLearningPreferenceCreate(
            preference_type="tone_preference",
            preference_value="noir",
        )
        assert data.active is True

    def test_update_preference(self) -> None:
        data = CIDOrganizationLearningPreferenceUpdate(priority=5)
        assert data.priority == 5

    def test_preference_response(self) -> None:
        data = CIDOrganizationLearningPreferenceResponse(
            id="pref-1",
            organization_id="org-1",
            preference_type="tone_preference",
            preference_value="noir",
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
        )
        assert data.preference_type == "tone_preference"


class TestCIDFeedbackAuditSchema:
    def test_audit_response(self) -> None:
        data = CIDFeedbackAuditResponse(
            id="aud-1",
            organization_id="org-1",
            project_id="proj-1",
            user_id="user-1",
            action="created",
            created_at="2026-01-01T00:00:00",
        )
        assert data.action == "created"
        assert data.previous_status is None
        assert data.new_status is None
