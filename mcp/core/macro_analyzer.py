"""
Writing Suite - Macro-Structure & Narrative Flow Analyzer
Valuta l'architettura macroscopica del testo (capitoli, sezioni, report aziendali, saggi):
1. Rileva l'iper-frammentazione (sezioni troppo brevi < 100 parole che sembrano slide).
2. Misura la densità e la coesione narrativa tra sezioni adiacenti.
3. Fornisce suggerimenti per accorpare, riorganizzare o fluidificare la composizione generale.
"""

import re
from typing import List, Dict, Any, Optional
from pathlib import Path


def analyze_macro_structure(content: str, file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Analizza la composizione strutturale del documento identificando sezioni,
    sottosezioni e densità dei paragrafi.
    """
    lines = content.split("\n")
    sections = []
    current_title = "Incipit / Introduzione"
    current_level = 1
    current_lines = []

    for line in lines:
        stripped = line.strip()
        # Rileva intestazioni Typst (= Titolo, == Sottotitolo), Markdown (#, ##) o LaTeX (\section)
        is_header = False
        level = 1
        title = ""

        # Typst
        if re.match(r"^={1,4}\s+", stripped):
            is_header = True
            m = re.match(r"^(={1,4})\s+(.+)$", stripped)
            level = len(m.group(1))
            title = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        # Markdown
        elif re.match(r"^#{1,4}\s+", stripped):
            is_header = True
            m = re.match(r"^(#{1,4})\s+(.+)$", stripped)
            level = len(m.group(1))
            title = m.group(2).strip()
        # LaTeX
        elif re.match(r"\\(?:sub)*section\{([^}]+)\}", stripped):
            is_header = True
            m = re.match(r"\\(sub)*section\{([^}]+)\}", stripped)
            level = 1 + (len(m.group(1)) // 3 if m.group(1) else 0)
            title = m.group(2).strip()

        if is_header:
            if current_lines:
                sec_text = "\n".join(current_lines).strip()
                words = len(sec_text.split())
                sections.append({
                    "title": current_title,
                    "level": current_level,
                    "word_count": words,
                    "is_too_short": words < 90 and words > 0,
                    "preview": sec_text[:120] + "..." if len(sec_text) > 120 else sec_text
                })
                current_lines = []
            current_title = title
            current_level = level
        else:
            current_lines.append(line)

    if current_lines:
        sec_text = "\n".join(current_lines).strip()
        words = len(sec_text.split())
        sections.append({
            "title": current_title,
            "level": current_level,
            "word_count": words,
            "is_too_short": words < 90 and words > 0,
            "preview": sec_text[:120] + "..." if len(sec_text) > 120 else sec_text
        })

    # Analisi dei difetti macrostrutturali
    total_sections = len(sections)
    too_short_sections = [s for s in sections if s["is_too_short"]]
    avg_words_per_section = (
        round(sum(s["word_count"] for s in sections) / max(1, total_sections), 1)
        if total_sections > 0 else 0
    )

    structural_flaws = []
    coalescing_recommendations = []

    if total_sections > 8 and avg_words_per_section < 150:
        structural_flaws.append({
            "issue": "IPER_FRAMMENTAZIONE",
            "description": f"Il documento è eccessivamente spezzettato ({total_sections} sezioni con media di sole {avg_words_per_section} parole). Sembra una scaletta di slide o un datasheet piuttosto che un testo narrativo o accademico coeso.",
            "severity": "HIGH"
        })

    # Rileva sezioni consecutive troppo corte che andrebbero accorpate
    consecutive_short = []
    for s in sections:
        if s["is_too_short"]:
            consecutive_short.append(s["title"])
        else:
            if len(consecutive_short) >= 2:
                coalescing_recommendations.append(
                    f"Consiglio fusione: le sezioni micro-frammentate [{', '.join(consecutive_short)}] hanno meno di 90 parole ciascuna. Dovrebbero essere accorpate in un'unica trattazione narrativa fluida."
                )
            consecutive_short = []
    if len(consecutive_short) >= 2:
        coalescing_recommendations.append(
            f"Consiglio fusione: le sezioni finali [{', '.join(consecutive_short)}] sono micro-frammentate (<90 parole) e trarrebbero beneficio da un'unificazione organica."
        )

    health = "ECCELLENTE"
    if len(too_short_sections) >= 3 or len(structural_flaws) > 0:
        health = "FRAMMENTATO"
    elif len(too_short_sections) >= 1:
        health = "BUONO"

    return {
        "file_path": file_path,
        "total_sections": total_sections,
        "average_words_per_section": avg_words_per_section,
        "too_short_sections_count": len(too_short_sections),
        "macro_health": health,
        "sections": sections,
        "flaws": structural_flaws,
        "recommendations": coalescing_recommendations or [
            "La macro-struttura è equilibrata: le sezioni hanno densità sufficiente per sviluppare argomentazioni continue senza spezzettature eccessive."
        ]
    }
