# Visual style and asset guide

## Design language

Use the template's black canvas as an intelligence-operations surface: precise, evidence-led and restrained. Bright colors should communicate system state, not decoration.

### Color roles

| Role | Suggested color | Use |
|---|---|---|
| Trust / verified | `#00A99D` | citations, verified states, secure flow |
| Intelligence / data | `#087ED1` | retrieval, charts, technical labels |
| Graph / AI | `#6338EE` | similarity, provider and graph layers |
| Caution / human review | `#D7B04B` | limitations and confirmation gates |
| Primary text | `#FFFFFF` | headlines and key numbers |
| Secondary text | `#9BA7AB` | labels and explanatory copy |
| Cards | `#11191C` | dark raised panels |

### Typography

- Headlines: Aptos Display, Avenir Next, Montserrat, or Arial Bold
- Body: Aptos, Inter, or Arial
- Numbers: use bold tabular figures
- Avoid novelty fonts; the supplied Datathon wordmark already carries the display personality

## Copy-ready visual assets

| File | Best slide | Purpose |
|---|---:|---|
| `visuals/01_grounded_pipeline.svg` | 5 | Six trust gates from question to audit |
| `visuals/02_architecture.svg` | 7 | Full reference architecture |
| `visuals/03_benchmark_chart.svg` | 12 | Measured local performance |
| `visuals/04_scale_and_scope.svg` | 2 or 4 | Dataset and role statistics |

PowerPoint can insert these SVG files directly using **Insert > Pictures > This Device**. SVG keeps the diagrams sharp and editable at presentation resolution.

## Required product screenshots

Capture these from the running frontend at 1440 x 900 or higher:

1. **Grounded chat:** query, answer, confidence and FIR citation chips visible.
2. **Explain panel:** verified audit entry and hash fragment visible.
3. **Operations overview:** case cards, district bars and fairness note visible.
4. **Swagger evidence:** `/api/cases/{id}/similar` response with shared MO elements.

### Screenshot hygiene

- Use the same browser zoom for every screenshot.
- Hide bookmarks, personal account names and extensions.
- Never show API keys, tokens, terminal histories or `.env` files.
- Crop to the product window; add a 1 px teal border and subtle shadow.
- Use short callout labels, not large arrows covering the interface.

## Recommended chart rules

- Start quantitative axes at zero unless explicitly showing a distribution.
- Label whether metrics are local, synthetic, measured or estimated.
- Never describe local TestClient latency as a Catalyst production SLA.
- Never present synthetic MO similarity as real-world accuracy.
- Use direct labels instead of legends wherever possible.

