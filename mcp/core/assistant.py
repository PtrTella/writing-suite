"""
Writing Suite - Assistant, Fact-Checker & Multi-LLM Writing Orchestrator
Compatibile con qualsiasi agente o interfaccia: Claude, ChatGPT / OpenAI, Gemini.

Funzionalità:
1. Fact-checking citazionale rigoroso incrociato con references.bib.
2. Identificazione e isolamento degli hotspot sintetici (paragrafi metronomici o robotici).
3. Generazione di Prompt Chirurgici ottimizzati e pronti da incollare in qualsiasi LLM.
4. Supporto opzionale per copia diretta negli appunti di macOS (pbcopy).
5. Meaning Lock enforcement per formule ($...$), riferimenti bib (@...) ed etichette (<...>).
"""

import os
import re
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from .cleaner import clean_markup, extract_sentences, extract_words
from .citations import audit_citations, parse_bib_keys
from .modern_evaluator import evaluate_paragraph, split_into_paragraphs

# Mappatura tematica di parole chiave -> chiavi bibliografiche tipiche in references.bib
TOPIC_CITATION_MAP = {
    "supply chain": ["ladisa2023taxonomy", "ohm2020backstabber", "duan2020measuring"],
    "package update": ["cappos2008package", "samuel2010tuf", "kuppusamy2016diplomat"],
    "provenance": ["torres2019toto", "zacchiroli2020software", "pietri2019software"],
    "reproducible": ["lamb2022reproducible", "courtes2015reproducible"],
    "ipfs": ["benet2014ipfs", "trautwein2022ipfs", "stutzbach2006churn"],
    "kademlia": ["maymounkov2002kademlia"],
    "ethereum": ["buterin2014ethereum", "wood2014ethereum"],
    "rollup": ["buterin2021rollups", "kalodner2018arbitrum"],
    "eip": ["eip1559", "eip2929", "eip4844", "pep706"],
    "tarfile": ["pep706"],
    "bandit": ["bandit"],
    "software heritage": ["dicosmo2017swh", "dicosmo2020swhid", "zacchiroli2020software"],
}


def find_relevant_bib_keys(text: str, bib_keys: set) -> List[str]:
    """Suggerisce chiavi bibliografiche pertinenti presenti nel file .bib basandosi sul contesto del testo."""
    text_lower = text.lower()
    suggested = []
    for topic, keys in TOPIC_CITATION_MAP.items():
        if topic in text_lower:
            for k in keys:
                if k in bib_keys and k not in suggested:
                    suggested.append(k)
    return suggested[:4]


def build_surgical_prompt(
    paragraph: str,
    para_idx: int,
    prescriptions: List[str],
    relevant_keys: List[str],
    used_keys: List[str]
) -> str:
    """Costruisce il prompt ad alta fedeltà pronto per Claude, ChatGPT o Gemini."""
    keys_instruction = ""
    if used_keys:
        keys_instruction += f"\n- EXISTING CITATIONS TO PRESERVE: {', '.join(['@' + k for k in used_keys])}"
    if relevant_keys:
        keys_instruction += f"\n- RELEVANT BIB KEYS TO CONSIDER (if making assertions): {', '.join(['@' + k for k in relevant_keys])}"

    presc_str = "\n".join([f"  • {p}" for p in prescriptions]) if prescriptions else "  • Enforce strong sentence length variation (short staccato mixed with complex compound)."

    return f"""Act as a Senior Academic Reviewer and Co-Author (IEEE S&P / ACM CCS register).
Rewrite the following paragraph from my Computer Science master's thesis to achieve authentic human academic flow and eliminate all AI synthetic patterns.

=== HARD REQUIREMENTS (NO EXCEPTIONS) ===
1. CADENCE ASYMMETRY (σ_len ≥ 10.0):
   Include at least one punchy staccato sentence (≤8 words) AND at least one complex compound period (≥28 words).
2. PUNCTUATION VARIETY:
   Use an explanatory colon (":") or asymmetric semicolon. Avoid em-dashes ("---" or "—") as connectors.
3. ELIMINATE AI TELLS:
   Remove all trailing participial "-ing" codas (e.g. ", thereby ensuring...", ", facilitating...").
   Avoid textbook philosophical preambles; open directly with concrete systems constraints.
4. MEANING & REFERENCE LOCK:
   Never alter or remove mathematical formulas ($...$), Typst labels (<...>), or citation keys (@key).{keys_instruction}

=== SPECIFIC SURGICAL PRESCRIPTIONS ===
{presc_str}

=== ORIGINAL PARAGRAPH (Paragraph §{para_idx:02d}) ===
{paragraph.strip()}

=== INSTRUCTION ===
Return ONLY the rewritten Typst paragraph. No intro, no conversational remarks, no meta-commentary."""


