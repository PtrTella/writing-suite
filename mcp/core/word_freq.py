"""
Writing Suite - Word Frequency & Forensic GLTR Engine
Implementa:
1. Lexicon di frequenza Zipf normalizzato integrato con LanguageRegistry
2. Profilazione Forense GLTR (Giant Language Model Test Room - Harvard/MIT) a 5 bucket:
   - Green: Top 10 (Funzioni grammaticali, connettori essenziali)
   - Yellow: Top 100 (Pronomi, verbi ausiliari, preposizioni ad altissima frequenza)
   - Red: Top 1000 (Lessico comune, sostantivi e verbi base)
   - Orange: Top 3000 (Lessico esteso, terminologia di settore standard)
   - Purple/Tail: Fuori dai Top 3000 (Lessico specialistico, creativo o idiosincratico umano)
3. MTLD (Measure of Textual Lexical Diversity - McCarthy & Jarvis 2010), invariante rispetto alla lunghezza
4. Valutazione continua tramite funzioni logistiche differenziabili (senza soglie discrete)
"""

import math
import re
from typing import Dict, List
from .languages import LanguageRegistry, BaseLanguagePack

def calculate_gltr_profile(words: List[str], lang: str = "it") -> Dict:
    """
    Calcola la distribuzione forense GLTR del testo sui 5 bucket di probabilità Zipf.
    Applica una funzione logistica continua su tail_pct (senza scatti o soglie fisse).
    """
    pack = LanguageRegistry.get(lang)
    total = len(words)
    if total == 0:
        return {
            "top_10_pct": 0.0,
            "top_100_pct": 0.0,
            "top_1000_pct": 0.0,
            "top_3000_pct": 0.0,
            "tail_pct": 0.0,
            "saturation_pct": 0.0,
            "gltr_risk_score": 50.0
        }

    b_counts = [0, 0, 0, 0, 0]
    for w in words:
        b = pack.get_word_bucket(w)
        b_counts[b - 1] += 1

    p1 = round((b_counts[0] / total) * 100.0, 1)
    p2 = round((b_counts[1] / total) * 100.0, 1)
    p3 = round((b_counts[2] / total) * 100.0, 1)
    p4 = round((b_counts[3] / total) * 100.0, 1)
    p5 = round((b_counts[4] / total) * 100.0, 1)
    saturation = round(p1 + p2 + p3 + p4, 1)
    tail_pct = p5

    # Curva logistica continua: midpoint a 14% di coda, steepness 0.25
    gltr_risk = 100.0 / (1.0 + math.exp(0.25 * (tail_pct - 14.0)))

    return {
        "top_10_pct": p1,
        "top_100_pct": p2,
        "top_1000_pct": p3,
        "top_3000_pct": p4,
        "tail_pct": tail_pct,
        "saturation_pct": saturation,
        "gltr_risk_score": round(gltr_risk, 1)
    }

def calculate_sentence_zipf_surprisal(sentence: str, lang: str = "it") -> float:
    """Calcola l'entropia media della frase basata sul valore Zipf reale delle parole."""
    pack = LanguageRegistry.get(lang)
    words = re.findall(r"\b[a-zA-ZàèéìòùÀÈÉÌÒÙ0-9'-]+\b", sentence.lower())
    if not words:
        return 50.0

    surprisals = [(7.5 - pack.get_word_zipf(w)) for w in words]
    mean_surprisal = sum(surprisals) / len(words)
    score = (mean_surprisal / 5.0) * 85.0
    return round(max(5.0, min(100.0, score)), 1)

def calculate_mtld(words: List[str], threshold: float = 0.72) -> float:
    """
    Calcola il Measure of Textual Lexical Diversity (MTLD, McCarthy & Jarvis 2010).
    Invariante rispetto alla lunghezza del documento.
    """
    if len(words) < 15:
        return 50.0

    def _factor_count(seq: List[str]) -> float:
        factors = 0.0
        current_types = set()
        tokens = 0
        ttr = 1.0
        for w in seq:
            tokens += 1
            current_types.add(w)
            ttr = len(current_types) / tokens
            if ttr <= threshold:
                factors += 1.0
                current_types = set()
                tokens = 0
        if tokens > 0:
            partial_factor = (1.0 - ttr) / (1.0 - threshold) if ttr < 1.0 else 0.0
            factors += max(0.0, min(1.0, partial_factor))
        return len(seq) / max(0.001, factors)

    forward = _factor_count(words)
    backward = _factor_count(list(reversed(words)))
    return round((forward + backward) / 2.0, 1)
