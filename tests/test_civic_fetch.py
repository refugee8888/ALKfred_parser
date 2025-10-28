# tests/test_civic_fetch.py
import json
from pathlib import Path
from alkfred.etl import civic_fetch

def test_fetch_returns_cached_when_not_overwrite(tmp_path, monkeypatch):
    raw = tmp_path / "civic_raw_evidence_db.json"
    raw.write_text(json.dumps([{"id": 1, "molecularProfile": {"name": "EML4-ALK"}}]))

    # no network call should happen if file exists and overwrite=False
    called = {"count": 0}
    def _fake_fetch():
        called["count"] += 1
        return [{"id": 999}]
    # Patch the api fetcher just to prove it won't be called
    monkeypatch.setattr(civic_fetch.api_calls, "fetch_civic_all_evidence_items", _fake_fetch)

    out = civic_fetch.fetch_civic_evidence(oncogene=None, raw_path=raw, overwrite=False, limit=None)

    assert out == [{"id": 1, "molecularProfile": {"name": "EML4-ALK"}}]
    assert called["count"] == 0  # no fetch

def test_fetch_filters_and_limit(tmp_path, monkeypatch):
    raw = tmp_path / "civic_raw_evidence_db.json"

    # fake upstream payload (mixed gene content)
    payload = [
        {"id": 1, "molecularProfile": {"name": "BCR-ABL1 fusion"}},
        {"id": 2, "molecularProfile": {"name": "EML4-ALK fusion"}},
        {"id": 3, "molecularProfile": {"name": "ALK L1196M"}},
        {"id": 4, "molecularProfile": {"name": "EGFR L858R"}},
    ]

    # patch network + gene detector
    monkeypatch.setattr(civic_fetch.api_calls, "fetch_civic_all_evidence_items", lambda: payload)
    monkeypatch.setattr(civic_fetch.civic_parser, "gene_in_molecular_profile",
                        lambda name, oncogene: (oncogene == "ALK") and ("ALK" in (name or "")))

    out = civic_fetch.fetch_civic_evidence(oncogene="ALK", raw_path=raw, overwrite=True, limit=1)

    # limited to 1 ALK item
    assert len(out) == 1
    assert out[0]["id"] in (2, 3)

    # file was written
    assert raw.exists()
    on_disk = json.loads(raw.read_text())
    assert on_disk == out

def test_fetch_overwrite_replaces_file(tmp_path, monkeypatch):
    raw = tmp_path / "civic_raw_evidence_db.json"
    raw.write_text(json.dumps([{"id": "OLD"}]))

    monkeypatch.setattr(civic_fetch.api_calls, "fetch_civic_all_evidence_items",
                        lambda: [{"id": 101, "molecularProfile": {"name": "EML4-ALK"}}])
    monkeypatch.setattr(civic_fetch.civic_parser, "gene_in_molecular_profile",
                        lambda name, oncogene: True)

    out = civic_fetch.fetch_civic_evidence(oncogene=None, raw_path=raw, overwrite=True, limit=None)

    assert out == [{"id": 101, "molecularProfile": {"name": "EML4-ALK"}}]
    assert json.loads(raw.read_text()) == out