---
name: pdf-to-ppt
description: 将化学（实验化学 or 理论计算化学）学术论文 PDF 转换为专业学术型 PowerPoint 演示文稿。自动识别论文类型（实验/理论/混合），提取关键信息，生成结构化、可直接用于组会/答辩/学术报告的 PPTX 文件。当用户提到"论文转PPT"、"PDF转PPT"、"做组会PPT"、"文献汇报"、"学术报告PPT"、"化学论文PPT"、"实验化学PPT"、"计算化学PPT"，或提供化学相关 PDF/arXiv 论文要求生成演示文稿时触发。
---

# PDF → 化学学术 PPT 生成器

将化学领域学术论文 PDF 转换为可直接使用的学术 PowerPoint 演示文稿。

## 核心原则

**让论文的科学论证逻辑驱动 PPT 结构，而非套用固定模板。**

化学论文分为实验化学和理论计算化学两大范式，两者的叙事逻辑完全不同：

- **实验化学**：问题 → 设计策略 → 合成/制备 → 表征 → 性能 → 机理 → 结论
- **理论计算化学**：问题 → 计算方法 → 模型验证 → 电子结构/能量分析 → 机理阐释 → 实验对照 → 结论
- **实验+理论混合**：问题 → 实验部分 → 计算部分 → 实验-理论互验 → 统一机理 → 结论

生成的 PPT 应当让听众能够依次回答：
1. 这个化学问题为什么重要？
2. 前人做到了什么程度，瓶颈在哪？
3. 本文的设计思路/计算策略是什么？
4. 关键实验证据/计算结果是什么？
5. 机理解释是否自洽？
6. 有什么新认识，能推广吗？
7. 局限性和开放问题是什么？

## 输入形式

接受以下任意形式：
- 完整的论文 PDF 文件
- arXiv / chemRxiv 预印本 PDF
- 论文摘要 + 图表 + 结果文字
- 结构化阅读笔记
- 用户粘贴的论文内容

默认输出语言为中文，保留关键化学术语、缩写、化合物名称、方法名的英文原文。

## 工作流程

### Step 0: 安装依赖（首次使用）

```bash
pip install -r <SKILL_ROOT>/requirements.txt
```

### Step 1: 读取并理解论文

使用 PyMuPDF (fitz) 提取论文全文文本：

```python
import fitz
doc = fitz.open("paper.pdf")
full_text = ""
for page in doc:
    full_text += page.get_text()
```

从全文中识别以下关键信息：
- **标题、作者、期刊、年份、DOI**
- **论文化学类型**：实验化学 / 理论计算化学 / 实验+理论混合
- **核心化学问题**：催化、合成、材料、能源、环境、药物、机理等
- **研究空白**：前人工作的局限
- **核心论点/假说**
- **关键方法**：
  - 实验：合成路线、催化剂制备方法、表征手段（XRD, TEM, SEM, XPS, BET, NMR, IR, Raman, EPR, XAS 等）、性能测试条件
  - 计算：理论水平（DFT functional, basis set）、软件包（VASP, Gaussian, CP2K, QE 等）、模型体系、自由能计算方法
- **关键结果**：性能数据、表征结论、能量数据、选择性/转化率/产率、TOF、稳定性等
- **关键图表**：Figure 编号及内容概述
- **机理/构效关系**
- **创新点与局限**

**重要**：不要编造论文中不存在的数据、机理或图表信息。如信息不明确，标注 "[待确认]"。

### Step 2: 判定论文化学类型并选择叙事弧

根据论文内容判定类型，选择对应的叙事逻辑：

#### 类型 A: 实验化学
**识别信号**：包含合成步骤、湿化学方法、材料制备、催化剂测试、表征数据（XRD/TEM/SEM/XPS 等）、性能评价（转化率/选择性/产率/循环稳定性）

**叙事弧**（question-to-evidence）：
1. 化学问题与重要性
2. 前人策略局限 → 本文设计思路
3. 合成/制备路线
4. 结构与组成表征
5. 催化/性能评价
6. 机理探究（in-situ 表征、对照实验、动力学等）
7. 构效关系总结
8. 结论与展望

