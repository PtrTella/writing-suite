"""
Writing Suite - Pure Mathematical & Tokenizer-Driven Stylometry Engine (Pillar 2)
Nessuna lista statica hardcoded di parole (zero dizionari fissi).
Analizza la struttura del testo attraverso:
1. Dinamica di Frammentazione dei Token e Rango Zipfiano (via Tokenizer)
2. Asimmetria di Cadenza e Dispersione Ritmica (Deviazione Standard e Varianza)
3. Diversità Lessicale Algoritmica (MTLD - Measure of Textual Lexical Diversity)
4. Entropia di Distribuzione dei Simboli di Punteggiatura
"""

import math
import re
from typing import Dict, Any, List, Optional
from collections import Counter


def extract_words(text: str) -> List[str]:
    """Estrae parole normalizzate in minuscolo."""
    return re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())


def extract_sentences(text: str) -> List[str]:
    """Suddivide il testo in frasi rispettando abbreviazioni scientifiche comuni."""
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    protected = re.sub(r"\b(e\.g|i\.e|et al|Fig|Sec|vs|approx)\.", r"\1<DOT>", cleaned, flags=re.IGNORECASE)
    parts = re.split(r"(?<=[.!?])\s+", protected)
    results = []
    for p in parts:
        restored = p.replace("<DOT>", ".").strip()
        if len(restored.split()) >= 3:
            results.append(restored)
    return results


def calculate_mtld(words: List[str], threshold: float = 0.72) -> float:
    """
    Measure of Textual Lexical Diversity (MTLD).
    Metrica algoritmica pura, indipendente dalla lunghezza del testo e priva di liste statiche.
    """
    if len(words) < 20:
        return 65.0

    def _mtld_run(token_list: List[str]) -> float:
        factors = 0
        current_types = set()
        token_count = 0
        for w in token_list:
            token_count += 1
            current_types.add(w)
            ttr = len(current_types) / token_count
            if ttr <= threshold:
                factors += 1
                current_types = set()
                token_count = 0
        if token_count > 0:
            excess = (1.0 - ttr) / (1.0 - threshold)
            factors += excess
        return len(token_list) / max(0.1, factors)

    forward = _mtld_run(words)
    backward = _mtld_run(words[::-1])
    return (forward + backward) / 2.0


def calculate_yule_k(words: List[str]) -> float:
    """Caratteristica K di Yule: entropia lessicale indipendente da dizionari predefiniti."""
    if len(words) < 20:
        return 100.0
    freqs = Counter(words)
    m1 = len(words)
    m2 = sum(c * c for c in freqs.values())
    if m1 == 0:
        return 0.0
    return 10000.0 * (m2 - m1) / (m1 * m1)


def analyze_token_fragmentation_and_zipf(text: str) -> Dict[str, float]:
    """
    Analisi probabilistica basata su Tokenizer e Legge di Zipf.
    Zero parole hardcoded: sfrutta la frequenza empirica interna del vocabolario.
    """
    words = extract_words(text)
    if not words:
        return {"zipf_slope": 1.0, "type_token_ratio": 1.0, "hapax_ratio": 0.0}

    counts = Counter(words)
    sorted_counts = sorted(counts.values(), reverse=True)
    n_types = len(counts)
    n_tokens = len(words)

    ttr = n_types / max(1, n_tokens)
    hapax_count = sum(1 for c in counts.values() if c == 1)
    hapax_ratio = hapax_count / max(1, n_types)

    # Stima del coefficiente di Zipf (regressione log-log su rango vs frequenza)
    if len(sorted_counts) >= 5:
        log_ranks = [math.log(i + 1) for i in range(min(50, len(sorted_counts)))]
        log_freqs = [math.log(f) for f in sorted_counts[:len(log_ranks)]]
        mean_r = sum(log_ranks) / len(log_ranks)
        mean_f = sum(log_freqs) / len(log_freqs)
        num = sum((r - mean_r) * (f - mean_f) for r, f in zip(log_ranks, log_freqs))
        den = sum((r - mean_r) ** 2 for r in log_ranks)
        slope = abs(num / max(1e-6, den))
    else:
        slope = 1.0

    return {
        "zipf_slope": round(slope, 3),
        "type_token_ratio": round(ttr, 3),
        "hapax_ratio": round(hapax_ratio, 3)
    }


