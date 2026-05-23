# -*- coding: utf-8 -*-
"""
DOI → Figure sources resolver.

Resolves a DOI to available figure sources via free APIs (no key needed):
- Semantic Scholar API: paper metadata, external IDs
- arXiv API: source download link (high-res figures in tarball)
- Publisher abstract page: link for manual browsing

Usage:
    python fetch_from_doi.py 10.1021/jacs.4c01234
    python fetch_from_doi.py 10.1021/jacs.4c01234 --output figures/

Outputs a JSON report with available figure source URLs and download instructions.
"""

import sys
import os
import json
import re
import urllib.request
import urllib.error
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

# Ensure scripts/ dir on path
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)
from utils import safe_print as _safe_print


# ============================================================
# API helpers
# ============================================================

def _api_get(url, timeout=15):
    """GET a JSON API with rate-limit handling and user-agent."""
    headers = {
        "User-Agent": "PDF2PPT-Skill/1.0 (mailto:example@example.com)",
        "Accept": "application/json",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            _safe_print("  Rate limited, waiting 3s...")
            time.sleep(3)
            return _api_get(url, timeout)
        return None
    except Exception as e:
        _safe_print(f"  API error: {e}")
        return None


# ============================================================
# Source resolvers
# ============================================================

def resolve_semantic_scholar(doi):  # type: (str) -> Optional[Dict]
    """Query Semantic Scholar for paper metadata and external IDs."""
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}"
    params = "?fields=title,externalIds,openAccessPdf,publicationVenue,year"
    data = _api_get(url + params)
    if not data or "paperId" not in data:
        return None

    result = {
        "source": "semantic_scholar",
        "paper_id": data.get("paperId"),
        "title": data.get("title", ""),
        "venue": data.get("publicationVenue", {}).get("name", "") if data.get("publicationVenue") else "",
        "year": data.get("year"),
        "external_ids": data.get("externalIds", {}),
        "open_access_pdf": data.get("openAccessPdf", {}).get("url") if data.get("openAccessPdf") else None,
    }
    return result


