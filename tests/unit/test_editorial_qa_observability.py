from __future__ import annotations

import asyncio
import hashlib
import io
import json

from scripts.editorial_intelligence.semantic_index.semantic_index import SemanticSearchResult
from scripts.local_media_agent import cid_cli, editorial_qa_pilot_cli
from services.editorial_qa_orchestration import EditorialQAOrchestrator, EditorialQARequest
from services.llm.editorial_qa import EditorialQAGenerationResult, GenerationUsage


class FakeRetriever:
    def __init__(self):
        self.calls = 0

    def search(self, query):
        self.calls += 1
        return [
            SemanticSearchResult(
                rank=1,
                score=0.9,
                asset_id="asset-a",
                segment_ref="asset-a::0::7",
                text="Evidence one.",
                source_start_seconds=7.0,
                source_end_seconds=8.0,
                source_start_timecode=None,
                source_end_timecode=None,
            ),
            SemanticSearchResult(
                rank=2,
                score=0.8,
                asset_id="asset-a",
                segment_ref="asset-a::0::8",
                text="Evidence two.",
                source_start_seconds=8.0,
                source_end_seconds=9.0,
                source_start_timecode=None,
                source_end_timecode=None,
            ),
        ]


class FakeProvider:
    def __init__(self, insufficient=False):
        self.calls = 0
        self.request = None
        self.insufficient = insufficient

    async def generate_editorial_qa(self, request):
        self.calls += 1
        self.request = request
        return EditorialQAGenerationResult(
            answer="",
            citation_ids=() if self.insufficient else ("CIT-0001",),
            insufficient_evidence=self.insufficient,
            provider="fake",
            model="fake-model",
            usage=GenerationUsage(),
        )


def test_diagnostics_disabled_by_default_and_normal_stdout_unchanged(tmp_path):
    provider = FakeProvider()
    stdout = io.StringIO()
    result = editorial_qa_pilot_cli.run_cli(
        ["--question", "Question", "--corpus-id", "corpus-a"],
        stdout,
        io.StringIO(),
        retriever=FakeRetriever(),
        generation_provider=provider,
    )
    assert result == 0
    assert json.loads(stdout.getvalue())["answer"] == ""
    assert list(tmp_path.iterdir()) == []


def test_opt_in_diagnostics_capture_exact_trace_without_extra_calls(tmp_path):
    retriever = FakeRetriever()
    provider = FakeProvider()
    stdout = io.StringIO()
    output_path = tmp_path / "diagnostic.json"
    result = editorial_qa_pilot_cli.run_cli(
        [
            "--question", "Question", "--corpus-id", "corpus-a",
            "--diagnostic-output", str(output_path),
        ],
        stdout,
        io.StringIO(),
        retriever=retriever,
        generation_provider=provider,
    )
    assert result == 0
    trace = json.loads(output_path.read_text(encoding="utf-8"))
    assert trace["retrieved_result_count"] == 2
    assert [item["canonical_segment_id"] for item in trace["retrieved_results"]] == [
        "asset-a::0::7", "asset-a::0::8"
    ]
    assert trace["selected_evidence_count"] == 2
    assert trace["citation_id_to_canonical_segment_map"] == {
        "CIT-0001": "asset-a::0::7", "CIT-0002": "asset-a::0::8"
    }
    assert trace["provider_boundary"]["allowed_citation_ids"] == ["CIT-0001", "CIT-0002"]
    assert trace["logical_result"]["citation_ids"] == ["CIT-0001"]
    context = "[CIT-0001]\n<source_data citation_id=CIT-0001>\nEvidence one.\n</source_data>\n\n[CIT-0002]\n<source_data citation_id=CIT-0002>\nEvidence two.\n</source_data>"
    assert trace["selected_context_bytes"] == len(context.encode("utf-8"))
    assert trace["selected_context_sha256"] == hashlib.sha256(context.encode("utf-8")).hexdigest()
    assert json.loads(stdout.getvalue())["citations"][0]["segment_ref"] == "asset-a::0::7"
    assert retriever.calls == 1
    assert provider.calls == 1
    assert "OPENAI_API_KEY" not in output_path.read_text(encoding="utf-8")


def test_insufficient_result_is_captured_without_citation_resolution(tmp_path):
    output_path = tmp_path / "insufficient.json"
    editorial_qa_pilot_cli.run_cli(
        ["--question", "Question", "--corpus-id", "corpus-a", "--diagnostic-output", str(output_path)],
        io.StringIO(),
        io.StringIO(),
        retriever=FakeRetriever(),
        generation_provider=FakeProvider(insufficient=True),
    )
    trace = json.loads(output_path.read_text(encoding="utf-8"))
    assert trace["logical_result"] == {
        "answer": "",
        "citation_ids": [],
        "insufficient_evidence": True,
    }
    assert trace["resolved_returned_citations"] == []


def test_direct_editorial_help_accepts_diagnostic_option_without_changing_umbrella():
    direct = io.StringIO()
    assert cid_cli.run_cli(["editorial-qa", "--help"], direct, io.StringIO()) == 0
    assert "--diagnostic-output PATH" in direct.getvalue()
    umbrella = io.StringIO()
    assert cid_cli.run_cli(["--help"], umbrella, io.StringIO()) == 0
    assert "--diagnostic-output" not in umbrella.getvalue()
