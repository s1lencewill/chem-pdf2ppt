# -*- coding: utf-8 -*-
"""
PDF 论文分析脚本 — 化学论文类型识别、章节结构、图表位置、关键信息提取
Chemistry Paper Analyzer with JSON output and robust encoding handling
"""
import fitz
import sys
import os
import re
import json
from collections import defaultdict


def _safe_print(msg):
    """Windows-safe print."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', errors='replace').decode('ascii'))


# ============================================================
# 化学关键词库 / Chemistry Keyword Database
# ============================================================

CHEM_KEYWORDS = {
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
        "reorganization energy", "Marcus theory"
    ],
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

# 表征关键词（仅在方法/实验段落出现时才算实验信号）
CHARACTERIZATION_TERMS = [
    "XRD", "XPS", "TEM", "SEM", "STEM", "HAADF", "NMR", "IR",
    "Raman", "EXAFS", "XANES", "BET", "EPR", "UV-vis", "AFM", "FTIR"
]

# 计算关键词（强信号）
COMPUTATIONAL_STRONG = [
    "DFT", "density functional theory", "VASP", "Gaussian", "CP2K",
    "Quantum ESPRESSO", "ab initio molecular dynamics", "AIMD",
    "PBE0", "B3LYP", "PBE", "Hartree-Fock", "CCSD", "MP2",
    "transition state", "reaction coordinate", "diabatic",
    "pseudopotential", "basis set", "k-point", "cutoff",
    "molecular dynamics simulation", "trajector"
]


def analyze_pdf(pdf_path, verbose=True, output_json=None):
    """分析 PDF 论文的完整结构和内容

    Returns:
        dict: 论文全部分析结果
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

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

    # ---- 标题提取 ----
    lines = [l.strip() for l in first_page_text.split('\n') if l.strip()]
    if lines:
        result["title"] = lines[0]

    # ---- 章节检测 ----
    section_patterns = [
        (r'^\s*(?:Abstract|摘要)\s*$', "Abstract"),
        (r'^\s*(?:Introduction|引言|绪论)\s*$', "Introduction"),
        (r'^\s*(?:Method|Experimental|Computational|计算方法?|实验方法?|Theory)\s*', "Methods"),
        (r'^\s*(?:Result|Discussion|结果|讨论)\s*', "Results"),
        (r'^\s*(?:Conclusion|结论|Summary|总结)\s*$', "Conclusions"),
        (r'^\s*(?:Supporting Information|SI|附录|补充|References?)\s*', "SI/References"),
    ]

    for page_num in range(len(doc)):
        try:
            page = doc[page_num]
            text = page.get_text()
            for line in text.split('\n'):
                line_stripped = line.strip()
                if not line_stripped or len(line_stripped) > 80:
                    continue
                for pat, label in section_patterns:
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
    def _cluster_compat(page, x_tol=3, y_tol=3):
        """兼容 PyMuPDF 新旧版本的图形聚类"""
        if hasattr(page, 'cluster_drawings'):
            try:
                return page.cluster_drawings(x_tolerance=x_tol, y_tolerance=y_tol)
            except Exception:
                pass
        try:
            drawings = page.get_drawings()
        except Exception:
            return []
        if not drawings:
            return []
        rects = []
        for d in drawings:
            r = d.get('rect')
            if r and r.x1 - r.x0 > 0.5 and r.y1 - r.y0 > 0.5:
                rects.append(fitz.Rect(r.x0 - x_tol, r.y0 - y_tol, r.x1 + x_tol, r.y1 + y_tol))
        if not rects:
            return []
        rects.sort(key=lambda r: (r.y0, r.x0))
        clusters = [rects[0]]
        for r in rects[1:]:
            merged = False
            for i, c in enumerate(clusters):
                if r.intersects(c):
                    clusters[i] = c | r
                    merged = True
                    break
            if not merged:
                clusters.append(r)
        return [fitz.Rect(c.x0 + x_tol, c.y0 + y_tol, c.x1 - x_tol, c.y1 - y_tol) & page.rect for c in clusters]

    for page_num in range(len(doc)):
        try:
            page = doc[page_num]
            rects = _cluster_compat(page)
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

    # ---- 论文类型判定 (改进逻辑) ----
    # 在正文前1/3部分（通常不含大量参考文献）检测信号
    text_first_third = full_text[:len(full_text) // 3].lower()

    computational_score = 0
    for kw in COMPUTATIONAL_STRONG:
        if kw.lower() in full_text_lower:
            # 强信号在方法部分（前1/3）权重更高
            if kw.lower() in text_first_third:
                computational_score += 3
            else:
                computational_score += 1

    # 表征关键词检测 — 只在 methods/results 区域有意义
    char_in_text = sum(1 for t in CHARACTERIZATION_TERMS if t.lower() in full_text_lower)
    char_in_first_third = sum(1 for t in CHARACTERIZATION_TERMS if t.lower() in text_first_third)

    # 判定逻辑
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
    for subfield, keywords in CHEM_KEYWORDS.items():
        match_count = sum(1 for kw in keywords if kw.lower() in full_text_lower)
        if match_count >= 2:
            result["subfields"].append(subfield)

    # ---- 特征方法提取 ----
    method_patterns = [
        (r'(CP2K|VASP|Gaussian\s*\d+|Q-Chem\s*\d+|GROMACS|LAMMPS|Quantum\s+ESPRESSO)', 2),
        (r'(PBE0|B3LYP|PBE|RPBE|SCAN|HSE06|GGA|LDA|meta-GGA)', 1),
        (r'(impregnation|sol-gel|hydrothermal|solvothermal|co-precipitation|calcination|pyrolysis)', 1),
        (r'(XRD|XPS|TEM|SEM|STEM|HAADF-STEM|NMR|IR|Raman|EXAFS|XANES|BET|EPR)', 1),
    ]
    for pattern, weight in method_patterns:
        for m in re.finditer(pattern, full_text, re.I):
            method = m.group(0).strip()
            if method and method not in result["chemical_methods"]:
                result["chemical_methods"].append(method)

    # ---- 支持信息检测 ----
    if 'supporting information' in full_text_lower or 'supplementary' in full_text_lower:
        result["has_supporting_info"] = True

    doc.close()

    # ---- 输出 ----
    if verbose:
        _safe_print(f"PDF Analysis: {result['source']}")
        _safe_print(f"  Pages: {result['total_pages']}")
        _safe_print(f"  Paper Type: {result['paper_type']} (confidence: {result['paper_type_confidence']})")
        _safe_print(f"  Subfields: {', '.join(result['subfields']) or '未识别'}")
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
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(result_out, f, indent=2, ensure_ascii=False)
        _safe_print(f"  JSON report: {output_json}")

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_paper.py <pdf_file> [--json output.json]")
        print("Example: python analyze_paper.py paper.pdf --json report.json")
        return

    pdf_path = sys.argv[1]
    output_json = None

    for i, arg in enumerate(sys.argv):
        if arg == "--json" and i + 1 < len(sys.argv):
            output_json = sys.argv[i + 1]

    analyze_pdf(pdf_path, verbose=True, output_json=output_json)


if __name__ == "__main__":
    main()
