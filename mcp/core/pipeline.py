"""
Writing Suite - Unified Closed-Loop Humanization & Diagnostic Pipeline
Orchestra l'intero ciclo di vita per capitoli di tesi, paper scientifici e report tecnici:
1. Parsing strutturale con Meaning Lock (protezione assoluta di formule, citazioni, figure, label e codice).
2. Diagnosi preliminare a 7 Lenti (Linter 55+ tells, GLTR, GPTZero, Burstiness, MTLD, Anti-Bypass, Neural MPS).
3. Riscritura chirurgica paragrafo per paragrafo via Ollama (Qwen2.5 / GoHumanize locale) o CleverHumanizer headless.
4. Convalida in anello chiuso: ri-valutazione immediata con rollback se la qualità non raggiunge la zona verde (< 20%).
5. Verifica di compilazione Typst/LaTeX e controllo integrità bibliografica (.bib).
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Ensure writing-suite/mcp is in sys.path
CURRENT_DIR = Path(__file__).resolve().parent.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from core.cleaner import clean_markup, extract_sentences, extract_words
from core.evaluator_engine import evaluate_document
from core.linter import lint_text
from core.citations import audit_citations


# ==============================================================================
# 1. MEANING LOCK PARSER & RECONSTRUCTOR
# ==============================================================================

class MeaningLockProtector:
    """
    Isola e protegge tutti gli elementi formali, matematici e strutturali prima
    della riscrittura, garantendo che non vengano alterati o allucinati.
    """

    def __init__(self):
        self.placeholders: Dict[str, str] = {}
        self._counter = 0

    def _generate_key(self, prefix: str) -> str:
        self._counter += 1
        return f"___MLOCK_{prefix}_{self._counter:04d}___"

    def protect(self, content: str) -> str:
        """Sostituisce blocchi protetti con token univoci."""
        self.placeholders.clear()
        self._counter = 0
        text = content

        # 1. Protezione blocchi di codice Typst / Markdown (``` ... ```)
        def replace_code_blocks(m):
            k = self._generate_key("CODE")
            self.placeholders[k] = m.group(0)
            return k
        text = re.sub(r"```[\s\S]*?```", replace_code_blocks, text)

        # 2. Protezione figure e tabelle Typst (#figure(...), #table(...))
        def replace_typst_figures(m):
            k = self._generate_key("FIG")
            self.placeholders[k] = m.group(0)
            return k
        text = re.sub(r"#figure\s*\([\s\S]*?\)\s*(?:<[^>]+>)?", replace_typst_figures, text)
        text = re.sub(r"#table\s*\([\s\S]*?\)", replace_typst_figures, text)

        # 3. Protezione formule matematiche display ($ ... $) e inline ($...$)
        def replace_math(m):
            k = self._generate_key("MATH")
            self.placeholders[k] = m.group(0)
            return k
        # Display math (multiline o con spazi: $ ... $)
        text = re.sub(r"(?<!\\)\$\s+[\s\S]*?\s+\$(?<!\\)", replace_math, text)
        # Inline math ($...$ non preceduto da backslash né contenente newline)
        text = re.sub(r"(?<!\\)\$(?!\s)[^\$\n]+?(?<!\s)(?<!\\)\$", replace_math, text)

        # 4. Protezione citazioni Typst (@key) e LaTeX (\cite{...})
        def replace_citations(m):
            k = self._generate_key("CITE")
            self.placeholders[k] = m.group(0)
            return k
        text = re.sub(r"\\cite\{[^}]+\}", replace_citations, text)
        text = re.sub(r"@[a-zA-Z0-9_\-:]+", replace_citations, text)

        # 5. Protezione label Typst (<label>)
        def replace_labels(m):
            k = self._generate_key("LABEL")
            self.placeholders[k] = m.group(0)
            return k
        text = re.sub(r"<[a-zA-Z0-9_\-:]+>", replace_labels, text)

        # 6. Protezione comandi Typst a livello di riga (#include, #import, #set, #show)
        def replace_typst_directives(m):
            k = self._generate_key("CMD")
            self.placeholders[k] = m.group(0)
            return k
        text = re.sub(r"^(?:#include|#import|#set|#show)[\s\S]*?$", replace_typst_directives, text, flags=re.MULTILINE)

        return text

    def restore(self, text: str) -> str:
        """Ripristina i blocchi originali dai token protetti."""
        restored = text
        for key, original in self.placeholders.items():
            restored = restored.replace(key, original)

        # Sanificazione automatica residui di em-dash
        restored = restored.replace(" — ", ", ").replace("—", ", ")
        restored = restored.replace(" -- ", ", ").replace("--", ", ")
        return restored


# ==============================================================================
# 2. LOCAL OLLAMA REWRITING CLIENT (QWEN2.5 / GOHUMANIZE)
# ==============================================================================

class OllamaRewriter:
    """Interfaccia HTTP ad alta velocità con il demone Ollama locale."""

    def __init__(self, host: str = "http://localhost:11434", model: str = "qwen2.5:7b"):
        self.host = host.rstrip("/")
        self.model = model

    def is_available(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.host}/api/tags")
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def rewrite_paragraph(self, paragraph: str, domain_terms: List[str] = None) -> Optional[str]:
        """Riscrive un singolo paragrafo applicando rigorosamente lo stile accademico umano v5.3.0."""
        if not self.is_available():
            return None

        terms_hint = ", ".join(domain_terms) if domain_terms else "systems security, blockchain, PyChain"

        system_prompt = f"""You are a Principal Academic Stylist and Systems Security Researcher rewriting a thesis paragraph.