def run_assistant(
    target_path: str,
    bib_path: Optional[str] = None,
    target_para: Optional[int] = None,
    copy_to_clipboard: bool = False
) -> Dict[str, Any]:
    """Esegue l'audit integrato di scrittura, fact-checking e genera prompt pronti per LLM."""
    p = Path(target_path)
    if not p.is_file():
        return {"error": f"File non trovato: {target_path}"}

    text = p.read_text(encoding="utf-8", errors="ignore")

    # Risolvi percorso .bib
    if not bib_path:
        # Cerca references.bib nella stessa cartella o in thesis_typst
        candidates = [
            p.parent / "references.bib",
            p.parent.parent / "references.bib",
            p.parent.parent / "thesis_typst" / "references.bib",
            Path("/Users/tella/Workspace/PyChain/thesis_typst/references.bib")
        ]
        for c in candidates:
            if c.is_file():
                bib_path = str(c.resolve())
                break

    # 1. Fact-checking e Citazioni
    citation_audit = audit_citations(text, bib_path)
    bib_keys = set(citation_audit.get("citation_keys", []))
    if bib_path:
        all_bib_keys = parse_bib_keys(bib_path)
    else:
        all_bib_keys = set()

    # 2. Suddivisione in paragrafi
    cleaned = clean_markup(text)
    paragraphs = split_into_paragraphs(cleaned)

    # Mappa dei paragrafi originali Typst (per estrarre il testo grezzo con macro e formule intatte)
    raw_blocks = [b.strip() for b in re.split(r"\n\s*\n+", text) if len(extract_words(clean_markup(b))) >= 15]

    evaluations = []
    for idx, p_clean in enumerate(paragraphs):
        ev = evaluate_paragraph(p_clean, idx + 1)
        # Associa il testo sorgente grezzo corrispondente se disponibile
        raw_text = raw_blocks[idx] if idx < len(raw_blocks) else p_clean
        ev["raw_text"] = raw_text
        evaluations.append(ev)

    # Identifica hotspot critici
    hotspots = [ev for ev in evaluations if ev["risk_score"] >= 35.0 or ev.get("cadence_sigma", 0) < 6.0 or len(ev.get("prescriptions", [])) >= 2]

    cards = []
    copied_prompt = None

    target_list = evaluations
    if target_para is not None:
        target_list = [ev for ev in evaluations if ev["index"] == target_para]
        if not target_list:
            return {"error": f"Paragrafo §{target_para} non trovato (totale paragrafi: {len(evaluations)})."}

    for ev in target_list:
        idx = ev["index"]
        raw_para = ev["raw_text"]
        presc = ev.get("prescriptions", [])
        
        # Estrai chiavi usate in questo specifico paragrafo
        used_in_para = [k for k in extract_citation_keys(raw_para)]
        # Suggerisci chiavi pertinenti non ancora usate
        suggested_keys = find_relevant_bib_keys(raw_para, all_bib_keys)
        suggested_keys = [k for k in suggested_keys if k not in used_in_para]

        prompt = build_surgical_prompt(
            paragraph=raw_para,
            para_idx=idx,
            prescriptions=presc,
            relevant_keys=suggested_keys,
            used_keys=used_in_para
        )

        cards.append({
            "index": idx,
            "risk_score": ev["risk_score"],
            "cadence_sigma": ev.get("cadence_sigma", 0.0),
            "punctuation_entropy": ev.get("punctuation_entropy", 1.5),
            "prescriptions": presc,
            "used_citations": used_in_para,
            "suggested_citations": suggested_keys,
            "prompt": prompt,
            "raw_paragraph": raw_para
        })

    # Se copy_to_clipboard è richiesto, copia il prompt del primo hotspot (o del paragrafo specificato)
    if copy_to_clipboard and cards:
        first_prompt = cards[0]["prompt"]
        try:
            p_copy = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            p_copy.communicate(first_prompt.encode("utf-8"))
            copied_prompt = f"Prompt per Paragrafo §{cards[0]['index']:02d} copiato negli appunti (Cmd+V per incollare)."
        except Exception as e:
            copied_prompt = f"Copia negli appunti non riuscita: {e}"

    return {
        "file_path": str(p),
        "total_paragraphs": len(evaluations),
        "hotspots_count": len(hotspots),
        "citation_audit": citation_audit,
        "cards": cards,
        "copied_to_clipboard": copied_prompt
    }


