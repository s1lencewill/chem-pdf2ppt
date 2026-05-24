# 图表提取工具说明

## 优先方案：MinerU MCP

检索是否有 MinerU MCP 工具可用，优先使用。

## 备用方案：PyMuPDF

### 安装

```bash
pip install pymupdf
```

### 两种提取方式

| 类型 | 特点 | 提取方法 |
|------|------|---------|
| **嵌入式图片** | 作者插入的 PNG/JPEG | `page.get_images()` |
| **矢量图形** | 架构图、流程图等绘制的图形 | `page.cluster_drawings()` |

### 矢量图形提取（推荐用于方法流程图）

```python
import fitz

doc = fitz.open("paper.pdf")
for page_num in range(len(doc)):
    page = doc[page_num]
    rects = page.cluster_drawings(x_tolerance=3, y_tolerance=3)
    for idx, rect in enumerate(rects):
        if rect.width > 100 and rect.height > 100:
            rect = (rect + (-10, -10, 10, 10)) & page.rect
            zoom = 200 / 72  # 200 DPI
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=rect)
            pix.save(f"images/p{page_num+1}_fig{idx+1}.png")
doc.close()
```

### 参数调整

| 问题 | 解决方案 |
|------|---------|
| 多图合在一起 | 减小 `x_tolerance`/`y_tolerance`（如 1-2）|
| 单图被切块 | 增大容差（如 10-20）|
| 图形未被识别 | 可能是嵌入式图片，尝试 `get_images()` |
| 图片模糊 | 提高 DPI 到 300 |
| 缺矢量图形 | 使用手动区域截取：`page.get_pixmap(clip=fitz.Rect(x0,y0,x1,y1))` |

### 嵌入式图片提取

```python
import fitz

doc = fitz.open("paper.pdf")
for page_num in range(len(doc)):
    page = doc[page_num]
    for img_idx, img in enumerate(page.get_images(full=True)):
        xref = img[0]
        base = doc.extract_image(xref)
        if base["width"] > 100 and base["height"] > 100:
            with open(f"images/p{page_num+1}_img{img_idx+1}.{base['ext']}", "wb") as f:
                f.write(base["image"])
doc.close()
```

> 注：完整综合提取脚本（含自动去重和过滤）参见 `readpaper.md` 原文。
