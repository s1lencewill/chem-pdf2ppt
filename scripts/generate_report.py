# -*- coding: utf-8 -*-
"""
化学学术论文 Markdown 报告生成器
Chemistry Academic Paper Report Generator — produces publication-ready reading notes
"""
import os
import re


def _safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', errors='replace').decode('ascii'))

def _escape_md(text):
    """Escape special markdown chars in plain text contexts (not code blocks)"""
    return text

# ============================================================
# Paper Type Definitions
# ============================================================

PAPER_TYPES = {
    "experimental": {
        "label": "Experimental Chemistry",
        "label_cn": "实验化学",
        "method_sections": [
            "Synthesis / Preparation",
            "Characterization Techniques",
            "Performance Testing",
            "Control Experiments",
        ],
    },
    "computational": {
        "label": "Theoretical / Computational Chemistry",
        "label_cn": "理论计算化学",
        "method_sections": [
            "Potential Energy Description",
            "Dynamics & Sampling",
            "Analysis Tools & Parameters",
        ],
    },
    "hybrid": {
        "label": "Experimental + Theoretical Hybrid",
        "label_cn": "实验+理论混合",
        "method_sections": [
            "Experimental Methods",
            "Computational Methods",
            "Cross-Validation Strategy",
        ],
    },
}

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
        self._buf = []

    def set_meta(self, title, authors, journal, doi="", paper_type="computational",
                 difficulty=3, prerequisites=None, peer_review_status="Journal Article"):
        self.paper = {
            "title": title,
            "title_en": getattr(self, '_title_en', ''),
            "authors": authors,
            "journal": journal,
            "doi": doi,
            "paper_type": paper_type,
            "difficulty": difficulty,
            "prerequisites": prerequisites or [],
            "peer_review_status": peer_review_status,
        }

    def _stars(self, n):
        return "⭐" * n

    def _h(self, level, text):
        return f"\n{'#' * level} {text}\n"

    def add_section(self, heading_level, title, content):
        self.sections.append({"level": heading_level, "title": title, "content": content})

    def add_figure(self, fig_id, path, description, key_points, section_ref=""):
        self.figures.append({
            "id": fig_id, "path": path, "description": description,
            "key_points": key_points, "section_ref": section_ref,
        })

    def add_qa(self, question, answer, category="principle"):
        self.qa_items.append({"question": question, "answer": answer, "category": category})

    # ---- Build ----

    def build(self):
        p = self.paper
        b = []

        # 0. Meta
        b.append(f"# {p.get('title', 'Untitled')}\n")
        b.append("> **Authors**: " + p.get('authors', 'N/A'))
        b.append(f"> **Published**: {p.get('journal', 'N/A')}")
        if p.get('doi'):
            b.append(f"> **DOI**: [{p['doi']}](https://doi.org/{p['doi']})")
        b.append(f"> **Peer Review Status**: {p.get('peer_review_status', 'Journal Article')}")
        b.append(f"> **Difficulty**: {self._stars(p.get('difficulty', 3))}")
        prereqs = p.get('prerequisites', [])
        if prereqs:
            b.append(f"> **Prerequisites**: {' · '.join(prereqs)}")
        b.append("")

        # 1. Overview
        b.append(self._h(2, "一、总览"))
        b.append(self._h(3, "核心创新点"))
        b.append(p.get('innovation', '*（从论文提取）*'))
        b.append("")
        b.append(self._h(3, "摘要"))
        b.append(p.get('abstract', '*（从论文提取）*'))
        b.append("")

        # 2. Paper Summary
        b.append(self._h(2, "二、论文概述"))
        b.append(f"- **解决什么问题**：{p.get('problem', '')}")
        b.append(f"- **核心方案**：{p.get('approach', '')}")
        b.append(f"- **论文类型**：{PAPER_TYPES.get(p.get('paper_type',''), PAPER_TYPES['computational']).get('label_cn','')}")
        contributions = p.get('contributions', [])
        for c in contributions:
            b.append(f"  - {c}")
        b.append("")

        # 3. Background
        b.append(self._h(2, "三、背景与动机"))
        b.append(p.get('background', ''))
        b.append("")

        # 4. Core Methods
        b.append(self._h(2, "四、核心方法"))
        for s in self.sections:
            if s["level"] <= 3:
                b.append(self._h(s["level"], s["title"]))
            else:
                b.append(f"{'#' * s['level']} {s['title']}\n")
            b.append(s["content"])
            b.append("")

        # 5. Results
        b.append(self._h(2, "五、结果与讨论"))
        b.append(self._h(3, "结果逻辑链"))
        b.append(p.get('result_chain', ''))
        b.append("")
        b.append(self._h(3, "关键结果详情"))
        results = p.get('key_results', [])
        for r in results:
            b.append(f"**{r.get('title', '')}**")
            for pt in r.get('points', []):
                b.append(f"- {pt}")
            if r.get('figure'):
                b.append(f"  📊 *参见 Figure {r['figure']}*")
            b.append("")

        # Figures gallery
        if self.figures:
            for fig in self.figures:
                b.append(f"![{fig['description']}]({fig['path']})")
                b.append(f"**{fig['id']}**：{fig['description']}")
                for kp in fig['key_points']:
                    b.append(f"- {kp}")
                if fig.get('section_ref'):
                    b.append(f"*对应正文 {fig['section_ref']}*")
                b.append("")

        # 6. Summary
        b.append(self._h(2, "六、总结与思考"))
        b.append(self._h(3, "核心贡献"))
        for c in p.get('contributions', []):
            b.append(f"- {c}")
        b.append("")
        b.append(self._h(3, "局限性"))
        for l in p.get('limitations', ['（从论文或分析中提取）']):
            b.append(f"- {l}")
        b.append("")
        b.append(self._h(3, "适用场景"))
        for s in p.get('applicable_scenarios', ['（分析适用和不适用的情况）']):
            b.append(f"- {s}")
        b.append("")

        # 7. Q&A
        b.append(self._h(2, "Q&A 深度思考"))
        qa_categories = {
            "principle": "原理理解",
            "detail": "细节辨析",
            "boundary": "边界条件",
            "extension": "延伸思考",
        }
        for i, qa in enumerate(self.qa_items, 1):
            cat_label = qa_categories.get(qa['category'], '')
            b.append(f"**Q{i}** [{cat_label}] {qa['question']}")
            b.append(f"**A{i}** {qa['answer']}")
            b.append("")

        return '\n'.join(b)

    def save(self, output_path):
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        content = self.build()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        _safe_print(f"[Report] Saved: {output_path} ({len(content)} chars, {content.count(chr(10))+1} lines)")
        return output_path


