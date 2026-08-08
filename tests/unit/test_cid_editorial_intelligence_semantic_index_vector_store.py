from __future__ import annotations

from dataclasses import FrozenInstanceError

import httpx
import pytest

from scripts.editorial_intelligence.semantic_index.vector_store import (
    QdrantVectorStore,
    ReadPoint,
    VectorStoreError,
)


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def request(self, method, url, **kwargs):
        self.requests.append((method, url, kwargs))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def response(body, status_code=200):
    return httpx.Response(status_code, json=body)


def store(client):
    return QdrantVectorStore(client=client)


def test_count_forwards_exact_filter_and_returns_integer_without_writes():
    client = FakeClient([response({"result": {"count": 0}})])
    value = store(client).count_points(filters={"corpus_id": "corpus-a"})
    assert value == 0
    method, url, kwargs = client.requests[0]
    assert method == "POST"
    assert url.endswith("/collections/cid_editorial_transcripts_v1/points/count")
    assert kwargs["json"] == {
        "filter": {"must": [{"key": "corpus_id", "match": {"value": "corpus-a"}}]},
        "exact": True,
    }


def test_count_rejects_transport_and_malformed_failures():
    for client in (
        FakeClient([response({}, 500)]),
        FakeClient([httpx.ConnectError("offline")]),
        FakeClient([response({"result": {"count": "1"}})]),
    ):
        with pytest.raises(VectorStoreError, match="filtered count failed|vector store unavailable"):
            store(client).count_points(filters={})


def test_count_missing_collection_is_distinct():
    with pytest.raises(VectorStoreError, match="collection not found"):
        store(FakeClient([response({}, 404)])).count_points(filters={})


def test_scroll_one_page_preserves_ids_payload_and_excludes_vectors():
    payload = {"corpus_id": "corpus-a", "text": "alpha"}
    client = FakeClient([response({"result": {"points": [{"id": 7, "payload": payload}], "next_page_offset": None}})])
    result = store(client).scroll_points(filters={"corpus_id": "corpus-a"})
    assert result == (ReadPoint("7", payload),)
    assert client.requests[0][2]["json"] == {
        "filter": {"must": [{"key": "corpus_id", "match": {"value": "corpus-a"}}]},
        "limit": 256,
        "with_payload": True,
        "with_vector": False,
    }


def test_scroll_multi_page_forwards_exact_continuation_and_stops():
    client = FakeClient([
        response({"result": {"points": [{"id": "a", "payload": {"n": 1}}], "next_page_offset": {"id": 1}}}),
        response({"result": {"points": [{"id": "b", "payload": {"n": 2}}], "next_page_offset": None}}),
    ])
    result = store(client).scroll_points(filters={"asset_id": "asset-a"}, page_size=1, max_pages=2)
    assert [point.point_id for point in result] == ["a", "b"]
    assert "offset" not in client.requests[0][2]["json"]
    assert client.requests[1][2]["json"]["offset"] == {"id": 1}


def test_scroll_validates_page_size_and_max_pages():
    for page_size in (0, -1, 257):
        with pytest.raises(VectorStoreError, match="invalid page size"):
            store(FakeClient([])).scroll_points(filters={}, page_size=page_size)
    for max_pages in (0, -1, 4):
        with pytest.raises(VectorStoreError, match="invalid max pages"):
            store(FakeClient([])).scroll_points(filters={}, max_pages=max_pages)


def test_scroll_stops_when_offset_absent_and_bounds_608_pages_at_three_requests():
    responses = [
        response({"result": {"points": [{"id": str(index), "payload": {}} for index in range(size)], "next_page_offset": offset}})
        for size, offset in ((256, 256), (256, 512), (96, None))
    ]
    client = FakeClient(responses)
    result = store(client).scroll_points(filters={"corpus_id": "generic"}, page_size=256, max_pages=3)
    assert len(result) == 608
    assert len(client.requests) == 3


def test_scroll_fails_closed_without_partial_result_when_truncated():
    client = FakeClient([
        response({"result": {"points": [], "next_page_offset": 1}}),
        response({"result": {"points": [], "next_page_offset": 2}}),
    ])
    with pytest.raises(VectorStoreError, match="read verification limit exceeded"):
        store(client).scroll_points(filters={}, page_size=1, max_pages=2)
    assert len(client.requests) == 2


def test_scroll_rejects_transport_missing_collection_and_malformed_responses():
    with pytest.raises(VectorStoreError, match="collection not found"):
        store(FakeClient([response({}, 404)])).scroll_points(filters={})
    with pytest.raises(VectorStoreError, match="filtered read failed"):
        store(FakeClient([response({}, 500)])).scroll_points(filters={})
    with pytest.raises(VectorStoreError, match="filtered read response invalid"):
        store(FakeClient([response({"result": {"points": [{"id": "x"}]}})])).scroll_points(filters={})


