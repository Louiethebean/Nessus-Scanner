#!/usr/bin/env python3
"""Parse a .nessus (XML) export and produce a severity-ranked findings report.

Usage:
    python parse_nessus_report.py report.nessus [--format md|csv] [--min-severity 1]
"""
import argparse
import csv
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List

SEVERITY_NAMES = {0: "Info", 1: "Low", 2: "Medium", 3: "High", 4: "Critical"}


@dataclass
class Finding:
    host: str
    plugin_id: str
    plugin_name: str
    severity: int
    cvss_base_score: float
    cves: List[str] = field(default_factory=list)
    port: str = ""
    protocol: str = ""

    @property
    def severity_name(self) -> str:
        return SEVERITY_NAMES.get(self.severity, "Unknown")


def parse_nessus_file(path: str) -> List[Finding]:
    tree = ET.parse(path)
    root = tree.getroot()
    findings: List[Finding] = []

    for report_host in root.iter("ReportHost"):
        host = report_host.get("name", "unknown-host")
        for item in report_host.findall("ReportItem"):
            severity = int(item.get("severity", "0"))
            cvss_elem = item.find("cvss_base_score")
            cvss_score = float(cvss_elem.text) if cvss_elem is not None and cvss_elem.text else 0.0
            cves = [cve.text for cve in item.findall("cve") if cve.text]

            findings.append(
                Finding(
                    host=host,
                    plugin_id=item.get("pluginID", ""),
                    plugin_name=item.get("pluginName", ""),
                    severity=severity,
                    cvss_base_score=cvss_score,
                    cves=cves,
                    port=item.get("port", ""),
                    protocol=item.get("protocol", ""),
                )
            )

    return findings


def rank_findings(findings: List[Finding], min_severity: int = 1) -> List[Finding]:
    filtered = [f for f in findings if f.severity >= min_severity]
    return sorted(filtered, key=lambda f: (-f.severity, -f.cvss_base_score))


def to_markdown(findings: List[Finding]) -> str:
    if not findings:
        return "# Nessus Findings Report\n\nNo findings at or above the requested severity threshold.\n"

    lines = ["# Nessus Findings Report", ""]
    lines.append(f"**Total findings:** {len(findings)}")
    counts = {}
    for f in findings:
        counts[f.severity_name] = counts.get(f.severity_name, 0) + 1
    summary = ", ".join(f"{name}: {count}" for name, count in sorted(counts.items(), key=lambda kv: -SEVERITY_NAMES_REVERSE.get(kv[0], 0)))
    lines.append(f"**By severity:** {summary}")
    lines.append("")
    lines.append("| Severity | Host | Port | Plugin | CVSS | CVEs |")
    lines.append("|---|---|---|---|---|---|")
    for f in findings:
        cve_str = ", ".join(f.cves) if f.cves else "-"
        lines.append(
            f"| {f.severity_name} | {f.host} | {f.port}/{f.protocol} | {f.plugin_name} (#{f.plugin_id}) | {f.cvss_base_score} | {cve_str} |"
        )
    return "\n".join(lines) + "\n"


SEVERITY_NAMES_REVERSE = {v: k for k, v in SEVERITY_NAMES.items()}


def to_csv(findings: List[Finding], out) -> None:
    writer = csv.writer(out)
    writer.writerow(["severity", "host", "port", "protocol", "plugin_id", "plugin_name", "cvss_base_score", "cves"])
    for f in findings:
        writer.writerow(
            [f.severity_name, f.host, f.port, f.protocol, f.plugin_id, f.plugin_name, f.cvss_base_score, ";".join(f.cves)]
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse a .nessus report into a ranked findings summary.")
    parser.add_argument("report", help="Path to a .nessus XML export")
    parser.add_argument("--format", choices=["md", "csv"], default="md")
    parser.add_argument("--min-severity", type=int, default=1, help="Minimum severity to include (0=Info..4=Critical)")
    args = parser.parse_args()

    findings = parse_nessus_file(args.report)
    ranked = rank_findings(findings, args.min_severity)

    if args.format == "md":
        sys.stdout.write(to_markdown(ranked))
    else:
        to_csv(ranked, sys.stdout)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
