---
name: pdf-to-ppt
description: Convert chemistry (experimental or theoretical/computational) academic paper PDFs into professional academic PowerPoint presentations. Automatically identifies paper type (experimental/theoretical/hybrid), extracts key information, and generates structured PPTX files ready for group meetings, defenses, and academic reports. Trigger when the user mentions "paper to PPT", "PDF to PPT", "group meeting slides", "journal club", "academic presentation", "chemistry paper PPT", or provides a chemistry-related PDF/arXiv paper asking for presentation generation.
---

# PDF → Chemistry Academic PPT Generator

Convert chemistry academic paper PDFs into professional, ready-to-use academic PowerPoint presentations.

## Core Principles

**Let the paper's scientific argument drive the PPT structure, not a fixed template.**

Chemistry papers fall into two primary paradigms with fundamentally different narrative logic:

- **Experimental Chemistry**: Problem → Design Strategy → Synthesis/Preparation → Characterization → Performance → Mechanism → Conclusions
- **Theoretical/Computational Chemistry**: Problem → Methods → Model Validation → Electronic Structure/Energy Analysis → Mechanism → Experimental Comparison → Conclusions
- **Experimental + Theoretical Hybrid**: Problem → Experimental Part → Computational Part → Cross-Validation → Unified Mechanism → Conclusions

The generated PPT should guide the audience through:
1. Why is this chemistry problem important?
2. What has been achieved, what is the bottleneck?
3. What is the design strategy / computational approach?
4. What is the key experimental evidence / computational result?
5. Is the mechanistic explanation self-consistent?
6. What new understanding has been gained? Is it generalizable?
7. What are the limitations and open questions?

## Input Formats

Any of the following are accepted:
- Full paper PDF
- arXiv / chemRxiv preprint PDF
- Abstract + figures + results text
- Structured reading notes
- User-pasted paper content

Default output language is Chinese; preserve key chemical terminology, abbreviations, compound names, and method names in English. For fully English output, pass `--lang en` when calling analysis scripts.

## Script Import Convention

All Python scripts are in `<SKILL_ROOT>/scripts/`. Use the following once before any script import:

```python
import sys, os
_scripts_dir = os.path.join('<SKILL_ROOT>', 'scripts')
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)
```

## Workflow

### Step 0: Install Dependencies (first use)

```bash
pip install -r <SKILL_ROOT>/requirements.txt
```

### Step 1: Read and Understand the Paper

**First, determine the input format and choose the appropriate path:**

| Input | Path |
|-------|------|
| PDF file (local / arXiv / chemRxiv) | → Step 1A: PyMuPDF structured analysis |
| Abstract + figures + text snippets | → Skip Steps 1A–3, go directly to Step 4 |
| User-pasted full-text | → Skip PDF extraction; use `is_chemistry_domain()` then go to Step 4 |
| Structured reading notes | → Map directly to PPT structure in Steps 4–5 |

#### Step 1A: PDF Input — Structured Analysis

Use `scripts/analyze_paper.py` for full paper analysis:

```bash
python <SKILL_ROOT>/scripts/analyze_paper.py paper.pdf --json analysis.json
```

The script automatically performs:
- Full-text extraction
- Title / section structure detection
- **Domain detection**: returns an `is_chemistry` field. If `false`, the paper may not be in the chemistry domain — **inform the user**: "Few chemistry signals detected; results may be inaccurate. Continue anyway?" Wait for confirmation before proceeding
- **Paper chemistry type classification**: Experimental / Computational / Hybrid (with confidence annotation)
- **Subfield identification**: catalysis / materials / organic synthesis / computational chemistry / electrochemistry / spectroscopy / environmental / energy / radiation chemistry
- Figure/table location detection (via caption text)
- Method extraction (DFT functional, software packages, experimental techniques)

The following information should be manually identified from the text:
- **Core chemistry problem and research gap**
- **Core claim/hypothesis**
- **Key results**: performance data, characterization conclusions, energy data, TOF, stability
- **Mechanism / structure-property relationships**
- **Innovations and limitations**

**Important**: Do not fabricate data, mechanisms, or figure details not present in the paper. Mark uncertain information as "[TBD]".