def test_read_point_is_immutable_and_has_no_vector():
    point = ReadPoint("id", {"corpus_id": "generic"})
    with pytest.raises(FrozenInstanceError):
        point.point_id = "other"
    assert not hasattr(point, "vector")


def test_generic_filters_have_no_corpus_specific_behavior():
    client = FakeClient([response({"result": {"count": 3}})])
    assert store(client).count_points(filters={"source_audio_stream_index": 4}) == 3
    assert "kenya_tarjeta" not in str(client.requests[0])
    assert "cid_memory" not in str(client.requests[0])


@pytest.mark.parametrize("page_size", [1, 256])
def test_valid_page_size_boundaries_are_forwarded(page_size):
    client = FakeClient([response({"result": {"points": [], "next_page_offset": None}})])
    store(client).scroll_points(filters={}, page_size=page_size, max_pages=1)
    assert client.requests[0][2]["json"]["limit"] == page_size


def test_count_preserves_positive_exact_value():
    assert store(FakeClient([response({"result": {"count": 608}})])).count_points(filters={}) == 608


def test_count_rejects_boolean_count():
    with pytest.raises(VectorStoreError, match="filtered count failed"):
        store(FakeClient([response({"result": {"count": True}})])).count_points(filters={})


def test_count_rejects_negative_count():
    with pytest.raises(VectorStoreError, match="filtered count failed"):
        store(FakeClient([response({"result": {"count": -1}})])).count_points(filters={})


def test_scroll_forwards_multiple_exact_filter_fields():
    filters = {"corpus_id": "generic", "asset_id": "asset", "source_audio_stream_index": 2}
    client = FakeClient([response({"result": {"points": [], "next_page_offset": None}})])
    store(client).scroll_points(filters=filters, max_pages=1)
    assert len(client.requests[0][2]["json"]["filter"]["must"]) == 3


def test_scroll_preserves_multiple_payloads():
    points = [
        {"id": "a", "payload": {"text": "one"}},
        {"id": "b", "payload": {"text": "two"}},
    ]
    result = store(FakeClient([response({"result": {"points": points, "next_page_offset": None}})])).scroll_points(filters={})
    assert [point.payload for point in result] == [{"text": "one"}, {"text": "two"}]


def test_scroll_rejects_point_without_payload():
    client = FakeClient([response({"result": {"points": [{"id": "x", "payload": None}], "next_page_offset": None}})])
    with pytest.raises(VectorStoreError, match="filtered read response invalid"):
        store(client).scroll_points(filters={})


def test_scroll_rejects_missing_result():
    with pytest.raises(VectorStoreError, match="filtered read response invalid"):
        store(FakeClient([response({})])).scroll_points(filters={})


def test_scroll_rejects_non_list_points():
    body = {"result": {"points": {}, "next_page_offset": None}}
    with pytest.raises(VectorStoreError, match="filtered read response invalid"):
        store(FakeClient([response(body)])).scroll_points(filters={})


def test_scroll_does_not_search_or_write():
    client = FakeClient([response({"result": {"points": [], "next_page_offset": None}})])
    store(client).scroll_points(filters={}, max_pages=1)
    assert all("/search" not in request[1] for request in client.requests)
    assert all(request[0] == "POST" for request in client.requests)


def test_count_does_not_create_collection():
    client = FakeClient([response({"result": {"count": 1}})])
    store(client).count_points(filters={})
    assert all(request[0] == "POST" for request in client.requests)
    assert all("/collections/cid_editorial_transcripts_v1" in request[1] for request in client.requests)


def test_scroll_does_not_include_offset_on_first_page():
    client = FakeClient([response({"result": {"points": [], "next_page_offset": None}})])
    store(client).scroll_points(filters={}, max_pages=1)
    assert "offset" not in client.requests[0][2]["json"]


def test_scroll_uses_exact_integer_continuation():
    client = FakeClient([
        response({"result": {"points": [], "next_page_offset": 17}}),
        response({"result": {"points": [], "next_page_offset": None}}),
    ])
    store(client).scroll_points(filters={}, page_size=1, max_pages=2)
    assert client.requests[1][2]["json"]["offset"] == 17


def test_read_point_payload_is_not_replaced_or_normalized():
    payload = {"nested": {"value": 1}, "text": "  raw  "}
    result = store(FakeClient([response({"result": {"points": [{"id": "x", "payload": payload}], "next_page_offset": None}})])).scroll_points(filters={})
    assert result[0].payload == payload


def test_indexing_contract_methods_remain_available():
    boundary = store(FakeClient([]))
    assert callable(boundary.replace_corpus)
    assert callable(boundary.delete_corpus)
    assert callable(boundary.search)


def test_empty_filter_is_forwarded_as_empty_must_clause():
    client = FakeClient([response({"result": {"count": 0}})])
    store(client).count_points(filters={})
    assert client.requests[0][2]["json"]["filter"] == {"must": []}
