# -*- coding: utf-8 -*-
"""
化学学术论文 Markdown 报告生成器
Chemistry Academic Paper Report Generator — produces publication-ready reading notes
输出格式: Markdown (.md), HTML (.html, 可在浏览器中打印为 PDF)
"""
import os
import sys

# Ensure scripts/ dir on path for direct invocation
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from utils import safe_print as _safe_print


# ============================================================
# Report Builder
# ============================================================

class ReportBuilder:
    """化学学术论文 Markdown 报告构建器"""

    def __init__(self, paper_info=None):
        self.paper = paper_info or {}
        self.sections = []
        self.figures = []
        self.qa_items = []

    def set_meta(self, title, authors, journal, doi="", paper_type="computational",
                 difficulty=3, prerequisites=None, peer_review_status="Journal Article"):
        self.paper = {
            "title": title, "authors": authors, "journal": journal,
            "doi": doi, "paper_type": paper_type, "difficulty": difficulty,
            "prerequisites": prerequisites or [],
            "peer_review_status": peer_review_status,
        }

    def add_section(self, heading_level, title, content):
        self.sections.append({"level": heading_level, "title": title, "content": content})

    def add_figure(self, fig_id, path, description, key_points, section_ref=""):
        self.figures.append({
            "id": fig_id, "path": path, "description": description,
            "key_points": key_points, "section_ref": section_ref,
        })

    def add_qa(self, question, answer, category="principle"):
        self.qa_items.append({"question": question, "answer": answer, "category": category})

    @staticmethod
    def _stars(n):
        return "⭐" * n

    # ---- Build ----

    def build(self):
        p = self.paper
        b = []

        # 0. Meta
        b.append(f"# {p.get('title', 'Untitled')}\n")
        b.append(f"> **Authors**: {p.get('authors', 'N/A')}")
        b.append(f"> **Published**: {p.get('journal', 'N/A')}")
        if p.get('doi'):
            b.append(f"> **DOI**: [{p['doi']}](https://doi.org/{p['doi']})")
        b.append(f"> **Peer Review**: {p.get('peer_review_status', 'Journal Article')}")
        b.append(f"> **Difficulty**: {self._stars(p.get('difficulty', 3))}")
        prereqs = p.get('prerequisites', [])
        if prereqs:
            b.append(f"> **Prerequisites**: {' · '.join(prereqs)}")
        b.append("")

        # 1. Overview
        b.append("## 一、总览\n")
        b.append("### 核心创新点")
        b.append(p.get('innovation', '*(from paper)*'))
        b.append("\n### 摘要")
        b.append(p.get('abstract', '*(from paper)*'))
        b.append("")

        # 2. Summary
        b.append("## 二、论文概述\n")
        b.append(f"- **解决的问题**: {p.get('problem', '')}")
        b.append(f"- **核心方案**: {p.get('approach', '')}")
        for c in p.get('contributions', []):
            b.append(f"  - {c}")
        b.append("")

        # 3. Background
        b.append("## 三、背景与动机\n")
        b.append(p.get('background', ''))
        b.append("")

        # 4. Methods
        b.append("## 四、核心方法\n")
        for s in self.sections:
            b.append(f"{'#' * s['level']} {s['title']}\n")
            b.append(s["content"])
            b.append("")

        # 5. Results
        b.append("## 五、结果与讨论\n")
        b.append("### 结果逻辑链")
        b.append(p.get('result_chain', ''))
        b.append("\n### 关键结果详情\n")
        for r in p.get('key_results', []):
            b.append(f"**{r.get('title', '')}**")
            for pt in r.get('points', []):
                b.append(f"- {pt}")
            if r.get('figure'):
                b.append(f"  *参见 Figure {r['figure']}*")
            b.append("")

        # Figures
        for fig in self.figures:
            b.append(f"![{fig['description']}]({fig['path']})")
            b.append(f"**{fig['id']}**: {fig['description']}")
            for kp in fig['key_points']:
                b.append(f"- {kp}")
            if fig.get('section_ref'):
                b.append(f"*{fig['section_ref']}*")
            b.append("")

        # 6. Summary
        b.append("## 六、总结与思考\n")
        b.append("### 核心贡献")
        for c in p.get('contributions', []):
            b.append(f"- {c}")
        b.append("\n### 局限性")
        for l in p.get('limitations', ['*(from paper)*']):
            b.append(f"- {l}")
        b.append("\n### 适用场景")
        for s in p.get('applicable_scenarios', ['*(分析适用/不适用情况)*']):
            b.append(f"- {s}")
        b.append("")

        # 7. Q&A
        b.append("## Q&A 深度思考\n")
        qa_cats = {"principle": "原理理解", "detail": "细节辨析",
                    "boundary": "边界条件", "extension": "延伸思考"}
        for i, qa in enumerate(self.qa_items, 1):
            cat = qa_cats.get(qa['category'], '')
            b.append(f"**Q{i}** [{cat}] {qa['question']}")
            b.append(f"**A{i}** {qa['answer']}")
            b.append("")

        return '\n'.join(b)

    # ---- Save Methods ----

    def save(self, output_path):
        """保存为 Markdown 文件"""
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        content = self.build()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        lines = content.count('\n') + 1
        _safe_print(f"[Report] Markdown saved: {output_path} ({len(content)} chars, {lines} lines)")
        return output_path

    def save_html(self, output_path):
        """保存为单文件 HTML（可在浏览器中 Ctrl+P 打印为 PDF）"""
        content = self.build()
        try:
            import markdown
        except ImportError:
            _safe_print("[Report] 'markdown' not installed. Saving as plain text HTML.")
            html_body = content.replace('\n', '<br>')
        else:
            html_body = markdown.markdown(content, extensions=['tables', 'fenced_code', 'nl2br'])

        title = self.paper.get('title', 'Report')[:100]
        html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><title>{title}</title>
