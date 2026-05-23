# -*- coding: utf-8 -*-
"""
图表提取脚本 — 多策略提取 PDF 中的矢量图、嵌入式图片，含回退机制
Chart Extraction — multi-strategy: vector graphics, embedded images, page renders as fallback
"""
import fitz
import os
import sys
import json
import io
from PIL import Image

# Ensure scripts/ dir on path for direct invocation
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from utils import safe_print as _safe_print, cluster_drawings_compat


# ============================================================
# 核心提取函数 / Core Extraction Functions
# ============================================================

def extract_embedded_images(pdf_path, output_dir, min_size=100):
    """提取 PDF 中嵌入的位图 (PNG, JPEG)"""
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    count = 0
    extracted = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        images = page.get_images(full=True)

        for img_idx, img in enumerate(images):
            xref = img[0]
            base = doc.extract_image(xref)
            width = base["width"]
            height = base["height"]

            if width > min_size and height > min_size:
                ext = base["ext"]
                fname = f"p{page_num+1}_img{img_idx+1}.{ext}"
                output_path = os.path.join(output_dir, fname)
                with open(output_path, "wb") as f:
                    f.write(base["image"])
                count += 1
                extracted.append({
                    "page": page_num + 1,
                    "file": fname,
                    "size": f"{width}x{height}",
                    "method": "embedded"
                })
                _safe_print(f"  [embedded] {fname} ({width}x{height})")

    doc.close()
    return count, extracted


def extract_vector_figures(pdf_path, output_dir, dpi=200, min_size=100,
                           x_tolerance=3, y_tolerance=3):
    """提取矢量图形 — 兼容 PyMuPDF 1.19+ 和 1.23+"""
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    count = 0
    extracted = []

    for page_num in range(len(doc)):
        page = doc[page_num]

        try:
            drawing_rects = cluster_drawings_compat(
                page, x_tolerance=x_tolerance, y_tolerance=y_tolerance)
        except Exception as e:
            _safe_print(f"  [warn] Page {page_num+1}: drawing clustering failed: {e}")
            continue

        for idx, rect in enumerate(drawing_rects):
            if rect.width < min_size or rect.height < min_size:
                continue

            rect = rect + (-10, -10, 10, 10)
            rect = rect & page.rect

            zoom = dpi / 72
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, clip=rect)

            fname = f"p{page_num+1}_vec{idx+1}.png"
            output_path = os.path.join(output_dir, fname)
            pix.save(output_path)
            count += 1
            extracted.append({
                "page": page_num + 1,
                "file": fname,
                "size": f"{int(rect.width)}x{int(rect.height)}",
                "method": "vector"
            })
            _safe_print(f"  [vector] {fname} ({int(rect.width)}x{int(rect.height)})")

    doc.close()
    return count, extracted


def extract_vector_multi_tolerance(pdf_path, output_dir, dpi=200, min_size=100):
    """多容忍度尝试"""
    tolerances = [(3, 3), (6, 6), (10, 10), (15, 15), (20, 20)]
    all_extracted = []
    seen_hashes = set()

    for x_tol, y_tol in tolerances:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            try:
                rects = cluster_drawings_compat(
                    page, x_tolerance=x_tol, y_tolerance=y_tol)
            except Exception:
                continue

            for idx, rect in enumerate(rects):
                if rect.width < min_size or rect.height < min_size:
                    continue

                rect = (rect + (-10, -10, 10, 10)) & page.rect
                rect_hash = f"{page_num}_{int(rect.x0)}_{int(rect.y0)}_{int(rect.width)}_{int(rect.height)}"

                if rect_hash in seen_hashes:
                    continue
                seen_hashes.add(rect_hash)

                zoom = dpi / 72
                pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=rect)
                fname = f"p{page_num+1}_vec{len(all_extracted)+1}.png"
                output_path = os.path.join(output_dir, fname)
                pix.save(output_path)
                all_extracted.append({
                    "page": page_num + 1,
                    "file": fname,
                    "size": f"{int(rect.width)}x{int(rect.height)}",
                    "method": f"vector(tol={x_tol},{y_tol})"
                })
        doc.close()

    _safe_print(f"  [vector multi-tol] {len(all_extracted)} figures total")
    return len(all_extracted), all_extracted


def extract_page_renders(pdf_path, output_dir, pages=None, dpi=200):
    """页面渲染回退 — 将整页渲染为图片（当矢量提取失败时使用）"""
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    count = 0
    extracted = []

    if pages is None:
        pages = list(range(len(doc)))

    for page_num in pages:
        page = doc[page_num]
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        fname = f"page_{page_num+1}_render.png"
        output_path = os.path.join(output_dir, fname)
        pix.save(output_path)
        count += 1
        extracted.append({
            "page": page_num + 1,
            "file": fname,
            "size": f"{pix.width}x{pix.height}",
            "method": "page_render"
        })
    doc.close()
    return count, extracted