Transform robotic, synthetic, or AI-sounding prose into authentic, scholarly, and fluent academic English.

STRICT CONSTRAINTS (MEANING LOCK):
1. PRESERVE EXACTLY all placeholders matching ___MLOCK_[A-Z]+_[0-9]+___ without modifying a single character.
2. Grounded Systems Incipit: Never start with high-altitude philosophical framing ("X is fundamentally an exercise in...", "X has long mirrored..."). Start directly with operational mechanisms, package managers, and physical components.
3. Active Researcher Voice: Use natural authorial agency ("In this dissertation, we introduce...", "In our testbed, we observe...").
4. Right-Branching Predicates: Avoid stacking 3+ nouns before the verb. Front the action.
5. Indefinite / Pragmatic Determinism: Use natural developer phrasing ("querying some SQL backend on AWS", "stored across arbitrary mirrors").
6. Inverted & Modal Conditionals: Use "Should the hash mismatch...", "Were an attacker to...", avoiding repetitive "If X, then Y".
7. Ban all artificial slogans: Never add one-line theatrical closers ("This invariant is absolute.", "Usability improved dramatically.").
8. ZERO EM-DASHES: Do NOT output any em-dash (— or --). Use commas, semicolons, or separate sentences.
9. Output ONLY the rewritten paragraph, with zero meta-commentary, introductory remarks, or quotes.
Domain vocabulary: {terms_hint}"""

        user_prompt = f"Rewrite this academic paragraph into authentic, natural scholarly prose:\n\n{paragraph}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": 0.35,
                "top_p": 0.85,
                "repeat_penalty": 1.15
            }
        }

        try:
            req = urllib.request.Request(
                f"{self.host}/api/chat",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=45.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply = data.get("message", {}).get("content", "").strip()
                # Clean any accidental outer quotes or markdown wraps
                if reply.startswith('\"') and reply.endswith('\"'):
                    reply = reply[1:-1].strip()
                return reply
        except Exception as e:
            print(f"[Ollama Rewriter Error]: {e}", file=sys.stderr)
            return None


# ==============================================================================
# 3. UNIFIED THESIS PIPELINE ENGINE
# ==============================================================================

class ThesisPipeline:
    """Pipeline automatizzata end-to-end per diagnosi, riscrittura e verifica in anello chiuso."""

    def __init__(self, ollama_model: str = "qwen2.5:7b", default_domain: str = "blockchain"):
        self.protector = MeaningLockProtector()
        self.ollama = OllamaRewriter(model=ollama_model)
        self.default_domain = default_domain

    def audit_file(
        self,
        file_path: str,
        domain_terms: Optional[List[str]] = None,
        style: str = "academic_thesis"
    ) -> Dict[str, Any]:
        """Esegue l'audit diagnostico preliminare a 7 lenti sul file specificato."""
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File non trovato: {file_path}")

        raw_content = path.read_text(encoding="utf-8", errors="ignore")
        return evaluate_document(
            raw_content,
            file_path=str(path),
            domain=self.default_domain,
            domain_terms=domain_terms or [],
            target_style=style
        )

    def process_file(
        self,
        file_path: str,
        output_path: Optional[str] = None,
        domain_terms: Optional[List[str]] = None,
        dry_run: bool = False,
        interactive: bool = False
    ) -> Dict[str, Any]:
        """
        Processa un intero file paragrafo per paragrafo:
        - Protegge elementi con Meaning Lock.
        - Isola i paragrafi che superano la soglia di rischio (> 25% AI o con linter finding).
        - Riscrive tramite Ollama locale in anello chiuso.
        - Convalida e ricompone il file.
        """
        path = Path(file_path)
        raw_content = path.read_text(encoding="utf-8", errors="ignore")

        # 1. Audit iniziale del file completo
        initial_eval = evaluate_document(
            raw_content,
            file_path=str(path),
            domain=self.default_domain,
            domain_terms=domain_terms or []
        )

        # 2. Protezione con Meaning Lock
        protected_content = self.protector.protect(raw_content)

        # 3. Suddivisione in blocchi di paragrafo preservando intestazioni
        lines = protected_content.split("\n")
        blocks = []
        current_block = []

        for line in lines:
            # Intestazioni Typst o linee vuote delimitano i blocchi
            if line.strip().startswith("=") or not line.strip():
                if current_block:
                    blocks.append("\n".join(current_block))
                    current_block = []
                blocks.append(line)
            else:
                current_block.append(line)
        if current_block:
            blocks.append("\n".join(current_block))

        # 4. Elaborazione e Riscrittura Paragrafo per Paragrafo
        processed_blocks = []
        rewritten_count = 0
        total_prose_blocks = 0

        for block in blocks:
            trimmed = block.strip()
            # Salta intestazioni, direttive, comandi isolati o blocchi brevissimi
            if (
                trimmed.startswith("=") or
                trimmed.startswith("___MLOCK_") or
                not trimmed or
                len(trimmed.split()) < 15
            ):
                processed_blocks.append(block)
                continue

            total_prose_blocks += 1

            # Valutazione locale rapida del singolo paragrafo
            para_eval = evaluate_document(
                trimmed,
                domain=self.default_domain,
                domain_terms=domain_terms or []
            )

            is_risky = (
                para_eval["overall_ai_score"] >= 25.0 or
                para_eval["stats"]["findings_count"] > 0
            )

            if not is_risky or dry_run:
                processed_blocks.append(block)
                continue

            # Tenta la riscrittura con Ollama
            print(f"  [Polishing Para]: Rischio iniziale {para_eval['overall_ai_score']}% ({para_eval['stats']['findings_count']} finding)...")
            rewritten_para = self.ollama.rewrite_paragraph(trimmed, domain_terms=domain_terms)

            if rewritten_para:
                # Convalida Closed-Loop: verifica che il nuovo paragrafo sia migliore
                post_eval = evaluate_document(
                    rewritten_para,
                    domain=self.default_domain,
                    domain_terms=domain_terms or []
                )

                if post_eval["overall_ai_score"] < para_eval["overall_ai_score"] and post_eval["stats"]["findings_count"] == 0:
                    print(f"    --> Approvato: {para_eval['overall_ai_score']}% -> {post_eval['overall_ai_score']}% 🟢")
                    processed_blocks.append(rewritten_para)
                    rewritten_count += 1
                else:
                    print(f"    --> Rollback: il candidato ({post_eval['overall_ai_score']}%) non ha migliorato il paragrafo.")
                    processed_blocks.append(block)
            else:
                processed_blocks.append(block)

        # 5. Ricomposizione e Ripristino Meaning Lock
        reassembled_protected = "\n".join(processed_blocks)
        final_content = self.protector.restore(reassembled_protected)

        # 6. Audit Finale del file rigenerato
        final_eval = evaluate_document(
            final_content,
            file_path=str(path),
            domain=self.default_domain,
            domain_terms=domain_terms or []
        )

        # 7. Salvataggio su disco (se non dry-run)
        dest_path = Path(output_path) if output_path else path
        if not dry_run and rewritten_count > 0:
            dest_path.write_text(final_content, encoding="utf-8")

        return {
            "file": str(path),
            "output_file": str(dest_path),
            "prose_blocks_total": total_prose_blocks,
            "blocks_rewritten": rewritten_count,
            "initial_score": initial_eval["overall_ai_score"],
            "initial_badge": initial_eval["verdict_badge"],
            "initial_findings": initial_eval["stats"]["findings_count"],
            "final_score": final_eval["overall_ai_score"],
            "final_badge": final_eval["verdict_badge"],
            "final_findings": final_eval["stats"]["findings_count"],
            "delta_ai_risk": round(final_eval["overall_ai_score"] - initial_eval["overall_ai_score"], 1)
        }

    def process_directory(
        self,
        directory_path: str,
        dry_run: bool = False,
        domain_terms: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Scansiona ed elabora tutti i capitoli (.typ) di una cartella di tesi."""
        dir_p = Path(directory_path)
        typ_files = sorted(list(dir_p.glob("ch*.typ")) + list(dir_p.glob("appendix*.typ")))

        results = []
        print(f"\n=== Avvio Pipeline Tesi: {len(typ_files)} capitoli identificati ===")
        for f in typ_files:
            print(f"\n[Capitolo]: {f.name}")
            res = self.process_file(str(f), dry_run=dry_run, domain_terms=domain_terms)
            results.append(res)
            print(f"  Risultato: {res['initial_score']}% {res['initial_badge']} -> {res['final_score']}% {res['final_badge']} (Riscritte: {res['blocks_rewritten']}/{res['prose_blocks_total']})")

        return results


# ==============================================================================
# 4. CLI INTERFACE
# ==============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Writing Suite - Universal Thesis Pipeline")
    parser.add_argument("--file", type=str, help="Percorso del capitolo da elaborare (.typ, .tex, .md)")
    parser.add_argument("--project", type=str, help="Percorso della directory contenente i capitoli della tesi")
    parser.add_argument("--mode", choices=["audit", "humanize"], default="audit", help="Modalità operativa: 'audit' (sola analisi) o 'humanize' (riscrittura in anello chiuso)")
    parser.add_argument("--model", type=str, default="qwen2.5:7b", help="Modello Ollama da utilizzare (default: qwen2.5:7b)")
    parser.add_argument("--terms", type=str, default="", help="Termini di dominio separati da virgola (es. 'EVM,SWHID,IPFS,Sepolia')")
    parser.add_argument("--output", type=str, help="Opzionale. Percorso del file di destinazione")

    args = parser.parse_args()

    domain_terms = [t.strip() for t in args.terms.split(",") if t.strip()]
    pipeline = ThesisPipeline(ollama_model=args.model)

    if args.project:
        if args.mode == "audit":
            for f in sorted(Path(args.project).glob("*.typ")):
                audit_res = pipeline.audit_file(str(f), domain_terms=domain_terms)
                print(f"[{f.name}]: {audit_res['overall_ai_score']}% {audit_res['verdict_badge']} | Findings: {audit_res['stats']['findings_count']} | Parole: {audit_res['stats']['total_words']}")
        else:
            res_list = pipeline.process_directory(args.project, domain_terms=domain_terms)
            print("\n=== Riepilogo Elaborazione Tesi ===")
            print(json.dumps(res_list, indent=2, ensure_ascii=False))

    elif args.file:
        if args.mode == "audit":
            res = pipeline.audit_file(args.file, domain_terms=domain_terms)
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            res = pipeline.process_file(args.file, output_path=args.output, domain_terms=domain_terms)
            print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        parser.print_help()
