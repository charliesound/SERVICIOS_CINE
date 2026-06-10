from __future__ import annotations

import os
import sys
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://cid_test_user@localhost:5432/cid_test",
)
os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)
os.environ.setdefault("APP_SECRET_KEY", "a" * 32)

from database import get_db
from dependencies.ai_job_orchestration import get_ai_job_orchestration_service
from dependencies.tenant_context import get_tenant_context, require_write_permission
from schemas.auth_schema import TenantContext


ROUTE_MODULE_PATH = SRC_DIR / "routes" / "ai_job_routes.py"
spec = importlib.util.spec_from_file_location("ai_job_routes_under_test", ROUTE_MODULE_PATH)
assert spec is not None and spec.loader is not None
ai_job_routes_under_test = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai_job_routes_under_test)

router = ai_job_routes_under_test.router


class FakeAIJobService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []
        self.insufficient_check = False

    def _result(self, message: str = "ok", accounting: object | None = None):
        return SimpleNamespace(
            job=SimpleNamespace(
                id="job-1",
                organization_id="org-tenant",
                user_id="user-tenant",
                operation_type="image_generation",
                status="created",
                estimated_credits=1,
            ),
            transition_plan=SimpleNamespace(from_status="created", to_status="estimated"),
            accounting_result=accounting,
            message=message,
        )

    async def create_ai_job(self, session, request):
        del session
        self.calls.append(("create", request))
        return self._result("created")

    async def estimate_ai_job(self, session, request):
        del session
        self.calls.append(("estimate", request))
        return self._result("estimated")

    async def check_ai_job_credits(self, session, request):
        del session
        self.calls.append(("check", request))
        accounting = SimpleNamespace(
            sufficient=not self.insufficient_check,
            required_credits=10,
            available_credits=0 if self.insufficient_check else 50,
        )
        return self._result("checked", accounting=accounting)

    async def reserve_ai_job_credits(self, session, request):
        del session
        self.calls.append(("reserve", request))
        return self._result("reserved")

    async def consume_ai_job_credits(self, session, request):
        del session
        self.calls.append(("consume", request))
        return self._result("consumed")

    async def release_ai_job_credits(self, session, request):
        del session
        self.calls.append(("release", request))
        return self._result("released")

    async def get_ai_job(self, session, organization_id, job_id):
        del session
        self.calls.append(("get", (organization_id, job_id)))
        return SimpleNamespace(
            id=job_id,
            organization_id=organization_id,
            user_id="user-tenant",
            operation_type="image_generation",
            status="created",
        )

    async def list_ai_jobs(self, session, request):
        del session
        self.calls.append(("list", request))
        return [
            SimpleNamespace(
                id="job-1",
                organization_id=request.organization_id,
                user_id="user-tenant",
                operation_type="image_generation",
                status=request.status or "created",
            )
        ], "job-next"

    async def get_ai_job_history(self, session, organization_id, job_id):
        del session
        self.calls.append(("history", (organization_id, job_id)))
        return SimpleNamespace(
            job_id=job_id,
            events=[{"status": "created", "timestamp": "2026-06-09T10:00:00"}],
        )


@pytest.fixture
def fake_service() -> FakeAIJobService:
    return FakeAIJobService()


def _tenant(auth_method: str = "jwt", role: str = "producer") -> TenantContext:
    return TenantContext(
        user_id="user-tenant",
        organization_id="org-tenant",
        plan="pro",
        role=role,
        is_admin=False,
        auth_method=auth_method,
    )


@pytest.fixture
def app(fake_service: FakeAIJobService) -> FastAPI:
    application = FastAPI()
    application.include_router(router)

    async def override_db():
        yield object()

    async def override_tenant():
        return _tenant()

    application.dependency_overrides[get_db] = override_db
    application.dependency_overrides[get_tenant_context] = override_tenant
    application.dependency_overrides[require_write_permission] = override_tenant
    application.dependency_overrides[get_ai_job_orchestration_service] = lambda: fake_service
    return application


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


def test_create_uses_tenant_organization_and_user(client: TestClient, fake_service: FakeAIJobService) -> None:
    response = client.post(
        "/api/v1/ai-jobs",
        json={"operation_type": "image_generation", "project_id": "project-1"},
    )

    assert response.status_code == 200
    call, request = fake_service.calls[-1]
    assert call == "create"
    assert request.organization_id == "org-tenant"
    assert request.user_id == "user-tenant"
    assert request.project_id == "project-1"


def test_create_rejects_organization_id_in_body(client: TestClient) -> None:
    response = client.post(
        "/api/v1/ai-jobs",
        json={"operation_type": "image_generation", "organization_id": "org-forged"},
    )

    assert response.status_code == 422


def test_estimate_uses_path_job_id_and_tenant(client: TestClient, fake_service: FakeAIJobService) -> None:
    response = client.post("/api/v1/ai-jobs/job-path/estimate", json={})

    assert response.status_code == 200
    call, request = fake_service.calls[-1]
    assert call == "estimate"
    assert request.organization_id == "org-tenant"
    assert request.job_id == "job-path"
    assert request.estimated_credits is None


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        ("/api/v1/ai-jobs/job-1/estimate", {"estimated_credits": 7}),
        ("/api/v1/ai-jobs/job-1/check-credits", {"estimated_credits": 7}),
        ("/api/v1/ai-jobs/job-1/reserve", {"estimated_credits": 7}),
    ],
)
def test_credit_override_rejected_for_normal_jwt_caller(
    client: TestClient,
    path: str,
    payload: dict,
) -> None:
    response = client.post(path, json=payload)
    assert response.status_code == 403