# ============================================================
# Quick build helper
# ============================================================

def quick_build(paper_data, output_path):
    """
    Build a report from a dictionary of paper data.

    paper_data keys:
        title, authors, journal, doi, paper_type, difficulty, prerequisites,
        innovation, abstract, problem, approach, contributions, background,
        sections: [{level, title, content}],
        result_chain, key_results: [{title, points, figure}],
        figures: [{id, path, description, key_points, section_ref}],
        limitations, applicable_scenarios,
        qa: [{question, answer, category}]
    """
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
    r.paper['innovation'] = paper_data.get('innovation', '')
    r.paper['abstract'] = paper_data.get('abstract', '')
    r.paper['problem'] = paper_data.get('problem', '')
    r.paper['approach'] = paper_data.get('approach', '')
    r.paper['contributions'] = paper_data.get('contributions', [])
    r.paper['background'] = paper_data.get('background', '')
    r.paper['result_chain'] = paper_data.get('result_chain', '')
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
    # Demo
    r = ReportBuilder()
    r.set_meta(
        title="Acids at the Edge: Why Nitric and Formic Acid Dissociations at Air–Water Interfaces Depend on Depth and on Interface Specific Area",
        authors="Miguel de la Puente, Rolf David, Axel Gomez, Damien Laage*",
        journal="J. Am. Chem. Soc., 2022, 144, 10524–10529",
        doi="10.1021/jacs.2c03099",
        paper_type="computational",
        difficulty=3,
        prerequisites=["Basic MD concepts", "Free energy calculation", "Acid-base chemistry"],
    )
    r.paper['innovation'] = (
        "通过 DeePMD-kit 训练的 NNP 反应力场，首次以 DFT 精度 + ns 级采样揭示了空气-水界面处 "
        "HNO₃ 和 HCOOH 的解离自由能深度分布，建立了局域溶剂化模型将界面酸碱性定量关联到各物种的溶剂化自由能，"
        "并从分子层面解释了 SFG/XPS（酸性减弱）与 OESI-MS（酸性增强）的实验矛盾。"
    )
    r.paper['abstract'] = "（略，见论文原文）"
    r.paper['problem'] = "空气-水界面的酸碱性如何随深度变化？为什么不同实验方法给出矛盾结论？"
    r.paper['approach'] = "NNP 反应力场 + metadynamics 增强采样的自由能计算 + 局域溶剂化模型"
    r.paper['contributions'] = [
        "首次以 DFT 精度计算界面不同深度的酸解离自由能（≃ns 级采样，精度 0.1 kcal/mol）",
        "建立局域溶剂化模型，将界面酸碱性分解为各物种溶剂化自由能贡献",
        "从分子层面解释了 SFG/XPS（探测顶层→酸性弱）与 OESI-MS（探测更深→酸性强）的矛盾",
    ]
    r.paper['background'] = (
        "空气-水界面广泛存在于大气气溶胶、海洋酸化等关键环境过程。"
        "SFG 和 XPS 实验表明界面酸性弱于体相，而 OESI-MS 实验则显示部分羧酸在界面酸性增强。"
        "DFT-based MD 模拟精度高但计算代价极大，采样严重不足。"
    )
    r.add_section(3, "整体计算策略",
        "NNP 训练（BLYP-D3 参考数据）→ MD 模拟（DeePMD-kit + LAMMPS）→ metadynamics 自由能计算 → 局域溶剂化模型分析。")
    r.add_section(3, "机器学习势函数",
        "- **架构**：DeepMD-kit (Deep Potential)\n"
        "- **参考级别**：BLYP-D3 DFT（1 酸 + 128 H₂O）\n"
        "- **训练策略**：迭代富集 (DP-GEN)，覆盖体相和界面的反应物/产物构型\n"
        "- **加速比**：相对 DFT-based MD > 1000×")
    r.add_section(3, "动力学与采样",
        "- **MD 类型**：经典 NNP MD\n"
        "- **增强采样**：metadynamics\n"
        "- **集体变量 (CV)**：酸氧原子周围的氢配位数\n"
        "- **约束**：酸在 slab 中不同深度处约束\n"
        "- **模拟时长**：每条自由能曲线 ≃ns（达到 0.1 kcal/mol 精度）")
    r.paper['result_chain'] = (
        "体相 pKa 验证 → 各深度解离自由能曲线 → 各物种独立水化自由能 → 局域溶剂化模型 → "
        "解释实验矛盾 → 气溶胶尺寸效应预测"
    )
    r.paper['key_results'] = [
        {"title": "体相 pKa 验证", "points": [
            "HNO₃ pKa_calc=−2.0±0.1 vs pKa_exp=−1.4", "HCOOH pKa_calc=3.5±0.1 vs pKa_exp=3.7"]},
        {"title": "界面酸碱性在 2 个分子层内突变", "points": [
            "界面处（顶层）：酸性弱于体相——共轭碱去溶剂化效应显著",
            "界面下方：酸性强于体相——H₃O⁺ 可扩散至界面并被优先溶剂化（~1.0±0.2 kcal/mol）",
        ], "figure": "1"},
        {"title": "局域溶剂化模型", "points": [
            "ΔrG(d) = ΔrG_bulk + ΔG_hyd(B,d) + ⟨ΔG_hyd(H)⟩L − ΔG_hyd(A,d) − ⟨ΔG_hyd(W)⟩L",
            "模型预测与直接计算在所有深度高度一致",
        ], "figure": "3"},
    ]
    r.paper['limitations'] = [
        "NNP 精度受 BLYP-D3 参考级别限制",
        "体系仅含 128 H₂O，有限尺寸效应未完全排除",
        "仅研究了两种酸（HNO₃ 和 HCOOH），推广到其他酸需进一步验证",
    ]
    r.paper['applicable_scenarios'] = [
        "适合：界面酸碱性、气溶胶化学、大气化学中涉及酸解离的体系",
        "不适合：非水溶剂界面、含复杂离子效应的多组分体系（需扩展模型）",
    ]
    r.add_qa(
        "为什么选择 H 配位数作为 metadynamics 的 CV？",
        "酸解离过程本质上是 H⁺ 从酸转移到溶剂水的过程。酸氧原子周围的 H 配位数（0→1→2）直接反映了"
        "质子从酸到水的转移程度，是描述解离反应最直观的几何变量。同时该 CV 计算简单，不依赖"
        "先验的路径知识，适合无偏探索。",
        "principle"
    )
    r.add_qa(
        "NNP vs DFT-based AIMD 的成本-精度取舍如何？",
        "BLYP-D3 NNP 的精度受限于参考 DFT（无 exact exchange，可能低估某些电子相关效应），"
        "但通过 ≥1000× 加速，实现了 ns 级的自由能采样，使 pKa 精度达到 ±0.1。"
        "而 DFT-based AIMD 虽然可用 hybrid functional（如 PBE0），但 ps 级的采样不足以收敛"
        "自由能曲线。对于酸解离这类需要充分采样的事件，NNP 的统计精度优势远大于参考级别的局限。",
        "detail"
    )
    r.add_qa(
        "该模型的假设条件是什么？什么情况下会失效？",
        "（1）假设酸/碱/水合物种的溶剂化自由能可加和分离——在多离子强耦合体系可能失效。"
        "（2）H₃O⁺ 的贡献以 slab 厚度平均——对于极薄 slab（< 1 nm）可能不够准确。"
        "（3）模型针对中性酸设计——正离子酸（如三甲基铵）需扩展公式。"
        "（4）未考虑界面 pH 梯度与离子强度效应。",
        "boundary"
    )
    r.save("output/demo_report.md")
    _safe_print("Demo report generated: output/demo_report.md")