#### Step 1B: Non-PDF Input — Domain Check

For pasted text or reading notes, call `is_chemistry_domain()` for a quick check:

```python
from analyze_paper import is_chemistry_domain
if not is_chemistry_domain(user_text):
    # Inform user, wait for confirmation, then continue
    print("Few chemistry domain signals detected...")
```

#### Customizing Keywords

To adapt for new subfields or adjust keyword weights, edit `references/chemistry_keywords.json`:

```json
{
  "subfields": {
    "photochemistry": {
      "en": "photochemistry",
      "keywords": ["photoredox", "photoinduced", "visible light", ...]
    }
  },
  "computational_strong_signals": ["DFT", "VASP", ...],
  "characterization_terms": ["XRD", "XPS", ...],
  "method_patterns": [["regex", weight], ...],
  "section_patterns": [["regex", "label"], ...]
}
```

Modifications take effect immediately — no code changes needed.

### Step 2: Classify Paper Type and Select Narrative Arc

#### Type A: Experimental Chemistry
**Signals**: synthesis steps, wet chemistry methods, materials preparation, catalyst testing, characterization data (XRD/TEM/SEM/XPS), performance metrics (conversion/selectivity/yield/stability)

**Narrative arc** (question-to-evidence):
1. Chemical problem and significance
2. Prior strategy limitations → This work's design rationale
3. Synthesis/preparation route
4. Structure and composition characterization
5. Catalytic/performance evaluation
6. Mechanistic investigation (in-situ characterization, control experiments, kinetics)
7. Structure-activity relationships
8. Conclusions and outlook

**PPT structure** (12–16 slides):
```
Slide 1:  Title
Slide 2:  Background & chemical problem
Slide 3:  Prior work & bottlenecks
Slide 4:  Design strategy
Slide 5:  Synthesis/preparation route
Slide 6:  Structure & composition (XRD/TEM/XPS...)
Slide 7:  Morphology & microstructure (SEM/TEM/HRTEM...)
Slide 8:  Performance evaluation
Slide 9:  Key control experiments or comparison table
Slide 10: Mechanism (in-situ / kinetics / poisoning...)
Slide 11: Structure-activity / active site discussion
Slide 12: Benchmark comparison
Slide 13: Summary & innovations
Slide 14: Limitations & outlook
```

#### Type B: Theoretical/Computational Chemistry
**Signals**: DFT calculations, molecular dynamics, Monte Carlo, electronic structure, reaction path search, free energy calculations, software names (VASP/Gaussian/CP2K/QE/GROMACS), k-point/cutoff energy

**Narrative arc** (method-to-mechanism):
1. Chemical problem and need for computation
2. Limitations of prior computational studies
3. Computational methods and model systems
4. Method validation / benchmarking
5. Electronic structure / adsorption / reaction intermediates
6. Energy profiles and reaction pathways
7. Selectivity origins / rate-determining step analysis
8. Comparison with experiment (if available)
9. Conclusions and outlook

**PPT structure** (12–16 slides):
```
Slide 1:  Title
Slide 2:  Background & chemical problem
Slide 3:  Prior computational studies
Slide 4:  Computational methods & models
Slide 5:  Method validation / benchmarking
Slide 6:  Key intermediate / transition state structures
Slide 7:  Energy profiles / free energy diagrams
Slide 8:  Electronic structure analysis (PDOS/Bader/COHP...)
Slide 9:  Selectivity analysis
Slide 10: Microkinetics / volcano plot (if applicable)
Slide 11: Comparison with experiment (if applicable)
Slide 12: Summary & innovations
Slide 13: Limitations & outlook
```

#### Type C: Experimental + Theoretical Hybrid
**Narrative arc** (experiment-theory-unified):
1. Chemical problem and joint strategy
2. Experimental: synthesis + characterization + performance
3. Computational: model + method + results
4. Experiment-theory cross-validation
5. Unified mechanistic model
6. Conclusions

