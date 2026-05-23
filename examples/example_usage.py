# -*- coding: utf-8 -*-
"""
PDF2PPT 完整使用示例 — 三种化学论文类型的 PPT 生成
Complete examples for experimental, computational, and hybrid chemistry papers.
"""
import sys
import os

# Ensure the scripts/ directory is importable
_scripts_dir = os.path.join(os.path.dirname(__file__), '..', 'scripts')
_scripts_dir = os.path.abspath(_scripts_dir)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from create_ppt import ChemistryPPT


# ================================================================
# 示例 1: 实验化学论文 — 催化类
# Example 1: Experimental Chemistry — Catalysis Paper
# ================================================================

def example_experimental_catalysis():
    ppt = ChemistryPPT(theme="academic")

    # 封面
    ppt.add_title_slide(
        title_cn="Ru₁/Cu 单原子合金高效电催化 CO₂ 还原制 C₂₊ 产物",
        title_en="Single-Atom Ru Alloyed with Cu for Efficient Electrochemical CO₂ Reduction to C₂₊ Products",
        authors="Zhang, L. et al.",
        journal="J. Am. Chem. Soc., 2024, 146, 12345-12356",
        doi="10.1021/jacs.4c01234"
    )

    # 章节 1: 研究背景
    ppt.add_section_slide("第一部分：研究背景与设计策略")

    ppt.add_content_slide(
        title="电催化 CO₂ 还原面临的核心挑战",
        bullets=[
            "CO₂RR 可将温室气体转化为高附加值燃料和化学品（CO, C₂H₄, EtOH 等）",
            "Cu 基催化剂是目前唯一能有效生成 C₂₊ 产物的金属，但法拉第效率通常 < 50%",
            "关键瓶颈：*CO 中间体的吸附能难以独立调控，C-C 偶联动力学受限",
            "单原子合金（SAA）策略可精确调控活性位点的电子结构和几何环境"
        ]
    )

    ppt.add_content_slide(
        title="本文设计策略",
        bullets=[
            "设计思路：将 Ru 单原子分散于 Cu(111) 表面，利用 Ru 的强 *CO 吸附能力",
            "预期效果：Ru 位点富集 *CO，邻近 Cu 位点促进 C-C 偶联",
            "表征策略：HAADF-STEM + XAS 确认单原子分散，Operando FTIR 追踪中间体",
            "理论支撑：DFT 计算验证 Ru 位点的 *CO 富集效应和 C-C 偶联能垒降低"
        ]
    )

    # 章节 2: 表征
    ppt.add_section_slide("第二部分：催化剂结构与组成表征")

    ppt.add_figure_slide(
        title="HAADF-STEM 确认 Ru 以单原子形式分散在 Cu 表面",
        figure_path="figures/HAADF_STEM.png",
        figure_label="Figure 1",
        bullets=[
            "HAADF-STEM 图像显示 Ru 原子（亮点）均匀分散，无纳米颗粒或团簇形成",
            "EDS elemental mapping 证实 Ru 在 Cu 基体上的均匀空间分布",
            "Ru 负载量经 ICP-OES 测定为 1.2 wt%，与投料比一致"
        ],
        caption="Source: Fig. 1a-d, adapted from original paper",
        layout="figure_right"
    )

    ppt.add_figure_slide(
        title="XAS 揭示 Ru 的氧化态和配位环境",
        figure_path="figures/XAS.png",
        figure_label="Figure 2",
        bullets=[
            "XANES：Ru K-edge 白线峰位置介于 Ru 箔 (0) 和 RuO₂ (+4) 之间，表明 Ruᵟ⁺（0<δ<3）",
            "EXAFS 拟合：Ru-Cu 配位路径 (~2.55 Å) 为主，无 Ru-Ru 键 (~2.68 Å)，确认单原子分散",
            "小波变换（WT-EXAFS）：进一步排除 Ru 团簇的存在"
        ],
        caption="Source: Fig. 2a-e, adapted from original paper",
        layout="figure_right"
    )

    # 章节 3: 性能
    ppt.add_section_slide("第三部分：催化性能评价")

    ppt.add_figure_slide(
        title="Ru₁/Cu 在 -0.9 V vs RHE 实现 82% C₂₊ 法拉第效率",
        figure_path="figures/performance.png",
        figure_label="Figure 3",
        bullets=[
            "C₂₊ FE 在 -0.9 V 时达到峰值 82%，远超纯 Cu NPs (45%)",
            "部分电流密度 j(C₂₊) = 300 mA/cm²，优于大多数文献报道的 Cu 基催化剂",
            "100 小时恒电位电解稳定性测试：FE(C₂₊) 仅下降 8%",
            "主要产物分布：C₂H₄ (48%), EtOH (22%), C₂H₅OH (12%)"
        ],
        caption="Source: Fig. 3a-f, adapted from original paper",
        layout="figure_right"
    )

    ppt.add_table_slide(
        title="与文献代表性 Cu 基催化剂的性能对比",
        headers=["催化剂", "FE(C₂₊)%", "j(C₂₊) (mA/cm²)", "电解液", "稳定性 (h)", "Ref"],
        rows=[
            ["Ru₁/Cu", "82", "300", "1M KOH", "100", "This work"],
            ["Cu NPs", "45", "150", "1M KOH", "20", "Nat. Catal. 2019"],
            ["Ag/Cu NWs", "60", "200", "1M KHCO₃", "50", "JACS 2022"],
            ["F-Cu", "65", "180", "1M KOH", "40", "Nature 2021"],
            ["B-Cu", "55", "120", "0.1M KHCO₃", "30", "Science 2020"],
        ]
    )

    # 章节 4: 机理
    ppt.add_section_slide("第四部分：反应机理探究")

    ppt.add_figure_slide(
        title="Operando ATR-SEIRAS 揭示 *CO 中间体的表面富集",
        figure_path="figures/SEIRAS.png",
        figure_label="Figure 4",
        bullets=[
            "Ru₁/Cu 表面的 *COₐₜₒₚ 峰面积是纯 Cu 的 2.3 倍",
            "出现低频 *CO 峰 (~1880 cm⁻¹)，归属于 Ru 位点上桥式吸附的 *CO",
            "*CO 覆盖度增加促进 C-C 偶联：邻近 *CO 距离缩短",
            "无 *CHO/*COH 信号，排除了卡宾/类卡宾路径"
        ],
        caption="Source: Fig. 4a-d, adapted from original paper",
        layout="figure_right"
    )

    ppt.add_figure_slide(
        title="DFT 揭示 Ru 位点促进 *CO 富集并降低 C-C 偶联能垒",
        figure_path="figures/DFT_mechanism.png",
        figure_label="Figure 5",
        bullets=[
            "*CO 在 Ru 位点的吸附能 (-1.32 eV) 显著强于 Cu (-0.87 eV)",
            "Ru 位点捕获的 *CO 与邻近 Cu 位点上的 *CO 发生 C-C 偶联，能垒仅 0.45 eV",
            "Bader charge 分析：Ru→Cu 的电荷转移增强 *CO 的 π 反馈键",
            "PDOS 分析：Ru 的 d-band center (-1.85 eV) 比 Cu (-2.45 eV) 更接近 Fermi 能级"
        ],
        caption="Source: Fig. 5a-f, adapted from original paper",
        layout="figure_right"
    )

    # 总结
    ppt.add_section_slide("总结与展望")

    ppt.add_summary_slide(
        title="全文总结",
        bullets=[
            "1. 成功制备 Ru₁/Cu 单原子合金催化剂，实现 CO₂RR 到 C₂₊ 的 FE 82%，j = 300 mA/cm²",
            "2. HAADF-STEM + XAS 确证 Ru 的单原子分散状态和 Ruᵟ⁺ 氧化态",
            "3. Operando SEIRAS + DFT 联合揭示 Ru 位点促进 *CO 富集和 C-C 偶联的协同机制",
            "4. 该 SAA 设计策略为高选择性 CO₂RR 电催化剂提供了新的设计范式"
        ]
    )

    ppt.add_thankyou_slide()

    ppt.save("output/example_experimental.pptx")
    print("Example 1 saved: output/example_experimental.pptx")