def detect_figure_pages(pdf_path):
    """检测包含图表的页码 — 通过搜索文本中的 Figure/Fig/图 引用"""
    doc = fitz.open(pdf_path)
    figure_pages = {}

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        # 搜索 Figure 编号
        import re
        fig_refs = re.findall(r'(?:Figure|Fig\.?)\s*(\d+)', text, re.I)
        for fig_num in fig_refs:
            if fig_num not in figure_pages:
                figure_pages[fig_num] = page_num + 1

    doc.close()
    return figure_pages


# ============================================================
# Caption-guided figure extraction / Caption 引导的图表定位
# ============================================================

def extract_figures_by_caption(pdf_path, output_dir, dpi=300, min_size=80):
    """Locate figures by finding their captions, then crop the region above.

    Academic papers place figure captions below (or sometimes beside) the figure.
    This strategy searches for "Figure X" / "Fig. X" / "图 X" text, then renders
    the content area above the caption. Because it targets known figure locations,
    confidence is high and noise is low.

    Returns:
        (count, list_of_items)
    """
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    count = 0
    extracted = []

    # Patterns for figure captions — English + Chinese
    caption_pat = re.compile(
        r'(?:^|\n)\s*(?:Fig(?:ure)?\.?\s*(\d+[a-z]?)|图\s*(\d+[a-z]?))[\s\.\:,]',
        re.IGNORECASE
    )

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        page_height = page.rect.y1
        page_width = page.rect.x1

        for m in caption_pat.finditer(text):
            fig_id = m.group(1) or m.group(2)
            # Find caption position on page
            caption_start = m.start()
            # Get text blocks with positions
            blocks = page.get_text("blocks")
            caption_bbox = None
            for b in blocks:
                if len(b) >= 5 and b[4].strip() and m.group(0).strip()[:30] in b[4]:
                    caption_bbox = fitz.Rect(b[0], b[1], b[2], b[3])
                    break

            if caption_bbox is None:
                continue

            # Figure region: above the caption, extending up to page top or
            # previous text block. Typical: figure occupies area from caption top
            # upward for 30-70% of page height.
            fig_top = max(0, caption_bbox.y0 - page_height * 0.65)
            fig_bottom = caption_bbox.y0 - 5  # small gap above caption

            # Try to find the actual figure content within this region
            fig_rect = fitz.Rect(30, fig_top, page_width - 30, fig_bottom)

            # Look for drawing clusters within the figure region
            try:
                clusters = cluster_drawings_compat(page, x_tolerance=5, y_tolerance=5)
            except Exception:
                clusters = []

            # Find clusters that overlap the figure region
            fig_clusters = [c for c in clusters
                          if c.intersects(fig_rect)
                          and c.width > min_size and c.height > min_size]

            if fig_clusters:
                # Use the union of all clusters in the figure region
                union_rect = fig_clusters[0]
                for c in fig_clusters[1:]:
                    union_rect = union_rect | c
                crop_rect = (union_rect + (-10, -10, 10, 10)) & page.rect
                confidence = "high"
            else:
                # No clusters found — use the full region above caption
                crop_rect = fig_rect & page.rect
                confidence = "medium"

            # Render
            zoom = dpi / 72
            mat = fitz.Matrix(zoom, zoom)
            try:
                pix = page.get_pixmap(matrix=mat, clip=crop_rect)
            except Exception:
                continue

            fname = f"fig{fig_id}_p{page_num+1}.png"
            output_path = os.path.join(output_dir, fname)
            pix.save(output_path)
            count += 1
            extracted.append({
                "page": page_num + 1,
                "figure_id": f"Figure {fig_id}",
                "file": fname,
                "size": f"{int(crop_rect.width)}x{int(crop_rect.height)}",
                "method": "caption_guided",
                "confidence": confidence,
            })
            _safe_print(f"  [caption] {fname} → Figure {fig_id} (confidence: {confidence}, {int(crop_rect.width)}x{int(crop_rect.height)})")

    doc.close()
    return count, extracted


# ============================================================
# 智能提取 + 回退 / Smart Extract with Fallback
# ============================================================

