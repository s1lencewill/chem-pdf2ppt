# chem-pdf2ppt — 化学学术论文 → 演示文稿转换器

[![npm version](https://img.shields.io/npm/v/chem-pdf2ppt)](https://www.npmjs.com/package/chem-pdf2ppt)
[![npm downloads](https://img.shields.io/npm/dm/chem-pdf2ppt)](https://www.npmjs.com/package/chem-pdf2ppt)
[![license](https://img.shields.io/npm/l/chem-pdf2ppt)](https://github.com/s1lencewill/chem-pdf2ppt/blob/main/LICENSE)
[![github stars](https://img.shields.io/github/stars/s1lencewill/chem-pdf2ppt?style=social)](https://github.com/s1lencewill/chem-pdf2ppt)

将化学领域学术论文 PDF 转换为专业学术演示文稿的Agent skill。支持 **PPTX** 和 **HTML** 两种输出格式。

## 核心特性

- **论文化学类型自动识别**：实验化学 / 理论计算化学 / 实验+理论混合，自动匹配叙事结构
- **双格式输出**：PPTX（python-pptx）和单文件 HTML（横向翻页，图片 base64 嵌入）
- **化学领域深度适配**：催化、材料、有机合成、计算化学、电化学、能源、环境、辐射化学等
- **智能内容生成**：从论文提取真实信息，不生成"请手动添加XX"占位符
- **多策略图表提取**：矢量图聚类 + 嵌入式图片 + 整页渲染回退，兼容 PyMuPDF 1.19–1.23+
- **错误追踪与报告**：全链路 JSON 报告（分析 → 提取 → 构建），Windows 编码安全
- **4 套学术配色**：学术经典 / 分子科技 / 绿色化学 / Nature 风格
- **7 种幻灯片类型**：封面、章节分隔、内容要点、图表说明（4 种布局）、数据表格、总结、致谢

---

## 安装

### npm（推荐）

```bash
npm install -g chem-pdf2ppt
```

```bash
chem-pdf2ppt analyze paper.pdf --json analysis.json
chem-pdf2ppt extract paper.pdf figures/ 300 --report
```

### Python API

```bash
pip install -r requirements.txt
```

**依赖**：`pymupdf>=1.19.0` · `python-pptx>=0.6.23` · `pdfplumber>=0.10.0` · `Pillow>=10.0.0`

`pdf2image` 可选（需系统安装 Poppler）。

---

## 为什么选择 chem-pdf2ppt？

| | chem-pdf2ppt | 手动做 PPT | 通用 PDF→PPT 工具 |
|---|---|---|---|
| 化学论文理解 | 自动识别实验/计算/混合类型 | 靠你自己 | 不理解论文内容 |
| 内容生成 | 从 PDF 提取真实数据，无占位符 | 2-4 小时/篇 | 截图转 PPT，无结构化内容 |
| 图表处理 | 多策略提取 + 自动回退 | 手动截图裁剪 | 整页截图 |
| 输出格式 | PPTX + HTML（横向翻页） | PPTX | PPTX |
| 学术风格 | 4 套化学配色 + 结论式标题 | 看个人审美 | 通用模板 |

---

## 快速开始

### 完整工作流

```bash
# Step 1: 分析论文类型与结构
python scripts/analyze_paper.py paper.pdf --json analysis.json

# Step 2: 提取图表（多策略 + 自动回退）
python scripts/extract_charts.py paper.pdf output/figures 300 --report

# Step 3: 构建 PPTX 或 HTML
python build_my_ppt.py
```

### PPTX 格式

```python
import sys
sys.path.insert(0, 'scripts')
from create_ppt import ChemistryPPT

ppt = ChemistryPPT(theme='academic')

ppt.add_title_slide(
    title_cn='Ru₁/Cu 单原子合金高效电催化 CO₂ 还原',
    title_en='Single-Atom Ru Alloyed with Cu for Efficient CO₂RR',
    authors='Zhang, L. et al.',
    journal='J. Am. Chem. Soc., 2024, 146, 12345',
    doi='10.1021/jacs.4c01234'
)

ppt.add_section_slide('研究背景')
ppt.add_content_slide(
    title='电催化 CO₂ 还原的核心挑战',
    bullets=[
        'CO₂RR 产物分布广泛，选择性控制困难',
        'Cu 基催化剂 C₂₊ FE 通常 < 50%',
        '关键瓶颈：*CO 吸附能与 C-C 偶联动力学的矛盾'
    ]
)
ppt.add_figure_slide(
    title='HAADF-STEM 确认 Ru 单原子分散',
    figure_path='figures/p3_fig1.png',
    bullets=['亮点均匀分散，无团簇', 'EDS mapping 确认均匀分布'],
    figure_label='Figure 1',
    layout='figure_right'
)
ppt.add_table_slide(
    title='催化性能对比',
    headers=['催化剂', 'FE(C₂₊)%', 'j (mA/cm²)', '稳定性 (h)'],
    rows=[['Ru₁/Cu', '82%', '300', '100'], ['Cu NPs', '45%', '150', '20']]
)
ppt.add_summary_slide(
    title='全文总结',
    bullets=['核心发现1', '核心发现2', '核心发现3']
)
ppt.add_thankyou_slide()

ppt.save('output/presentation.pptx')
ppt.save_report('output/presentation.pptx')  # 生成 JSON 构建报告
```

### HTML 格式

```python
import sys
sys.path.insert(0, 'scripts')
from generate_html import HtmlPPT

html = HtmlPPT(title="学术报告", theme="molecular")

# API 与 ChemistryPPT 完全一致
html.add_title_slide("标题", title_en="Title", authors="...", journal="...")
html.add_section_slide("第一部分")
html.add_content_slide("要点标题", ["bullet 1", "bullet 2"])
html.add_figure_slide("图表", figure_path="figures/fig1.png",
                       bullets=["说明"], figure_label="Figure 1",
                       layout="figure_right")
html.add_summary_slide("总结", ["结论1", "结论2"])
html.add_thankyou_slide()

html.save('output/presentation.html')  # 单文件，可直接浏览器打开
```

**HTML 特性**：
- 图片以 base64 嵌入，单文件零依赖
- 横向翻页：键盘 ← → Home End、滚轮、触摸滑动、底部圆点导航
- 页码追踪 + 键盘提示
- 响应式设计，适配投影仪和移动端

---

## 配色主题

| 主题 | PPTX 参数 | HTML 参数 | 适合 |
|------|-----------|-----------|------|
| 学术经典 | `theme="academic"` | `theme="academic"` | 通用化学（默认） |
| 分子科技 | `theme="molecular"` | `theme="molecular"` | 计算化学/材料 |
| 绿色化学 | `theme="green"` | `theme="green"` | 催化/能源/环境 |
| Nature 风格 | `theme="nature"` | `theme="nature"` | CNS 期刊汇报 |

---

## 幻灯片类型

| 方法 | PPTX | HTML | 用途 |
|------|------|------|------|
| `add_title_slide()` | ✓ | ✓ | 封面页（中英文标题、作者、期刊、DOI） |
| `add_section_slide()` | ✓ | ✓ | 章节分隔页（深色背景） |
| `add_content_slide()` | ✓ | ✓ | 文字要点页（标题 + bullets + 备注） |
| `add_figure_slide()` | ✓ | ✓ | 图表+说明（4 种布局：right/top/left/full） |
| `add_table_slide()` | ✓ | ✓ | 数据对比表（斑马纹、表头着色） |
| `add_image_grid_slide()` | ✓ | — | 多图网格页 |
| `add_summary_slide()` | ✓ | ✓ | 总结页（浅色背景） |
| `add_thankyou_slide()` | ✓ | ✓ | 致谢/提问页 |

---

## 图表提取：多策略 + 版本兼容

```
策略 1: cluster_drawings() 默认容忍度 (3,3)
   ↓ 结果 < 3
策略 2: 多容忍度尝试 (6,6) → (10,10) → (15,15) → (20,20)
   ↓
策略 3: 提取嵌入式位图 (get_images)
   ↓ 结果 < 3
策略 4: 图页整页渲染回退
```

- 兼容 PyMuPDF 1.19+ (`get_drawings` 手动聚类) 和 1.23+ (`cluster_drawings`)
- `--report` 输出 `extraction_report.json`（各策略提取详情）

---

## 错误处理与报告

全链路 JSON 报告，便于自动化集成和问题诊断：

| 阶段 | 报告文件 | 生成方式 |
|------|---------|---------|
| 论文分析 | `analysis.json` | `analyze_paper.py --json analysis.json` |
| 图表提取 | `extraction_report.json` | `extract_charts.py --report` |
| PPTX 构建 | `presentation_report.json` | `ppt.save_report("output.pptx")` |

**Windows 编码安全**：所有脚本使用 `_safe_print()` 避免 GBK 编码崩溃。

**常见问题自动诊断**：

| 症状 | 可能原因 | 脚本输出 |
|------|---------|---------|
| 矢量图提取 0 个 | PyMuPDF < 1.23 或 PDF 渲染特殊 | 自动回退到 `get_drawings` 手动聚类 |
| 图表总数仍不足 | 图片均为嵌入式位图 | 策略 3 自动覆盖 |
| Windows `print` 崩溃 | Unicode 字符 (如 − ₂) | `_safe_print` 回退 ASCII |
| 论文类型误判 | 参考文献含表征术语 | 加权检测 + confidence 标注 |
| PPT 中图片缺失 | 图片路径不存在 | 记录到 `missing_images`，构建不中断 |

---

## 论文化学类型适配

| 实验化学 | 理论计算化学 | 实验+理论混合 |
|---------|------------|-------------|
| 合成 → 表征 → 性能 → 机理 | 方法 → 模型 → 电子结构 → 能量 → 机理 | 实验 → 计算 → 互验 → 统一机理 |
| 催化/材料/有机/能源 | DFT/MM/AIMD/电子结构 | 实验+DFT 联合 |

详细模板见 `references/chemistry_templates.md`。

---

## 文件结构

```
PDF2PPT/
├── SKILL.md                         # Skill 主文件
├── README.md                        # 本文件
├── requirements.txt
├── assets/
│   └── academic_template.html       # HTML PPT 模板（CSS + 翻页 JS）
├── scripts/
│   ├── create_ppt.py                # PPTX 构建器 (ChemistryPPT)
│   ├── generate_html.py             # HTML 构建器 (HtmlPPT)
│   ├── extract_charts.py            # 多策略图表提取
│   ├── analyze_paper.py             # 论文分析 + 类型分类
│   └── convert_to_images.py         # PDF 页面 → 图片
├── references/
│   ├── chemistry_templates.md       # 三种论文类型的逐页模板
│   └── visual_style.md              # 学术 PPT 视觉设计规范
└── examples/
    └── example_usage.py             # 三种化学论文类型的完整示例
```

---

## 兼容性

- **OS**: macOS / Linux / Windows
- **Python**: 3.8+
- **PyMuPDF**: 1.19+（自动兼容新旧 API）
- **环境**: Claude Code / Claude Desktop / Cursor / VS Code / 任何 Python 环境
- **HTML 输出**: 任何现代浏览器（Chrome / Firefox / Edge / Safari）

## 推广与社区

**如果你觉得有用，请：**
- ⭐ [GitHub Star](https://github.com/s1lencewill/chem-pdf2ppt) — 让更多研究者看到
- 📦 [npm](https://www.npmjs.com/package/chem-pdf2ppt) — 每周下载量帮助排名
- 🐛 [提交 Issue](https://github.com/s1lencewill/chem-pdf2ppt/issues) — 反馈问题或建议

**分享到学术社区：**
- 知乎/小红书：分享你的使用体验
- B站：录制使用教程
- Twitter/X：`#chemistry #academicPPT #chemPDF2PPT`
- GitHub Trending / Hacker News

**需要帮助？** [GitHub Discussions](https://github.com/s1lencewill/chem-pdf2ppt/discussions)

## 许可证

MIT License
