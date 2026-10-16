"""
Writing Suite - Structural Syntax & POS Sequence Diagnostic Engine
Utilizza un modello di Part-Of-Speech tagging leggero (Averaged Perceptron POS Tagger)
e analisi delle strutture grammaticali:
1. Coordinazione sintattica e parallelismi POS (NP, NP, and NP)
2. Densità lessicale (rapporto tra parole di contenuto NN/VB/JJ/RB e parole funzionali)
3. Costruzioni passive e hedging grammaticale (forme passive aux + VBN)
4. Simmetrie di punteggiatura (punto e virgola, em-dash, blocchi monoriga)
5. Aperture transizionali (avverbiali isolati all'inizio del periodo)
Zero liste di parole hardcoded. Modello statistico-grammaticale puro.
"""

import math
import re
from collections import Counter
from typing import Dict, Any, List

# Rilevamento di modelli NLP leggeri
_HAS_NLTK = False
try:
    import nltk
    from nltk import pos_tag, word_tokenize
    _HAS_NLTK = True
except Exception:
    _HAS_NLTK = False


# Pattern di fallback strutturali indipendenti dalla lingua
RE_STRUCTURAL_TRIAD = re.compile(
    r"(?:(?:\b[\w\-]+\b\s+){1,5}[\w\-]+,\s+){2}(?:and|or|e|ed|o|od)\s+(?:(?:\b[\w\-]+\b\s+){1,5}[\w\-]+)",
    re.IGNORECASE
)

RE_SEMICOLON_CLAUSE = re.compile(
    r"[a-zA-Z0-9\)]\s*;\s*[a-zA-Z]",
    re.IGNORECASE
)

RE_EMDASH_STRUCTURAL = re.compile(
    r"(?:---|—|--)\s*[a-zA-Z]",
    re.IGNORECASE
)

RE_LEADING_ADVERBIAL = re.compile(
    r"(?:^|[.!?]\s+)([A-Z][a-z]{3,18}),\s+",
    re.MULTILINE
)


def _detect_pos_parallelism(tagged_tokens: List[tuple]) -> List[str]:
    """Rileva sequenze grammaticali parallele coordinate tramite POS n-grams."""
    # Semplifica i tag in macro-categorie: N (Noun), V (Verb), J (Adj), R (Adv), C (Conj), P (Punct)
    simplified = []
    for word, tag in tagged_tokens:
        if tag.startswith("NN"):
            simplified.append(("N", word))
        elif tag.startswith("VB"):
            simplified.append(("V", word))
        elif tag.startswith("JJ"):
            simplified.append(("J", word))
        elif tag.startswith("RB"):
            simplified.append(("R", word))
        elif tag == "CC":
            simplified.append(("C", word))
        elif tag in (",", ";"):
            simplified.append(("P", word))
        else:
            simplified.append(("O", word))

    # Cerca pattern di coordinazione ternaria a livello di POS:
    # es: (N/J/V) , (N/J/V) , C (N/J/V)
    triad_instances = []
    for i in range(len(simplified) - 6):
        w = simplified[i:i+7]
        types = [x[0] for x in w]
        # Match pattern: N P N P C N oppure J P J P C J oppure V P V P C V
        if (types[0] in ("N", "J", "V") and types[1] == "P" and 
            types[2] == types[0] and types[3] == "P" and 
            types[4] == "C" and types[5] == types[0]):
            matched_words = " ".join([x[1] for x in w[:6]])
            triad_instances.append(matched_words)

    return triad_instances


def _calculate_pos_transition_entropy(tagged_tokens: List[tuple]) -> float:
    """
    Calcola l'entropia di Shannon delle transizioni bigramma tra tag POS (H_POS).
    Rileva la varietà o la rigidità delle strutture grammaticali.
    """
    tags = [t for _, t in tagged_tokens if t.isalnum() or t in (",", ".")]
    if len(tags) < 4:
        return 0.0
    bigrams = [(tags[i], tags[i+1]) for i in range(len(tags) - 1)]
    counts = Counter(bigrams)
    total = len(bigrams)
    h_pos = -sum((c / total) * math.log2(c / total) for c in counts.values())
    return round(float(h_pos), 2)


