import logging
import api_calls


def _make_page(nodes, has_next, cursor=None):
    return {
        "evidenceItems": {
            "nodes": nodes,
            "pageInfo": {"hasNextPage": has_next, "endCursor": cursor},
        }
    }


def test_deduplication_across_pages(monkeypatch):
    """Same ID appearing on two pages should only appear once in output."""
    logger = logging.getLogger("test_api_calls")

    duplicate_item = {"id": 101, "molecularProfile": {"name": "EML4-ALK"}}

    pages = [
        _make_page([duplicate_item], has_next=True, cursor="cursor1"),
        _make_page([duplicate_item], has_next=False),
    ]
    call_count = {"n": 0}

    def fake_graphql_query(**kwargs):
        result = pages[call_count["n"]]
        call_count["n"] += 1
        return result

    monkeypatch.setattr(api_calls, "graphql_query", fake_graphql_query)

    out = api_calls.fetch_civic_all_evidence_items(logger=logger)

    assert len(out) == 1
    assert out[0]["id"] == 101


def test_stops_when_no_next_page(monkeypatch):
    """Should stop after a single page when hasNextPage is False."""
    logger = logging.getLogger("test_api_calls")

    pages = [
        _make_page([{"id": 1}, {"id": 2}], has_next=False),
    ]
    call_count = {"n": 0}

    def fake_graphql_query(**kwargs):
        result = pages[call_count["n"]]
        call_count["n"] += 1
        return result

    monkeypatch.setattr(api_calls, "graphql_query", fake_graphql_query)

    out = api_calls.fetch_civic_all_evidence_items(logger=logger)

    assert call_count["n"] == 1
    assert len(out) == 2