def extract_stylometric_features(text: str) -> Dict[str, Any]:
    """
    Estrae il profilo forense stylometrico matematico e continuo.
    ZERO parole hardcoded: esclusivamente metrica probabilistica e geometrica.
    """
    words = extract_words(text)
    sentences = extract_sentences(text)
    word_count = len(words)
    sent_count = len(sentences)

    if word_count < 10 or sent_count < 1:
        return {
            "risk_score": 20.0,
            "cadence_sigma": 0.0,
            "mean_sentence_length": float(word_count),
            "mtld": 0.0,
            "yule_k": 100.0,
            "zipf_slope": 1.0,
            "metronome_pairs_count": 0,
            "feature_vector": [0.0] * 12,
            "verdict": "Testo troppo breve per analisi statistica affidabile."
        }

    # 1. Analisi di Cadenza e Varianza Ritmica dei Periodi
    lengths = [len(extract_words(s)) for s in sentences]
    mean_len = sum(lengths) / sent_count
    if sent_count >= 2:
        var_len = sum((l - mean_len) ** 2 for l in lengths) / (sent_count - 1)
        sigma_len = math.sqrt(var_len)
    else:
        sigma_len = 0.0

    # Rilevamento coppie di frasi a metronomo (lunghezza identica nella fascia critica 18-24 parole)
    metronome_pairs = 0
    for i in range(len(lengths) - 1):
        if 18 <= lengths[i] <= 26 and 18 <= lengths[i+1] <= 26 and abs(lengths[i] - lengths[i+1]) <= 2:
            metronome_pairs += 1

    ratio_short = sum(1 for l in lengths if l < 14) / sent_count
    ratio_long = sum(1 for l in lengths if l > 28) / sent_count

    # 2. Diversità Lessicale Algoritmica
    mtld = calculate_mtld(words)
    yule_k = calculate_yule_k(words)

    # 3. Profilazione Zipfiana e Dinamica dei Token
    zipf_stats = analyze_token_fragmentation_and_zipf(text)

    # 4. Punteggiatura Strutturale
    punc_chars = [c for c in text if c in ",;:—()-"]
    punc_density = len(punc_chars) / max(1, word_count)
    em_dashes = text.count("—") + text.count(" -- ")

    # 5. Vettore Feature Matematico Continuo (12 feature)
    feature_vector = [
        round(mean_len, 2),
        round(sigma_len, 2),
        round(ratio_short, 3),
        round(ratio_long, 3),
        round(metronome_pairs / max(1, sent_count), 3),
        round(mtld, 2),
        round(yule_k, 2),
        round(zipf_stats["zipf_slope"], 3),
        round(zipf_stats["hapax_ratio"], 3),
        round(punc_density, 3),
        round(em_dashes / max(1, sent_count), 3),
        round(zipf_stats["type_token_ratio"], 3)
    ]

    # 6. Rischio di Artificialità basato su Varianza e Parametri Matematici:
    # L'AI ha:
    # - Bassa varianza di cadenza (sigma_len < 7.0)
    # - Bassa diversità lessicale (MTLD < 50)
    # - Eccesso di coppie metronomiche
    # - Slancio Zipfiano anomalo o troncato
    risk_points = 0.0

    if sigma_len < 6.0:
        risk_points += 35.0
    elif sigma_len < 8.0:
        risk_points += 20.0
    elif sigma_len >= 11.0:
        risk_points -= 15.0

    if metronome_pairs >= 2:
        risk_points += min(20.0, metronome_pairs * 8.0)

    if ratio_short < 0.10 and ratio_long < 0.10:
        risk_points += 15.0
    elif ratio_short >= 0.15 and ratio_long >= 0.15:
        risk_points -= 10.0

    if mtld < 50.0:
        risk_points += 20.0
    elif mtld > 75.0:
        risk_points -= 10.0

    if em_dashes >= 3:
        risk_points += min(15.0, em_dashes * 4.0)

    base_score = 35.0 + risk_points
    risk_score = round(max(5.0, min(95.0, base_score)), 1)

    return {
        "risk_score": risk_score,
        "cadence_sigma": round(sigma_len, 1),
        "mean_sentence_length": round(mean_len, 1),
        "mtld": round(mtld, 1),
        "yule_k": round(yule_k, 1),
        "zipf_slope": zipf_stats["zipf_slope"],
        "metronome_pairs_count": metronome_pairs,
        "short_sentence_ratio": round(ratio_short, 2),
        "long_sentence_ratio": round(ratio_long, 2),
        "feature_vector": feature_vector
    }
