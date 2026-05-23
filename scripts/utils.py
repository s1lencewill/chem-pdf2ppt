# -*- coding: utf-8 -*-
"""
PDF2PPT shared utilities.

Provides:
- safe_print: Windows GBK-safe stdout
- cluster_drawings_compat: PyMuPDF cross-version figure clustering
- setup_utf8_stdout: reconfigure stdout for UTF-8
"""

import sys
import os


def setup_utf8_stdout():
    """Reconfigure stdout to use UTF-8, avoiding GBK crashes on Windows."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    elif hasattr(sys.stdout, "buffer"):
        sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", errors="replace", buffering=1)


def safe_print(msg):
    """Print to stdout, replacing unencodable characters on legacy terminals."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))


# ---------------------------------------------------------------------------
# PyMuPDF cross-version figure clustering
# ---------------------------------------------------------------------------

def cluster_drawings_compat(page, x_tolerance=3, y_tolerance=3):
    """Cluster PDF draw commands into figure bounding boxes.

    Uses page.cluster_drawings() on PyMuPDF >= 1.23, falls back to
    page.get_drawings() + manual clustering on older versions.

    Args:
        page: PyMuPDF Page object.
        x_tolerance, y_tolerance: merge distance for nearby drawings.
    Returns:
        list of fitz.Rect (empty list on failure).
    """
    import fitz

    # Try the 1.23+ API first
    if hasattr(page, "cluster_drawings"):
        try:
            return page.cluster_drawings(
                x_tolerance=x_tolerance, y_tolerance=y_tolerance
            )
        except Exception:
            pass

    # Fallback: manual clustering from get_drawings()
    try:
        drawings = page.get_drawings()
    except Exception:
        return []

    if not drawings:
        return []

    rects = []
    for d in drawings:
        r = d.get("rect")
        if r is None:
            continue
        w = r.x1 - r.x0
        h = r.y1 - r.y0
        if w < 0.5 or h < 0.5:
            continue
        rects.append(
            fitz.Rect(
                r.x0 - x_tolerance,
                r.y0 - y_tolerance,
                r.x1 + x_tolerance,
                r.y1 + y_tolerance,
            )
        )

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

    # Shrink back by tolerance padding
    result = []
    for c in clusters:
        shrunk = fitz.Rect(
            c.x0 + x_tolerance,
            c.y0 + y_tolerance,
            c.x1 - x_tolerance,
            c.y1 - y_tolerance,
        )
        result.append(shrunk & page.rect)
    return result