**PPT 结构**（12-16 页）：
```
Slide 1:  标题页
Slide 2:  研究背景与化学问题
Slide 3:  文献进展与瓶颈
Slide 4:  本文设计策略
Slide 5:  合成/制备路线
Slide 6:  结构与组成表征（XRD/TEM/XPS...）
Slide 7:  形貌与微观结构（SEM/TEM/HRTEM...）
Slide 8:  性能评价（催化活性/选择性/稳定性）
Slide 9:  关键对照实验或性能对比表
Slide 10: 机理探究（in-situ / 动力学 / 毒化实验...）
Slide 11: 构效关系 / 活性位点讨论
Slide 12: 与文献基准对比
Slide 13: 总结与创新点
Slide 14: 局限性与展望
```

#### 类型 B: 理论计算化学
**识别信号**：包含 DFT 计算、分子动力学、蒙特卡罗、电子结构分析、反应路径搜索、自由能计算、软件包名（VASP/Gaussian/CP2K/QE/GROMACS 等）、k-point/截断能/cutoff energy

**叙事弧**（method-to-mechanism）：
1. 化学问题与计算必要性
2. 前人计算研究的局限
3. 计算方法与模型体系
4. 方法验证/基准测试
5. 电子结构/吸附/反应中间体
6. 能量剖面与反应路径
7. 选择性起源/速控步分析
8. 与实验对照（如有）
9. 结论与展望

**PPT 结构**（12-16 页）：
```
Slide 1:  标题页
Slide 2:  研究背景与化学问题
Slide 3:  前人计算研究回顾
Slide 4:  计算方法与模型
Slide 5:  方法验证/基准测试
Slide 6:  关键中间体/过渡态结构
Slide 7:  能量剖面 / 自由能图
Slide 8:  电子结构分析（PDOS/Bader/COHP...）
Slide 9:  反应选择性分析
Slide 10: 微动力学/火山图（如有）
Slide 11: 与实验数据对照（如有）
Slide 12: 总结与创新点
Slide 13: 局限性与展望
```

#### 类型 C: 实验+理论混合
**识别信号**：同时包含实验部分和计算部分，计算用于解释实验现象

**叙事弧**（experiment-theory-unified）：
1. 化学问题与联合策略
2. 实验部分（合成+表征+性能）
3. 计算部分（模型+方法+结果）
4. 实验-理论互验
5. 统一机理解释
6. 结论

**PPT 结构**（14-18 页，选核心组合）：
```
Slide 1:  标题页
Slide 2:  研究背景与化学问题
Slide 3:  研究策略（实验+计算联合）
Slide 4:  实验：合成与表征
Slide 5:  实验：性能/催化结果
Slide 6:  实验：关键表征证据
Slide 7:  计算：方法与模型
Slide 8:  计算：能量与电子结构
Slide 9:  计算：反应路径/机理
Slide 10: 实验-理论互验
Slide 11: 统一机理模型
Slide 12: 总结与展望
```

幻灯片数量根据论文实际内容灵活调整。内容丰富的论文可扩展至 16-18 页；短论文保持 10-12 页。

### Step 3: 提取图表

使用 `scripts/extract_charts.py` 提取论文中的图表（矢量图优先）：

```bash
python <SKILL_ROOT>/scripts/extract_charts.py paper.pdf output/figures 300
```

这会自动：
1. 用 `cluster_drawings()` 提取矢量图（流程图、机理图、数据图）
2. 用 `get_images()` 提取嵌入式位图（TEM/SEM 照片等）
3. 过滤小尺寸装饰元素
4. 以 300 DPI 保存高清图片

然后，将提取的图表与论文中的 Figure 编号对应。检查 `output/figures/` 目录下的图片，根据页码和出现顺序关联到论文中的 Figure。

**图表选择原则**：
- 只选支撑论文论证的关键图表（通常 4-8 张）
- 优先选：研究策略图/示意图 → 核心结果图 → 机理图 → 验证/对照图
- 宁可少而清晰，不要多而拥挤
- 对于密集的多面板图，考虑裁剪到最关键的 1-2 个面板

### Step 4: 撰写幻灯片内容

