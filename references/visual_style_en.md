# Chemistry Academic PPT Visual Standards

This document defines the visual design standards for chemistry academic PPTs, targeting **professional, publication-quality** presentations.

## Color Schemes

### Preset Themes

#### 1. Academic Classic (academic) — Default, General Chemistry

| Role | Hex | Usage |
|------|-----|-------|
| Primary | `#003366` | Titles, section slide backgrounds |
| Background | `#FFFFFF` | Content slide backgrounds |
| Body text | `#333333` | Main text |
| Accent | `#B41E1E` | Decorative lines, key data highlights |
| Light bg | `#F0F4F8` | Summary slide backgrounds, table zebra stripes |
| Muted | `#8C8C8C` | Page numbers, figure captions, source labels |

#### 2. Molecular Tech (molecular) — Computational Chemistry / Materials

| Role | Hex | Usage |
|------|-----|-------|
| Primary | `#1A5276` | Titles, section slide backgrounds |
| Background | `#F8F9FA` | Content slide backgrounds |
| Body text | `#2C3E50` | Main text |
| Accent | `#E74C3C` | Decorative lines, key data highlights |
| Light bg | `#EBF0F5` | Summary slide backgrounds, table zebra stripes |

#### 3. Green Chemistry (green) — Catalysis / Energy / Environment

| Role | Hex | Usage |
|------|-----|-------|
| Primary | `#1E5631` | Titles, section slide backgrounds |
| Background | `#F7F9F4` | Content slide backgrounds |
| Body text | `#333333` | Main text |
| Accent | `#D4A017` | Decorative lines, key data highlights |
| Light bg | `#EEF3E9` | Summary slide backgrounds, table zebra stripes |

#### 4. Nature Style (nature) — CNS Journal Presentations

| Role | Hex | Usage |
|------|-----|-------|
| Primary | `#222222` | Titles, section slide backgrounds |
| Background | `#FFFFFF` | Content slide backgrounds |
| Body text | `#444444` | Main text |
| Accent | `#0066CC` | Decorative lines, key data highlights |
| Light bg | `#F8F8F8` | Summary slide backgrounds, table zebra stripes |

### Color Principles

- One theme per deck — do not mix themes
- Accent color only for decorative lines, key numbers, emphasis marks — ≤ 5% of slide area
- Dark section slides must use white or near-white text for sufficient contrast
- No fluorescent colors, rainbow gradients, or decorative shadows

## Typography

### Recommended Fonts

| Usage | Chinese | English / Numbers | Size |
|------|---------|-------------------|------|
| Cover title | Microsoft YaHei Bold / Source Han Sans Bold | Arial Bold / Helvetica Bold | 36–42pt |
| Section divider | Microsoft YaHei Bold / Source Han Sans Bold | Arial Bold | 36–40pt |
| Slide title | Microsoft YaHei Bold / Source Han Sans Bold | Arial Bold | 28–34pt |
| Body bullets | Microsoft YaHei Regular / Source Han Sans Regular | Arial Regular | 16–20pt |
| Figure captions/sources | Microsoft YaHei Regular / Source Han Sans Regular | Arial Regular | 9–11pt |
| Table content | Microsoft YaHei Regular / Source Han Sans Regular | Arial Regular | 12–14pt |
| Data highlights | Microsoft YaHei Bold / Source Han Sans Bold | Arial Bold | 24–28pt |

### Typography Principles

- Title at least 10pt larger than body — clear hierarchy
- Subscripts in chemical formulas (H₂O, SO₄²⁻) — accept plain text if styling unavailable
- Variables in italics (*E*a, *k*cat) — not mandatory
- No more than 3 font sizes per slide

## Layout Standards

### Canvas

- 16:9 widescreen (13.333" × 7.5")
- Horizontal padding ≥ 0.5" (0.7" recommended)
- Vertical padding ≥ 0.3"

### Title Position

- Content slide titles fixed at top-left (0.7", 0.3"), left-aligned
- Thin decorative line below title (1.5pt, accent color) at 0.1–0.15"
- Section divider titles may be centered or left-aligned (recommended: left-aligned + vertical accent bar)

### Figure Layouts (4 modes)

1. **figure_right** (default): best for landscape figures with detailed captions
   - Left text: 0.7"–6.5" (5.8" wide)
   - Right figure: 7.2"–12.7" (5.5" wide)

2. **figure_top**: best for wide figures with short descriptions
   - Figure area: 0.7"–12.6" (3.0–3.5" tall)
   - Text below in remaining space

3. **figure_left**: best for portrait figures or figure-emphasis slides
   - Left figure: 5.5" wide
   - Right text: 6.2" wide

4. **figure_full**: best for complex mechanism diagrams, multi-panel figures
   - Figure: 0.5"–12.8" (full width)
   - Brief caption at bottom

**Selection principle**: let the figure dictate the layout. Wide figures → `figure_top`, tall figures → `figure_left/right`, complex figures → `figure_full`.

## Chemistry-Specific Visual Elements

### Reaction Schemes

- Use → or chemistry arrow to connect reactants and products
- Reaction conditions above or below arrow (small font)
- Example: `A + B ──→ C (yield: 85%)`
- Use monospace or Arial font

### Data Highlights

- Key numbers (FE%, TOF, yield, selectivity) may be enlarged and boldfaced
- Use accent color for breakthrough data
- Do not highlight more than 3 numbers simultaneously

### Energy / Free Energy Diagrams

- Preserve original figure; annotate key barrier values on the slide
- If redrawing: X-axis = reaction coordinate, Y-axis = energy (eV or kcal/mol)
- Label the rate-determining step barrier

### Characterization Data Interpretation Template

```
XRD:    → Phase confirmed as [...], crystallite size [...] nm (Scherrer)
TEM:    → Morphology: [...], particle size distribution [...] nm
HRTEM:  → Lattice fringe [...] nm, corresponding to [...] plane
XPS:    → [...] element in [...] valence state, binding energy [...] eV
BET:    → Surface area [...] m²/g, pore size [...] nm
```

### Performance Data Table Template

```
| Catalyst   | FE(C₂₊)% | j (mA/cm²) | Stability/h | Electrolyte | Ref      |
|------------|----------|------------|-------------|-------------|----------|
| Ru₁/Cu     | 82%      | 300        | 100         | 1M KOH      | This work |
| Cu NPs     | 45%      | 150        | 20          | 1M KOH      | [1]       |
| Benchmark  | 60%      | 200        | 50          | 1M KHCO₃    | [2]       |
```

## Readability Checklist

- [ ] Body text ≥ 16pt
- [ ] Figure text legible at presentation scale
- [ ] Sufficient color contrast (dark text on light background, or vice versa)
- [ ] No text overflow or overlapping
- [ ] Figures not cropped or distorted
- [ ] Page numbers consecutive
- [ ] One core message per slide

## Don'ts

- No decorative images, clip art, or emoji
- No gradient backgrounds
- No dark backgrounds on content slides
- No more than 6 bullet points per slide
- No copy-pasting paper paragraphs verbatim
- No figures too small to read
- No cramming multiple dense figures onto one slide
- No accent bar below titles on regular content slides (section slides only)
