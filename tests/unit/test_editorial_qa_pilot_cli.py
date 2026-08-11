from __future__ import annotations

import io
import json

from scripts.editorial_intelligence.semantic_index.semantic_index import SemanticSearchResult
from scripts.local_media_agent import cid_cli, editorial_qa_pilot_cli
from services.llm.editorial_qa import EditorialQAGenerationResult, GenerationUsage


class FakeRetriever:
    def search(self, query):
        return [
            SemanticSearchResult(
                rank=1,
                score=1.0,
                asset_id="asset-a",
                segment_ref="asset-a::0::0",
                text="The station opened.",
                source_start_seconds=1.0,
                source_end_seconds=2.0,
                source_start_timecode=None,
                source_end_timecode=None,
            )
        ]


class FakeProvider:
    def __init__(self):
        self.calls = 0
        self.request = None

    async def generate_editorial_qa(self, request):
        self.calls += 1
        self.request = request
        return EditorialQAGenerationResult(
            answer="Supported.",
            citation_ids=("CIT-0001",),
            insufficient_evidence=False,
            provider="fake",
            model="fake-model",
            usage=GenerationUsage(),
        )


def test_editorial_qa_is_explicitly_dispatched() -> None:
    called = {}

    def fake_run_cli(argv, stdout, stderr):
        called["argv"] = argv
        return 17

    original = editorial_qa_pilot_cli.run_cli
    editorial_qa_pilot_cli.run_cli = fake_run_cli
    try:
        result = cid_cli.run_cli(
            ["editorial-qa", "--question", "q"], io.StringIO(), io.StringIO()
        )
    finally:
        editorial_qa_pilot_cli.run_cli = original
    assert result == 17
    assert called["argv"] == ["--question", "q"]


def test_pilot_cli_reaches_existing_orchestrator_and_preserves_result_shape() -> None:
    provider = FakeProvider()
    stdout = io.StringIO()
    result = editorial_qa_pilot_cli.run_cli(
        ["--question", "What happened?", "--corpus-id", "corpus-a"],
        stdout,
        io.StringIO(),
        retriever=FakeRetriever(),
        generation_provider=provider,
    )
    assert result == 0
    payload = json.loads(stdout.getvalue())
    assert payload["answer"] == "Supported."
    assert payload["citations"][0]["segment_ref"] == "asset-a::0::0"
    assert payload["insufficient_evidence"] is False
    assert provider.calls == 1


def test_unrelated_scan_dispatch_does_not_select_pilot() -> None:
    called = {}

    def fake_scan(argv, stdout, stderr):
        called["argv"] = argv
        return 0

    original = cid_cli.read_only_folder_scanner_cli.run_cli
    cid_cli.read_only_folder_scanner_cli.run_cli = fake_scan
    try:
        result = cid_cli.run_cli(
            ["scan", "--input-root", "/tmp/input"], io.StringIO(), io.StringIO()
        )
    finally:
        cid_cli.read_only_folder_scanner_cli.run_cli = original
    assert result == 0
    assert called["argv"] == ["--input-root", "/tmp/input"]