**PPT structure** (14–18 slides):
```
Slide 1:  Title
Slide 2:  Background & chemical problem
Slide 3:  Research strategy (experimental + computational)
Slide 4:  Experimental: synthesis & characterization
Slide 5:  Experimental: performance / catalytic results
Slide 6:  Experimental: key characterization evidence
Slide 7:  Computational: methods & models
Slide 8:  Computational: energetics & electronic structure
Slide 9:  Computational: reaction pathways / mechanism
Slide 10: Experiment-theory cross-validation
Slide 11: Unified mechanism model
Slide 12: Summary & outlook
```

### Step 3: Obtain Figures (Multi-Pathway)

Figures are the core of the PPT. Try paths in priority order; later paths serve as fallback when earlier ones fail.

#### Path A: Local PDF Extraction (preferred, most automated)

```bash
python <SKILL_ROOT>/scripts/extract_charts.py paper.pdf output/figures 300 --report
```

**5-layer extraction strategy** (newly enhanced):

| Strategy | Method | Confidence |
|----------|--------|------------|
| 0. Caption-guided | Search "Figure X" captions → locate region above caption → precise crop | **High** |
| 1. Vector clustering | `cluster_drawings()` default tolerance (3,3) | Medium |
| 2. Multi-tolerance retry | Relax to (6,6)→(10,10)→(15,15)→(20,20) | Medium |
| 3. Embedded bitmaps | `get_images()` extract JPEG/PNG | Low (limited resolution) |
| 4. Page render fallback | Full page at 300 DPI | Lowest (manual crop needed) |

Strategy 0 is the key new enhancement — it uses figure caption positions to reverse-locate the actual figure region, dramatically reducing noise from decorative line elements. The `--report` flag generates `extraction_report.json` with per-strategy results and confidence scores.

Check `output/figures/` and map files to paper Figure numbers using the `fig{N}` numbering in filenames.

#### Path B: DOI → arXiv Source (high-res originals)

If the paper has an arXiv version, the source `.tar.gz` contains the authors' original high-resolution figures (PDF/EPS/PNG), typically far better quality than PDF-extracted images:

```bash
# Resolve DOI to get arXiv ID and metadata
python <SKILL_ROOT>/scripts/fetch_from_doi.py 10.1021/jacs.4c01234 --output output/

# If arXiv source detected, download and extract figures automatically
python <SKILL_ROOT>/scripts/fetch_from_doi.py 10.1021/jacs.4c01234 --download-arxiv --output output/
```

`fetch_from_doi.py` will:
1. Query the Semantic Scholar API (free, no API key) to resolve DOI → paper metadata
2. Detect arXiv ID and Open Access PDF links
3. With `--download-arxiv`, download the arXiv source tarball and auto-extract figures

#### Path C: MCP Tools for Remote Download (when no local PDF)

When the user only provides a DOI or paper link without a local PDF file, use MCP tools:

```
mcp__ai4scholar__download_semantic  — Download paper PDF from Semantic Scholar
mcp__ai4scholar__download_arxiv     — Download paper PDF from arXiv
mcp__ai4scholar__read_semantic_paper — Extract full text (including figure captions)
```

After obtaining the PDF, return to Path A for figure extraction. MCP tools are best for:
- User only has a DOI, no local file
- Publisher PDF has compressed figures — try Semantic Scholar's open-access version
- arXiv preprints often have better quality than paywalled publisher versions

#### Path D: User Manual Provision (last resort)

If all above paths fail, ask the user:
- "Please provide the key figure files (Figure 1, Figure 2...)"
- User can screenshot from publisher website or extract from Supporting Information

**Figure selection principles**:
- Select only figures that support the paper's argument (typically 4–8)
- Priority: strategy/scheme diagram → core results → mechanism → validation/controls
- Fewer, clearer figures are better than many crowded ones
- For dense multi-panel figures, consider cropping to the 1–2 most critical panels

### Step 4: Write Slide-by-Slide Content

For each slide, prepare:
- **Title** (conclusion-style: "Ru SAs achieve 98% CO conversion at 300°C" not just "Catalytic Performance")
- **3–4 bullet points** (concise)
- **Associated figure** (Figure number and file path)
- **Figure caption** (short interpretation)
- **One core takeaway**
- **Speaker notes** (optional oral commentary)

Each slide should convey ONE core message. Result slides should prioritize figures — let the data speak.

