import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from parse_nessus_report import parse_nessus_file, rank_findings, to_markdown  # noqa: E402

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "sample_report.nessus")


def test_parse_nessus_file_counts_all_items():
    findings = parse_nessus_file(FIXTURE)
    assert len(findings) == 4


def test_rank_findings_filters_by_min_severity():
    findings = parse_nessus_file(FIXTURE)
    ranked = rank_findings(findings, min_severity=3)
    assert len(ranked) == 2
    assert all(f.severity >= 3 for f in ranked)


def test_rank_findings_sorts_critical_first():
    findings = parse_nessus_file(FIXTURE)
    ranked = rank_findings(findings, min_severity=0)
    assert ranked[0].severity == 4
    assert ranked[0].plugin_id == "58453"


def test_parses_cves():
    findings = parse_nessus_file(FIXTURE)
    critical = next(f for f in findings if f.plugin_id == "58453")
    assert "CVE-2019-0708" in critical.cves
    assert "CVE-2019-1182" in critical.cves


def test_to_markdown_includes_summary_counts():
    findings = parse_nessus_file(FIXTURE)
    ranked = rank_findings(findings, min_severity=1)
    md = to_markdown(ranked)
    assert "Total findings:** 3" in md
    assert "Critical" in md


def test_to_markdown_empty_findings():
    md = to_markdown([])
    assert "No findings" in md