<style>
@page {{ margin: 2cm; size: A4; }}
@media print {{ body {{ font-size: 10pt; }} }}
body {{ font-family: 'Helvetica Neue', Arial, 'Microsoft YaHei', 'SimHei', sans-serif;
       font-size: 11pt; line-height: 1.7; color: #222; max-width: 820px; margin: auto; padding: 40px 30px; }}
h1 {{ font-size: 20pt; border-bottom: 3px solid #003366; padding-bottom: 8px; color: #003366; }}
h2 {{ font-size: 15pt; color: #003366; margin-top: 28px; border-bottom: 1px solid #ddd; padding-bottom: 4px; }}
h3 {{ font-size: 13pt; color: #1A5276; margin-top: 20px; }}
blockquote {{ background: #f5f7fa; border-left: 4px solid #003366; padding: 8px 16px; color: #555; margin: 12px 0; }}
code {{ background: #f0f0f0; padding: 1px 4px; font-size: 10pt; }}
pre {{ background: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 9.5pt; overflow-x: auto; }}
img {{ max-width: 100%; margin: 12px 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
th, td {{ border: 1px solid #ddd; padding: 6px 10px; text-align: left; }}
th {{ background: #003366; color: #fff; }}
tr:nth-child(even) {{ background: #f9f9f9; }}
ul, ol {{ margin: 6px 0; padding-left: 24px; }}
li {{ margin: 3px 0; }}
strong {{ color: #003366; }}
hr {{ border: none; border-top: 1px solid #eee; margin: 20px 0; }}
em {{ color: #666; }}
</style></head><body>
{html_body}
</body></html>"""

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        _safe_print(f"[Report] HTML saved: {output_path} ({len(html)/1024:.0f} KB)")
        _safe_print("[Report]  Tip: Open in browser -> Ctrl+P -> Save as PDF")
        return output_path

    def save_auto(self, output_path, fmt=None):
        """自动选择格式保存。

        Args:
            output_path: 输出路径 (不含扩展名或含扩展名)
            fmt: 'md' | 'html' | None (从扩展名自动检测)
        """
        if fmt is None:
            ext = os.path.splitext(output_path)[1].lower()
            fmt = 'html' if ext in ('.html', '.htm') else 'md'
            if ext:
                output_path = output_path[:-len(ext)]

        if fmt == 'html':
            return self.save_html(output_path + ('.html' if not output_path.endswith('.html') else ''))
        else:
            return self.save(output_path + ('.md' if not output_path.endswith('.md') else ''))


# ============================================================
# Quick build helper
# ============================================================

def quick_build(paper_data, output_path):
    """从字典快速构建报告"""
    r = ReportBuilder()
    r.set_meta(
        title=paper_data.get('title', ''),
        authors=paper_data.get('authors', ''),
        journal=paper_data.get('journal', ''),
        doi=paper_data.get('doi', ''),
        paper_type=paper_data.get('paper_type', 'computational'),
        difficulty=paper_data.get('difficulty', 3),
        prerequisites=paper_data.get('prerequisites', []),
        peer_review_status=paper_data.get('peer_review_status', 'Journal Article'),
    )
    for k in ['innovation', 'abstract', 'problem', 'approach', 'background', 'result_chain']:
        if k in paper_data:
            r.paper[k] = paper_data[k]
    r.paper['contributions'] = paper_data.get('contributions', [])
    r.paper['key_results'] = paper_data.get('key_results', [])
    r.paper['limitations'] = paper_data.get('limitations', [])
    r.paper['applicable_scenarios'] = paper_data.get('applicable_scenarios', [])

    for s in paper_data.get('sections', []):
        r.add_section(s.get('level', 3), s.get('title', ''), s.get('content', ''))
    for f in paper_data.get('figures', []):
        r.add_figure(f.get('id', ''), f.get('path', ''), f.get('description', ''),
                      f.get('key_points', []), f.get('section_ref', ''))
    for q in paper_data.get('qa', []):
        r.add_qa(q.get('question', ''), q.get('answer', ''), q.get('category', 'principle'))

    return r.save(output_path)


if __name__ == "__main__":
    r = ReportBuilder()
    r.set_meta(title="Demo Report", authors="Test", journal="Test J.", paper_type="computational", difficulty=2)
    r.paper['innovation'] = "Demo innovation"
    r.paper['abstract'] = "Demo abstract"
    r.paper['problem'] = "Demo problem"
    r.paper['approach'] = "Demo approach"
    r.paper['background'] = "Demo background"
    r.paper['contributions'] = ["C1", "C2"]
    r.add_section(3, "Methods", "Demo methods content")
    r.paper['result_chain'] = "A -> B -> C"
    r.paper['key_results'] = [{"title": "R1", "points": ["p1", "p2"]}]
    r.paper['limitations'] = ["L1"]
    r.paper['applicable_scenarios'] = ["S1"]
    r.add_qa("Q1?", "A1.", "principle")
    r.save("output/demo_report.md")
    r.save_html("output/demo_report.html")