### Step 5: Build PPTX

Use `scripts/create_ppt.py`:

```python
from create_ppt import ChemistryPPT

ppt = ChemistryPPT(theme="academic")  # "academic" | "molecular" | "green" | "nature"

ppt.add_title_slide(
    title_cn="中文标题",
    title_en="English Title",
    authors="Authors et al.",
    journal="J. Am. Chem. Soc., 2024, 146, xxx",
    doi="10.xxxx/xxxx"
)

ppt.add_section_slide("Part 1: Research Background")

ppt.add_content_slide(
    title="Core Challenge in Electrocatalytic CO₂ Reduction",
    bullets=[
        "CO₂RR produces a wide range of products (CO, HCOOH, CH₄, C₂H₄, EtOH...) — selectivity control is difficult",
        "Cu-based catalysts are the only metals capable of C₂₊ products, but FE is typically < 50%",
        "Key bottleneck: simultaneous optimization of *CO binding energy and C-C coupling kinetics"
    ],
    notes="Emphasize the uniqueness of Cu and the selectivity challenge"
)

ppt.add_figure_slide(
    title="HAADF-STEM Confirms Single-Atom Ru Dispersion on Cu Surface",
    figure_path="output/figures/p3_fig1.png",
    figure_label="Figure 1",
    bullets=[
        "HAADF-STEM shows Ru atoms (bright dots) uniformly dispersed — no NPs or clusters",
        "EDS elemental mapping confirms uniform Ru distribution on Cu matrix",
        "XANES indicates Ruᵟ⁺ oxidation state (0 < δ < 3)"
    ],
    caption="Source: Fig. 1a-c, adapted from original paper",
    layout="figure_right"  # "figure_right" | "figure_top" | "figure_full"
)

ppt.add_table_slide(
    title="Catalytic Performance Comparison",
    headers=["Catalyst", "FE(C₂₊)%", "j (mA/cm²)", "Stability (h)", "Ref"],
    rows=[
        ["Ru₁/Cu", "82%", "300", "100", "This work"],
        ["Cu NPs", "45%", "150", "20", "Nat. Catal. 2020"],
        ["Ag/Cu", "60%", "200", "50", "JACS 2022"],
    ]
)

ppt.add_summary_slide(
    title="Summary & Outlook",
    bullets=[
        "First demonstration of Ru SAC alloy for highly selective CO₂-to-C₂₊ conversion (FE 82%)",
        "Operando XAS + DFT reveal Ru sites promote *CO enrichment and C-C coupling",
        "Design strategy extensible to other SAC systems (Pt/Cu, Pd/Cu)",
        "Future: MEA testing under practical conditions"
    ]
)

ppt.save("output/presentation.pptx")
ppt.save_report("output/presentation.pptx")  # JSON build report
```

**Slide type reference**:

| Method | Purpose |
|--------|---------|
| `add_title_slide()` | Cover: bilingual title, authors, journal info |
| `add_section_slide()` | Section divider |
| `add_content_slide()` | Text content with bullets and optional subtitle |
| `add_figure_slide()` | Figure + explanation (4 layout options) |
| `add_table_slide()` | Data comparison table |
| `add_summary_slide()` | Summary/conclusions |
| `add_thankyou_slide()` | Thank you / Q&A |

### Step 6: (Optional) Generate HTML Version

In addition to PPTX, generate a single-file HTML presentation with embedded figures (horizontal-slide style):

```python
from generate_html import HtmlPPT

html = HtmlPPT(title="Academic Report", theme="molecular")

# API identical to ChemistryPPT
html.add_title_slide("Title CN", title_en="Title EN", authors="...", journal="...")
html.add_section_slide("Part 1")
html.add_content_slide("Key Point", ["bullet 1", "bullet 2"])
html.add_figure_slide("Figure Title", figure_path="figures/p3_fig1.png",
                       bullets=["description"], figure_label="Figure 1",
                       layout="figure_right")
html.add_summary_slide("Summary", ["finding 1", "finding 2"])
html.add_thankyou_slide()

html.save("output/presentation.html")
```