def resolve_arxiv(arxiv_id):  # type: (str) -> Optional[Dict]
    """Query arXiv API for paper metadata and source download."""
    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}&max_results=1"
    headers = {"User-Agent": "PDF2PPT-Skill/1.0"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml_text = resp.read().decode("utf-8")
    except Exception as e:
        _safe_print(f"  arXiv API error: {e}")
        return None

    # Parse minimal XML
    title_m = re.search(r"<title>(.*?)</title>", xml_text, re.DOTALL)
    title = title_m.group(1).strip() if title_m else ""
    # Remove the first title (feed title), keep second (paper title)
    titles = re.findall(r"<title>(.*?)</title>", xml_text, re.DOTALL)
    paper_title = titles[1].strip() if len(titles) > 1 else title

    return {
        "source": "arxiv",
        "arxiv_id": arxiv_id,
        "title": paper_title,
        "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
        "source_url": f"https://arxiv.org/e-print/{arxiv_id}",  # .tar.gz with figures
        "abstract_url": f"https://arxiv.org/abs/{arxiv_id}",
    }


def resolve_doi(doi):  # type: (str) -> Dict[str, Any]
    """Resolve a DOI through multiple sources and return available figure paths.

    Returns a dict with:
        doi, metadata, arxiv_info, semantic_scholar_info,
        figure_sources: list of {type, url, description}
    """
    doi = doi.strip()
    # Strip URL prefix if present
    doi = re.sub(r"^https?://doi\.org/", "", doi)

    report = {
        "doi": doi,
        "resolved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "arxiv": None,
        "semantic_scholar": None,
        "figure_sources": [],
        "download_suggestions": [],
    }

    # 1. Try Semantic Scholar
    _safe_print(f"Resolving DOI: {doi}")
    _safe_print("  [1/2] Semantic Scholar...")
    ss = resolve_semantic_scholar(doi)
    if ss:
        report["semantic_scholar"] = ss
        _safe_print(f"    Title: {ss['title'][:80]}...")
        _safe_print(f"    Year: {ss.get('year')}, Venue: {ss.get('venue', 'N/A')}")

        # Open access PDF
        if ss.get("open_access_pdf"):
            report["figure_sources"].append({
                "type": "open_access_pdf",
                "url": ss["open_access_pdf"],
                "description": "Open-access PDF from Semantic Scholar — higher quality than some publisher PDFs",
            })
            report["download_suggestions"].append(
                "Download the open-access PDF, then run extract_charts.py on it for higher quality"
            )

        # arXiv ID
        arxiv_id = ss.get("external_ids", {}).get("ArXiv")
        if arxiv_id:
            _safe_print(f"    ArXiv ID: {arxiv_id}")
            report["figure_sources"].append({
                "type": "arxiv_source",
                "arxiv_id": arxiv_id,
                "url": f"https://arxiv.org/e-print/{arxiv_id}",
                "description": "arXiv source tarball — contains original high-res figures",
            })
    else:
        _safe_print("    No Semantic Scholar entry found for this DOI")
        report["download_suggestions"].append(
            "Paper not found on Semantic Scholar. Try searching by title instead."
        )

    # 2. Try arXiv directly (in case Semantic Scholar missed it, or for direct access)
    _safe_print("  [2/2] arXiv...")
    if ss and ss.get("external_ids", {}).get("ArXiv"):
        arxiv_id = ss["external_ids"]["ArXiv"]
        arxiv_info = resolve_arxiv(arxiv_id)
        if arxiv_info:
            report["arxiv"] = arxiv_info
            _safe_print(f"    arXiv: {arxiv_id} — {arxiv_info['title'][:80]}...")
    else:
        _safe_print("    No arXiv ID available for this DOI")

    # Summary
    _safe_print(f"\n  Figure sources found: {len(report['figure_sources'])}")
    for i, src in enumerate(report["figure_sources"], 1):
        _safe_print(f"    [{i}] {src['type']}: {src.get('description', src.get('url', ''))[:100]}")

    return report


# ============================================================
# Figure download helpers
# ============================================================

def download_arxiv_source(arxiv_id, output_dir):  # type: (str, str) -> Optional[str]
    """Download arXiv source tarball, extract figures.

    The arXiv source .tar.gz often contains original high-resolution
    figures (PDF/EPS/PNG) used in the manuscript.

    Returns path to extracted figures directory, or None.
    """
    import tarfile
    import tempfile

    url = f"https://arxiv.org/e-print/{arxiv_id}"
    os.makedirs(output_dir, exist_ok=True)

    _safe_print(f"  Downloading arXiv source: {arxiv_id}...")
    headers = {"User-Agent": "PDF2PPT-Skill/1.0"}
    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
    except Exception as e:
        _safe_print(f"  Download failed: {e}")
        return None

    # Save and extract
    extract_dir = os.path.join(output_dir, f"arxiv_{arxiv_id}_figures")
    os.makedirs(extract_dir, exist_ok=True)

    tmp_path = os.path.join(output_dir, f"arxiv_{arxiv_id}.tar.gz")
    with open(tmp_path, "wb") as f:
        f.write(data)

    try:
        with tarfile.open(tmp_path, "r:gz") as tar:
            tar.extractall(extract_dir)
        _safe_print(f"  Extracted to: {extract_dir}")

        # Find figure files
        fig_exts = {".png", ".jpg", ".jpeg", ".pdf", ".eps", ".svg"}
        figures = []
        for root, dirs, files in os.walk(extract_dir):
            for fn in files:
                if Path(fn).suffix.lower() in fig_exts and "figure" not in root.lower():
                    # Check if filename looks like a figure
                    name_lower = fn.lower()
                    if any(kw in name_lower for kw in ("fig", "figure", "graph", "chart", "plot", "schema", "scheme")):
                        figures.append(os.path.join(root, fn))

        _safe_print(f"  Found {len(figures)} potential figure files")
        if figures:
            # Copy to flat output dir
            fig_out = os.path.join(extract_dir, "figures_flat")
            os.makedirs(fig_out, exist_ok=True)
            for f in figures:
                dst = os.path.join(fig_out, os.path.basename(f))
                with open(f, "rb") as src_f:
                    with open(dst, "wb") as dst_f:
                        dst_f.write(src_f.read())
            _safe_print(f"  Figures copied to: {fig_out}")

    except Exception as e:
        _safe_print(f"  Extraction failed: {e}")
        return None
    finally:
        # Clean up tarball
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    return extract_dir


# ============================================================
# CLI
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_from_doi.py <doi> [--output dir] [--download-arxiv]")
        print()
        print("Examples:")
        print("  python fetch_from_doi.py 10.1021/jacs.4c01234")
        print("  python fetch_from_doi.py 10.1021/jacs.4c01234 --output figures/")
        print("  python fetch_from_doi.py 10.1021/jacs.4c01234 --download-arxiv")
        print()
        print("Outputs a JSON report listing available figure sources and download URLs.")
        return

    doi = sys.argv[1]
    output_dir = "output"
    download_arxiv = False

    for i, arg in enumerate(sys.argv):
        if arg == "--output" and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]
        if arg == "--download-arxiv":
            download_arxiv = True

    report = resolve_doi(doi)

    # Save JSON report
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "doi_resolution.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    _safe_print(f"\nReport saved: {report_path}")

    # Download arXiv source if requested
    if download_arxiv:
        arxiv_src = next((s for s in report["figure_sources"] if s["type"] == "arxiv_source"), None)
        if arxiv_src:
            arxiv_id = arxiv_src["arxiv_id"]
            download_arxiv_source(arxiv_id, output_dir)
        else:
            _safe_print("No arXiv source available for this DOI")


if __name__ == "__main__":
    main()