def smart_extract_figures(pdf_path, output_dir, dpi=200, min_size=100,
                          fallback_pages=True, report_path=None):
    """
    智能提取论文中的所有图表，多策略回退

    策略顺序:
    0. Caption-guided: 定位 "Figure X" 标题，裁剪上方图表区域（最可靠）
    1. cluster_drawings() 默认容忍度 (3,3)
    2. 如果结果 < 3，尝试更宽松容忍度 (6,6) → (10,10) → (15,15) → (20,20)
    3. 提取嵌入式位图
    4. 回退：将包含图表的页面整页渲染（可选）

    Returns:
        dict: 包含提取统计和详细报告
    """
    os.makedirs(output_dir, exist_ok=True)

    report = {
        "source": os.path.basename(pdf_path),
        "dpi": dpi,
        "min_size": min_size,
        "strategies": {},
        "all_extracted": [],
        "warnings": [],
        "suggestions": [],
    }

    _safe_print(f"Processing: {os.path.basename(pdf_path)}")
    _safe_print("-" * 50)

    # Strategy 0: Caption-guided (NEW — most reliable, tried first)
    _safe_print("\n[0/5] Caption-guided extraction...")
    n_caption, caption_items = extract_figures_by_caption(
        pdf_path, output_dir, dpi=dpi * 2, min_size=min_size // 2)
    report["strategies"]["caption_guided"] = {"count": n_caption, "items": caption_items}
    report["all_extracted"].extend(caption_items)
    if n_caption > 0:
        _safe_print(f"  Caption-guided found {n_caption} figures (high confidence)")

    # Strategy 1: Vector extraction (complementary — catches uncaptioned figures)
    _safe_print("\n[1/5] Vector graphics (default tolerances)...")
    n_vec_default, vec_default = extract_vector_figures(
        pdf_path, output_dir, dpi, min_size, x_tolerance=3, y_tolerance=3)
    # Deduplicate: skip items whose rect overlaps an existing caption-guided item
    caption_rects = set()
    for item in caption_items:
        caption_rects.add((item["page"], item.get("rect_hash", "")))
    new_vec = [v for v in vec_default
               if not any(v["page"] == c["page"] for c in caption_items)]
    report["strategies"]["vector_default"] = {"count": len(new_vec), "items": new_vec}
    report["all_extracted"].extend(new_vec)

    # Strategy 2: Multi-tolerance if default found too few
    if n_caption + len(new_vec) < 3:
        _safe_print(f"\n[2/5] Only {n_caption + len(new_vec)} figures so far. Trying relaxed tolerances...")
        n_vec_multi, vec_multi = extract_vector_multi_tolerance(
            pdf_path, output_dir, dpi, min_size)
        report["strategies"]["vector_multi_tol"] = {"count": n_vec_multi, "items": vec_multi}
        report["all_extracted"].extend(vec_multi)
    else:
        _safe_print("\n[2/5] Skipped (enough figures already)")
        report["strategies"]["vector_multi_tol"] = {"count": 0, "items": [], "skipped": True}

    # Strategy 3: Embedded images
    _safe_print("\n[3/5] Embedded bitmap images...")
    n_emb, emb_items = extract_embedded_images(pdf_path, output_dir, min_size)
    report["strategies"]["embedded"] = {"count": n_emb, "items": emb_items}
    report["all_extracted"].extend(emb_items)

    # Strategy 4: Page renders as fallback
    total_figures = len(report["all_extracted"])
    if total_figures < 3 and fallback_pages:
        _safe_print(f"\n[4/5] Only {total_figures} figures — rendering figure pages...")
        fig_pages = detect_figure_pages(pdf_path)
        pages_to_render = sorted(set(fig_pages.values()))
        n_pages, page_items = extract_page_renders(
            pdf_path, output_dir, pages=pages_to_render, dpi=dpi)
        report["strategies"]["page_render_fallback"] = {
            "count": n_pages,
            "pages": pages_to_render,
            "figure_page_map": fig_pages,
            "items": page_items
        }
        report["all_extracted"].extend(page_items)
        report["warnings"].append(
            f"Vector extraction found few figures. Rendered {n_pages} pages as images. "
            f"Figures detected on pages: {pages_to_render}"
        )
        report["suggestions"].append(
            "Consider using page_*_render.png as figure placeholders, "
            "or try DOI-based figure download as alternative source."
        )
    elif total_figures < 3:
        _safe_print(f"\n[4/5] Only {total_figures} figures found!")
        report["warnings"].append(
            f"Only {total_figures} figures extracted. "
            "The PDF may use vector rendering that resists automatic extraction."
        )
        report["suggestions"].append(
            "Try: (1) DOI-based figure download via Semantic Scholar / arXiv, "
            "(2) increase --dpi to 400, (3) manually crop from page renders."
        )
    else:
        _safe_print(f"\n[4/5] Skipped ({total_figures} figures extracted)")

    # Summary
    _safe_print("\n" + "-" * 50)
    _safe_print(f"Extraction complete!")
    _safe_print(f"  Total extracted: {total_figures}")
    _safe_print(f"  Output directory: {output_dir}")
    # Show confidence breakdown
    high_conf = sum(1 for item in report["all_extracted"] if item.get("confidence") == "high")
    if high_conf > 0:
        _safe_print(f"  High confidence: {high_conf} (caption-guided)")

    if report["warnings"]:
        _safe_print(f"\n  Warnings:")
        for w in report["warnings"]:
            _safe_print(f"  - {w}")
    if report["suggestions"]:
        _safe_print(f"\n  Suggestions:")
        for s in report["suggestions"]:
            _safe_print(f"  - {s}")

    # Save report
    if report_path:
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        _safe_print(f"\nReport saved: {report_path}")

    return report


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_charts.py <pdf_file> [output_dir] [dpi] [--report]")
        print()
        print("Examples:")
        print("  python extract_charts.py paper.pdf")
        print("  python extract_charts.py paper.pdf charts 300")
        print("  python extract_charts.py paper.pdf figures 400 --report")
        return

    pdf_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "extracted_charts"
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 200
    do_report = "--report" in sys.argv

    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        return

    report_path = os.path.join(output_dir, "extraction_report.json") if do_report else None
    smart_extract_figures(pdf_path, output_dir, dpi=dpi, report_path=report_path)


if __name__ == "__main__":
    main()