**HTML features**:
- Single self-contained file, figures embedded as base64
- Horizontal slide navigation: keyboard ← → Home End, scroll wheel, touch swipe, dot navigation
- 4 academic color themes (academic / molecular / green / nature)
- Responsive design for projectors and mobile
- No local server or dependencies needed

### Step 7: Verify and Review Reports

After generating PPTX, run verification:

```python
from pptx import Presentation

prs = Presentation("output/presentation.pptx")
print(f"Slide count: {len(prs.slides)}")

# Check all images are present
for i, slide in enumerate(prs.slides):
    for shape in slide.shapes:
        if shape.shape_type == 13:  # Picture
            print(f"  Slide {i+1}: image {shape.image.content_type}")
```

The `ChemistryPPT` class includes built-in error tracking:

```python
ppt.save("output/presentation.pptx")
ppt.save_report("output/presentation.pptx")  # generates JSON report

# Or access directly
report = ppt.get_report()
print(report["missing_images"])  # list of image paths not found
print(report["warnings"])        # non-fatal issues
print(report["errors"])          # actual errors
```

**Report fields**:
- `missing_images`: all paths passed to `add_figure_slide()` that don't exist
- `errors`: actual image insertion failures
- `warnings`: non-fatal issues
- `slide_types`: slide type statistics

### Error Handling & Fallback Mechanisms

**Figure extraction** (`extract_charts.py`):
1. 5-layer strategy: caption-guided → vector graphics → multi-tolerance → embedded images → page rendering
2. Compatible with PyMuPDF 1.19+ and 1.23+ (auto-switch `cluster_drawings` / `get_drawings` with manual clustering)
3. Caption-guided extraction locates "Figure X" text then crops the region above, yielding high-confidence results
4. Auto-generated JSON extraction report via `--report` flag with per-item confidence scores

**DOI-based retrieval** (`fetch_from_doi.py`):
1. Resolves DOI via Semantic Scholar API (free, no key) to find arXiv ID and open-access PDF links
2. Can download and extract original high-res figures from arXiv source tarballs
3. Provides fallback URLs for manual figure sourcing

**Paper analysis** (`analyze_paper.py`):
1. Domain detection: `is_chemistry` flag warns when input may not be a chemistry paper
2. Encoding-safe: stdout UTF-8 reconfiguration for Windows compatibility
3. Confidence-annotated paper classification (high/medium/low)
4. Structured JSON output: `--json report.json` for workflow integration
5. Weighted keyword detection: ×3 weight in first 1/3 of text (methods/results), ×1 in references
6. Configurable keywords via `references/chemistry_keywords.json` — no code changes needed

**PPT building** (`create_ppt.py`):
1. Missing images auto-recorded (build continues), summarized on `save()`
2. Image insertion exceptions caught (corrupt/unsupported formats)
3. `save_report()` exports complete build log

**Common issues and resolutions**:

| Issue | Cause | Resolution |
|-------|-------|------------|
| `cluster_drawings` not found | PyMuPDF < 1.23 | Auto-fallback to `get_drawings()` manual clustering |
| 0 vector figures extracted | Special PDF rendering | Caption-guided extraction → multi-tolerance retry → page rendering |
| Low-res figures in PDF | Publisher PDF compression | Path B: fetch arXiv source for original high-res figures |
| No local PDF available | User only provided DOI/link | Path C: MCP tools to download PDF, then Path A extraction |
| Windows encoding crash | Unicode chars (e.g. `−`, `₂`) | `setup_utf8_stdout()` in utils.py, `_safe_print()` fallback |
| Paper type misclassification | Characterization keywords in references | Weighted detection (body ×3), confidence annotation |
| Non-chemistry input | Biology/physics/medicine paper | `is_chemistry` flag warns user; proceed only after confirmation |
| Missing image files | Incorrect extraction or path | Recorded in `missing_images`, slide shows placeholder |

---

## Chemistry Academic Visual Standards

See `references/visual_style.md` for full details. Summary below:

### Color Schemes

