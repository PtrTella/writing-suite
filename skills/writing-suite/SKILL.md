---
name: writing-suite
description: |
  Official operational and forensic evaluation CLI for academic theses and technical documents.
  Executes the 4-pillar forensic evaluator (Apple Silicon Metal MPS Causal Surprisal, Mathematical Stylometry,
  Dense Embeddings, and DeBERTa-v3), generates paragraph-by-paragraph Visual Heatmaps, runs BibTeX citation audits,
  validates live against CleverHumanizer.ai via headless Chromium, and compiles Typst documents into PDF with 0 errors.
license: MIT
metadata:
  version: "2.0.0"
---

# Writing Suite 2.0: Modern Academic & Forensic Architecture

You have access to the **Writing Suite 2.0** engine located in `/Users/tella/Workspace/writing-suite`. This suite replaces obsolete, brittle regex linters and static word lists with an objective, scientific **4-pillar forensic evaluator** calibrated on Apple Silicon Metal (`mps`).

---

## 1. The Core 4 Pillars

Writing Suite evaluates text through four complementary analytical lenses:
1. **Causal Surprisal & Perplexity (SmolLM2-135M on MPS)**:
   * Measures token-by-token surprisal: $s(w_t) = -\log_2 P(w_t \mid w_{<t})$.
   * Low PPL ($< 35$) signals generic, flat, synthetic text. High PPL ($> 75$) indicates authentic, information-dense domain prose.
2. **Pure Mathematical Stylometry (Zero Hardcoded Dictionaries)**:
   * Calculates sentence length std dev ($\sigma_{\text{len}}$) to detect metronomic rhythm ($\sigma < 8.0$).
   * Measures subword Zipfian frequency decay ($\alpha$) and length-invariant lexical richness (MTLD).
3. **Dense Latent Embedding Classifier**:
   * Combines 576-dimensional pooled hidden states from SmolLM2 with a 12-dimensional stylometric feature vector in a transparent classifier.
4. **Multi-Scale Transformer (DeBERTa-v3 on MPS)**:
   * Evaluates text using fine-tuned disentangled attention across sliding windows to identify local spikes in synthetic predictability.

---

## 2. Command Reference (`uv run`)

Always execute commands using `uv run` in `/Users/tella/Workspace/writing-suite`:

### A. Document Evaluation & Visual Heatmap
```bash
uv run --directory /Users/tella/Workspace/writing-suite bin/writing-suite evaluate "<path/to/file.typ>"
```
* **Output**: Complete corpus statistics (mean PPL, surprisal burstiness, cadence $\sigma$, MTLD) followed by a **paragraph-by-paragraph Visual Heatmap**:
  ```text
  §    | Parole | PPL     | σ_len  | DeBERTa  | Rischio AI | Status
  --------------------------------------------------------------------------------
  §01  | 162    | 102.4   | 9.4    | 1.6%     | 🟢 10.8%    | Public package repositories...
  §07  | 124    | 116.0   | 6.1    | 4.6%     | 🟢 17.0%    | When a build pipeline runs...
  ```
* **Interpreting Thresholds**:
  * 🟢 **Safe Zone (< 25% AI Risk)**: Authentic human writing. No action needed.
  * 🟡 **Mixed Zone (25% – 50% AI Risk)**: Check for low cadence variance ($\sigma < 8.0$) or generic phrasing.
  * 🔴 **Critical Hotspot (> 50% AI Risk)**: Priority rewrite required. Check DeBERTa spike or metronomic rhythm.

### B. Bibliographic Integrity & Unsupported Claim Audit
```bash
uv run --directory /Users/tella/Workspace/writing-suite bin/writing-suite citations "<file.typ>" [references.bib]
```
* Validates that all in-text `@key` citations exist in the `.bib` file (no orphaned keys).
* Scans for sweeping ungrounded claims (*"studies have shown"*, *"researchers widely agree"*).

### C. Live Commercial Validation (CleverHumanizer.ai)
```bash
uv run --directory /Users/tella/Workspace/writing-suite bin/writing-suite check-live "<path/to/file.typ>"
```
* Queries CleverHumanizer.ai via headless Chromium using the local Google Chrome installation.
* Returns sentence-level classification (⚪ Human, 🟡 Mixed, 🔴 Synthetic).

### D. Typst PDF Compilation Check
```bash
uv run --directory /Users/tella/Workspace/writing-suite bin/writing-suite compile [path/to/main.typ]
```
* Compiles the master document using `typst compile` and certifies 0 errors / 0 warnings.

---

## 3. The Closed-Loop Chapter Revision Runbook

Whenever invoked to review, polish, or rewrite a thesis chapter:

1. **Step 1: Diagnostics**:
   Run `uv run --directory /Users/tella/Workspace/writing-suite bin/writing-suite evaluate <chapter.typ>`.
   Identify any paragraphs flagged as 🔴 ($> 50\%$) or 🟡 ($25-50\%$).
2. **Step 2: In-Place Targeted Rewrite**:
   Refer to the `academic-writing-guide` skill. Rewrite only the flagged paragraphs directly in the `.typ` file adhering to the Impersonal Architecture Register and Meaning Lock.
3. **Step 3: Verification**:
   Re-run `evaluate`. Confirm that the overall score is firmly in the **🟢 Safe Zone (< 20%)** with **0 critical red hotspots**.
4. **Step 4: Commercial Cross-Check**:
   Run `check-live` to confirm zero critical red sentences on CleverHumanizer.
5. **Step 5: Compilation**:
   Run `compile` to guarantee the PDF builds cleanly with 0 errors.