对每张幻灯片撰写：
- **中文标题**（结论式标题，而非仅标签——如"Ru SAs 在 300°C 下实现 98% CO 转化率"，而非"催化性能"）
- **3-4 个要点**（简洁中文 bullet points）
- **关联的图表**（Figure 编号和文件路径）
- **图表说明**（简短中文解读）
- **一个核心 takeaway**（听众离开这一页时应该记住什么）
- **演讲者备注**（口头报告时的补充说明，可选）

每张幻灯片只传达一个核心信息。结果页优先放图表，让数据说话。

### Step 5: 创建 PPTX

使用 `scripts/create_ppt.py` 生成 PPTX：

```python
import sys
sys.path.insert(0, '<SKILL_ROOT>/scripts')
from create_ppt import ChemistryPPT

ppt = ChemistryPPT(theme="academic")  # "academic" | "dark" | "nature"

# 添加幻灯片
ppt.add_title_slide(
    title_cn="中文标题",
    title_en="English Title",
    authors="Authors et al.",
    journal="J. Am. Chem. Soc., 2024, 146, xxx",
    doi="10.xxxx/xxxx"
)

ppt.add_section_slide("第一部分：研究背景")

ppt.add_content_slide(
    title="电催化 CO₂ 还原面临的选择性挑战",
    bullets=[
        "CO₂RR 产物分布广泛（CO, HCOOH, CH₄, C₂H₄, EtOH...），选择性控制困难",
        "Cu 基催化剂是目前唯一能生成 C₂₊ 产物的金属，但法拉第效率通常 < 50%",
        "关键瓶颈：*CO 中间体的吸附能和 C-C 偶联动力学难以同时优化"
    ],
    notes="强调 Cu 的独特性和选择性问题的根源"
)

ppt.add_figure_slide(
    title="Ru₁/Cu 单原子合金的 HAADF-STEM 表征",
    figure_path="output/figures/p3_fig1.png",
    figure_label="Figure 1",
    bullets=[
        "HAADF-STEM 确认 Ru 以单原子形式分散在 Cu(111) 表面",
        "EDS mapping 显示 Ru 均匀分布，无团簇形成",
        "XANES 证实 Ru 处于氧化态 Ruᵟ⁺（0 < δ < 3）"
    ],
    caption="Source: Fig. 1a-c, adapted from original paper",
    layout="figure_right"  # "figure_right" | "figure_top" | "figure_full"
)

ppt.add_table_slide(
    title="催化性能对比",
    headers=["催化剂", "FE(C₂₊)%", "电流密度 (mA/cm²)", "稳定性 (h)", "参考文献"],
    rows=[
        ["Ru₁/Cu", "82%", "300", "100", "This work"],
        ["Cu NPs", "45%", "150", "20", "Nat. Catal. 2020"],
        ["Ag/Cu", "60%", "200", "50", "JACS 2022"],
    ]
)

ppt.add_summary_slide(
    title="总结与展望",
    bullets=[
        "首次实现 Ru 单原子合金催化 CO₂ 到 C₂₊ 的高选择性转化（FE 82%）",
        "Operando XAS + DFT 揭示了 Ru 位点促进 *CO 富集和 C-C 偶联的机制",
        "该设计策略可拓展至其他单原子合金体系（Pt/Cu, Pd/Cu）",
        "未来方向：膜电极（MEA）中的实际工况测试与放大"
    ]
)

ppt.save("output/presentation.pptx")
```

**Slide 类型一览**：

| 方法 | 用途 |
|------|------|
| `add_title_slide()` | 封面页：中英文标题、作者、期刊信息 |
| `add_section_slide()` | 章节分隔页 |
| `add_content_slide()` | 文字要点页（带可选副标题） |
| `add_figure_slide()` | 图表+说明页（多种布局选项） |
| `add_table_slide()` | 数据对比表 |
| `add_summary_slide()` | 总结/结论页 |
| `add_thankyou_slide()` | 致谢/提问页 |

### Step 6: (可选) 生成 HTML 版本

除 PPTX 外，还可生成带图的单文件 HTML 演示文稿（仿 guizang-ppt-skill 横向翻页风格，学术配色）：

