# -*- coding: utf-8 -*-
"""
PDF 论文分析脚本 — 化学论文类型识别、章节结构、图表位置、关键信息提取
Chemistry Paper Analyzer with JSON output and robust encoding handling.

Keywords are loaded from references/chemistry_keywords.json (configurable).
"""
import fitz
import sys
import os
import re
import json
from collections import defaultdict

# Ensure scripts/ dir on path for direct invocation
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from utils import safe_print as _safe_print, cluster_drawings_compat


# ============================================================
# 关键词加载 / Keyword Loading
# ============================================================

def _load_keywords():
    """Load chemistry keywords from JSON config, with embedded fallback."""
    config_paths = [
        os.path.join(_scripts_dir, "..", "references", "chemistry_keywords.json"),
        os.path.join(_scripts_dir, "chemistry_keywords.json"),
    ]
    for cp in config_paths:
        try:
            cfg = json.loads(open(cp, encoding="utf-8").read())
            subfields_raw = cfg.get("subfields", {})
            chem_keywords = {}
            for name, entry in subfields_raw.items():
                chem_keywords[name] = entry.get("keywords", [])
            char_terms = cfg.get("characterization_terms", [])
            comp_strong = cfg.get("computational_strong_signals", [])
            section_pats = cfg.get("section_patterns", [])
            method_pats = cfg.get("method_patterns", [])
            return chem_keywords, char_terms, comp_strong, section_pats, method_pats
        except Exception:
            continue

    # Fallback: embedded defaults (keeps script self-contained)
    _safe_print("[analyze_paper] Config file not found, using built-in defaults.")
    return _builtin_defaults()


def _builtin_defaults():
    """Built-in keyword defaults — used when JSON config is unavailable."""
    chem_keywords = {
        "催化": ["cataly", "TOF", "turnover", "selectivity", "conversion",
                 "catalyst", "active site", "Sabatier", "d-band", "overpotential"],
        "材料": ["MOF", "COF", "perovskite", "zeolite", "framework",
                 "polymer", "nanosheet", "nanoparticle", "quantum dot"],
        "有机合成": ["synthesis", "yield", "substrate scope", "coupling",
                     "cross-coupling", "organocatal", "asymmetric", "functional group"],
        "计算化学": [
            "DFT", "density functional", "VASP", "Gaussian", "CP2K",
            "Quantum ESPRESSO", "molecular dynamics", "AIMD", "ab initio",
            "MD simulation", "free energy", "transition state",
            "k-point", "pseudopotential", "PAW", "basis set",
            "B3LYP", "PBE", "RPBE", "SCAN", "HSE", "GGA", "PBE0",
            "Hartree-Fock", "coupled cluster", "CCSD", "MP2",
            "Monte Carlo", "metadynamics", "enhanced sampling",
            "reaction coordinate", "diabatic", "adiabatic",
            "reorganization energy", "Marcus theory"],
        "电化学": ["electrochem", "ORR", "OER", "HER", "CO2RR", "NRR",
                   "Li-ion", "battery", "supercapacitor", "electrolyte",
                   "faradaic efficiency", "Tafel", "RHE", "SHE"],
        "光谱/表征": ["XRD", "XPS", "TEM", "SEM", "STEM", "HAADF",
                      "NMR", "IR", "Raman", "EXAFS", "XANES", "BET",
                      "EPR", "UV-vis", "AFM", "FTIR", "spectroscopy"],
        "环境/大气": ["atmospheric", "aerosol", "SOA", "PM2.5", "oxidation",
                      "OH radical", "ozone", "photochem", "tropospheric"],
        "能源": ["solar cell", "perovskite solar", "water splitting",
                 "hydrogen evolution", "photocatal", "fuel cell", "battery"],
        "辐射化学": ["radiolysis", "pulse radiolysis", "hydrated electron",
                     "solvated electron", "transient absorption"],
    }
    char_terms = ["XRD", "XPS", "TEM", "SEM", "STEM", "HAADF", "NMR", "IR",
                  "Raman", "EXAFS", "XANES", "BET", "EPR", "UV-vis", "AFM", "FTIR"]
    comp_strong = ["DFT", "density functional theory", "VASP", "Gaussian", "CP2K",
                   "Quantum ESPRESSO", "ab initio molecular dynamics", "AIMD",
                   "PBE0", "B3LYP", "PBE", "Hartree-Fock", "CCSD", "MP2",
                   "transition state", "reaction coordinate", "diabatic",
                   "pseudopotential", "basis set", "k-point", "cutoff",
                   "molecular dynamics simulation", "trajector"]
    section_pats = [
        [r"^\s*(?:Abstract|摘要)\s*$", "Abstract"],
        [r"^\s*(?:Introduction|引言|绪论)\s*$", "Introduction"],
        [r"^\s*(?:Method|Experimental|Computational|计算方法?|实验方法?|Theory)\s*", "Methods"],
        [r"^\s*(?:Result|Discussion|结果|讨论)\s*", "Results"],
        [r"^\s*(?:Conclusion|结论|Summary|总结)\s*$", "Conclusions"],
        [r"^\s*(?:Supporting Information|SI|附录|补充|References?)\s*", "SI/References"],
    ]
    method_pats = [
        [r"CP2K|VASP|Gaussian\s*\d+|Q-Chem\s*\d+|GROMACS|LAMMPS|Quantum\s+ESPRESSO", 2],
        [r"PBE0|B3LYP|PBE|RPBE|SCAN|HSE06|GGA|LDA|meta-GGA", 1],
        [r"impregnation|sol-gel|hydrothermal|solvothermal|co-precipitation|calcination|pyrolysis", 1],
        [r"XRD|XPS|TEM|SEM|STEM|HAADF-STEM|NMR|IR|Raman|EXAFS|XANES|BET|EPR", 1],
    ]
    return chem_keywords, char_terms, comp_strong, section_pats, method_pats


