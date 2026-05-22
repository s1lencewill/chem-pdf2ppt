# chem-pdf2ppt — Chemistry Academic Paper → Presentation Converter

[![npm version](https://img.shields.io/npm/v/chem-pdf2ppt)](https://www.npmjs.com/package/chem-pdf2ppt)
[![npm downloads](https://img.shields.io/npm/dm/chem-pdf2ppt)](https://www.npmjs.com/package/chem-pdf2ppt)
[![license](https://img.shields.io/npm/l/chem-pdf2ppt)](https://github.com/s1lencewill/PDF2PPT/blob/main/LICENSE)
[![github stars](https://img.shields.io/github/stars/s1lencewill/PDF2PPT?style=social)](https://github.com/s1lencewill/PDF2PPT)

Convert chemistry academic paper PDFs into professional presentations for group meetings, defenses, and academic reports. Supports both **PPTX** and **HTML** output formats.

## Key Features

- **Automatic paper type recognition**: Experimental / Computational / Hybrid chemistry — auto-matched narrative structure
- **Dual output formats**: PPTX (python-pptx) and single-file HTML (horizontal-slide, base64-embedded figures)
- **Deep chemistry domain support**: Catalysis, materials, organic synthesis, computational chemistry, electrochemistry, energy, environmental, radiation chemistry, and more
- **Intelligent content generation**: Extracts real information from papers — no "please fill in XX" placeholder content
- **Multi-strategy figure extraction**: Vector clustering + embedded images + page rendering fallback, compatible with PyMuPDF 1.19–1.23+
- **Error tracking & reporting**: Full-chain JSON reports (analysis → extraction → build), Windows encoding-safe
- **4 academic color themes**: Academic Classic / Molecular Tech / Green Chemistry / Nature Style
- **7 slide types**: Title, section divider, content, figure (4 layouts), data table, summary, thank you

---

## Installation

```bash
pip install -r requirements.txt
```

**Dependencies**: `pymupdf>=1.19.0` · `python-pptx>=0.6.23` · `pdfplumber>=0.10.0` · `Pillow>=10.0.0`

`pdf2image` is optional (requires system Poppler installation).

---

## Quick Start

### Complete Workflow

```bash
# Step 1: Analyze paper type and structure
python scripts/analyze_paper.py paper.pdf --json analysis.json

# Step 2: Extract figures (multi-strategy + auto-fallback)
python scripts/extract_charts.py paper.pdf output/figures 300 --report

# Step 3: Build PPTX or HTML
python build_my_ppt.py
```

### PPTX Format

```python
import sys
sys.path.insert(0, 'scripts')
from create_ppt import ChemistryPPT

ppt = ChemistryPPT(theme='academic')

ppt.add_title_slide(
    title_cn='Ru₁/Cu Single-Atom Alloy for Efficient CO₂ Electroreduction',
    title_en='Single-Atom Ru Alloyed with Cu for Efficient CO₂RR',
    authors='Zhang, L. et al.',
    journal='J. Am. Chem. Soc., 2024, 146, 12345',
    doi='10.1021/jacs.4c01234'
)

ppt.add_section_slide('Background')
ppt.add_content_slide(
    title='Core Challenge in Electrocatalytic CO₂ Reduction',
    bullets=[
        'CO₂RR produces diverse products — selectivity control is difficult',
        'Cu-based catalysts achieve C₂₊ FE typically < 50%',
        'Key bottleneck: conflicting demands on *CO binding and C-C coupling'
    ]
)
ppt.add_figure_slide(
    title='HAADF-STEM Confirms Single-Atom Ru Dispersion',
    figure_path='figures/p3_fig1.png',
    bullets=['Bright dots uniformly dispersed — no clusters', 'EDS mapping confirms uniformity'],
    figure_label='Figure 1',
    layout='figure_right'
)
ppt.add_table_slide(
    title='Performance Comparison',
    headers=['Catalyst', 'FE(C₂₊)%', 'j (mA/cm²)', 'Stability (h)'],
    rows=[['Ru₁/Cu', '82%', '300', '100'], ['Cu NPs', '45%', '150', '20']]
)
ppt.add_summary_slide(
    title='Summary',
    bullets=['Finding 1', 'Finding 2', 'Finding 3']
)
ppt.add_thankyou_slide()

ppt.save('output/presentation.pptx')
ppt.save_report('output/presentation.pptx')  # JSON build report
```

### HTML Format

```python
import sys
sys.path.insert(0, 'scripts')
from generate_html import HtmlPPT

html = HtmlPPT(title="Academic Report", theme="molecular")

# API is identical to ChemistryPPT
html.add_title_slide("Title", title_en="Title EN", authors="...", journal="...")
html.add_section_slide("Part 1")
html.add_content_slide("Key Point", ["bullet 1", "bullet 2"])
html.add_figure_slide("Figure", figure_path="figures/fig1.png",
                       bullets=["description"], figure_label="Figure 1",
                       layout="figure_right")
html.add_summary_slide("Summary", ["finding 1", "finding 2"])
html.add_thankyou_slide()

html.save('output/presentation.html')  # Single file, open directly in browser
```

**HTML features**:
- Figures embedded as base64 — single file, zero dependencies
- Horizontal navigation: keyboard ← → Home End, scroll wheel, touch swipe, dot navigation
- Page counter + keyboard hints
- Responsive design for projectors and mobile

---

## Color Themes

| Theme | PPTX param | HTML param | Best for |
|-------|-----------|------------|----------|
| Academic Classic | `theme="academic"` | `theme="academic"` | General chemistry (default) |
| Molecular Tech | `theme="molecular"` | `theme="molecular"` | Computational/materials |
| Green Chemistry | `theme="green"` | `theme="green"` | Catalysis/energy/environment |
| Nature Style | `theme="nature"` | `theme="nature"` | CNS journal presentations |

---

## Slide Types

| Method | PPTX | HTML | Purpose |
|--------|------|------|---------|
| `add_title_slide()` | ✓ | ✓ | Cover: bilingual title, authors, journal, DOI |
| `add_section_slide()` | ✓ | ✓ | Section divider (dark background) |
| `add_content_slide()` | ✓ | ✓ | Text content: title + bullets + notes |
| `add_figure_slide()` | ✓ | ✓ | Figure + explanation (4 layouts: right/top/left/full) |
| `add_table_slide()` | ✓ | ✓ | Data comparison table (striped rows, colored header) |
| `add_image_grid_slide()` | ✓ | — | Multi-image grid |
| `add_summary_slide()` | ✓ | ✓ | Summary (light background) |
| `add_thankyou_slide()` | ✓ | ✓ | Thank you / Q&A |

---

## Figure Extraction: Multi-Strategy + Version Compatibility

```
Strategy 1: cluster_drawings() default tolerance (3,3)
   ↓ < 3 results
Strategy 2: Multi-tolerance retry (6,6) → (10,10) → (15,15) → (20,20)
   ↓
Strategy 3: Extract embedded bitmaps (get_images)
   ↓ < 3 results
Strategy 4: Full-page rendering fallback for figure pages
```

- Compatible with PyMuPDF 1.19+ (`get_drawings` manual clustering) and 1.23+ (`cluster_drawings`)
- `--report` outputs `extraction_report.json` (per-strategy details)

---

## Error Handling & Reports

Full-chain JSON reports for workflow automation and diagnostics:

| Stage | Report File | Generated By |
|-------|------------|--------------|
| Paper analysis | `analysis.json` | `analyze_paper.py --json analysis.json` |
| Figure extraction | `extraction_report.json` | `extract_charts.py --report` |
| PPTX build | `presentation_report.json` | `ppt.save_report("output.pptx")` |

**Windows encoding safety**: All scripts use `_safe_print()` to prevent GBK encoding crashes.

**Common issue diagnostics**:

| Symptom | Likely Cause | Script Behavior |
|---------|-------------|-----------------|
| 0 vector figures extracted | PyMuPDF < 1.23 or special PDF rendering | Auto-fallback to `get_drawings` manual clustering |
| Still too few figures total | All bitmaps | Strategy 3 auto-covers |
| Windows `print` crash | Unicode chars (e.g. − ₂) | `_safe_print` fallback to ASCII |
| Paper type misclassified | Characterization terms in references | Weighted detection + confidence annotation |
| Images missing in PPT | Non-existent file paths | Recorded in `missing_images`, build continues |

---

## Paper Type Adaptations

| Experimental Chemistry | Computational Chemistry | Experimental + Theoretical |
|------------------------|------------------------|---------------------------|
| Synthesis → Characterization → Performance → Mechanism | Method → Model → Electronic Structure → Energetics → Mechanism | Experiment → Computation → Cross-Validation → Unified Mechanism |
| Catalysis / Materials / Organic / Energy | DFT / MM / AIMD / Electronic Structure | Experiment + DFT joint studies |

Detailed templates in `references/chemistry_templates.md`.

---

## File Structure

```
PDF2PPT/
├── SKILL.md                         # Skill main file (Chinese)
├── SKILL_EN.md                      # Skill main file (English)
├── README.md                        # This file (Chinese)
├── README_EN.md                     # This file (English)
├── requirements.txt
├── assets/
│   └── academic_template.html       # HTML PPT template (CSS + navigation JS)
├── scripts/
│   ├── create_ppt.py                # PPTX builder (ChemistryPPT)
│   ├── generate_html.py             # HTML builder (HtmlPPT)
│   ├── extract_charts.py            # Multi-strategy figure extraction
│   ├── analyze_paper.py             # Paper analysis + type classification
│   └── convert_to_images.py         # PDF page → image conversion
├── references/
│   ├── chemistry_templates.md       # Slide-by-slide templates for 3 paper types
│   ├── chemistry_templates_en.md    # (English version)
│   ├── visual_style.md              # Academic PPT visual design spec
│   └── visual_style_en.md           # (English version)
└── examples/
    └── example_usage.py             # Complete examples for 3 chemistry paper types
```

---

## Compatibility

- **OS**: macOS / Linux / Windows
- **Python**: 3.8+
- **PyMuPDF**: 1.19+ (auto-detects and adapts API)
- **Environment**: Claude Code / Claude Desktop / Cursor / VS Code / any Python environment
- **HTML output**: Any modern browser (Chrome / Firefox / Edge / Safari)

## License

MIT License