# ================================================================
# 示例 2: 理论计算化学论文 — DFT 计算类
# Example 2: Computational Chemistry — DFT Paper
# ================================================================

def example_computational_dft():
    ppt = ChemistryPPT(theme="molecular")

    ppt.add_title_slide(
        title_cn="第一性原理筛选过渡金属单原子催化剂用于电催化氮还原",
        title_en="First-Principles Screening of Transition Metal Single-Atom Catalysts for Electrocatalytic Nitrogen Reduction",
        authors="Wang, Y. et al.",
        journal="ACS Catal., 2024, 14, 5678-5690",
        doi="10.1021/acscatal.4c00567"
    )

    ppt.add_section_slide("研究背景与计算方法")

    ppt.add_content_slide(
        title="电催化 NRR 面临的挑战",
        bullets=[
            "NRR 是实现常温常压合成氨的理想替代路径，但 FE 和产率远低于 Haber-Bosch 法",
            "竞争反应 HER 在 NRR 电位区间热力学更有利，严重抑制 NH₃ 选择性",
            "单原子催化剂（SACs）因独特的电子结构和最大原子效率成为 NRR 研究热点",
            "关键问题：如何理性筛选和设计高活性、高选择性的 NRR SAC？"
        ]
    )

    ppt.add_content_slide(
        title="计算方法与模型",
        bullets=[
            "软件：VASP 6.3，PAW 赝势，PBE 泛函 + DFT-D3(BJ) 范德华校正",
            "截断能 520 eV, k-point: 3×3×1 (slab 模型), 真空层 20 Å",
            "模型：4×4 石墨烯超胞 (含 N₄ 空位缺陷) + 单原子 TM (TM = Sc-Zn, Mo, Ru, Rh, Pd, Ag, W, Pt, Au)",
            "自由能计算：CHE 模型 (Computational Hydrogen Electrode)",
            "溶剂化效应：VASPsol 隐式溶剂模型 (ε = 78.4 for H₂O)",
            "过渡态搜索：CI-NEB 方法 + dimer method 验证"
        ]
    )

    ppt.add_section_slide("关键计算结果")

    ppt.add_figure_slide(
        title="NRR 自由能图揭示 Mo-N₄/C 具有最优的决速步能垒",
        figure_path="figures/free_energy.png",
        figure_label="Figure 3",
        bullets=[
            "Mo-N₄/C 的 PDS（*NH₂ → *NH₃）自由能变化仅 +0.35 eV",
            "ΔG(*N₂ → *N₂H) = +0.28 eV，表明第一步质子化可自发进行",
            "对比：Fe-N₄/C 的 PDS 能垒为 +0.89 eV, Co-N₄/C 为 +0.72 eV",
            "Mo-N₄/C 遵循 alternating 路径, 远端路径（distal）能垒更高"
        ],
        caption="Source: Fig. 3a-d, adapted from original paper",
        layout="figure_right"
    )

    ppt.add_figure_slide(
        title="PDOS 分析揭示 Mo 的 d 轨道与 N₂ 的 π* 轨道杂化机制",
        figure_path="figures/PDOS.png",
        figure_label="Figure 4",
        bullets=[
            "Mo 的 d₂² 轨道与 N₂ 的 2π* 轨道在 -0.5 to +0.5 eV 区间显著杂化",
            "Bader charge: Mo 向 N₂ 转移 0.62 e⁻，活化 N≡N 键",
            "N≡N 键长从气相的 1.10 Å 伸长至吸附态的 1.18 Å",
            "COHP 分析：N≡N 的 ICOHP 从 -21.3 降至 -17.8 eV，键级削弱"
        ],
        caption="Source: Fig. 4a-e, adapted from original paper",
        layout="figure_right"
    )

    ppt.add_figure_slide(
        title="NRR vs HER 选择性描述符：ΔG(*N₂H) vs ΔG(*H)",
        figure_path="figures/selectivity.png",
        figure_label="Figure 5",
        bullets=[
            "构建 ΔG(*N₂H) vs ΔG(*H) 选择性图，筛选同时满足强 N₂ 吸附和弱 H 吸附的催化剂",
            "Mo-N₄/C 位于最优区域：ΔG(*N₂H) < -0.5 eV 且 ΔG(*H) > +0.3 eV",
            "Cr, W, Re 也是潜在的 NRR 候选催化剂的候选",
            "Ag, Au, Cu 位于 HER 主导区（ΔG(*H) < 0），不适合 NRR"
        ],
        caption="Source: Fig. 5a-c, adapted from original paper",
        layout="figure_right"
    )

    ppt.add_content_slide(
        title="微动力学模拟验证 DFT 预测",
        bullets=[
            "基于 DFT 计算的所有基元步能垒进行微动力学模拟 (CatMAP)",
            "Mo-N₄/C 的理论 TOF 为 2.1×10⁻³ s⁻¹ site⁻¹ (300 K, pH=7)",
            "NH₃ 理论产率 ~5.2×10⁻¹¹ mol s⁻¹ cm⁻² at -0.3 V vs RHE",
            "理论 FE(NH₃) = 72%，与实验结果 (FE=65%, 文献值) 定性一致"
        ]
    )

    ppt.add_section_slide("总结与展望")

    ppt.add_summary_slide(
        title="全文总结",
        bullets=[
            "1. 高通量 DFT 筛选了 20 种 TM-N₄/C SAC 的 NRR 催化活性",
            "2. Mo-N₄/C 的理论过电位最低 (0.35 V)，归因于 Mo 的 d 轨道与 N₂ 的 2π* 轨道杂化",
            "3. 建立了 ΔG(*N₂H) vs ΔG(*H) 选择性描述符，可快速筛选 NRR 催化剂",
            "4. 微动力学模拟与实验趋势一致，验证了计算预测的可靠性"
        ]
    )

    ppt.add_thankyou_slide()

    ppt.save("output/example_computational.pptx")
    print("Example 2 saved: output/example_computational.pptx")