```python
import sys
sys.path.insert(0, '<SKILL_ROOT>/scripts')
from generate_html import HtmlPPT

html = HtmlPPT(title="学术报告", theme="molecular")

# API 与 ChemistryPPT 完全一致
html.add_title_slide("中文标题", title_en="English Title", authors="...", journal="...")
html.add_section_slide("第一部分")
html.add_content_slide("要点标题", ["要点1", "要点2"])
html.add_figure_slide("图表标题", figure_path="figures/p3_fig1.png",
                       bullets=["说明1", "说明2"], figure_label="Figure 1",
                       layout="figure_right")
html.add_summary_slide("总结", ["结论1", "结论2"])
html.add_thankyou_slide()

html.save("output/presentation.html")
```

**HTML 特性**：
- 单文件，图片以 base64 嵌入，可直接用浏览器打开
- 横向翻页：键盘 ← →、滚轮、触摸滑动、底部圆点导航
- 4 套学术配色主题 (academic / molecular / green / nature)
- 支持所有幻灯片类型（封面、章节、内容、图表、表格、总结、致谢）
- 响应式设计，适配投影仪和移动端
- 无需本地服务器，无需安装任何依赖

### Step 7: 验证与错误报告

生成 PPTX 后执行检查。`ChemistryPPT` 内置了错误追踪：

```python
ppt.save("output/presentation.pptx")
ppt.save_report("output/presentation.pptx")  # 生成 JSON 报告

# 或直接获取
report = ppt.get_report()
print(report["missing_images"])  # 未找到的图片列表
print(report["warnings"])        # 警告
print(report["errors"])          # 错误
```

**报告字段说明**：
- `missing_images`: 所有 `add_figure_slide()` 中路径不存在的图片
- `errors`: 图片插入失败等实际错误
- `warnings`: 非致命问题
- `slide_types`: 各类型幻灯片统计

**自查清单**：
- 所有引用的图表文件存在且正确插入
- 幻灯片数量合理（10-18 页）
- 无文字溢出或重叠
- `missing_images` 为空或已确认可忽略

### 错误处理与回退机制

**图表提取阶段** (`extract_charts.py`)：
1. 多策略提取：矢量图 `cluster_drawings()` → 嵌入图片 `get_images()` → 整页渲染回退
2. 兼容 PyMuPDF 1.19+ 和 1.23+（自动切换 `cluster_drawings` / `get_drawings` + 手动聚类）
3. 多容忍度尝试（3→6→10→15→20）当默认容忍度提取不足时
4. 提取报告 JSON 自动生成：`--report` 参数输出 `extraction_report.json`

**论文分析阶段** (`analyze_paper.py`)：
1. 编码安全：Windows GBK/ASCII 回退，避免 Unicode 字符导致崩溃
2. 论文分类置信度标注（high/medium/low），误分类时给出明确提示
3. 结构化 JSON 输出：`--json report.json` 可集成到自动化流程
4. 计算关键词权重：前 1/3 文本中的信号权重 ×3，参考文献区的信号权重 ×1

**PPT 构建阶段** (`create_ppt.py`)：
1. 缺失图片自动记录（不中断构建），在 `save()` 时汇总输出
2. 图片插入异常捕获（损坏/格式不支持）
3. `save_report()` 导出完整构建日志

**常见错误及处理**：

| 错误 | 原因 | 处理 |
|------|------|------|
| `cluster_drawings` 不存在 | PyMuPDF < 1.23 | 自动回退到 `get_drawings()` 手动聚类 |
| 矢量图提取 0 个 | PDF 渲染方式特殊 | 自动尝试多容忍度，最终回退到整页渲染 |
| Windows 编码崩溃 | Unicode 字符 (如 `−` `₂`) | `_safe_print()` 自动回退到 ASCII |
| 论文类型误判 | 参考文献含表征关键词 | 加权检测（正文权重 ×3），confidence 标注 |
| 图片文件不存在 | 用户未正确提取或路径错误 | 记录到 `missing_images`，幻灯片显示占位文本 |

## 化学学术 PPT 视觉规范

详见 `references/visual_style.md`。摘要如下：

### 配色方案