# Module-level lazy load
_CHEM_KW, _CHAR_TERMS, _COMP_STRONG, _SECTION_PATS, _METHOD_PATS = (None,) * 5


def _kw():
    """Lazy keyword loader — loads JSON once on first access."""
    global _CHEM_KW, _CHAR_TERMS, _COMP_STRONG, _SECTION_PATS, _METHOD_PATS
    if _CHEM_KW is None:
        _CHEM_KW, _CHAR_TERMS, _COMP_STRONG, _SECTION_PATS, _METHOD_PATS = _load_keywords()
    return _CHEM_KW, _CHAR_TERMS, _COMP_STRONG, _SECTION_PATS, _METHOD_PATS


def is_chemistry_domain(text: str, min_signal_count: int = 3) -> bool:
    """Detect whether the text is likely a chemistry paper.

    Returns False for clearly non-chemistry domains (biology, physics, medicine
    without chemical content), allowing the caller to warn or switch strategies.

    Args:
        text: Full paper text.
        min_signal_count: Minimum unique keyword matches to classify as chemistry.
    """
    chem_kw, char_terms, comp_strong, _, _ = _kw()
    text_lower = text.lower()
    hits = 0
    # Count unique keyword families that match
    for subfield, keywords in chem_kw.items():
        if any(kw.lower() in text_lower for kw in keywords):
            hits += 1
    return hits >= min_signal_count