# ================================================================
# 示例 3: 实验+理论混合论文
# Example 3: Experimental + Computational Hybrid Paper
# ================================================================

def example_hybrid():
    ppt = ChemistryPPT(theme="green")

    ppt.add_title_slide(
        title_cn="单原子 Fe-N/C 催化剂的活性位点辨识与氧还原反应机理",
        title_en="Identification of Active Sites and Mechanism of Oxygen Reduction Reaction on Single-Atom Fe-N/C Catalysts",
        authors="Chen, X. et al.",
        journal="Nat. Catal., 2024, 7, 234-245",
        doi="10.1038/s41929-024-01012-3"
    )

    ppt.add_section_slide("研究背景与策略")

    ppt.add_content_slide(
        title="Fe-N/C ORR 催化剂的活性位点争议",
        bullets=[
            "Fe-N/C 是最有希望替代 Pt/C 的非贵金属 ORR 催化剂",
            "活性位点长期存在争议：Fe-N₄ (吡咯型 vs 吡啶型)、Fe-N₂O₂、Fe 纳米颗粒？",
            "不同前驱体和热解条件可能导致不同的位点分布，难以单独通过实验分辨",
            "本文策略：XAS + Mössbauer 实验确定位点结构 → DFT 计算验证活性 → 实验-理论互验"
        ]
    )

    ppt.add_section_slide("实验结果")

    ppt.add_figure_slide(
        title="Fe K-edge XAS 确认 Fe-N₄ 平面四方配位结构",
        figure_path="figures/Fe_XAS.png",
        figure_label="Figure 2",
        bullets=[
            "XANES：Fe K-edge 吸收边位置确认 Fe 以 +2/+3 混合价态存在",
            "EXAFS 拟合：第一壳层 Fe-N ~1.98 Å (CN=4.1)，无 Fe-Fe (~2.50 Å)",
            "WT-EXAFS：排除了 Fe 纳米颗粒和 Fe₂O₃ 的存在",
            "Mössbauer 谱：D1 (Fe²⁺-N₄, LS) 和 D2 (Fe³⁺-N₄, HS) 双峰"
        ],
        caption="Source: Fig. 2a-f, adapted from original paper",
        layout="figure_right"
    )

    ppt.add_figure_slide(
        title="ORR 性能：Fe-N/C 在酸性介质中半波电位达 0.82 V vs RHE",
        figure_path="figures/ORR_performance.png",
        figure_label="Figure 3",
        bullets=[
            "E₁/₂ = 0.82 V vs RHE (0.1M HClO₄)，与 Pt/C (0.85 V) 仅差 30 mV",
            "Tafel 斜率 58 mV/dec，表明第一个电子转移是决速步",
            "H₂O₂ 产率 < 1%，电子转移数 n ≈ 3.95，接近完全 4e⁻ 路径",
            "加速老化测试 (0.6-1.0 V, 10k 圈) 后 E₁/₂ 仅衰减 15 mV"
        ],
        caption="Source: Fig. 3a-e, adapted from original paper",
        layout="figure_right"
    )

    ppt.add_section_slide("DFT 计算：活性位点与机理")

    ppt.add_content_slide(
        title="DFT 计算模型与方法",
        bullets=[
            "VASP 6.3, PBE+U (Ueff=4.0 eV for Fe 3d), PAW 赝势, 截断能 500 eV",
            "模型：6×6 石墨烯超胞，分别构建 Fe-N₄-C₁₀ (吡咯型), Fe-N₄-C₁₂ (吡啶型), Fe-N₂O₂-C₁₀",
            "隐式溶剂化 (VASPsol, ε=78.4) 模拟酸性电解质环境",
            "ORR 自由能计算：4e⁻ 缔合路径 (O₂ → *OOH → *O → *OH → H₂O)"
        ]
    )

    ppt.add_figure_slide(
        title="DFT 自由能图：Fe-N₄ (吡咯型) 的 ORR 过电位最低",
        figure_path="figures/DFT_ORR.png",
        figure_label="Figure 5",
        bullets=[
            "Fe-N₄-C₁₀ (吡咯型): 理论过电位 η = 0.38 V，与实验值 η = 0.41 V 一致",
            "Fe-N₄-C₁₂ (吡啶型): η = 0.58 V，活性显著低于吡咯型",
            "Fe-N₂O₂: η = 0.92 V，几乎无 ORR 活性",
            "决速步：*OH → H₂O（吡咯型，ΔG = 1.61 eV）"
        ],
        caption="Source: Fig. 5a-d, adapted from original paper",
        layout="figure_right"
    )

    ppt.add_content_slide(
        title="实验-理论互验：活性位点为吡咯型 Fe-N₄",
        bullets=[
            "EXAFS 获得的 Fe-N 键长 (1.98 Å) 与 DFT 优化的吡咯型 Fe-N₄ (1.97 Å) 一致",
            "XANES 模拟谱：吡咯型 Fe-N₄ 的模拟 XANES 与实验谱吻合最佳",
            "理论过电位 (0.38 V) 与实验值 (0.41 V) 高度吻合",
            "CO 毒化实验 + DFT 的 CO 吸附能计算均表明 Fe 为活性中心"
        ]
    )

    ppt.add_section_slide("总结与展望")

    ppt.add_summary_slide(
        title="全文总结",
        bullets=[
            "1. XAS + Mössbauer 联合确证 Fe-N/C 的活性位点为吡咯型 Fe-N₄ 结构",
            "2. DFT 计算揭示吡咯型 Fe-N₄ 的 ORR 过电位 (0.38 V) 远低于吡啶型和 Fe-N₂O₂",
            "3. 实验-理论互验：键长、XANES 谱、过电位三方面高度一致",
            "4. 为理性设计高性能单原子 ORR 催化剂提供了明确的位点结构指导"
        ]
    )

    ppt.add_thankyou_slide()

    ppt.save("output/example_hybrid.pptx")
    print("Example 3 saved: output/example_hybrid.pptx")


# ================================================================
# 运行所有示例
# ================================================================

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)

    print("=" * 60)
    print("PDF2PPT — Chemistry Academic PPT Examples")
    print("=" * 60)

    print("\n[1/3] Experimental Catalysis Example...")
    example_experimental_catalysis()

    print("\n[2/3] Computational DFT Example...")
    example_computational_dft()

    print("\n[3/3] Hybrid Paper Example...")
    example_hybrid()

    print("\n" + "=" * 60)
    print("All examples generated successfully in output/")
    print("=" * 60)