| 名称 | 主色 | 辅助色 | 强调色 | 适合 |
|------|------|--------|--------|------|
| **学术经典** (默认) | `003366` 深蓝 | `F5F5F5` 浅灰 | `CC3333` 暗红 | 通用化学 |
| **分子科技** | `1A5276` 钢蓝 | `F8F9FA` 近白 | `E74C3C` 亮红 | 计算化学/材料 |
| **绿色化学** | `1E5631` 深绿 | `F7F9F4` 米白 | `D4A017` 金 | 催化/能源/环境 |
| **Nature 风格** | `222222` 近黑 | `FFFFFF` 白 | `0066CC` 蓝 | CNS 期刊汇报 |

### 字体

- 中文标题：微软雅黑 / 思源黑体 Bold, 28-36pt
- 中文正文：微软雅黑 / 思源黑体 Regular, 16-20pt
- 英文/数字：Arial / Helvetica, 对应大小
- 化学式/公式：保持等宽或合适的衬线字体

### 幻灯片布局

- 16:9 宽屏（13.333" × 7.5"）
- 内边距 ≥ 0.5"
- 左对齐为主，标题可居中
- 图表优先给大空间，说明文字简洁

### 化学特色元素

- **反应式/合成路线**：用化学结构式图片或 → 连接的文本式反应式
- **数据表**：对比催化剂性能/计算参数时，用清晰的表格而非嵌入图片
- **机理图**：保留原图，在旁边标注关键步骤（i, ii, iii...）
- **能量图**：自由能剖面图标注关键过渡态和中间体能量
- **表征数据**：XRD 谱图标注关键峰；XPS 标注价态；TEM 标注晶格间距

## 输出文件

默认在 `output/` 目录下生成：

```
output/
├── presentation.pptx          # 最终 PPTX 文件
├── presentation.html          # (可选) 单文件 HTML 演示文稿
├── presentation_report.json   # PPTX 构建报告
├── figures/                   # 提取的图表
│   ├── p2_fig1.png
│   ├── p4_fig2.png
│   └── ...
└── qa_report.md               # 质量检查报告（可选）
```

## 脚本说明

| 脚本 | 功能 |
|------|------|
| `scripts/extract_charts.py` | 提取 PDF 中的矢量图和嵌入式图片（多策略 + 版本兼容） |
| `scripts/analyze_paper.py` | 分析 PDF 结构，识别论文化学类型和图表位置 |
| `scripts/convert_to_images.py` | 将 PDF 页面转为高清图片（用于图片型 PDF） |
| `scripts/create_ppt.py` | 主脚本：创建化学学术 PPTX（ChemistryPPT 类） |
| `scripts/generate_html.py` | HTML 生成器：创建带图单文件横向翻页网页 PPT |

## 容错与回退

- 如果 PDF 文本提取失败（扫描版 PDF），尝试用 OCR 或要求用户提供文本
- 如果图表提取不理想，手动指定页面区域裁剪
- 如果论文信息不完整（无 DOI/作者等），标注 "[信息缺失]" 继续生成
- 如果无法确定化学子类型，默认使用"实验化学"模板
- 绝不编造数据、机理或图表信息

## 常见化学论文类型适配

### 催化化学
重点关注：制备方法、表征（XRD/TEM/XPS/BET）、活性/选择性/稳定性数据、TOF、活化能、in-situ 表征、DFT 辅助机理

### 材料化学
重点关注：合成策略、形貌调控、结构表征、物理化学性质、应用性能、构效关系

### 有机合成化学
重点关注：合成路线、底物适用范围、反应条件优化、机理验证实验、选择性控制

### 计算化学/理论化学
重点关注：计算方法和参数、模型合理性、能量/结构数据、与实验或基准的对照、反应机理的原子级阐释

### 能源/电池化学
重点关注：材料设计、电化学性能（容量/倍率/循环）、原位表征、界面化学、衰减机制

### 环境/大气化学
重点关注：反应动力学、产物分析、机理路径、环境意义、模型计算

## 禁止事项

- 不要生成占位符内容（"请手动添加XX"、"在此填写XX"）
- 不要用固定模板套所有论文——应根据论文实际内容调整结构
- 不要忽略化学式/元素符号的正确格式（上下标、斜体等）
- 不要在结果页不放图表只放文字
- 不要编造论文中不存在的数据或结论
- 不要把 PPT 做成纯文字大纲而非可用的演示文稿