@pytest.mark.parametrize(
    ("path", "expected_call"),
    [
        ("/api/v1/ai-jobs/job-1/estimate", "estimate"),
        ("/api/v1/ai-jobs/job-1/check-credits", "check"),
        ("/api/v1/ai-jobs/job-1/reserve", "reserve"),
    ],
)
def test_internal_api_key_can_send_estimated_credits(
    app: FastAPI,
    fake_service: FakeAIJobService,
    path: str,
    expected_call: str,
) -> None:
    async def override_internal_tenant():
        return _tenant(auth_method="internal_api_key")

    app.dependency_overrides[get_tenant_context] = override_internal_tenant
    app.dependency_overrides[require_write_permission] = override_internal_tenant
    with TestClient(app) as test_client:
        response = test_client.post(path, json={"estimated_credits": 7})

    assert response.status_code == 200
    call, request = fake_service.calls[-1]
    assert call == expected_call
    assert request.estimated_credits == 7


def test_check_credits_maps_insufficient_result_to_402(
    client: TestClient,
    fake_service: FakeAIJobService,
) -> None:
    fake_service.insufficient_check = True

    response = client.post("/api/v1/ai-jobs/job-1/check-credits", json={})

    assert response.status_code == 402


def test_reserve_route_requires_write_permission_dependency() -> None:
    source = (SRC_DIR / "routes" / "ai_job_routes.py").read_text()
    reserve_block = source[source.index("async def reserve_ai_job_credits_endpoint") :]
    reserve_block = reserve_block[: reserve_block.index("@router.post", 1)]
    assert "Depends(require_write_permission)" in reserve_block


def test_router_does_not_import_low_level_ai_job_dependencies() -> None:
    source = ROUTE_MODULE_PATH.read_text()
    assert "AIJobCostingService" not in source
    assert "AIJobAccountingGateway" not in source
    assert "AIJobRepository" not in source


def test_consume_rejects_non_internal_caller(client: TestClient) -> None:
    response = client.post("/api/v1/ai-jobs/job-1/consume", json={"actual_credits": 1})
    assert response.status_code == 403


def test_release_rejects_non_internal_caller(client: TestClient) -> None:
    response = client.post("/api/v1/ai-jobs/job-1/release", json={"release_credits": 1})
    assert response.status_code == 403


def test_consume_internal_caller_invokes_service(app: FastAPI, fake_service: FakeAIJobService) -> None:
    async def override_internal_tenant():
        return _tenant(auth_method="internal_api_key")

    app.dependency_overrides[get_tenant_context] = override_internal_tenant
    with TestClient(app) as test_client:
        response = test_client.post("/api/v1/ai-jobs/job-1/consume", json={"actual_credits": 3})

    assert response.status_code == 200
    call, request = fake_service.calls[-1]
    assert call == "consume"
    assert request.organization_id == "org-tenant"
    assert request.job_id == "job-1"
    assert request.actual_credits == 3


def test_release_internal_caller_invokes_service(app: FastAPI, fake_service: FakeAIJobService) -> None:
    async def override_internal_tenant():
        return _tenant(auth_method="internal_api_key")

    app.dependency_overrides[get_tenant_context] = override_internal_tenant
    with TestClient(app) as test_client:
        response = test_client.post("/api/v1/ai-jobs/job-1/release", json={"release_credits": 2})

    assert response.status_code == 200
    call, request = fake_service.calls[-1]
    assert call == "release"
    assert request.organization_id == "org-tenant"
    assert request.job_id == "job-1"
    assert request.release_credits == 2


def test_get_ai_job_uses_tenant_and_path_job_id(client: TestClient, fake_service: FakeAIJobService) -> None:
    response = client.get("/api/v1/ai-jobs/job-path")

    assert response.status_code == 200
    assert response.json()["job"]["id"] == "job-path"
    assert fake_service.calls[-1] == ("get", ("org-tenant", "job-path"))


def test_list_ai_jobs_uses_tenant_and_filters(client: TestClient, fake_service: FakeAIJobService) -> None:
    response = client.get(
        "/api/v1/ai-jobs",
        params={"status": "created", "project_id": "project-1", "limit": 25},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["items"][0]["organization_id"] == "org-tenant"
    assert body["next_cursor"] == "job-next"
    call, request = fake_service.calls[-1]
    assert call == "list"
    assert request.organization_id == "org-tenant"
    assert request.status == "created"
    assert request.project_id == "project-1"
    assert request.limit == 25


def test_list_ai_jobs_rejects_organization_id_query(client: TestClient) -> None:
    response = client.get("/api/v1/ai-jobs", params={"organization_id": "org-forged"})
    assert response.status_code == 422


def test_get_ai_job_history_uses_tenant_and_path_job_id(
    client: TestClient,
    fake_service: FakeAIJobService,
) -> None:
    response = client.get("/api/v1/ai-jobs/job-path/history")

    assert response.status_code == 200
    assert response.json()["job_id"] == "job-path"
    assert fake_service.calls[-1] == ("history", ("org-tenant", "job-path"))


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        ("/api/v1/ai-jobs/job-1/estimate", {"job_id": "body-job"}),
        ("/api/v1/ai-jobs/job-1/check-credits", {"organization_id": "org-forged"}),
        ("/api/v1/ai-jobs/job-1/reserve", {"amount": 999}),
        ("/api/v1/ai-jobs/job-1/consume", {"job_id": "body-job"}),
        ("/api/v1/ai-jobs/job-1/release", {"organization_id": "org-forged"}),
    ],
)
def test_action_bodies_reject_forbidden_fields(client: TestClient, path: str, payload: dict) -> None:
    response = client.post(path, json=payload)
    assert response.status_code in {403, 422}
