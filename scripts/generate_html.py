# -*- coding: utf-8 -*-
"""
HTML 学术 PPT 生成器 — 生成单文件、横向翻页的化学学术 HTML 演示文稿
Academic HTML Presentation Generator — Single-file horizontal-slide deck with figures
"""
import sys
import os
import json
import re
import base64


def _safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', errors='replace').decode('ascii'))


# ============================================================
# 配色主题 (与 create_ppt.py 一致)
# ============================================================
THEMES = {
    "academic": {
        "name": "学术经典",
        "primary": "#003366", "primary_rgb": "0,51,102",
        "accent": "#B41E1E", "bg": "#FFFFFF",
        "bg_light": "#F0F4F8", "text": "#333333",
        "muted": "#8C8C8C", "section_bg": "#003366",
        "section_text": "#FFFFFF", "table_stripe": "#F0F4F8",
    },
    "molecular": {
        "name": "分子科技",
        "primary": "#1A5276", "primary_rgb": "26,82,118",
        "accent": "#E74C3C", "bg": "#F8F9FA",
        "bg_light": "#EBF0F5", "text": "#2C3E50",
        "muted": "#95A5A6", "section_bg": "#1A5276",
        "section_text": "#FFFFFF", "table_stripe": "#EBF0F5",
    },
    "green": {
        "name": "绿色化学",
        "primary": "#1E5631", "primary_rgb": "30,86,49",
        "accent": "#D4A017", "bg": "#F7F9F4",
        "bg_light": "#EEF3E9", "text": "#333333",
        "muted": "#96A590", "section_bg": "#1E5631",
        "section_text": "#FFFFFF", "table_stripe": "#EEF3E9",
    },
    "nature": {
        "name": "Nature 风格",
        "primary": "#222222", "primary_rgb": "34,34,34",
        "accent": "#0066CC", "bg": "#FFFFFF",
        "bg_light": "#F8F8F8", "text": "#444444",
        "muted": "#A0A0A0", "section_bg": "#222222",
        "section_text": "#FFFFFF", "table_stripe": "#F5F5F5",
    },
}


def _img_to_data_uri(img_path):
    """将图片转为 base64 data URI，嵌入 HTML"""
    if not img_path or not os.path.exists(img_path):
        return None
    try:
        ext = os.path.splitext(img_path)[1].lower()
        mime_map = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                     '.gif': 'image/gif', '.webp': 'image/webp', '.svg': 'image/svg+xml'}
        mime = mime_map.get(ext, 'image/png')
        with open(img_path, 'rb') as f:
            data = base64.b64encode(f.read()).decode('ascii')
        return f"data:{mime};base64,{data}"
    except Exception:
        return None


def _escape_html(text):
    """转义 HTML 特殊字符"""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