def render_assistant_cli(res: Dict[str, Any], show_prompt_for_all: bool = False) -> str:
    """Formatta l'output CLI per l'utente in modo chiaro, compatto e operativo."""
    if "error" in res:
        return f"\033[91mErrore: {res['error']}\033[0m"

    out = []
    out.append("=" * 86)
    out.append("   \033[1;36mWRITING SUITE - ASSISTENTE DI SCRITTURA, FACT-CHECKING & PROMPT MAKER\033[0m")
    out.append("=" * 86)
    out.append(f"File analizzato: \033[1m{res['file_path']}\033[0m")
    out.append(f"Paragrafi totali: {res['total_paragraphs']} | Hotspot da revisionare: \033[1;33m{res['hotspots_count']}\033[0m")
    
    # Sezione Fact-Checking Citazionale
    ca = res["citation_audit"]
    out.append("-" * 86)
    out.append("\033[1m1. FACT-CHECKING E RIGORE CITAZIONALE\033[0m")
    out.append(f"  • Citazioni verificate nel testo : {ca.get('total_citations_found', 0)}")
    
    if ca.get("missing_in_bib"):
        out.append(f"  • \033[91m🔴 CHIAVI ROTTE O ASSENTI NEL .BIB ({len(ca['missing_in_bib'])}):\033[0m")
        for k in ca["missing_in_bib"]:
            out.append(f"      ❌ @{k}")
    else:
        out.append("  • \033[92m🟢 100% delle citazioni sono coerenti con il file .bib\033[0m")

    if ca.get("unsupported_claims"):
        out.append(f"  • \033[93m⚠️ CLAIM PRIVI DI FONTE DIMOSTRATA ({len(ca['unsupported_claims'])}):\033[0m")
        for uc in ca["unsupported_claims"][:3]:
            out.append(f"      - Riga {uc['line']}: \"{uc['matched_text']}\" -> {uc['message']}")
    else:
        out.append("  • \033[92m🟢 Zero affermazioni apodittiche o non dimostrate rilevate.\033[0m")

    out.append("-" * 86)
    out.append("\033[1m2. HOTSPOTS E SCHEDE DI RE-WRITING PER I MODELLI (Claude / ChatGPT / Gemini)\033[0m")

    if res.get("copied_to_clipboard"):
        out.append(f"  \033[1;32m📋 {res['copied_to_clipboard']}\033[0m")

    cards = res.get("cards", [])
    if not cards:
        out.append("  \033[92m🟢 Nessun paragrafo critico rilevato! Il testo soddisfa tutti i requisiti.\033[0m")
    else:
        for card in cards:
            idx = card["index"]
            risk = card["risk_score"]
            badge = "\033[92m🟢\033[0m" if risk < 25 else ("\033[93m🟡\033[0m" if risk < 50 else "\033[91m🔴\033[0m")
            
            out.append(f"\n┌─ \033[1mPARAGRAFO §{idx:02d}\033[0m {badge} Rischio AI: \033[1m{risk:.1f}%\033[0m | σ_len: {card['cadence_sigma']:.1f} | H_punct: {card['punctuation_entropy']:.2f} bit")
            
            if card.get("prescriptions"):
                out.append("│  \033[33mDifetti rilevati:\033[0m")
                for pr in card["prescriptions"][:3]:
                    out.append(f"│   • {pr}")

            if card.get("used_citations"):
                out.append(f"│  \033[90mCitazioni presenti: {', '.join(['@' + k for k in card['used_citations']])}\033[0m")
            if card.get("suggested_citations"):
                out.append(f"│  \033[32mFonti consigliate da references.bib: {', '.join(['@' + k for k in card['suggested_citations']])}\033[0m")

            out.append("│")
            out.append("│  \033[1;35m>>> PROMPT DA COPIARE NELL'AGENTE (Claude / ChatGPT / Gemini):\033[0m")
            
            prompt_lines = card["prompt"].split("\n")
            for pl in prompt_lines:
                out.append(f"│  \033[36m{pl}\033[0m")
            out.append("└" + "─" * 84)

            # Se non è stato richiesto di mostrare tutti, mostra solo il primo per non allagare il terminale
            if not show_prompt_for_all and len(cards) > 1:
                out.append(f"\n\033[90m[Mostrato 1 di {len(cards)} hotspot. Usa 'writing-suite assist <file> <N>' per il paragrafo specifico o '--all' per vederli tutti]\033[0m")
                break

    out.append("=" * 86)
    return "\n".join(out)


def extract_citation_keys(text: str) -> set:
    """Funzione ausiliaria per estrarre chiavi da singolo paragrafo."""
    keys = set()
    typst_raw = re.findall(r"@([a-zA-Z0-9_:.-]+)", text)
    for k in typst_raw:
        clean_k = k.rstrip(".,;:-")
        if not re.match(r"^(?:ch|fig|sec|tbl|tab|table|eq|listing|app)[-_:]", clean_k, re.I) and not clean_k.startswith("openzeppelin"):
            keys.add(clean_k)
    return keys
