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


def _safe_print(msg):
    """Windows-safe print that avoids GBK encoding crashes."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', errors='replace').decode('ascii'))


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


def _get_pymupdf_version():
    """获取 PyMuPDF 主版本号"""
    try:
        ver = fitz.version
        if isinstance(ver, tuple):
            return int(ver[0].split('.')[0]) if '.' in str(ver[0]) else int(ver[0])
        return 0
    except Exception:
        return 0


def _cluster_drawings_compat(page, x_tolerance=3, y_tolerance=3):
    """
    兼容不同 PyMuPDF 版本的图形聚类

    PyMuPDF >= 1.23: 使用 page.cluster_drawings()
    PyMuPDF < 1.23: 使用 page.get_drawings() + 手动聚类
    """
    # 尝试新版 API
    if hasattr(page, 'cluster_drawings'):
        try:
            return page.cluster_drawings(
                x_tolerance=x_tolerance, y_tolerance=y_tolerance)
        except Exception:
            pass

    # 回退：手动聚类 get_drawings() 的 rect
    try:
        drawings = page.get_drawings()
    except Exception:
        return []

    if not drawings:
        return []

    # 收集所有 drawing rect
    rects = []
    for d in drawings:
        r = d.get('rect')
        if r is None:
            continue
        w = r.x1 - r.x0
        h = r.y1 - r.y0
        if w < 0.5 or h < 0.5:  # 过滤极小的装饰线
            continue
        # 扩展 rect 以利于聚类
        rects.append(fitz.Rect(
            r.x0 - x_tolerance, r.y0 - y_tolerance,
            r.x1 + x_tolerance, r.y1 + y_tolerance
        ))

    if not rects:
        return []

    # 排序并迭代合并重叠的 rect
    rects.sort(key=lambda r: (r.y0, r.x0))
    clusters = [rects[0]]
    for r in rects[1:]:
        last = clusters[-1]
        if r.intersects(last):
            # 合并
            clusters[-1] = last | r
        else:
            # 也检查与其他已有 cluster 的重叠
            merged = False
            for i, c in enumerate(clusters):
                if r.intersects(c):
                    clusters[i] = c | r
                    merged = True
                    break
            if not merged:
                clusters.append(r)

    # 收缩回原始大小，去掉我们加的 tolerance padding
    result = []
    for c in clusters:
        result.append(fitz.Rect(
            c.x0 + x_tolerance, c.y0 + y_tolerance,
            c.x1 - x_tolerance, c.y1 - y_tolerance
        ) & page.rect)

    return result


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
            drawing_rects = _cluster_drawings_compat(
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
                rects = _cluster_drawings_compat(
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
# 智能提取 + 回退 / Smart Extract with Fallback
# ============================================================

def smart_extract_figures(pdf_path, output_dir, dpi=200, min_size=100,
                          fallback_pages=True, report_path=None):
    """
    智能提取论文中的所有图表，多策略回退

    策略顺序:
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

    # Strategy 1: Default vector extraction
    _safe_print("\n[1/4] Vector graphics (default tolerances)...")
    n_vec_default, vec_default = extract_vector_figures(
        pdf_path, output_dir, dpi, min_size, x_tolerance=3, y_tolerance=3)
    report["strategies"]["vector_default"] = {"count": n_vec_default, "items": vec_default}
    report["all_extracted"].extend(vec_default)

    # Strategy 2: Multi-tolerance if default found too few
    if n_vec_default < 3:
        _safe_print(f"\n[2/4] Only {n_vec_default} vector figures found. Trying relaxed tolerances...")
        n_vec_multi, vec_multi = extract_vector_multi_tolerance(
            pdf_path, output_dir, dpi, min_size)
        report["strategies"]["vector_multi_tol"] = {"count": n_vec_multi, "items": vec_multi}
        report["all_extracted"].extend(vec_multi)
    else:
        _safe_print("\n[2/4] Skipped (enough vector figures found)")
        report["strategies"]["vector_multi_tol"] = {"count": 0, "items": [], "skipped": True}

    # Strategy 3: Embedded images
    _safe_print("\n[3/4] Embedded images...")
    n_emb, emb_items = extract_embedded_images(pdf_path, output_dir, min_size)
    report["strategies"]["embedded"] = {"count": n_emb, "items": emb_items}
    report["all_extracted"].extend(emb_items)

    # Strategy 4: Page renders as fallback
    total_figures = len(report["all_extracted"])
    if total_figures < 3 and fallback_pages:
        _safe_print(f"\n[4/4] Only {total_figures} figures — rendering figure pages...")
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
            "or manually crop from these full-page renders."
        )
    elif total_figures < 3:
        _safe_print(f"\n[4/4] Only {total_figures} figures found!")
        report["warnings"].append(
            f"Only {total_figures} figures extracted. "
            "The PDF may use vector rendering that resists automatic extraction."
        )
        report["suggestions"].append(
            "Try: (1) increase --dpi to 400, (2) use pdf2image for page-level conversion, "
            "(3) manually crop figures from page renders."
        )
    else:
        _safe_print(f"\n[4/4] Skipped ({total_figures} figures extracted)")

    # Summary
    _safe_print("\n" + "-" * 50)
    _safe_print(f"Extraction complete!")
    _safe_print(f"  Total extracted: {total_figures}")
    _safe_print(f"  Output directory: {output_dir}")

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