| Name | Primary | Accent | Best for |
|------|---------|--------|----------|
| **Academic Classic** (default) | `#003366` deep blue | `#B41E1E` dark red | General chemistry |
| **Molecular Tech** | `#1A5276` steel blue | `#E74C3C` bright red | Computational/materials |
| **Green Chemistry** | `#1E5631` deep green | `#D4A017` gold | Catalysis/energy/environment |
| **Nature Style** | `#222222` near-black | `#0066CC` blue | CNS journal presentations |
| **LaTeX Beamer** | `#003366` deep blue | `#B41E1E` dark red | Conference/defense talks (serif fonts) |

### Typography

- Title: Bold sans-serif, 28–36pt
- Body: Regular sans-serif, 16–20pt
- English/numbers: Arial / Helvetica
- Chemistry formulas: monospace or appropriate serif
- **LaTeX Beamer theme**: Full serif fonts (Latin Modern Roman / Georgia / Times New Roman), replicating the classic academic conference Beamer style. Install Latin Modern fonts for best results: download from CTAN or via system package manager

### Slide Layout

- 16:9 widescreen (13.333" × 7.5")
- Margins ≥ 0.5"
- Left-aligned body text; titles may be centered
- Figures get priority space; explanatory text is concise

### Chemistry-Specific Elements

- **Reaction schemes**: structure images or text-based with → connectors
- **Data tables**: comparison tables for catalyst performance / computational parameters
- **Mechanism diagrams**: keep originals, annotate key steps (i, ii, iii...)
- **Energy diagrams**: label key TS and intermediate energies on free energy profiles
- **Characterization data**: label key peaks (XRD), valence states (XPS), lattice spacings (TEM)

---

## Output Files

Default output in `output/`:

```
output/
├── presentation.pptx          # Final PPTX
├── presentation.html          # (optional) Single-file HTML deck
├── presentation_report.json   # PPTX build report
├── figures/                   # Extracted figures
│   ├── p2_fig1.png
│   ├── p4_fig2.png
│   └── ...
└── qa_report.md               # Quality check report (optional)
```

---

## Scripts

| Script | Function |
|--------|----------|
| `scripts/analyze_paper.py` | PDF structure analysis, paper type classification, domain detection, JSON output |
| `scripts/extract_charts.py` | 5-layer figure extraction (caption-guided → vector → embedded → page render) |
| `scripts/fetch_from_doi.py` | **New** DOI resolver: Semantic Scholar / arXiv API → high-res figure sources |
| `scripts/convert_to_images.py` | PDF page to high-res image conversion (requires poppler/pdf2image) |
| `scripts/create_ppt.py` | Main script: ChemistryPPT class for academic PPTX creation |
| `scripts/generate_html.py` | HTML generator: single-file horizontal-slide web deck |
| `scripts/generate_report.py` | Report generator: Markdown academic reading notes |
| `scripts/utils.py` | **New** Shared utilities: safe_print / cluster_drawings_compat / setup_utf8_stdout |

---

## Chemistry Paper Type Adaptations

### Catalysis Chemistry
Focus: preparation methods, characterization (XRD/TEM/XPS/BET), activity/selectivity/stability data, TOF, activation energy, in-situ characterization, DFT-assisted mechanism

### Materials Chemistry
Focus: synthesis strategy, morphology control, structure characterization, physicochemical properties, application performance, structure-property relationships

### Organic Synthesis Chemistry
Focus: synthetic route, substrate scope, condition optimization, mechanistic probe experiments, selectivity control

### Computational/Theoretical Chemistry
Focus: computational methods and parameters, model validity, energy/structure data, comparison with experiment/benchmarks, atomic-level mechanism

### Energy/Battery Chemistry
Focus: materials design, electrochemical performance (capacity/rate/cycling), in-situ characterization, interface chemistry, degradation mechanisms

### Environmental/Atmospheric Chemistry
Focus: reaction kinetics, product analysis, mechanistic pathways, environmental implications, model calculations

---

## Prohibitions

- Do not generate placeholder content ("Please manually add XX", "Fill in XX here")
- Do not force all papers into the same template — adapt structure to actual paper content
- Do not ignore correct formatting of chemical formulas / element symbols (subscripts, italics, etc.)
- Do not create text-only result slides when figures are available
- Do not fabricate data or conclusions not present in the paper
- Do not produce a text-only outline instead of a usable presentation