def analyze_syntax_patterns(text: str, sentences: List[str] = None) -> Dict[str, Any]:
    """Analizza le simmetrie sintattiche, la distribuzione POS e l'entropia di transizione grammaticale."""
    if sentences is None:
        from ..cleaner import extract_sentences
        sentences = extract_sentences(text)

    from ..cleaner import extract_words
    words = extract_words(text)

    signals = []
    prescriptions = []
    detected_patterns = []

    pos_info = {}
    if _HAS_NLTK and words:
        try:
            tokens = word_tokenize(text)
            tagged = pos_tag(tokens)

            # 1. Calcolo Densità Lessicale (Content POS: N, V, J, R rispetto al totale)
            content_tags = {"NN", "NNS", "NNP", "NNPS", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "JJ", "JJR", "JJS", "RB", "RBR", "RBS"}
            content_count = sum(1 for _, t in tagged if t in content_tags)
            total_clean_tokens = sum(1 for w, t in tagged if w.isalnum())
            lexical_density = (content_count / total_clean_tokens) if total_clean_tokens > 0 else 0.5
            pos_info["lexical_density"] = round(lexical_density, 3)

            # 2. Entropia di Transizione Bigramma POS
            h_pos = _calculate_pos_transition_entropy(tagged)
            pos_info["pos_transition_entropy"] = h_pos
            if len(words) >= 40 and h_pos < 4.2:
                signals.append({
                    "type": "low_pos_entropy",
                    "severity": "warning",
                    "description": f"Entropia di transizione sintattica ridotta (H_POS = {h_pos:.2f} bit, atteso ≥ 4.8): percorsi grammaticali rigidi."
                })
                prescriptions.append(
                    f"Sintassi prevedibile (H_POS = {h_pos:.2f}): diversifica le aperture proposizionali (subordinate temporali, causali, inversioni) per rompere la sequenza SVO standard."
                )
                detected_patterns.append(f"Low POS Entropy ({h_pos:.2f})")

            # 3. Rilevamento Forme Passive grammaticali: (be/been/being/is/was/were) + VBN
            passive_count = 0
            for i in range(len(tagged) - 1):
                w1, t1 = tagged[i]
                w2, t2 = tagged[i+1]
                if t1.startswith("VB") and t2 == "VBN":
                    passive_count += 1
            pos_info["passive_constructions"] = passive_count

            if passive_count >= 3:
                signals.append({
                    "type": "excessive_passive_voice",
                    "severity": "warning",
                    "description": f"Rilevate {passive_count} forme passive grammaticali concatenate."
                })
                prescriptions.append(
                    f"Rilevate {passive_count} costruzioni passive: convertile in forma attiva esplicitando l'agente o il componente software che compie l'azione."
                )
                detected_patterns.append(f"Passive Voice Chains ({passive_count})")

            # 4. Rilevamento coordinazione ternaria basato sul modello POS
            pos_triads = _detect_pos_parallelism(tagged)
            if pos_triads:
                for match in pos_triads[:2]:
                    signals.append({
                        "type": "pos_triadic_parallelism",
                        "severity": "warning",
                        "snippet": match,
                        "description": "Coordinazione ternaria rilevata a livello grammaticale POS."
                    })
                detected_patterns.append(f"POS Parallelism ({len(pos_triads)})")
        except Exception:
            pass


    # 1. Paragrafo a frase singola (varianza zero)
    if len(sentences) == 1 and len(words) >= 12:
        signals.append({
            "type": "single_sentence_block",
            "severity": "critical",
            "description": "Paragrafo a frase singola (varianza metrica zero, σ_len = 0.0)."
        })
        prescriptions.append(
            "Paragrafo a frase singola: integralo nella trattazione circostante o espandilo con evidenze empiriche."
        )
        detected_patterns.append("Single-Sentence Block")

    # 2. Elenchi ternari (fallback strutturale se non già presi dal modello POS)
    if not any("POS Parallelism" in p for p in detected_patterns):
        triad_matches = RE_STRUCTURAL_TRIAD.findall(text)
        if triad_matches:
            for match in triad_matches[:2]:
                signals.append({
                    "type": "triadic_list",
                    "severity": "warning",
                    "snippet": match.strip()[:80],
                    "description": "Elenco ternario bilanciato (struttura sintattica a 3 elementi)."
                })
            prescriptions.append(
                f"Rilevati {len(triad_matches)} elenchi ternari: rompi la simmetria a tre (cita solo due elementi o trasforma il terzo in proposizione subordinata causale)."
            )
            detected_patterns.append(f"Triadic Parallelism ({len(triad_matches)})")

    # 3. Punteggiatura simmetrica con punto e virgola
    semicolon_matches = RE_SEMICOLON_CLAUSE.findall(text)
    if len(semicolon_matches) >= 2 or (len(semicolon_matches) == 1 and len(sentences) <= 3):
        signals.append({
            "type": "semicolon_symmetry",
            "severity": "warning",
            "description": "Struttura binaria con punto e virgola a proposizioni bilanciate."
        })
        prescriptions.append(
            "Periodo bilanciato con punto e virgola: preferisci periodi asimmetrici, frasi brevi assertive o subordinate esplicite."
        )
        detected_patterns.append("Semicolon Symmetries")

    # 4. Incisi con em-dash
    emdash_matches = RE_EMDASH_STRUCTURAL.findall(text)
    if emdash_matches:
        signals.append({
            "type": "emdash_clause",
            "severity": "warning",
            "description": "Inciso separato da em-dash / trattino lungo."
        })
        prescriptions.append(
            "Inciso con trattino lungo: articola la spiegazione in una frase autonoma per spezzare il flusso continuo."
        )
        detected_patterns.append("Appositive Em-dash")

    # 5. Aperture con avverbiale isolato
    leading_adv = RE_LEADING_ADVERBIAL.findall(text)
    if leading_adv:
        connectors = list(set(leading_adv))
        signals.append({
            "type": "leading_connector",
            "severity": "warning",
            "description": f"Connettori iniziali isolati da virgola: {', '.join(connectors)}."
        })
        prescriptions.append(
            f"Aperture con avverbiale isolato ({', '.join(connectors)}): elimina la parola introduttiva e inizia direttamente con il soggetto o il dato sperimentale."
        )
        detected_patterns.append(f"Leading Adverbials ({len(connectors)})")

    # Determinazione dello status
    has_critical = any(s["severity"] == "critical" for s in signals)
    has_warning = any(s["severity"] == "warning" for s in signals)

    if has_critical or len(signals) >= 3:
        status = "critical"
        score = 80.0
    elif has_warning or len(signals) >= 1:
        status = "warning"
        score = 45.0
    else:
        status = "safe"
        score = 10.0

    return {
        "status": status,
        "score": score,
        "patterns_detected": detected_patterns,
        "pos_info": pos_info,
        "signals": signals,
        "prescriptions": prescriptions
    }