class HtmlPPT:
    """化学学术 HTML PPT 构建器"""

    def __init__(self, title="学术报告", theme="academic"):
        if theme not in THEMES:
            raise ValueError(f"Unknown theme: {theme}")
        self.title = title
        self.theme = theme
        self.t = THEMES[theme]
        self.slides = []
        self._warnings = []
        self._missing_images = []

    def add_title_slide(self, title_cn, title_en="", authors="", journal="", doi=""):
        meta_parts = []
        if authors:
            meta_parts.append(f'<span>{_escape_html(authors)}</span>')
        if journal:
            meta_parts.append(f'<span>{_escape_html(journal)}</span>')
        if doi:
            meta_parts.append(f'<span style="font-size:11px">DOI: {_escape_html(doi)}</span>')

        html = f'''<section class="slide light slide-title">
          <div class="accent-line"></div>
          <h1>{_escape_html(title_cn)}</h1>
          {f'<div class="en-title">{_escape_html(title_en)}</div>' if title_en else ''}
          <div class="meta">{''.join(meta_parts)}</div>
          <div class="page-num">1</div>
        </section>'''
        self.slides.append(html)

    def add_section_slide(self, title, subtitle=""):
        html = f'''<section class="slide dark slide-section">
          <div class="accent-bar"></div>
          <h2>{_escape_html(title)}</h2>
          {f'<div class="sub">{_escape_html(subtitle)}</div>' if subtitle else ''}
        </section>'''
        self.slides.append(html)

    def add_content_slide(self, title, bullets, subtitle="", notes=""):
        li_items = '\n'.join(f'<li>{_escape_html(b)}</li>' for b in bullets)
        html = f'''<section class="slide light slide-content">
          <h3>{_escape_html(title)}</h3>
          <div class="title-line"></div>
          {f'<div class="subtitle">{_escape_html(subtitle)}</div>' if subtitle else ''}
          <ul class="bullets">{li_items}</ul>
          {f'<div class="notes">📝 {_escape_html(notes)}</div>' if notes else ''}
        </section>'''
        self.slides.append(html)

    def add_figure_slide(self, title, figure_path, bullets=None,
                          figure_label="", caption="", layout="figure_right"):
        bullets = bullets or []
        fig_html = ""

        if figure_path and os.path.exists(figure_path):
            data_uri = _img_to_data_uri(figure_path)
            if data_uri:
                fig_html = f'<img src="{data_uri}" alt="{_escape_html(figure_label or title)}">'
            else:
                self._warnings.append(f"Failed to encode image: {figure_path}")
                fig_html = f'<div style="padding:2vh;color:var(--muted);border:1px dashed var(--muted)">[Image: {_escape_html(os.path.basename(figure_path))}]</div>'
        elif figure_path:
            self._missing_images.append(figure_path)
            fig_html = f'<div style="padding:2vh;color:var(--muted);border:1px dashed var(--muted)">[Figure: {_escape_html(os.path.basename(figure_path))}]</div>'

        li_items = '\n'.join(f'<li>{_escape_html(b)}</li>' for b in bullets)

        if layout == "figure_top":
            area_html = f'''<div class="fig-area top">
            {fig_html}
            <ul class="fig-text">{li_items}</ul>
          </div>'''
        elif layout == "figure_full":
            area_html = f'''<div class="fig-area top">
            {fig_html}
            {f'<ul class="fig-text" style="font-size:12px">{li_items}</ul>' if bullets else ''}
          </div>'''
        else:
            # figure_right (default)
            area_html = f'''<div class="fig-area">
            <ul class="fig-text">{li_items}</ul>
            {fig_html}
          </div>'''

        caption_line = ""
        if figure_label or caption:
            parts = []
            if figure_label:
                parts.append(figure_label)
            if caption:
                parts.append(caption)
            caption_line = f'<div class="fig-caption">{" | ".join(parts)}</div>'

        html = f'''<section class="slide light slide-figure">
          <h3>{_escape_html(title)}</h3>
          <div class="title-line"></div>
          {area_html}
          {caption_line}
        </section>'''
        self.slides.append(html)

    def add_table_slide(self, title, headers, rows, notes=""):
        th_html = '\n'.join(f'<th>{_escape_html(h)}</th>' for h in headers)
        tr_html = '\n'.join(
            '<tr>' + ''.join(f'<td>{_escape_html(str(c))}</td>' for c in row) + '</tr>'
            for row in rows
        )

        html = f'''<section class="slide light slide-table">
          <h3>{_escape_html(title)}</h3>
          <div class="title-line"></div>
          <table><thead><tr>{th_html}</tr></thead><tbody>{tr_html}</tbody></table>
          {f'<div class="notes">{_escape_html(notes)}</div>' if notes else ''}
        </section>'''
        self.slides.append(html)

    def add_summary_slide(self, title, bullets):
        li_items = '\n'.join(f'<li>{_escape_html(b)}</li>' for b in bullets)
        html = f'''<section class="slide light slide-summary">
          <div class="top-bar"></div>
          <h3>{_escape_html(title)}</h3>
          <ul class="bullets">{li_items}</ul>
        </section>'''
        self.slides.append(html)

    def add_thankyou_slide(self, title="谢谢！欢迎提问", subtitle="Thank you & Questions"):
        html = f'''<section class="slide dark slide-thanks">
          <div>
            <h2>{_escape_html(title)}</h2>
            {f'<div class="sub">{_escape_html(subtitle)}</div>' if subtitle else ''}
          </div>
        </section>'''
        self.slides.append(html)

    def _render(self):
        """渲染完整 HTML"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'academic_template.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            template = template_raw = f.read()

        theme = self.t
        replacements = {
            '__TITLE__': self.title,
            '__PRIMARY__': theme['primary'],
            '__PRIMARY_RGB__': theme['primary_rgb'],
            '__ACCENT__': theme['accent'],
            '__BG__': theme['bg'],
            '__BG_LIGHT__': theme['bg_light'],
            '__TEXT__': theme['text'],
            '__MUTED__': theme['muted'],
            '__SECTION_BG__': theme['section_bg'],
            '__SECTION_TEXT__': theme['section_text'],
            '__TABLE_STRIPE__': theme['table_stripe'],
            '__NSLIDES__': str(len(self.slides)),
            '__TOTAL__': str(len(self.slides)),
        }

        for key, val in replacements.items():
            template = template.replace(key, val)

        # Navigation dots
        dots_html = '\n'.join(
            f'<div class="dot{" active" if i == 0 else ""}" data-idx="{i}"></div>'
            for i in range(len(self.slides))
        )
        template = template.replace('__NAV_DOTS__', dots_html)

        # Slides with page numbers
        slides_html = []
        for i, s in enumerate(self.slides):
            modified = re.sub(
                r'<div class="page-num">(\d+)</div>',
                f'<div class="page-num">{i+1}</div>', s)
            if '<div class="page-num">' not in s and 'slide-content' in s:
                modified += f'\n  <div class="page-num">{i+1}</div>'
            if '<div class="page-num">' not in s and 'slide-figure' in s:
                modified += f'\n  <div class="page-num">{i+1}</div>'
            if '<div class="page-num">' not in s and 'slide-table' in s:
                modified += f'\n  <div class="page-num">{i+1}</div>'
            if '<div class="page-num">' not in s and 'slide-summary' in s:
                modified += f'\n  <div class="page-num">{i+1}</div>'
            slides_html.append(modified)

        template = template.replace('__SLIDES__', '\n'.join(slides_html))

        return template

    def save(self, output_path):
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        html = self._render()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        size_kb = len(html) / 1024
        _safe_print(f"[HtmlPPT] Saved: {output_path} ({size_kb:.0f} KB)")
        _safe_print(f"[HtmlPPT] Slides: {len(self.slides)}  |  Theme: {self.t['name']}")
        if self._missing_images:
            _safe_print(f"[HtmlPPT] Missing images: {len(self._missing_images)}")
        if self._warnings:
            _safe_print(f"[HtmlPPT] Warnings: {len(self._warnings)}")
        return output_path

    def get_report(self):
        return {
            "theme": self.theme,
            "total_slides": len(self.slides),
            "missing_images": self._missing_images,
            "warnings": self._warnings,
        }
