"""Extract SM-like heavy-scalar theory inputs for the Candidate B extended test.

Parses two pinned LHC Higgs Cross Section Working Group (HXSWG) TWiki pages held
in git-ignored ``data/external/candidate_b/raw``:

* CERNYellowReportPageBSMAt13TeV, topic revision r30: 13 TeV gluon-fusion
  (quark-loop induced, NNLO+NNLL QCD, narrow width) and VBF (approximate NNLO
  QCD) cross sections for an SM-like scalar of mass m_H.
* CERNYellowReportPageBR2014, topic revision r16 (CERN Report 3, 2013 update):
  SM Higgs branching ratios to WW and ZZ and the total width for 80-1000 GeV.

The extracted numbers are written to a small committed table so the extended
test can be reproduced without network access. The raw HTML hashes are pinned
in the data catalog; this script refuses to run if they differ.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "external" / "candidate_b" / "raw"
CATALOG = ROOT / "knowledgebase" / "library" / "data_catalog.json"
OUTPUT = ROOT / "knowledgebase" / "candidate_b_theory_inputs.json"
DATASET_ID = "hxswg-sm-like-heavy-higgs-13tev"
BSM_PAGE = RAW / "hxswg_bsm_at_13tev_r30.html"
BR_PAGE = RAW / "hxswg_br_yr3_2013update_r16.html"
EXPECTED_REVISIONS = {BSM_PAGE.name: "r30", BR_PAGE.name: "r16"}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _cells(row: str) -> list[str]:
    return [html.unescape(re.sub(r"<[^>]+>", "", cell)).strip()
            for cell in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, re.S)]


def tables(text: str) -> list[list[list[str]]]:
    return [[_cells(row) for row in re.findall(r"<tr.*?</tr>", table, re.S)]
            for table in re.findall(r"<table.*?</table>", text, re.S)]


def topic_revision(text: str) -> str:
    match = re.search(r"Topic revision: (r\d+) - (\d{4}-\d{2}-\d{2})", text)
    if match is None:
        raise ValueError("topic revision not found")
    return match.group(1)


def _number(cell: str) -> float | None:
    cleaned = cell.replace(",", "").replace("\u00b1", "").replace("\ufffd", "").strip()
    cleaned = cleaned.lstrip("+")
    if not cleaned:
        return None
    return float(cleaned)


def _find(all_tables: list[list[list[str]]], predicate: Any) -> list[list[str]]:
    matches = [table for table in all_tables if table and predicate(table)]
    if len(matches) != 1:
        raise ValueError(f"expected one matching table, found {len(matches)}")
    return matches[0]


def parse_bsm_page(text: str) -> dict[str, list[list[float | None]]]:
    all_tables = tables(text)
    ggf = _find(all_tables, lambda t: len(t) > 1 and "Quark-loop induced" in t[0]
                and t[1][:1] == ["mS or mH (GeV)"])
    if ggf[1][7:14] != ["Cross Section (pb)", "+QCD Scale %", "-QCD Scale %",
                        "\u00b1(PDF+\u03b1s) %", "\u00b1PDF %", "\u00b1\u03b1s %",
                        "1+\u03b4EW"]:
        raise ValueError(f"unexpected ggF quark-loop columns: {ggf[1][7:14]}")
    vbf = _find(all_tables, lambda t: t[0][:2] == ["mH (GeV)", "Cross Section (pb)"]
                and len(t) > 100 and t[0][-1] == "1+\u03b4EW" and len(t[0]) == 8)
    ggf_rows: list[list[float | None]] = []
    for row in ggf[2:]:
        mass, xs = _number(row[0]), _number(row[7])
        if mass is None or xs is None:
            continue
        # The page writes 0 where no EW factor is provided (outside 100-2500 GeV).
        ew = _number(row[13]) or None
        ggf_rows.append([mass, xs, _number(row[8]), _number(row[9]), _number(row[10]), ew])
    vbf_rows: list[list[float | None]] = [
        [_number(row[0]), _number(row[1]), _number(row[2]), _number(row[3]),
         _number(row[4]), _number(row[7]) if len(row) > 7 else None]
        for row in vbf[1:]]
    return {"ggF": ggf_rows, "VBF": vbf_rows}


def parse_br_page(text: str) -> list[list[float | None]]:
    all_tables = tables(text)
    gauge = _find(all_tables, lambda t: t[0][:1] == ["MH"] and "H \u2192 ZZ" in t[0]
                  and "Total \u0393H" in t[0])
    header = gauge[0]
    if header != ["MH", "H \u2192 gg", "H \u2192 \u03b3\u03b3", "H \u2192 Z\u03b3",
                  "H \u2192 WW", "H \u2192 ZZ", "Total \u0393H"]:
        raise ValueError(f"unexpected BR columns: {header}")
    rows: list[list[float | None]] = []
    for row in gauge[2:]:
        # Each BR occupies three cells (value, +err %, -err %).
        rows.append([_number(row[0]), _number(row[10]), _number(row[13]),
                     _number(row[16]), _number(row[17]), _number(row[18])])
    return rows


def build_table() -> dict[str, Any]:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    entry = next(d for d in catalog["datasets"] if d["id"] == DATASET_ID)
    holdings = []
    for holding in entry["holdings"]:
        path = ROOT / holding["path"]
        digest = sha256_file(path)
        if digest != holding["sha256"]:
            raise RuntimeError(f"{holding['path']} hash differs from the catalog; stop")
        text = path.read_text(encoding="utf-8", errors="replace")
        revision = topic_revision(text)
        if revision != EXPECTED_REVISIONS[path.name]:
            raise RuntimeError(f"{path.name} is {revision}, expected "
                               f"{EXPECTED_REVISIONS[path.name]}")
        holdings.append({"path": holding["path"], "url": holding["url"], "sha256": digest,
                         "topic_revision": revision})
    bsm = parse_bsm_page(BSM_PAGE.read_text(encoding="utf-8", errors="replace"))
    br = parse_br_page(BR_PAGE.read_text(encoding="utf-8", errors="replace"))
    return {
        "schema_version": 1,
        "artifact": "candidate_b_theory_inputs",
        "source": Path(__file__).relative_to(ROOT).as_posix(),
        "dataset": DATASET_ID,
        "holdings": holdings,
        "sqrt_s_TeV": 13.0,
        "ggF_columns": ["mass_GeV", "sigma_pb", "qcd_scale_up_pct", "qcd_scale_down_pct",
                        "pdf_alphas_pct", "one_plus_delta_ew"],
        "ggF_note": "Quark-loop induced SM-like scalar, NNLO+NNLL QCD, top/bottom/charm "
                    "loops, narrow width; 1+delta_EW is given separately and is not "
                    "included in sigma_pb.",
        "ggF": bsm["ggF"],
        "VBF_columns": ["mass_GeV", "sigma_pb", "qcd_scale_up_pct", "qcd_scale_down_pct",
                        "pdf_alphas_pct", "one_plus_delta_ew"],
        "VBF_note": "Approximate NNLO QCD (VBF@NNLO), narrow width; 1+delta_EW not included.",
        "VBF": bsm["VBF"],
        "sm_width_columns": ["mass_GeV", "BR_WW", "BR_ZZ", "total_width_GeV",
                             "total_width_err_up_pct", "total_width_err_down_pct"],
        "sm_width_note": "CERN Report 3 (2013 update) SM Higgs BR and total width "
                         "(HDECAY+Prophecy4f); 80-1000 GeV.",
        "sm_width": br,
    }


def main() -> None:
    table = build_table()
    OUTPUT.write_text(json.dumps(table, indent=1) + "\n", encoding="utf-8")
    print(f"Saved {OUTPUT}: ggF {len(table['ggF'])}, VBF {len(table['VBF'])}, "
          f"width {len(table['sm_width'])} rows")


if __name__ == "__main__":
    main()
