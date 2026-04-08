from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import unittest
from pathlib import Path
from typing import Any, Dict, Tuple
from urllib import error, request
from urllib.parse import quote


class SequenceRoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.port = cls._reserve_free_port()
        cls.base_url = f"http://127.0.0.1:{cls.port}"

        apps_api_dir = Path(__file__).resolve().parents[1]
        cls.render_jobs_sqlite_file = apps_api_dir / "data" / f"render_jobs_sequence_routes_test_{cls.port}.db"
        cls.auth_sqlite_file = apps_api_dir / "data" / f"auth_sequence_routes_test_{cls.port}.db"
        if cls.render_jobs_sqlite_file.exists():
            cls.render_jobs_sqlite_file.unlink()
        if cls.auth_sqlite_file.exists():
            cls.auth_sqlite_file.unlink()

        env = os.environ.copy()
        env.setdefault("COMFYUI_BASE_URL", "http://127.0.0.1:8188")
        env["RENDER_JOBS_SQLITE_FILE"] = str(cls.render_jobs_sqlite_file)
        env["AUTH_SQLITE_FILE"] = str(cls.auth_sqlite_file)
        env["AUTH_BOOTSTRAP_USERS"] = (
            "admin@cine.local:admin1234:admin,"
            "editor@cine.local:editor1234:editor,"
            "reviewer@cine.local:reviewer1234:reviewer,"
            "viewer@cine.local:viewer1234:viewer"
        )

        cls.process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "src.app:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(cls.port),
                "--log-level",
                "warning",
            ],
            cwd=str(apps_api_dir),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        cls._wait_until_server_is_ready()
        cls.auth_token = cls._login_bootstrap_user()

    @classmethod
    def tearDownClass(cls) -> None:
        process = getattr(cls, "process", None)
        if process is None:
            return

        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)

        if process.stdout is not None:
            process.stdout.close()
        if process.stderr is not None:
            process.stderr.close()

        render_jobs_sqlite_file = getattr(cls, "render_jobs_sqlite_file", None)
        if isinstance(render_jobs_sqlite_file, Path):
            for _ in range(10):
                if not render_jobs_sqlite_file.exists():
                    break
                try:
                    render_jobs_sqlite_file.unlink()
                    break
                except PermissionError:
                    time.sleep(0.2)

        auth_sqlite_file = getattr(cls, "auth_sqlite_file", None)
        if isinstance(auth_sqlite_file, Path):
            for _ in range(10):
                if not auth_sqlite_file.exists():
                    break
                try:
                    auth_sqlite_file.unlink()
                    break
                except PermissionError:
                    time.sleep(0.2)

    @classmethod
    def _reserve_free_port(cls) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])

    @classmethod
    def _wait_until_server_is_ready(cls) -> None:
        deadline = time.time() + 25
        health_url = f"{cls.base_url}/api/health"
        last_error: Exception | None = None

        while time.time() < deadline:
            if cls.process.poll() is not None:
                stderr_output = ""
                if cls.process.stderr is not None:
                    stderr_output = cls.process.stderr.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"uvicorn process exited before startup. stderr={stderr_output}")

            try:
                with request.urlopen(health_url, timeout=1) as response:
                    if response.status == 200:
                        return
            except Exception as error_value:  # pragma: no cover
                last_error = error_value
                time.sleep(0.2)

        raise RuntimeError(f"Timeout waiting for test API startup. last_error={last_error}")

    @classmethod
    def _login_bootstrap_user(cls) -> str:
        login_url = f"{cls.base_url}/api/auth/login"
        payload = json.dumps({"email": "admin@cine.local", "password": "admin1234"}).encode("utf-8")
        http_request = request.Request(url=login_url, data=payload, method="POST")
        http_request.add_header("Content-Type", "application/json")
        with request.urlopen(http_request, timeout=15) as response:
            raw_body = response.read().decode("utf-8")
            parsed = json.loads(raw_body) if raw_body else {}
            token = str(parsed.get("access_token") or "")
            if not token:
                raise RuntimeError(f"Bootstrap login returned no token: {parsed}")
            return token

    def _login_user(self, email: str, password: str) -> str:
        status_code, response = self._post_json(
            "/api/auth/login",
            {"email": email, "password": password},
            use_auth=False,
        )
        self.assertEqual(status_code, 200)
        token = str(response.get("access_token") or "")
        self.assertTrue(token)
        return token

    def _post_json(self, path: str, payload: Dict[str, Any], use_auth: bool = True) -> Tuple[int, Dict[str, Any]]:
        url = f"{self.base_url}{path}"
        data = json.dumps(payload).encode("utf-8")
        http_request = request.Request(url=url, data=data, method="POST")
        http_request.add_header("Content-Type", "application/json")
        if use_auth and getattr(self, "auth_token", ""):
            http_request.add_header("Authorization", f"Bearer {self.auth_token}")

        try:
            with request.urlopen(http_request, timeout=15) as response:
                raw_body = response.read().decode("utf-8")
                parsed = json.loads(raw_body) if raw_body else {}
                return int(response.status), parsed
        except error.HTTPError as http_error:
            raw_body = http_error.read().decode("utf-8")
            http_error.close()
            parsed = json.loads(raw_body) if raw_body else {}
            return int(http_error.code), parsed

    def _get_json(self, path: str, use_auth: bool = True) -> Tuple[int, Dict[str, Any]]:
        url = f"{self.base_url}{path}"
        http_request = request.Request(url=url, method="GET")
        if use_auth and getattr(self, "auth_token", ""):
            http_request.add_header("Authorization", f"Bearer {self.auth_token}")

        try:
            with request.urlopen(http_request, timeout=15) as response:
                raw_body = response.read().decode("utf-8")
                parsed = json.loads(raw_body) if raw_body else {}
                return int(response.status), parsed
        except error.HTTPError as http_error:
            raw_body = http_error.read().decode("utf-8")
            http_error.close()
            parsed = json.loads(raw_body) if raw_body else {}
            return int(http_error.code), parsed

    def _patch_json(self, path: str, payload: Dict[str, Any], use_auth: bool = True) -> Tuple[int, Dict[str, Any]]:
        url = f"{self.base_url}{path}"
        data = json.dumps(payload).encode("utf-8")
        http_request = request.Request(url=url, data=data, method="PATCH")
        http_request.add_header("Content-Type", "application/json")
        if use_auth and getattr(self, "auth_token", ""):
            http_request.add_header("Authorization", f"Bearer {self.auth_token}")

        try:
            with request.urlopen(http_request, timeout=15) as response:
                raw_body = response.read().decode("utf-8")
                parsed = json.loads(raw_body) if raw_body else {}
                return int(response.status), parsed
        except error.HTTPError as http_error:
            raw_body = http_error.read().decode("utf-8")
            http_error.close()
            parsed = json.loads(raw_body) if raw_body else {}
            return int(http_error.code), parsed

    def _delete_json(self, path: str, use_auth: bool = True) -> Tuple[int, Dict[str, Any]]:
        url = f"{self.base_url}{path}"
        http_request = request.Request(url=url, method="DELETE")
        if use_auth and getattr(self, "auth_token", ""):
            http_request.add_header("Authorization", f"Bearer {self.auth_token}")

        try:
            with request.urlopen(http_request, timeout=15) as response:
                raw_body = response.read().decode("utf-8")
                parsed = json.loads(raw_body) if raw_body else {}
                return int(response.status), parsed
        except error.HTTPError as http_error:
            raw_body = http_error.read().decode("utf-8")
            http_error.close()
            parsed = json.loads(raw_body) if raw_body else {}
            return int(http_error.code), parsed

    def _valid_payload(self) -> Dict[str, Any]:
        return {
            "script_text": (
                "INT. CASA - NOCHE. ANA entra al salon. "
                "LUIS le pregunta que paso mientras la lluvia cae afuera."
            ),
            "project_id": "project_001",
            "sequence_id": "seq_qa_001",
            "style_profile": "cinematic still",
            "continuity_mode": "strict",
        }

    def test_post_sequence_plan_valid_returns_200(self) -> None:
        status_code, response = self._post_json("/api/sequence/plan", self._valid_payload())

        self.assertEqual(status_code, 200)
        self.assertTrue(response.get("ok"))

    def test_post_sequence_plan_invalid_returns_422(self) -> None:
        status_code, response = self._post_json("/api/sequence/plan", {"project_id": "project_001"})

        self.assertEqual(status_code, 422)
        self.assertIn("detail", response)

    def test_post_sequence_plan_response_contains_required_keys(self) -> None:
        status_code, response = self._post_json("/api/sequence/plan", self._valid_payload())

        self.assertEqual(status_code, 200)
        required_keys = {
            "ok",
            "sequence_summary",
            "beats",
            "shots",
            "characters_detected",
            "locations_detected",
            "continuity_notes",
            "render_inputs",
        }
        self.assertTrue(required_keys.issubset(set(response.keys())))

    def test_post_sequence_plan_and_render_valid_returns_201(self) -> None:
        status_code, response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())

        self.assertEqual(status_code, 201)
        self.assertTrue(response.get("ok"))

    def test_post_sequence_plan_and_render_invalid_returns_422(self) -> None:
        status_code, response = self._post_json("/api/sequence/plan-and-render", {"project_id": "project_001"})

        self.assertEqual(status_code, 422)
        self.assertIn("detail", response)

    def test_post_sequence_plan_and_render_response_contains_required_keys(self) -> None:
        status_code, response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())

        self.assertEqual(status_code, 201)
        required_keys = {
            "ok",
            "request_id",
            "plan",
            "created_jobs",
            "job_count",
            "job_ids",
            "shot_job_links",
            "status_summary",
            "is_favorite",
            "tags",
            "note",
            "review_status",
            "review_note",
            "reviewed_at",
            "review_history_summary",
            "collections",
        }
        self.assertTrue(required_keys.issubset(set(response.keys())))

        self.assertEqual(response["job_count"], len(response["created_jobs"]))
        self.assertEqual(response["job_count"], len(response["job_ids"]))
        self.assertEqual(response["job_count"], len(response["shot_job_links"]))

        job_ids = set(response["job_ids"])
        for link in response["shot_job_links"]:
            self.assertIn("shot_id", link)
            self.assertTrue(link["shot_id"])
            self.assertIn("job_id", link)
            self.assertIn(link["job_id"], job_ids)

    def test_auth_login_valid_returns_token(self) -> None:
        status_code, response = self._post_json(
            "/api/auth/login",
            {"email": "editor@cine.local", "password": "editor1234"},
            use_auth=False,
        )

        self.assertEqual(status_code, 200)
        self.assertTrue(response.get("ok"))
        self.assertTrue(str(response.get("access_token") or ""))
        self.assertEqual(response.get("user", {}).get("role"), "editor")

    def test_auth_login_invalid_returns_401(self) -> None:
        status_code, response = self._post_json(
            "/api/auth/login",
            {"email": "editor@cine.local", "password": "wrong-password"},
            use_auth=False,
        )

        self.assertEqual(status_code, 401)
        self.assertFalse(response.get("ok", True))
        self.assertEqual(response.get("error", {}).get("code"), "AUTH_INVALID_CREDENTIALS")

    def test_protected_route_without_auth_returns_401(self) -> None:
        status_code, response = self._get_json("/api/sequence/plan-and-render?limit=1", use_auth=False)

        self.assertEqual(status_code, 401)
        self.assertFalse(response.get("ok", True))
        self.assertEqual(response.get("error", {}).get("code"), "AUTH_REQUIRED")

    def test_protected_route_with_insufficient_role_returns_403(self) -> None:
        viewer_token = self._login_user("viewer@cine.local", "viewer1234")
        previous_token = self.auth_token
        self.auth_token = viewer_token
        try:
            status_code, response = self._patch_json(
                "/api/sequence/notification-preferences",
                {"notifications_enabled": False},
            )
        finally:
            self.auth_token = previous_token

        self.assertEqual(status_code, 403)
        self.assertFalse(response.get("ok", True))
        self.assertEqual(response.get("error", {}).get("code"), "INSUFFICIENT_ROLE")

    def test_protected_route_with_correct_role_returns_200(self) -> None:
        status_code, response = self._patch_json(
            "/api/sequence/notification-preferences",
            {"notifications_enabled": True},
        )

        self.assertEqual(status_code, 200)
        self.assertTrue(response.get("ok"))

    def test_get_sequence_plan_and_render_recent_list_returns_200(self) -> None:
        first_status, first_response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())
        self.assertEqual(first_status, 201)

        second_payload = self._valid_payload()
        second_payload["sequence_id"] = "seq_qa_002"
        second_status, second_response = self._post_json("/api/sequence/plan-and-render", second_payload)
        self.assertEqual(second_status, 201)

        list_status, list_response = self._get_json("/api/sequence/plan-and-render?limit=5")
        self.assertEqual(list_status, 200)
        self.assertTrue(list_response.get("ok"))
        self.assertIn("executions", list_response)
        self.assertIn("limit", list_response)
        self.assertIn("count", list_response)
        self.assertLessEqual(list_response.get("count", 0), 5)

        executions = list_response.get("executions", [])
        self.assertGreaterEqual(len(executions), 2)

        required_item_keys = {
            "request_id",
            "created_at",
            "updated_at",
            "sequence_summary",
            "job_count",
            "success_ratio",
            "total_retries",
            "status_summary",
            "sequence_id",
            "project_id",
            "is_favorite",
            "tags",
            "note",
            "review_status",
            "review_note",
            "reviewed_at",
            "collection_candidate",
            "collection_added_at",
            "collection_best",
        }
        self.assertTrue(required_item_keys.issubset(set(executions[0].keys())))

        returned_ids = [item.get("request_id") for item in executions]
        self.assertIn(first_response.get("request_id"), returned_ids)
        self.assertIn(second_response.get("request_id"), returned_ids)

    def test_get_sequence_plan_and_render_recent_list_honors_limit(self) -> None:
        self._post_json("/api/sequence/plan-and-render", self._valid_payload())
        payload = self._valid_payload()
        payload["sequence_id"] = "seq_qa_limit"
        self._post_json("/api/sequence/plan-and-render", payload)

        list_status, list_response = self._get_json("/api/sequence/plan-and-render?limit=1")
        self.assertEqual(list_status, 200)
        self.assertTrue(list_response.get("ok"))
        self.assertEqual(list_response.get("limit"), 1)
        self.assertLessEqual(list_response.get("count", 0), 1)
        self.assertLessEqual(len(list_response.get("executions", [])), 1)

    def test_get_sequence_plan_and_render_recent_list_supports_filters(self) -> None:
        first_payload = self._valid_payload()
        first_payload["project_id"] = "project_filter_alpha"
        first_payload["sequence_id"] = "seq_filter_alpha"
        first_status, first_response = self._post_json("/api/sequence/plan-and-render", first_payload)
        self.assertEqual(first_status, 201)

        second_payload = self._valid_payload()
        second_payload["project_id"] = "project_filter_beta"
        second_payload["sequence_id"] = "seq_filter_beta"
        second_status, second_response = self._post_json("/api/sequence/plan-and-render", second_payload)
        self.assertEqual(second_status, 201)

        second_request_id = str(second_response.get("request_id") or "")
        request_fragment = quote(second_request_id[:8])
        list_path = (
            "/api/sequence/plan-and-render"
            f"?q={request_fragment}"
            "&project_id=project_filter_beta"
            "&sequence_id=seq_filter_beta"
            "&status=queued"
            "&limit=5"
        )
        list_status, list_response = self._get_json(list_path)

        self.assertEqual(list_status, 200)
        self.assertTrue(list_response.get("ok"))
        self.assertGreaterEqual(list_response.get("count", 0), 1)

        executions = list_response.get("executions", [])
        returned_ids = [item.get("request_id") for item in executions]
        self.assertIn(second_response.get("request_id"), returned_ids)
        self.assertNotIn(first_response.get("request_id"), returned_ids)

        for item in executions:
            self.assertEqual(item.get("project_id"), "project_filter_beta")
            self.assertEqual(item.get("sequence_id"), "seq_filter_beta")
            by_status = item.get("status_summary", {}).get("by_status", {})
            self.assertGreater(by_status.get("queued", 0), 0)

    def test_get_sequence_plan_and_render_recent_list_supports_favorite_and_tag_filters(self) -> None:
        first_status, first_response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())
        self.assertEqual(first_status, 201)

        second_payload = self._valid_payload()
        second_payload["sequence_id"] = "seq_filter_favorite_002"
        second_status, second_response = self._post_json("/api/sequence/plan-and-render", second_payload)
        self.assertEqual(second_status, 201)

        first_request_id = str(first_response.get("request_id") or "")
        second_request_id = str(second_response.get("request_id") or "")

        patch_favorite_status, _ = self._patch_json(
            f"/api/sequence/plan-and-render/{first_request_id}/meta",
            {
                "is_favorite": True,
                "tags": ["revision", "hero"],
            },
        )
        self.assertEqual(patch_favorite_status, 200)

        patch_regular_status, _ = self._patch_json(
            f"/api/sequence/plan-and-render/{second_request_id}/meta",
            {
                "is_favorite": False,
                "tags": ["baseline"],
            },
        )
        self.assertEqual(patch_regular_status, 200)

        list_status, list_response = self._get_json(
            "/api/sequence/plan-and-render?is_favorite=true&tag=revision&limit=5"
        )
        self.assertEqual(list_status, 200)
        self.assertTrue(list_response.get("ok"))

        executions = list_response.get("executions", [])
        returned_ids = [item.get("request_id") for item in executions]
        self.assertIn(first_request_id, returned_ids)
        self.assertNotIn(second_request_id, returned_ids)

        for item in executions:
            self.assertTrue(item.get("is_favorite"))
            tags = item.get("tags", [])
            self.assertIn("revision", tags)

    def test_get_sequence_plan_and_render_recent_list_supports_ranking(self) -> None:
        first_status, first_response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())
        self.assertEqual(first_status, 201)

        second_payload = self._valid_payload()
        second_payload["sequence_id"] = "seq_rank_route_002"
        second_status, second_response = self._post_json("/api/sequence/plan-and-render", second_payload)
        self.assertEqual(second_status, 201)

        first_request_id = str(first_response.get("request_id") or "")
        second_request_id = str(second_response.get("request_id") or "")

        first_links = first_response.get("shot_job_links", [])
        self.assertGreater(len(first_links), 0)
        retry_shot_id = first_links[0].get("shot_id")
        self.assertTrue(isinstance(retry_shot_id, str) and retry_shot_id)

        retry_status, _ = self._post_json(
            f"/api/sequence/plan-and-render/{first_request_id}/retry-shot",
            {
                "shot_id": retry_shot_id,
                "reason": "ranking retry",
            },
        )
        self.assertEqual(retry_status, 201)

        list_status, list_response = self._get_json(
            "/api/sequence/plan-and-render?ranking=most_retries&limit=200"
        )
        self.assertEqual(list_status, 200)
        self.assertTrue(list_response.get("ok"))
        self.assertGreaterEqual(list_response.get("count", 0), 2)

        executions = list_response.get("executions", [])
        self.assertGreaterEqual(len(executions), 2)

        first_item = executions[0]
        self.assertEqual(first_item.get("request_id"), first_request_id)
        self.assertGreaterEqual(first_item.get("total_retries", 0), 1)
        self.assertIn("ranking_score", first_item)
        self.assertIn("ranking_reason", first_item)

        returned_ids = [item.get("request_id") for item in executions]
        self.assertIn(first_request_id, returned_ids)
        self.assertIn(second_request_id, returned_ids)

    def test_collection_review_endpoints_support_crud_and_items(self) -> None:
        create_collection_status, create_collection_response = self._post_json(
            "/api/sequence/collections",
            {
                "name": "Coleccion de Revision",
                "description": "Revision semanal",
                "editorial_note": "Revisar consistencia",
                "color": "#0ea5e9",
            },
        )
        self.assertEqual(create_collection_status, 201)
        self.assertTrue(create_collection_response.get("ok"))

        collection = create_collection_response.get("collection", {})
        collection_id = str(collection.get("collection_id") or "")
        self.assertTrue(collection_id)
        self.assertIsNone(collection.get("best_request_id"))

        run_status, run_response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())
        self.assertEqual(run_status, 201)
        request_id = str(run_response.get("request_id") or "")
        self.assertTrue(request_id)

        add_status, add_response = self._post_json(
            f"/api/sequence/collections/{collection_id}/items",
            {"request_ids": [request_id]},
        )
        self.assertEqual(add_status, 200)
        self.assertTrue(add_response.get("ok"))
        self.assertEqual(add_response.get("collection", {}).get("item_count"), 1)

        highlight_status, highlight_response = self._patch_json(
            f"/api/sequence/collections/{collection_id}/items/{request_id}/highlight",
            {"is_highlighted": True},
        )
        self.assertEqual(highlight_status, 200)
        self.assertTrue(highlight_response.get("ok"))
        self.assertGreaterEqual(highlight_response.get("collection", {}).get("highlighted_count", 0), 1)

        set_best_status, set_best_response = self._patch_json(
            f"/api/sequence/collections/{collection_id}/best",
            {"request_id": request_id},
        )
        self.assertEqual(set_best_status, 200)
        self.assertTrue(set_best_response.get("ok"))
        self.assertEqual(set_best_response.get("collection", {}).get("best_request_id"), request_id)

        review_status, review_response = self._get_json(f"/api/sequence/collections/{collection_id}/review?limit=20")
        self.assertEqual(review_status, 200)
        self.assertTrue(review_response.get("ok"))
        self.assertEqual(review_response.get("collection", {}).get("collection_id"), collection_id)
        self.assertGreaterEqual(review_response.get("count", 0), 1)

        review_ids = [item.get("request_id") for item in review_response.get("executions", [])]
        self.assertIn(request_id, review_ids)

        matched = next((item for item in review_response.get("executions", []) if item.get("request_id") == request_id), None)
        self.assertIsNotNone(matched)
        assert matched is not None
        self.assertTrue(matched.get("collection_best"))

        clear_best_status, clear_best_response = self._patch_json(
            f"/api/sequence/collections/{collection_id}/best",
            {"request_id": None},
        )
        self.assertEqual(clear_best_status, 200)
        self.assertIsNone(clear_best_response.get("collection", {}).get("best_request_id"))

        remove_status, remove_response = self._delete_json(
            f"/api/sequence/collections/{collection_id}/items/{request_id}"
        )
        self.assertEqual(remove_status, 200)
        self.assertTrue(remove_response.get("ok"))
        self.assertEqual(remove_response.get("collection", {}).get("item_count"), 0)

        delete_status, delete_response = self._delete_json(f"/api/sequence/collections/{collection_id}")
        self.assertEqual(delete_status, 200)
        self.assertTrue(delete_response.get("ok"))
        self.assertTrue(delete_response.get("deleted"))

    def test_collection_audit_endpoint_returns_editorial_and_operational_summary(self) -> None:
        approved_status, approved_response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())
        self.assertEqual(approved_status, 201)
        approved_request_id = str(approved_response.get("request_id") or "")
        self.assertTrue(approved_request_id)

        rejected_payload = self._valid_payload()
        rejected_payload["sequence_id"] = "seq_audit_rejected_route"
        rejected_status, rejected_response = self._post_json("/api/sequence/plan-and-render", rejected_payload)
        self.assertEqual(rejected_status, 201)
        rejected_request_id = str(rejected_response.get("request_id") or "")
        self.assertTrue(rejected_request_id)

        pending_payload = self._valid_payload()
        pending_payload["sequence_id"] = "seq_audit_pending_route"
        pending_status, pending_response = self._post_json("/api/sequence/plan-and-render", pending_payload)
        self.assertEqual(pending_status, 201)
        pending_request_id = str(pending_response.get("request_id") or "")
        self.assertTrue(pending_request_id)

        patch_meta_status, _ = self._patch_json(
            f"/api/sequence/plan-and-render/{approved_request_id}/meta",
            {"is_favorite": True},
        )
        self.assertEqual(patch_meta_status, 200)

        patch_review_approved_status, _ = self._patch_json(
            f"/api/sequence/plan-and-render/{approved_request_id}/review",
            {"review_status": "approved", "review_note": "Aprobada"},
        )
        self.assertEqual(patch_review_approved_status, 200)

        patch_review_rejected_status, _ = self._patch_json(
            f"/api/sequence/plan-and-render/{rejected_request_id}/review",
            {"review_status": "rejected", "review_note": "Rechazada"},
        )
        self.assertEqual(patch_review_rejected_status, 200)

        create_collection_status, create_collection_response = self._post_json(
            "/api/sequence/collections",
            {"name": "Coleccion Audit Route"},
        )
        self.assertEqual(create_collection_status, 201)
        collection_id = str(create_collection_response.get("collection", {}).get("collection_id") or "")
        self.assertTrue(collection_id)

        add_status, _ = self._post_json(
            f"/api/sequence/collections/{collection_id}/items",
            {"request_ids": [approved_request_id, rejected_request_id, pending_request_id]},
        )
        self.assertEqual(add_status, 200)

        best_status, _ = self._patch_json(
            f"/api/sequence/collections/{collection_id}/best",
            {"request_id": approved_request_id},
        )
        self.assertEqual(best_status, 200)

        audit_status, audit_response = self._get_json(f"/api/sequence/collections/{collection_id}/audit")
        self.assertEqual(audit_status, 200)
        self.assertTrue(audit_response.get("ok"))
        self.assertEqual(audit_response.get("collection_id"), collection_id)
        self.assertEqual(audit_response.get("total_executions"), 3)
        self.assertEqual(audit_response.get("approved_count"), 1)
        self.assertEqual(audit_response.get("rejected_count"), 1)
        self.assertEqual(audit_response.get("pending_review_count"), 1)
        self.assertEqual(audit_response.get("favorite_count"), 1)
        self.assertEqual(audit_response.get("best_request_id"), approved_request_id)
        self.assertEqual(audit_response.get("executions_without_review"), 1)
        self.assertIn("success_ratio_summary", audit_response)
        self.assertIn(audit_response.get("health_status"), {"yellow", "red"})
        self.assertIsInstance(audit_response.get("alerts"), list)
        self.assertGreaterEqual(len(audit_response.get("alerts", [])), 1)
        self.assertIn("editorial_summary", audit_response)
        self.assertIn("operational_summary", audit_response)
        self.assertIsInstance(audit_response.get("signals"), list)

    def test_list_collections_includes_health_status_and_alerts(self) -> None:
        create_collection_status, create_collection_response = self._post_json(
            "/api/sequence/collections",
            {"name": "Coleccion Health Summary"},
        )
        self.assertEqual(create_collection_status, 201)
        collection_id = str(create_collection_response.get("collection", {}).get("collection_id") or "")
        self.assertTrue(collection_id)

        list_status, list_response = self._get_json("/api/sequence/collections?limit=20")
        self.assertEqual(list_status, 200)
        self.assertTrue(list_response.get("ok"))

        matched = next(
            (item for item in list_response.get("collections", []) if item.get("collection_id") == collection_id),
            None,
        )
        self.assertIsNotNone(matched)
        assert matched is not None
        self.assertIn(matched.get("health_status"), {"green", "yellow", "red"})
        self.assertIsInstance(matched.get("alerts"), list)

    def test_collection_audit_endpoint_returns_404_for_missing_collection(self) -> None:
        audit_status, audit_response = self._get_json("/api/sequence/collections/not-found-collection/audit")
        self.assertEqual(audit_status, 404)
        self.assertFalse(audit_response.get("ok", True))
        self.assertEqual(audit_response.get("error", {}).get("code"), "COLLECTION_NOT_FOUND")

    def test_collections_dashboard_endpoint_returns_global_summary(self) -> None:
        run_status, run_response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())
        self.assertEqual(run_status, 201)
        request_id = str(run_response.get("request_id") or "")
        self.assertTrue(request_id)

        create_collection_status, create_collection_response = self._post_json(
            "/api/sequence/collections",
            {"name": "Coleccion Dashboard Route"},
        )
        self.assertEqual(create_collection_status, 201)
        collection_id = str(create_collection_response.get("collection", {}).get("collection_id") or "")
        self.assertTrue(collection_id)

        add_status, _ = self._post_json(
            f"/api/sequence/collections/{collection_id}/items",
            {"request_ids": [request_id]},
        )
        self.assertEqual(add_status, 200)

        dashboard_status, dashboard_response = self._get_json(
            "/api/sequence/collections/dashboard?limit=200&top_limit=5"
        )
        self.assertEqual(dashboard_status, 200)
        self.assertTrue(dashboard_response.get("ok"))
        self.assertGreaterEqual(dashboard_response.get("total_collections", 0), 1)
        self.assertIn("collections_green", dashboard_response)
        self.assertIn("collections_yellow", dashboard_response)
        self.assertIn("collections_red", dashboard_response)
        self.assertIn("top_collections_by_executions", dashboard_response)
        self.assertIn("top_collections_by_retries", dashboard_response)
        self.assertIn("collections_without_best_execution", dashboard_response)
        self.assertIn("collections_with_pending_review", dashboard_response)
        self.assertIn("highlighted_collections", dashboard_response)

        top_by_executions = dashboard_response.get("top_collections_by_executions", [])
        self.assertIsInstance(top_by_executions, list)
        if top_by_executions:
            first = top_by_executions[0]
            self.assertIn("collection_id", first)
            self.assertIn("name", first)
            self.assertIn("health_status", first)
            self.assertIn("alerts", first)
            self.assertIn("total_executions", first)

    def test_notifications_endpoints_list_and_mark_read(self) -> None:
        first_status, first_response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())
        self.assertEqual(first_status, 201)
        first_request_id = str(first_response.get("request_id") or "")
        self.assertTrue(first_request_id)

        second_payload = self._valid_payload()
        second_payload["sequence_id"] = "seq_notifications_route_002"
        second_status, second_response = self._post_json("/api/sequence/plan-and-render", second_payload)
        self.assertEqual(second_status, 201)
        second_request_id = str(second_response.get("request_id") or "")
        self.assertTrue(second_request_id)

        create_collection_status, create_collection_response = self._post_json(
            "/api/sequence/collections",
            {"name": "Coleccion Notifications Route"},
        )
        self.assertEqual(create_collection_status, 201)
        collection_id = str(create_collection_response.get("collection", {}).get("collection_id") or "")
        self.assertTrue(collection_id)

        add_status, _ = self._post_json(
            f"/api/sequence/collections/{collection_id}/items",
            {"request_ids": [first_request_id, second_request_id]},
        )
        self.assertEqual(add_status, 200)

        audit_status, _ = self._get_json(f"/api/sequence/collections/{collection_id}/audit")
        self.assertEqual(audit_status, 200)

        list_status, list_response = self._get_json(
            f"/api/sequence/notifications?collection_id={quote(collection_id)}&is_read=false&limit=50"
        )
        self.assertEqual(list_status, 200)
        self.assertTrue(list_response.get("ok"))
        self.assertGreaterEqual(list_response.get("count", 0), 1)

        notifications = list_response.get("notifications", [])
        self.assertGreaterEqual(len(notifications), 1)
        first_notification = notifications[0]
        self.assertEqual(first_notification.get("collection_id"), collection_id)
        self.assertFalse(first_notification.get("is_read", True))

        notification_id = str(first_notification.get("notification_id") or "")
        self.assertTrue(notification_id)

        patch_status, patch_response = self._patch_json(
            f"/api/sequence/notifications/{notification_id}/read",
            {"is_read": True},
        )
        self.assertEqual(patch_status, 200)
        self.assertTrue(patch_response.get("ok"))
        self.assertTrue(patch_response.get("notification", {}).get("is_read"))

        read_list_status, read_list_response = self._get_json(
            f"/api/sequence/notifications?collection_id={quote(collection_id)}&is_read=true&limit=50"
        )
        self.assertEqual(read_list_status, 200)
        self.assertTrue(read_list_response.get("ok"))
        self.assertGreaterEqual(read_list_response.get("count", 0), 1)

    def test_notifications_mark_read_returns_404_when_missing(self) -> None:
        patch_status, patch_response = self._patch_json(
            "/api/sequence/notifications/not-found-notification/read",
            {"is_read": True},
        )
        self.assertEqual(patch_status, 404)
        self.assertFalse(patch_response.get("ok", True))
        self.assertEqual(patch_response.get("error", {}).get("code"), "NOTIFICATION_NOT_FOUND")

    def test_notification_preferences_get_and_patch(self) -> None:
        get_status, get_response = self._get_json("/api/sequence/notification-preferences")
        self.assertEqual(get_status, 200)
        self.assertTrue(get_response.get("ok"))

        preferences = get_response.get("preferences", {})
        self.assertIn("notifications_enabled", preferences)
        self.assertIn("min_severity", preferences)
        self.assertIn("enabled_types", preferences)
        self.assertIn("show_only_unread_by_default", preferences)

        patch_status, patch_response = self._patch_json(
            "/api/sequence/notification-preferences",
            {
                "notifications_enabled": True,
                "min_severity": "warning",
                "enabled_types": ["COLLECTION_ENTERED_RED", "PENDING_REVIEW_HIGH"],
                "show_only_unread_by_default": True,
            },
        )
        self.assertEqual(patch_status, 200)
        self.assertTrue(patch_response.get("ok"))

        updated = patch_response.get("preferences", {})
        self.assertTrue(updated.get("notifications_enabled"))
        self.assertEqual(updated.get("min_severity"), "warning")
        self.assertEqual(updated.get("enabled_types"), ["COLLECTION_ENTERED_RED", "PENDING_REVIEW_HIGH"])
        self.assertTrue(updated.get("show_only_unread_by_default"))

    def test_notification_preferences_patch_requires_at_least_one_field(self) -> None:
        patch_status, patch_response = self._patch_json(
            "/api/sequence/notification-preferences",
            {},
        )
        self.assertEqual(patch_status, 400)
        self.assertFalse(patch_response.get("ok", True))
        self.assertEqual(
            patch_response.get("error", {}).get("code"),
            "INVALID_NOTIFICATION_PREFERENCES_UPDATE",
        )

    def test_webhooks_endpoints_create_list_and_patch(self) -> None:
        list_status, list_response = self._get_json("/api/sequence/webhooks?limit=200&include_disabled=true")
        self.assertEqual(list_status, 200)
        self.assertTrue(list_response.get("ok"))
        self.assertIn("webhooks", list_response)

        create_status, create_response = self._post_json(
            "/api/sequence/webhooks",
            {
                "name": "Ops Route Webhook",
                "url": "https://example.test/route-webhook",
                "is_enabled": True,
                "min_severity": "warning",
                "enabled_types": ["HEALTH_STATUS_CHANGED", "MISSING_BEST_EXECUTION"],
            },
        )
        self.assertEqual(create_status, 201)
        self.assertTrue(create_response.get("ok"))

        webhook = create_response.get("webhook", {})
        webhook_id = str(webhook.get("webhook_id") or "")
        self.assertTrue(webhook_id)
        self.assertEqual(webhook.get("name"), "Ops Route Webhook")
        self.assertEqual(webhook.get("payload_template_mode"), "default")
        self.assertIsNone(webhook.get("payload_template"))
        self.assertEqual(webhook.get("health_status"), "green")
        self.assertEqual(webhook.get("alerts"), [])

        patch_status, patch_response = self._patch_json(
            f"/api/sequence/webhooks/{quote(webhook_id)}",
            {
                "name": "Ops Route Webhook Updated",
                "is_enabled": False,
                "min_severity": "critical",
                "enabled_types": ["COLLECTION_ENTERED_RED"],
                "payload_template_mode": "compact",
            },
        )
        self.assertEqual(patch_status, 200)
        self.assertTrue(patch_response.get("ok"))
        updated = patch_response.get("webhook", {})
        self.assertEqual(updated.get("name"), "Ops Route Webhook Updated")
        self.assertFalse(updated.get("is_enabled", True))
        self.assertEqual(updated.get("min_severity"), "critical")
        self.assertEqual(updated.get("payload_template_mode"), "compact")

        patch_custom_status, patch_custom_response = self._patch_json(
            f"/api/sequence/webhooks/{quote(webhook_id)}",
            {
                "payload_template_mode": "custom",
                "payload_template": {
                    "event": "{{type}}",
                    "level": "{{severity}}",
                },
            },
        )
        self.assertEqual(patch_custom_status, 200)
        self.assertTrue(patch_custom_response.get("ok"))
        custom_updated = patch_custom_response.get("webhook", {})
        self.assertEqual(custom_updated.get("payload_template_mode"), "custom")
        self.assertEqual(
            custom_updated.get("payload_template"),
            {
                "event": "{{type}}",
                "level": "{{severity}}",
            },
        )

    def test_webhook_health_endpoint_returns_operational_summary_and_signals(self) -> None:
        create_status, create_response = self._post_json(
            "/api/sequence/webhooks",
            {
                "name": "Health Route Webhook",
                "url": "http://127.0.0.1:1/health-route-webhook",
                "is_enabled": True,
                "min_severity": "info",
            },
        )
        self.assertEqual(create_status, 201)
        webhook_id = str(create_response.get("webhook", {}).get("webhook_id") or "")
        self.assertTrue(webhook_id)

        for _ in range(6):
            test_status, _ = self._post_json(
                f"/api/sequence/webhooks/{quote(webhook_id)}/test",
                {},
            )
            self.assertEqual(test_status, 200)

        health_status, health_response = self._get_json(
            f"/api/sequence/webhooks/{quote(webhook_id)}/health?recent_limit=40&signals_limit=10"
        )
        self.assertEqual(health_status, 200)
        self.assertTrue(health_response.get("ok"))
        self.assertEqual(health_response.get("webhook", {}).get("webhook_id"), webhook_id)
        self.assertIn(health_response.get("health_status"), {"green", "yellow", "red"})
        self.assertIn("operational_summary", health_response)
        self.assertIn("alerts", health_response)
        self.assertIn("recent_signals", health_response)

        summary = health_response.get("operational_summary", {})
        self.assertGreaterEqual(int(summary.get("total_deliveries") or 0), 6)
        self.assertGreaterEqual(int(summary.get("failed_deliveries") or 0), 1)

    def test_notification_channels_endpoints_create_list_patch_and_test(self) -> None:
        list_status, list_response = self._get_json(
            "/api/sequence/notification-channels?limit=200&include_disabled=true"
        )
        self.assertEqual(list_status, 200)
        self.assertTrue(list_response.get("ok"))
        self.assertIn("channels", list_response)

        create_status, create_response = self._post_json(
            "/api/sequence/notification-channels",
            {
                "channel_type": "slack",
                "name": "Ops Slack Route",
                "is_enabled": True,
                "config": {
                    "webhook_url": "http://127.0.0.1:1/slack-route"
                },
                "min_severity": "warning",
                "enabled_types": ["HEALTH_STATUS_CHANGED", "COLLECTION_ENTERED_RED"],
            },
        )
        self.assertEqual(create_status, 201)
        self.assertTrue(create_response.get("ok"))
        channel = create_response.get("channel", {})
        channel_id = str(channel.get("channel_id") or "")
        self.assertTrue(channel_id)
        self.assertEqual(channel.get("channel_type"), "slack")

        patch_status, patch_response = self._patch_json(
            f"/api/sequence/notification-channels/{quote(channel_id)}",
            {
                "name": "Ops Slack Route Disabled",
                "is_enabled": False,
                "min_severity": "critical",
            },
        )
        self.assertEqual(patch_status, 200)
        self.assertTrue(patch_response.get("ok"))
        updated = patch_response.get("channel", {})
        self.assertEqual(updated.get("name"), "Ops Slack Route Disabled")
        self.assertFalse(updated.get("is_enabled", True))
        self.assertEqual(updated.get("min_severity"), "critical")

        test_status, test_response = self._post_json(
            f"/api/sequence/notification-channels/{quote(channel_id)}/test",
            {},
        )
        self.assertEqual(test_status, 200)
        self.assertTrue(test_response.get("ok"))
        delivery = test_response.get("delivery", {})
        self.assertEqual(delivery.get("channel_id"), channel_id)
        self.assertTrue(delivery.get("is_test"))
        self.assertEqual(delivery.get("channel_type"), "slack")

    def test_notification_channel_deliveries_endpoints_list_retry_and_process(self) -> None:
        create_status, create_response = self._post_json(
            "/api/sequence/notification-channels",
            {
                "channel_type": "telegram",
                "name": "Ops Telegram Route",
                "is_enabled": True,
                "config": {
                    "bot_token": "telegram-route-token",
                    "chat_id": "12345"
                },
                "min_severity": "info",
            },
        )
        self.assertEqual(create_status, 201)
        channel_id = str(create_response.get("channel", {}).get("channel_id") or "")
        self.assertTrue(channel_id)

        test_status, test_response = self._post_json(
            f"/api/sequence/notification-channels/{quote(channel_id)}/test",
            {},
        )
        self.assertEqual(test_status, 200)
        delivery = test_response.get("delivery", {})
        delivery_id = str(delivery.get("delivery_id") or "")
        self.assertTrue(delivery_id)

        list_status, list_response = self._get_json(
            f"/api/sequence/notification-channel-deliveries?channel_id={quote(channel_id)}&is_test=true&limit=100"
        )
        self.assertEqual(list_status, 200)
        self.assertTrue(list_response.get("ok"))
        self.assertGreaterEqual(int(list_response.get("count") or 0), 1)

        retry_status, retry_response = self._post_json(
            f"/api/sequence/notification-channel-deliveries/{quote(delivery_id)}/retry",
            {},
        )
        self.assertIn(retry_status, {200, 400})
        if retry_status == 200:
            self.assertTrue(retry_response.get("ok"))
            self.assertIn("delivery", retry_response)
        else:
            self.assertFalse(retry_response.get("ok", True))

        process_status, process_response = self._post_json(
            "/api/sequence/notification-channel-deliveries/process-retries?limit=20",
            {},
        )
        self.assertEqual(process_status, 200)
        self.assertTrue(process_response.get("ok"))
        self.assertIn("processed_count", process_response)
        self.assertIn("deliveries", process_response)

    def test_alert_routing_rules_endpoints_crud(self) -> None:
        create_channel_status, create_channel_response = self._post_json(
            "/api/sequence/notification-channels",
            {
                "channel_type": "slack",
                "name": "Routing Rule Target Channel",
                "is_enabled": True,
                "config": {
                    "webhook_url": "http://127.0.0.1:1/routing-rule-target"
                },
                "min_severity": "info",
            },
        )
        self.assertEqual(create_channel_status, 201)
        target_channel_id = str(create_channel_response.get("channel", {}).get("channel_id") or "")
        self.assertTrue(target_channel_id)

        list_status, list_response = self._get_json("/api/sequence/alert-routing-rules?limit=200&include_disabled=true")
        self.assertEqual(list_status, 200)
        self.assertTrue(list_response.get("ok"))
        self.assertIn("rules", list_response)

        create_status, create_response = self._post_json(
            "/api/sequence/alert-routing-rules",
            {
                "name": "Route Missing Best",
                "is_enabled": True,
                "target_channel_id": target_channel_id,
                "target_channel_kind": "notification_channel",
                "match_types": ["MISSING_BEST_EXECUTION"],
                "min_severity": "warning",
            },
        )
        self.assertEqual(create_status, 201)
        self.assertTrue(create_response.get("ok"))
        rule = create_response.get("rule", {})
        rule_id = str(rule.get("rule_id") or "")
        self.assertTrue(rule_id)
        self.assertEqual(rule.get("target_channel_id"), target_channel_id)

        patch_status, patch_response = self._patch_json(
            f"/api/sequence/alert-routing-rules/{quote(rule_id)}",
            {
                "name": "Route Missing Best Updated",
                "is_enabled": False,
                "min_severity": "critical",
                "match_health_status": "red",
            },
        )
        self.assertEqual(patch_status, 200)
        self.assertTrue(patch_response.get("ok"))
        updated = patch_response.get("rule", {})
        self.assertEqual(updated.get("name"), "Route Missing Best Updated")
        self.assertFalse(updated.get("is_enabled", True))
        self.assertEqual(updated.get("min_severity"), "critical")
        self.assertEqual(updated.get("match_health_status"), "red")

        delete_status, delete_response = self._delete_json(
            f"/api/sequence/alert-routing-rules/{quote(rule_id)}"
        )
        self.assertEqual(delete_status, 200)
        self.assertTrue(delete_response.get("ok"))
        self.assertTrue(delete_response.get("deleted"))

        missing_delete_status, missing_delete_response = self._delete_json(
            f"/api/sequence/alert-routing-rules/{quote(rule_id)}"
        )
        self.assertEqual(missing_delete_status, 404)
        self.assertFalse(missing_delete_response.get("ok", True))
        self.assertEqual(missing_delete_response.get("error", {}).get("code"), "ALERT_ROUTING_RULE_NOT_FOUND")

    def test_alert_routing_rules_apply_and_trace_delivery_route(self) -> None:
        create_channel_status, create_channel_response = self._post_json(
            "/api/sequence/notification-channels",
            {
                "channel_type": "slack",
                "name": "Routing Apply Channel",
                "is_enabled": True,
                "config": {
                    "webhook_url": "http://127.0.0.1:1/routing-apply-target"
                },
                "min_severity": "info",
                "enabled_types": ["MISSING_BEST_EXECUTION"],
            },
        )
        self.assertEqual(create_channel_status, 201)
        target_channel_id = str(create_channel_response.get("channel", {}).get("channel_id") or "")
        self.assertTrue(target_channel_id)

        create_rule_status, create_rule_response = self._post_json(
            "/api/sequence/alert-routing-rules",
            {
                "name": "Route Missing Best To Channel",
                "is_enabled": True,
                "target_channel_id": target_channel_id,
                "target_channel_kind": "notification_channel",
                "match_types": ["MISSING_BEST_EXECUTION"],
                "min_severity": "warning",
            },
        )
        self.assertEqual(create_rule_status, 201)
        rule_id = str(create_rule_response.get("rule", {}).get("rule_id") or "")
        self.assertTrue(rule_id)

        run_status, run_response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())
        self.assertEqual(run_status, 201)
        request_id = str(run_response.get("request_id") or "")
        self.assertTrue(request_id)

        create_collection_status, create_collection_response = self._post_json(
            "/api/sequence/collections",
            {
                "name": "Routing Apply Collection",
            },
        )
        self.assertEqual(create_collection_status, 201)
        collection_id = str(create_collection_response.get("collection", {}).get("collection_id") or "")
        self.assertTrue(collection_id)

        add_items_status, _ = self._post_json(
            f"/api/sequence/collections/{quote(collection_id)}/items",
            {
                "request_ids": [request_id],
            },
        )
        self.assertEqual(add_items_status, 200)

        audit_status, audit_response = self._get_json(
            f"/api/sequence/collections/{quote(collection_id)}/audit"
        )
        self.assertEqual(audit_status, 200)
        self.assertTrue(audit_response.get("ok"))

        deliveries_status, deliveries_response = self._get_json(
            f"/api/sequence/notification-channel-deliveries?channel_id={quote(target_channel_id)}&limit=100"
        )
        self.assertEqual(deliveries_status, 200)
        self.assertTrue(deliveries_response.get("ok"))
        self.assertGreaterEqual(int(deliveries_response.get("count") or 0), 1)

        delivery = deliveries_response.get("deliveries", [])[0]
        self.assertEqual(delivery.get("channel_id"), target_channel_id)
        self.assertEqual(delivery.get("routing_rule_id"), rule_id)
        self.assertEqual(delivery.get("routing_rule_name"), "Route Missing Best To Channel")

        delete_rule_status, _ = self._delete_json(
            f"/api/sequence/alert-routing-rules/{quote(rule_id)}"
        )
        self.assertEqual(delete_rule_status, 200)

    def test_webhooks_dashboard_endpoint_includes_health_alerts(self) -> None:
        create_status, create_response = self._post_json(
            "/api/sequence/webhooks",
            {
                "name": "Dashboard Health Route Webhook",
                "url": "http://127.0.0.1:1/dashboard-health-route-webhook",
                "is_enabled": True,
                "min_severity": "info",
            },
        )
        self.assertEqual(create_status, 201)
        webhook_id = str(create_response.get("webhook", {}).get("webhook_id") or "")
        self.assertTrue(webhook_id)

        for _ in range(6):
            test_status, _ = self._post_json(
                f"/api/sequence/webhooks/{quote(webhook_id)}/test",
                {},
            )
            self.assertEqual(test_status, 200)

        dashboard_status, dashboard_response = self._get_json(
            "/api/sequence/webhooks/dashboard?top_limit=5&errors_limit=20"
        )
        self.assertEqual(dashboard_status, 200)
        self.assertTrue(dashboard_response.get("ok"))
        self.assertIn("webhooks_green", dashboard_response)
        self.assertIn("webhooks_yellow", dashboard_response)
        self.assertIn("webhooks_red", dashboard_response)
        self.assertIn("active_alerts", dashboard_response)

        all_webhooks = (
            dashboard_response.get("top_webhooks_by_volume", [])
            + dashboard_response.get("top_webhooks_by_failures", [])
            + dashboard_response.get("top_webhooks_by_retries", [])
        )
        risky_items = [item for item in all_webhooks if item.get("webhook_id") == webhook_id]
        self.assertTrue(any(item.get("health_status") in {"yellow", "red"} for item in risky_items))

    def test_webhook_test_event_endpoint_sends_test_delivery_without_auth(self) -> None:
        create_status, create_response = self._post_json(
            "/api/sequence/webhooks",
            {
                "name": "Test Event Route",
                "url": "http://127.0.0.1:1/test-event-route",
                "is_enabled": True,
                "auth_mode": "none",
            },
        )
        self.assertEqual(create_status, 201)
        webhook_id = str(create_response.get("webhook", {}).get("webhook_id") or "")
        self.assertTrue(webhook_id)

        test_status, test_response = self._post_json(
            f"/api/sequence/webhooks/{quote(webhook_id)}/test",
            {},
        )
        self.assertEqual(test_status, 200)
        self.assertTrue(test_response.get("ok"))

        delivery = test_response.get("delivery", {})
        self.assertTrue(delivery.get("is_test"))
        self.assertEqual(delivery.get("template_mode"), "default")
        payload = delivery.get("payload", {})
        self.assertEqual(payload.get("event_type"), "test_event")
        self.assertEqual(payload.get("webhook_id"), webhook_id)
        self.assertEqual(payload.get("message"), "This is a test webhook event")

    def test_webhook_test_event_endpoint_supports_hmac_signature(self) -> None:
        create_status, create_response = self._post_json(
            "/api/sequence/webhooks",
            {
                "name": "Test Event Route HMAC",
                "url": "http://127.0.0.1:1/test-event-route-hmac",
                "is_enabled": True,
                "auth_mode": "hmac_sha256",
                "secret_token": "route-hmac-secret",
            },
        )
        self.assertEqual(create_status, 201)
        webhook_id = str(create_response.get("webhook", {}).get("webhook_id") or "")
        self.assertTrue(webhook_id)

        test_status, test_response = self._post_json(
            f"/api/sequence/webhooks/{quote(webhook_id)}/test",
            {},
        )
        self.assertEqual(test_status, 200)
        self.assertTrue(test_response.get("ok"))

        delivery = test_response.get("delivery", {})
        self.assertTrue(delivery.get("is_test"))
        self.assertEqual(delivery.get("auth_mode"), "hmac_sha256")
        self.assertTrue(delivery.get("signature_timestamp"))

    def test_webhook_preview_endpoint_returns_rendered_payload_default(self) -> None:
        create_status, create_response = self._post_json(
            "/api/sequence/webhooks",
            {
                "name": "Preview Route Default",
                "url": "https://example.test/preview-route-default",
                "is_enabled": False,
                "payload_template_mode": "default",
            },
        )
        self.assertEqual(create_status, 201)
        webhook_id = str(create_response.get("webhook", {}).get("webhook_id") or "")
        self.assertTrue(webhook_id)

        preview_status, preview_response = self._post_json(
            f"/api/sequence/webhooks/{quote(webhook_id)}/preview",
            {},
        )
        self.assertEqual(preview_status, 200)
        self.assertTrue(preview_response.get("ok"))
        self.assertEqual(preview_response.get("webhook_id"), webhook_id)
        self.assertEqual(preview_response.get("auth_mode"), "none")
        self.assertEqual(preview_response.get("payload_template_mode"), "default")
        self.assertIn("rendered_payload", preview_response)
        self.assertIn("rendered_headers", preview_response)

        payload = preview_response.get("rendered_payload", {})
        self.assertEqual(payload.get("event_type"), "test_event")
        self.assertEqual(payload.get("webhook_id"), webhook_id)
        self.assertEqual(payload.get("message"), "This is a test webhook event")

    def test_webhook_preview_endpoint_supports_compact_and_hmac(self) -> None:
        create_status, create_response = self._post_json(
            "/api/sequence/webhooks",
            {
                "name": "Preview Route HMAC",
                "url": "https://example.test/preview-route-hmac",
                "is_enabled": False,
                "auth_mode": "hmac_sha256",
                "secret_token": "preview-route-hmac-secret",
                "payload_template_mode": "compact",
            },
        )
        self.assertEqual(create_status, 201)
        webhook_id = str(create_response.get("webhook", {}).get("webhook_id") or "")
        self.assertTrue(webhook_id)

        preview_status, preview_response = self._post_json(
            f"/api/sequence/webhooks/{quote(webhook_id)}/preview",
            {
                "event_type": "manual_preview",
                "sample_data": {
                    "custom_debug": "ignore",
                    "message": "Preview route message",
                },
            },
        )
        self.assertEqual(preview_status, 200)
        self.assertTrue(preview_response.get("ok"))
        self.assertEqual(preview_response.get("auth_mode"), "hmac_sha256")
        self.assertEqual(preview_response.get("payload_template_mode"), "compact")
        self.assertTrue(preview_response.get("signature_preview"))

        payload = preview_response.get("rendered_payload", {})
        self.assertEqual(payload.get("event_type"), "manual_preview")
        self.assertEqual(payload.get("message"), "Preview route message")
        self.assertNotIn("custom_debug", payload)

        headers = preview_response.get("rendered_headers", {})
        self.assertTrue(headers.get("X-Webhook-Timestamp"))
        self.assertEqual(headers.get("X-Webhook-Id"), webhook_id)
        self.assertEqual(headers.get("X-Webhook-Signature"), preview_response.get("signature_preview"))

    def test_webhook_deliveries_endpoint_filters_by_is_test(self) -> None:
        prefs_status, _ = self._patch_json(
            "/api/sequence/notification-preferences",
            {
                "notifications_enabled": True,
                "min_severity": "info",
                "enabled_types": [
                    "HEALTH_STATUS_CHANGED",
                    "COLLECTION_ENTERED_RED",
                    "MISSING_BEST_EXECUTION",
                    "PENDING_REVIEW_HIGH",
                    "OPERATIONAL_FAILURE_THRESHOLD",
                ],
                "show_only_unread_by_default": False,
            },
        )
        self.assertEqual(prefs_status, 200)

        webhook_status, webhook_response = self._post_json(
            "/api/sequence/webhooks",
            {
                "name": "History Filter Route Webhook",
                "url": "http://127.0.0.1:1/history-filter-route-webhook",
                "is_enabled": True,
                "min_severity": "info",
                "enabled_types": ["HEALTH_STATUS_CHANGED", "MISSING_BEST_EXECUTION"],
            },
        )
        self.assertEqual(webhook_status, 201)
        webhook_id = str(webhook_response.get("webhook", {}).get("webhook_id") or "")
        self.assertTrue(webhook_id)

        test_status, _ = self._post_json(
            f"/api/sequence/webhooks/{quote(webhook_id)}/test",
            {},
        )
        self.assertEqual(test_status, 200)

        run_status, run_response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())
        self.assertEqual(run_status, 201)
        request_id = str(run_response.get("request_id") or "")
        self.assertTrue(request_id)

        collection_status, collection_response = self._post_json(
            "/api/sequence/collections",
            {"name": "Coleccion History Filter"},
        )
        self.assertEqual(collection_status, 201)
        collection_id = str(collection_response.get("collection", {}).get("collection_id") or "")
        self.assertTrue(collection_id)

        add_status, _ = self._post_json(
            f"/api/sequence/collections/{quote(collection_id)}/items",
            {"request_ids": [request_id]},
        )
        self.assertEqual(add_status, 200)

        audit_status, _ = self._get_json(f"/api/sequence/collections/{collection_id}/audit")
        self.assertEqual(audit_status, 200)

        tests_only_status, tests_only_response = self._get_json(
            f"/api/sequence/webhook-deliveries?webhook_id={quote(webhook_id)}&is_test=true&limit=100"
        )
        self.assertEqual(tests_only_status, 200)
        self.assertTrue(tests_only_response.get("ok"))
        self.assertGreaterEqual(tests_only_response.get("count", 0), 1)
        self.assertTrue(all(bool(item.get("is_test", False)) for item in tests_only_response.get("deliveries", [])))

        notifications_only_status, notifications_only_response = self._get_json(
            f"/api/sequence/webhook-deliveries?webhook_id={quote(webhook_id)}&is_test=false&limit=100"
        )
        self.assertEqual(notifications_only_status, 200)
        self.assertTrue(notifications_only_response.get("ok"))
        self.assertGreaterEqual(notifications_only_response.get("count", 0), 1)
        self.assertTrue(all(not bool(item.get("is_test", False)) for item in notifications_only_response.get("deliveries", [])))

    def test_webhook_deliveries_compare_endpoint_returns_structured_diff(self) -> None:
        left_create_status, left_create_response = self._post_json(
            "/api/sequence/webhooks",
            {
                "name": "Compare Left Route",
                "url": "http://127.0.0.1:1/compare-left-route",
                "is_enabled": True,
                "auth_mode": "none",
                "payload_template_mode": "default",
            },
        )
        self.assertEqual(left_create_status, 201)
        left_webhook_id = str(left_create_response.get("webhook", {}).get("webhook_id") or "")
        self.assertTrue(left_webhook_id)

        right_create_status, right_create_response = self._post_json(
            "/api/sequence/webhooks",
            {
                "name": "Compare Right Route",
                "url": "http://127.0.0.1:1/compare-right-route",
                "is_enabled": True,
                "auth_mode": "hmac_sha256",
                "secret_token": "compare-route-secret",
                "payload_template_mode": "compact",
            },
        )
        self.assertEqual(right_create_status, 201)
        right_webhook_id = str(right_create_response.get("webhook", {}).get("webhook_id") or "")
        self.assertTrue(right_webhook_id)

        left_test_status, left_test_response = self._post_json(
            f"/api/sequence/webhooks/{quote(left_webhook_id)}/test",
            {},
        )
        self.assertEqual(left_test_status, 200)
        left_delivery_id = str(left_test_response.get("delivery", {}).get("delivery_id") or "")
        self.assertTrue(left_delivery_id)

        right_test_status, right_test_response = self._post_json(
            f"/api/sequence/webhooks/{quote(right_webhook_id)}/test",
            {},
        )
        self.assertEqual(right_test_status, 200)
        right_delivery_id = str(right_test_response.get("delivery", {}).get("delivery_id") or "")
        self.assertTrue(right_delivery_id)

        compare_status, compare_response = self._get_json(
            "/api/sequence/webhook-deliveries/compare"
            f"?left_delivery_id={quote(left_delivery_id)}&right_delivery_id={quote(right_delivery_id)}"
        )
        self.assertEqual(compare_status, 200)
        self.assertTrue(compare_response.get("ok"))
        self.assertEqual(compare_response.get("left_delivery_id"), left_delivery_id)
        self.assertEqual(compare_response.get("right_delivery_id"), right_delivery_id)
        self.assertEqual(compare_response.get("auth_mode_left"), "none")
        self.assertEqual(compare_response.get("auth_mode_right"), "hmac_sha256")
        self.assertEqual(compare_response.get("payload_template_mode_left"), "default")
        self.assertEqual(compare_response.get("payload_template_mode_right"), "compact")
        self.assertIn("payload_diff", compare_response)
        self.assertIn("headers_diff", compare_response)

    def test_webhook_patch_returns_404_when_missing(self) -> None:
        patch_status, patch_response = self._patch_json(
            "/api/sequence/webhooks/missing-webhook-id",
            {
                "name": "Webhook Missing",
            },
        )
        self.assertEqual(patch_status, 404)
        self.assertFalse(patch_response.get("ok", True))
        self.assertEqual(patch_response.get("error", {}).get("code"), "WEBHOOK_NOT_FOUND")

    def test_webhook_deliveries_endpoint_returns_200(self) -> None:
        deliveries_status, deliveries_response = self._get_json("/api/sequence/webhook-deliveries?limit=100")
        self.assertEqual(deliveries_status, 200)
        self.assertTrue(deliveries_response.get("ok"))
        self.assertIn("deliveries", deliveries_response)
        self.assertIn("count", deliveries_response)
        if deliveries_response.get("count", 0) > 0:
            first = deliveries_response.get("deliveries", [])[0]
            self.assertIn("attempt_count", first)
            self.assertIn("max_attempts", first)
            self.assertIn("last_attempt_at", first)
            self.assertIn("next_retry_at", first)
            self.assertIn("final_failure_at", first)
            self.assertIn("is_test", first)
            self.assertIn("template_mode", first)

    def test_webhook_process_retries_endpoint_returns_batch_shape(self) -> None:
        process_status, process_response = self._post_json(
            "/api/sequence/webhook-deliveries/process-retries?limit=10",
            {},
        )
        self.assertEqual(process_status, 200)
        self.assertTrue(process_response.get("ok"))
        self.assertIn("processed_count", process_response)
        self.assertIn("sent_count", process_response)
        self.assertIn("failed_count", process_response)
        self.assertIn("exhausted_count", process_response)
        self.assertIn("deliveries", process_response)
        self.assertIsInstance(process_response.get("deliveries"), list)

    def test_webhook_delivery_retry_endpoint_retries_failed_delivery(self) -> None:
        prefs_status, _ = self._patch_json(
            "/api/sequence/notification-preferences",
            {
                "notifications_enabled": True,
                "min_severity": "info",
                "enabled_types": ["HEALTH_STATUS_CHANGED"],
                "show_only_unread_by_default": False,
            },
        )
        self.assertEqual(prefs_status, 200)

        webhook_status, webhook_response = self._post_json(
            "/api/sequence/webhooks",
            {
                "name": "Retry Route Webhook",
                "url": "http://127.0.0.1:1/retry-route-webhook",
                "is_enabled": True,
                "min_severity": "info",
                "enabled_types": ["HEALTH_STATUS_CHANGED"],
            },
        )
        self.assertEqual(webhook_status, 201)
        webhook_id = str(webhook_response.get("webhook", {}).get("webhook_id") or "")
        self.assertTrue(webhook_id)

        run_status, run_response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())
        self.assertEqual(run_status, 201)
        request_id = str(run_response.get("request_id") or "")
        self.assertTrue(request_id)

        collection_status, collection_response = self._post_json(
            "/api/sequence/collections",
            {"name": "Coleccion Retry Route"},
        )
        self.assertEqual(collection_status, 201)
        collection_id = str(collection_response.get("collection", {}).get("collection_id") or "")
        self.assertTrue(collection_id)

        add_status, _ = self._post_json(
            f"/api/sequence/collections/{collection_id}/items",
            {"request_ids": [request_id]},
        )
        self.assertEqual(add_status, 200)

        audit_status, _ = self._get_json(f"/api/sequence/collections/{collection_id}/audit")
        self.assertEqual(audit_status, 200)

        deliveries_status, deliveries_response = self._get_json(
            f"/api/sequence/webhook-deliveries?webhook_id={quote(webhook_id)}&limit=100"
        )
        self.assertEqual(deliveries_status, 200)
        self.assertTrue(deliveries_response.get("ok"))
        deliveries = deliveries_response.get("deliveries", [])
        self.assertGreaterEqual(len(deliveries), 1)

        failed_delivery = next(
            (item for item in deliveries if item.get("delivery_status") == "failed"),
            None,
        )
        self.assertIsNotNone(failed_delivery)
        assert failed_delivery is not None

        delivery_id = str(failed_delivery.get("delivery_id") or "")
        attempt_count_before = int(failed_delivery.get("attempt_count") or 0)
        self.assertTrue(delivery_id)
        self.assertGreaterEqual(attempt_count_before, 1)

        retry_status, retry_response = self._post_json(
            f"/api/sequence/webhook-deliveries/{quote(delivery_id)}/retry",
            {},
        )
        self.assertEqual(retry_status, 200)
        self.assertTrue(retry_response.get("ok"))
        retried = retry_response.get("delivery", {})
        self.assertEqual(retried.get("delivery_id"), delivery_id)
        self.assertEqual(int(retried.get("attempt_count") or 0), attempt_count_before + 1)
        self.assertIn(retried.get("delivery_status"), {"failed", "sent"})
        self.assertIsNotNone(retried.get("last_attempt_at"))

    def test_webhook_delivery_retry_endpoint_returns_404_when_missing(self) -> None:
        retry_status, retry_response = self._post_json(
            "/api/sequence/webhook-deliveries/missing-delivery-id/retry",
            {},
        )
        self.assertEqual(retry_status, 404)
        self.assertFalse(retry_response.get("ok", True))
        self.assertEqual(
            retry_response.get("error", {}).get("code"),
            "WEBHOOK_DELIVERY_NOT_FOUND",
        )

    def test_recent_list_supports_collection_filter(self) -> None:
        first_status, first_response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())
        self.assertEqual(first_status, 201)
        first_request_id = str(first_response.get("request_id") or "")

        second_payload = self._valid_payload()
        second_payload["sequence_id"] = "seq_collection_filter_route"
        second_status, second_response = self._post_json("/api/sequence/plan-and-render", second_payload)
        self.assertEqual(second_status, 201)
        second_request_id = str(second_response.get("request_id") or "")

        create_collection_status, create_collection_response = self._post_json(
            "/api/sequence/collections",
            {"name": "Coleccion Filtro"},
        )
        self.assertEqual(create_collection_status, 201)
        collection_id = str(create_collection_response.get("collection", {}).get("collection_id") or "")
        self.assertTrue(collection_id)

        add_status, _ = self._post_json(
            f"/api/sequence/collections/{collection_id}/items",
            {"request_ids": [first_request_id]},
        )
        self.assertEqual(add_status, 200)

        list_status, list_response = self._get_json(
            f"/api/sequence/plan-and-render?collection_id={quote(collection_id)}&limit=20"
        )
        self.assertEqual(list_status, 200)
        self.assertTrue(list_response.get("ok"))

        returned_ids = [item.get("request_id") for item in list_response.get("executions", [])]
        self.assertIn(first_request_id, returned_ids)
        self.assertNotIn(second_request_id, returned_ids)

        first_item = next(
            (item for item in list_response.get("executions", []) if item.get("request_id") == first_request_id),
            None,
        )
        self.assertIsNotNone(first_item)
        assert first_item is not None
        self.assertFalse(first_item.get("collection_best"))

    def test_get_sequence_plan_and_render_recent_list_rejects_invalid_status(self) -> None:
        list_status, list_response = self._get_json("/api/sequence/plan-and-render?status=unknown")
        self.assertEqual(list_status, 422)
        self.assertIn("detail", list_response)

    def test_get_sequence_plan_and_render_by_request_id_returns_200(self) -> None:
        post_status, post_response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())
        self.assertEqual(post_status, 201)

        request_id = post_response.get("request_id")
        self.assertTrue(isinstance(request_id, str) and request_id)

        get_status, get_response = self._get_json(f"/api/sequence/plan-and-render/{request_id}")
        self.assertEqual(get_status, 200)
        self.assertTrue(get_response.get("ok"))
        self.assertEqual(get_response.get("request_id"), request_id)
        self.assertIn("status_summary", get_response)
        self.assertIn("is_favorite", get_response)
        self.assertIn("tags", get_response)
        self.assertIn("note", get_response)
        self.assertIn("review_status", get_response)
        self.assertIn("review_note", get_response)
        self.assertIn("reviewed_at", get_response)
        self.assertIn("review_history_summary", get_response)
        self.assertIn("collections", get_response)

    def test_get_sequence_plan_and_render_by_request_id_includes_collection_membership(self) -> None:
        post_status, post_response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())
        self.assertEqual(post_status, 201)
        request_id = str(post_response.get("request_id") or "")
        self.assertTrue(request_id)

        create_collection_status, create_collection_response = self._post_json(
            "/api/sequence/collections",
            {"name": "Coleccion GET membership"},
        )
        self.assertEqual(create_collection_status, 201)
        collection_id = str(create_collection_response.get("collection", {}).get("collection_id") or "")
        self.assertTrue(collection_id)

        add_status, _ = self._post_json(
            f"/api/sequence/collections/{collection_id}/items",
            {"request_ids": [request_id]},
        )
        self.assertEqual(add_status, 200)

        highlight_status, _ = self._patch_json(
            f"/api/sequence/collections/{collection_id}/items/{request_id}/highlight",
            {"is_highlighted": True},
        )
        self.assertEqual(highlight_status, 200)

        best_status, _ = self._patch_json(
            f"/api/sequence/collections/{collection_id}/best",
            {"request_id": request_id},
        )
        self.assertEqual(best_status, 200)

        get_status, get_response = self._get_json(f"/api/sequence/plan-and-render/{request_id}")
        self.assertEqual(get_status, 200)

        collections = get_response.get("collections", [])
        self.assertEqual(len(collections), 1)
        membership = collections[0]
        self.assertEqual(membership.get("collection_id"), collection_id)
        self.assertEqual(membership.get("name"), "Coleccion GET membership")
        self.assertTrue(membership.get("is_highlighted"))
        self.assertTrue(membership.get("is_best"))
        self.assertTrue(membership.get("added_at"))

    def test_patch_sequence_plan_and_render_review_updates_execution_and_recent_list(self) -> None:
        post_status, post_response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())
        self.assertEqual(post_status, 201)

        request_id = post_response.get("request_id")
        self.assertTrue(isinstance(request_id, str) and request_id)

        patch_status, patch_response = self._patch_json(
            f"/api/sequence/plan-and-render/{request_id}/review",
            {
                "review_status": "approved",
                "review_note": "Aprobada para entrega",
            },
        )
        self.assertEqual(patch_status, 200)
        self.assertEqual(patch_response.get("review_status"), "approved")
        self.assertEqual(patch_response.get("review_note"), "Aprobada para entrega")
        self.assertTrue(isinstance(patch_response.get("reviewed_at"), str) and patch_response.get("reviewed_at"))
        summary = patch_response.get("review_history_summary", {})
        self.assertGreaterEqual(summary.get("history_count", 0), 1)
        self.assertTrue(summary.get("latest_created_at"))

        get_status, get_response = self._get_json(f"/api/sequence/plan-and-render/{request_id}")
        self.assertEqual(get_status, 200)
        self.assertEqual(get_response.get("review_status"), "approved")
        self.assertEqual(get_response.get("review_note"), "Aprobada para entrega")
        self.assertTrue(isinstance(get_response.get("reviewed_at"), str) and get_response.get("reviewed_at"))
        self.assertGreaterEqual(get_response.get("review_history_summary", {}).get("history_count", 0), 1)

        list_status, list_response = self._get_json(f"/api/sequence/plan-and-render?q={request_id[:8]}&limit=5")
        self.assertEqual(list_status, 200)
        match = next(
            (item for item in list_response.get("executions", []) if item.get("request_id") == request_id),
            None,
        )
        self.assertIsNotNone(match)
        assert match is not None
        self.assertEqual(match.get("review_status"), "approved")
        self.assertEqual(match.get("review_note"), "Aprobada para entrega")
        self.assertTrue(isinstance(match.get("reviewed_at"), str) and match.get("reviewed_at"))

    def test_get_sequence_plan_and_render_review_history_returns_entries(self) -> None:
        post_status, post_response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())
        self.assertEqual(post_status, 201)

        request_id = str(post_response.get("request_id") or "")
        self.assertTrue(request_id)

        patch_status, _ = self._patch_json(
            f"/api/sequence/plan-and-render/{request_id}/review",
            {
                "review_status": "approved",
                "review_note": "Aprobada para entrega",
            },
        )
        self.assertEqual(patch_status, 200)

        history_status, history_response = self._get_json(
            f"/api/sequence/plan-and-render/{request_id}/review-history?limit=20"
        )
        self.assertEqual(history_status, 200)
        self.assertTrue(history_response.get("ok"))
        self.assertEqual(history_response.get("request_id"), request_id)
        self.assertGreaterEqual(history_response.get("count", 0), 1)

        history_items = history_response.get("history", [])
        self.assertGreaterEqual(len(history_items), 1)
        first_item = history_items[0]
        self.assertIn("history_id", first_item)
        self.assertEqual(first_item.get("request_id"), request_id)
        self.assertEqual(first_item.get("previous_review_status"), "pending_review")
        self.assertEqual(first_item.get("new_review_status"), "approved")
        self.assertEqual(first_item.get("review_note"), "Aprobada para entrega")
        self.assertTrue(first_item.get("created_at"))

    def test_get_sequence_plan_and_render_review_history_returns_404_when_missing(self) -> None:
        history_status, history_response = self._get_json(
            "/api/sequence/plan-and-render/not-found-request/review-history"
        )
        self.assertEqual(history_status, 404)
        self.assertFalse(history_response.get("ok", True))
        self.assertEqual(history_response.get("error", {}).get("code"), "REQUEST_NOT_FOUND")

    def test_patch_sequence_plan_and_render_review_requires_at_least_one_field(self) -> None:
        post_status, post_response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())
        self.assertEqual(post_status, 201)

        request_id = post_response.get("request_id")
        self.assertTrue(isinstance(request_id, str) and request_id)

        patch_status, patch_response = self._patch_json(
            f"/api/sequence/plan-and-render/{request_id}/review",
            {},
        )
        self.assertEqual(patch_status, 400)
        self.assertFalse(patch_response.get("ok", True))
        self.assertEqual(
            patch_response.get("error", {}).get("code"),
            "INVALID_SEQUENCE_PLAN_AND_RENDER_REVIEW",
        )

    def test_patch_sequence_plan_and_render_meta_updates_execution_and_recent_list(self) -> None:
        post_status, post_response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())
        self.assertEqual(post_status, 201)

        request_id = post_response.get("request_id")
        self.assertTrue(isinstance(request_id, str) and request_id)

        patch_status, patch_response = self._patch_json(
            f"/api/sequence/plan-and-render/{request_id}/meta",
            {
                "is_favorite": True,
                "tags": ["revision", "v2", "revision"],
                "note": "  Revisar prompt del close up  ",
            },
        )
        self.assertEqual(patch_status, 200)
        self.assertTrue(patch_response.get("is_favorite"))
        self.assertEqual(patch_response.get("tags"), ["revision", "v2"])
        self.assertEqual(patch_response.get("note"), "Revisar prompt del close up")

        get_status, get_response = self._get_json(f"/api/sequence/plan-and-render/{request_id}")
        self.assertEqual(get_status, 200)
        self.assertTrue(get_response.get("is_favorite"))
        self.assertEqual(get_response.get("tags"), ["revision", "v2"])
        self.assertEqual(get_response.get("note"), "Revisar prompt del close up")

        list_status, list_response = self._get_json(f"/api/sequence/plan-and-render?q={request_id[:8]}&limit=5")
        self.assertEqual(list_status, 200)
        self.assertGreaterEqual(list_response.get("count", 0), 1)

        matching_item = next(
            (item for item in list_response.get("executions", []) if item.get("request_id") == request_id),
            None,
        )
        self.assertIsNotNone(matching_item)
        assert matching_item is not None
        self.assertTrue(matching_item.get("is_favorite"))
        self.assertEqual(matching_item.get("tags"), ["revision", "v2"])
        self.assertEqual(matching_item.get("note"), "Revisar prompt del close up")

    def test_patch_sequence_plan_and_render_meta_requires_at_least_one_field(self) -> None:
        post_status, post_response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())
        self.assertEqual(post_status, 201)

        request_id = post_response.get("request_id")
        self.assertTrue(isinstance(request_id, str) and request_id)

        patch_status, patch_response = self._patch_json(
            f"/api/sequence/plan-and-render/{request_id}/meta",
            {},
        )
        self.assertEqual(patch_status, 400)
        self.assertFalse(patch_response.get("ok", True))
        self.assertEqual(patch_response.get("error", {}).get("code"), "INVALID_SEQUENCE_PLAN_AND_RENDER_META")

    def test_get_sequence_plan_and_render_by_request_id_returns_404_when_missing(self) -> None:
        get_status, get_response = self._get_json("/api/sequence/plan-and-render/not-found-request")
        self.assertEqual(get_status, 404)
        self.assertFalse(get_response.get("ok", True))
        self.assertEqual(get_response.get("error", {}).get("code"), "REQUEST_NOT_FOUND")

    def test_post_retry_shot_returns_201_and_links_new_job(self) -> None:
        post_status, post_response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())
        self.assertEqual(post_status, 201)

        request_id = post_response.get("request_id")
        first_link = post_response.get("shot_job_links", [])[0]
        shot_id = first_link.get("shot_id")
        parent_job_id = first_link.get("job_id")

        retry_payload = {
            "shot_id": shot_id,
            "override_prompt": "retry prompt override",
            "override_negative_prompt": "retry negative override",
            "override_render_context": {"character_id": "char_retry", "use_ipadapter": True},
            "reason": "qa retry",
        }
        retry_status, retry_response = self._post_json(
            f"/api/sequence/plan-and-render/{request_id}/retry-shot",
            retry_payload,
        )

        self.assertEqual(retry_status, 201)
        self.assertTrue(retry_response.get("ok"))
        self.assertEqual(retry_response.get("request_id"), request_id)
        self.assertEqual(retry_response.get("shot_id"), shot_id)
        self.assertEqual(retry_response.get("parent_job_id"), parent_job_id)
        self.assertEqual(retry_response.get("retry_index"), 1)
        self.assertEqual(retry_response.get("status"), "queued")
        self.assertTrue(retry_response.get("new_job_id"))

        get_status, get_response = self._get_json(f"/api/sequence/plan-and-render/{request_id}")
        self.assertEqual(get_status, 200)
        self.assertIn(retry_response.get("new_job_id"), get_response.get("job_ids", []))

    def test_post_retry_shot_returns_404_when_request_missing(self) -> None:
        retry_status, retry_response = self._post_json(
            "/api/sequence/plan-and-render/not-found-request/retry-shot",
            {"shot_id": "shot_001"},
        )

        self.assertEqual(retry_status, 404)
        self.assertFalse(retry_response.get("ok", True))
        self.assertEqual(retry_response.get("error", {}).get("code"), "REQUEST_NOT_FOUND")

    def test_post_retry_shot_returns_404_when_shot_missing(self) -> None:
        post_status, post_response = self._post_json("/api/sequence/plan-and-render", self._valid_payload())
        self.assertEqual(post_status, 201)

        request_id = post_response.get("request_id")
        retry_status, retry_response = self._post_json(
            f"/api/sequence/plan-and-render/{request_id}/retry-shot",
            {"shot_id": "shot_missing"},
        )

        self.assertEqual(retry_status, 404)
        self.assertFalse(retry_response.get("ok", True))
        self.assertEqual(retry_response.get("error", {}).get("code"), "SHOT_NOT_FOUND")


if __name__ == "__main__":
    unittest.main()