def analyze_pdf(pdf_path, verbose=True, output_json=None, lang="zh"):
    """分析 PDF 论文的完整结构和内容

    Args:
        pdf_path: Path to the PDF file.
        verbose: Print analysis summary to stdout.
        output_json: If set, write JSON report to this path.
        lang: Output language hint — 'zh' (Chinese) or 'en' (English).
              Affects log messages only; JSON keys remain English.

    Returns:
        dict: Structured analysis result. Contains ``is_chemistry`` flag
              indicating whether the paper was recognized as chemistry domain.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    chem_kw, char_terms, comp_strong, section_pats, method_pats = _kw()

    errors = []
    doc = fitz.open(pdf_path)
    result = {
        "source": os.path.basename(pdf_path),
        "title": "",
        "paper_type": "experimental",
        "paper_type_confidence": "low",
        "subfields": [],
        "sections": [],
        "figures_detected": defaultdict(list),
        "tables_detected": defaultdict(list),
        "chemical_methods": [],
        "total_pages": len(doc),
        "has_supporting_info": False,
        "is_chemistry": True,
        "errors": errors,
    }

    full_text = ""
    first_page_text = ""
    abstract_text = ""

    # 提取所有文本
    for page_num in range(len(doc)):
        try:
            page = doc[page_num]
            text = page.get_text()
            full_text += text
            if page_num == 0:
                first_page_text = text
            if page_num <= 1:
                abstract_text += text
        except Exception as e:
            errors.append(f"Page {page_num+1} text extraction failed: {e}")

    full_text_lower = full_text.lower()

    # ---- 领域检测 ----
    result["is_chemistry"] = is_chemistry_domain(full_text)
    if not result["is_chemistry"]:
        msg = ("Domain detection: few chemistry signals found. "
               "Paper may not be chemistry. Output may be inaccurate. "
               "Consider adapting keyword config for this domain.")
        errors.append(msg)
        if verbose:
            _safe_print(f"  [!] {msg}")

    # ---- 标题提取 ----
    lines = [l.strip() for l in first_page_text.split('\n') if l.strip()]
    if lines:
        result["title"] = lines[0]

    # ---- 章节检测 (from config) ----
    for page_num in range(len(doc)):
        try:
            page = doc[page_num]
            text = page.get_text()
            for line in text.split('\n'):
                line_stripped = line.strip()
                if not line_stripped or len(line_stripped) > 80:
                    continue
                for pat, label in section_pats:
                    if re.match(pat, line_stripped, re.I):
                        result["sections"].append({
                            "page": page_num + 1,
                            "heading": line_stripped,
                            "label": label
                        })
                        break
        except Exception:
            pass

    # ---- 图表检测 (version-compatible clustering) ----
    for page_num in range(len(doc)):
        try:
            page = doc[page_num]
            rects = cluster_drawings_compat(page)
            for rect in rects:
                if rect.width > 100 and rect.height > 80:
                    nearby_rect = fitz.Rect(
                        rect.x0 - 10, rect.y1,
                        rect.x1 + 10, min(rect.y1 + 120, page.rect.y1)
                    )
                    nearby_text = page.get_text(clip=nearby_rect)
                    caption = ""
                    if nearby_text:
                        for line in nearby_text.split('\n'):
                            m = re.match(r'(Fig|Figure|Table|Scheme)\s*[\.\s]', line, re.I)
                            if m:
                                caption = line.strip()[:150]
                                break

                    if caption:
                        if re.match(r'(Fig|Figure|Scheme)', caption, re.I):
                            result["figures_detected"][page_num + 1].append({
                                "rect": [rect.x0, rect.y0, rect.x1, rect.y1],
                                "caption": caption,
                                "size": f"{rect.width:.0f}x{rect.height:.0f}"
                            })
                        elif re.match(r'Table', caption, re.I):
                            result["tables_detected"][page_num + 1].append({
                                "rect": [rect.x0, rect.y0, rect.x1, rect.y1],
                                "caption": caption,
                                "size": f"{rect.width:.0f}x{rect.height:.0f}"
                            })
        except Exception:
            pass

    # ---- 论文类型判定 (加权检测) ----
    # 前1/3正文中的信号权重×3（参考文献区域通常在后半部）
    text_first_third = full_text[:len(full_text) // 3].lower()

    computational_score = 0
    for kw in comp_strong:
        if kw.lower() in full_text_lower:
            if kw.lower() in text_first_third:
                computational_score += 3
            else:
                computational_score += 1

    char_in_text = sum(1 for t in char_terms if t.lower() in full_text_lower)
    char_in_first_third = sum(1 for t in char_terms if t.lower() in text_first_third)

    has_strong_char = char_in_first_third >= 2
    has_strong_comp = computational_score >= 5

    if has_strong_comp and not has_strong_char:
        result["paper_type"] = "computational"
        result["paper_type_confidence"] = "high"
    elif has_strong_char and has_strong_comp:
        result["paper_type"] = "hybrid"
        result["paper_type_confidence"] = "medium"
    elif has_strong_comp and char_in_text >= 2:
        result["paper_type"] = "hybrid"
        result["paper_type_confidence"] = "low"
        errors.append("Computational signal strong but characterization terms found in text (may be from references). Classified as hybrid with low confidence.")
    elif has_strong_char:
        result["paper_type"] = "experimental"
        result["paper_type_confidence"] = "high"
    else:
        result["paper_type"] = "experimental"
        result["paper_type_confidence"] = "low"
        errors.append("Insufficient signals for confident paper type classification.")

    # ---- 化学子领域识别 ----
    for subfield, keywords in chem_kw.items():
        match_count = sum(1 for kw in keywords if kw.lower() in full_text_lower)
        if match_count >= 2:
            result["subfields"].append(subfield)

    # ---- 特征方法提取 ----
    for pattern, weight in method_pats:
        for m in re.finditer(pattern, full_text, re.I):
            method = m.group(0).strip()
            if method and method not in result["chemical_methods"]:
                result["chemical_methods"].append(method)

    # ---- 支持信息检测 ----
    if 'supporting information' in full_text_lower or 'supplementary' in full_text_lower:
        result["has_supporting_info"] = True

    doc.close()

    # ---- 输出 ----
    _unrecognized = "未识别" if lang == "zh" else "unrecognized"
    if verbose:
        _safe_print(f"PDF Analysis: {result['source']}")
        _safe_print(f"  Pages: {result['total_pages']}")
        _safe_print(f"  Paper Type: {result['paper_type']} (confidence: {result['paper_type_confidence']})")
        _safe_print(f"  Chemistry: {'yes' if result['is_chemistry'] else 'NO — see warnings'}")
        _safe_print(f"  Subfields: {', '.join(result['subfields']) or _unrecognized}")
        _safe_print(f"  Sections: {len(result['sections'])} detected")
        _safe_print(f"  Figures: {sum(len(v) for v in result['figures_detected'].values())} detected")
        _safe_print(f"  Methods: {', '.join(result['chemical_methods'][:8])}")
        if errors:
            _safe_print(f"  [!] {len(errors)} issue(s):")
            for e in errors:
                _safe_print(f"      - {e}")

    if output_json:
        # 将 defaultdict 转为普通 dict 以便 JSON 序列化
        result_out = result.copy()
        result_out["figures_detected"] = {
            k: v for k, v in result["figures_detected"].items()
        }
        result_out["tables_detected"] = {
            k: v for k, v in result["tables_detected"].items()
        }
        with open(output_json, 'w', encoding='utf-8') as f:  # encoding utf-8
            json.dump(result_out, f, indent=2, ensure_ascii=False)
        _safe_print(f"  JSON report: {output_json}")

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_paper.py <pdf_file> [--json output.json] [--lang zh|en]")
        print("Example: python analyze_paper.py paper.pdf --json report.json --lang en")
        return

    pdf_path = sys.argv[1]
    output_json = None
    lang = "zh"

    for i, arg in enumerate(sys.argv):
        if arg == "--json" and i + 1 < len(sys.argv):
            output_json = sys.argv[i + 1]
        if arg == "--lang" and i + 1 < len(sys.argv):
            lang = sys.argv[i + 1] if sys.argv[i + 1] in ("zh", "en") else "zh"

    analyze_pdf(pdf_path, verbose=True, output_json=output_json, lang=lang)


if __name__ == "__main__":
    main()
