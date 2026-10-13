"""
Writing Suite - Metrics Module
Motore deterministico matematico per il calcolo di:
1. Indice di Sorpresa (Emulatore Perplessità GPTZero locale) e Burstiness Frase-per-Frase
2. Stilometria Accademica Continua (Hapax Legomena Ratio e Caratteristica K di Yule)
3. Indici di Leggibilità: Gulpease (Italiano), Flesch-Kincaid (Inglese), Dispersione Sillabica
4. Analizzatore Anti-Bypass (Rilevamento frammentazione artificiale e stuffing)
"""

import math
import re
from collections import Counter
from .cleaner import extract_sentences, extract_words

# Dizionario di frequenze lessicali di riferimento (Top frequent token stopwords)
COMMON_TOKENS_IT = {
    "di", "a", "da", "in", "con", "su", "per", "tra", "fra", "il", "lo", "la", "i", "gli", "le",
    "un", "uno", "una", "e", "ed", "o", "ma", "se", "perché", "che", "cui", "quale", "quali",
    "è", "sono", "era", "erano", "stato", "stata", "stati", "state", "ha", "hanno", "aveva",
    "questo", "questa", "questi", "queste", "quello", "quella", "quelli", "quelle", "come", "anche",
    "più", "molto", "tutto", "tutti", "tutta", "tutte", "non", "solo", "prima", "dopo", "mentre"
}

COMMON_TOKENS_EN = {
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for", "not", "on",
    "with", "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they", "we",
    "say", "her", "she", "or", "an", "will", "my", "one", "all", "would", "there", "their",
    "what", "so", "up", "out", "if", "about", "who", "get", "which", "go", "me", "when", "make"
}

def count_syllables_it(word: str) -> int:
    """Stima approssimata delle sillabe per l'italiano (conteggio vocali e dittonghi normalizzati)."""
    w = word.lower()
    vowels = re.findall(r"[aeiouàèéìòù]", w)
    return max(1, len(vowels))

def count_syllables_en(word: str) -> int:
    """Stima delle sillabe per l'inglese."""
    w = word.lower()
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:[^laeiouy]|ed|es|e)$", "", w)
    w = re.sub(r"^y", "", w)
    vowels = re.findall(r"[aeiouy]{1,2}", w)
    return max(1, len(vowels))

def calculate_sentence_ppl_proxy(sentence: str) -> float:
    """
    Calcola un indice di sorpresa locale (0-100) per la frase.
    Frasi composte da token comuni adiacenti in ordine lineare ottengono sorpresa bassa (tipico AI).
    Frasi con lessico specialistico, punteggiatura complessa e variazioni ottengono sorpresa alta.
    """
    words = re.findall(r"\b[a-zA-ZàèéìòùÀÈÉÌÒÙ0-9'-]+\b", sentence.lower())
    if not words:
        return 50.0

    length = len(words)
    common_set = COMMON_TOKENS_IT | COMMON_TOKENS_EN
    common_count = sum(1 for w in words if w in common_set)
    rare_count = length - common_count

    # Calcolo entropia n-gramma approssimata
    bigrams = list(zip(words[:-1], words[1:])) if len(words) > 1 else []
    repeated_bigrams = len(bigrams) - len(set(bigrams))

    base_surprise = (rare_count / max(1, length)) * 75.0
    structural_bonus = min(25.0, (len(set(words)) / max(1, length)) * 20.0)
    repetition_penalty = repeated_bigrams * 5.0

    score = max(5.0, min(100.0, base_surprise + structural_bonus - repetition_penalty))
    return round(score, 1)

def calculate_perplexity_and_burstiness(sentences: list[str]) -> dict:
    """Calcola la perplessità media, la burstiness di sorpresa e la mappa frase-per-frase."""
    if not sentences:
        return {
            "mean_ppl": 50.0,
            "burstiness": 0.0,
            "heatmap": [],
            "risk_score": 50.0,
            "most_robotic": None,
            "most_human": None
        }

    sentence_scores = []
    for s in sentences:
        ppl = calculate_sentence_ppl_proxy(s)
        sentence_scores.append({"text": s, "ppl": ppl, "words": len(s.split())})

    ppls = [item["ppl"] for item in sentence_scores]
    mean_ppl = sum(ppls) / len(ppls)

    # Burstiness = Deviazione Standard della sorpresa
    variance = sum((p - mean_ppl) ** 2 for p in ppls) / max(1, len(ppls))
    burstiness = math.sqrt(variance)

    # Classificazione heatmap frase-per-frase
    heatmap = []
    for item in sentence_scores:
        p = item["ppl"]
        if p >= 55.0:
            status = "HUMAN_LIKE"
            badge = "🟢"
        elif p >= 40.0:
            status = "MIXED"
            badge = "🟡"
        else:
            status = "AI_SUSPECT"
            badge = "🔴"
        heatmap.append({
            "text": item["text"],
            "ppl": p,
            "words": item["words"],
            "status": status,
            "badge": badge
        })

    sorted_by_ppl = sorted(sentence_scores, key=lambda x: x["ppl"])
    most_robotic = sorted_by_ppl[0] if sorted_by_ppl else None
    most_human = sorted_by_ppl[-1] if sorted_by_ppl else None

    # Calibrazione lineare continua del rischio (niente scatti fissi)
    # Target umano autentico: mean_ppl >= 55 e burstiness >= 18
    # Testo AI puro: mean_ppl <= 38 e burstiness <= 8
    risk_ppl = max(0.0, min(100.0, (55.0 - mean_ppl) * 4.0))
    risk_burst = max(0.0, min(100.0, (18.0 - burstiness) * 5.0))
    risk_score = round(0.55 * risk_ppl + 0.45 * risk_burst, 1)

    return {
        "mean_ppl": round(mean_ppl, 1),
        "burstiness": round(burstiness, 1),
        "heatmap": heatmap,
        "risk_score": risk_score,
        "most_robotic": most_robotic,
        "most_human": most_human
    }

def calculate_stylometrics(words: list[str]) -> dict:
    """Calcola la ricchezza lessicale continua: Hapax Legomena e Caratteristica K di Yule."""
    if not words or len(words) < 5:
        return {"hapax_ratio": 0.0, "yule_k": 0.0, "risk_score": 50.0}

    freq = Counter(words)
    total_words = len(words)
    hapax_count = sum(1 for count in freq.values() if count == 1)
    hapax_ratio = (hapax_count / total_words) * 100.0

    # Calcolo della Caratteristica K di Yule
    # K = 10^4 * (sum(f_i * i^2) - N) / N^2
    m1 = total_words
    m2 = sum(c * c for c in freq.values())
    if m1 > 1:
        yule_k = 10000.0 * (m2 - m1) / (m1 * m1)
    else:
        yule_k = 0.0

    # Calibrazione continua
    # Negli umani: hapax_ratio > 50%, Yule K tra 60 e 140
    # Negli AI: lessico standardizzato, hapax_ratio spesso basso o artificialmente piatto
    risk_hapax = max(0.0, min(100.0, (55.0 - hapax_ratio) * 2.5))
    risk_score = round(risk_hapax, 1)

    return {
        "hapax_ratio": round(hapax_ratio, 1),
        "yule_k": round(yule_k, 1),
        "risk_score": risk_score
    }

def calculate_readability(text: str, lang: str = "it") -> dict:
    """
    Calcola gli indici di leggibilità e cadenza:
    - Italiano: Indice Gulpease (89 + (300*frasi - 10*lettere)/parole)
    - Inglese: Flesch-Kincaid Reading Ease & Grade Level
    - Metriche di ritmo: deviazione standard lunghezza frasi e dispersione sillabica (stile Copyleaks)
    """
    sentences = extract_sentences(text)
    words = extract_words(text)

    num_sentences = max(1, len(sentences))
    num_words = max(1, len(words))

    # Deviazione standard lunghezza frasi (words per sentence)
    lens = [len(s.split()) for s in sentences]
    avg_sentence_len = sum(lens) / num_sentences
    var_sentence_len = sum((l - avg_sentence_len) ** 2 for l in lens) / num_sentences
    std_sentence_len = round(math.sqrt(var_sentence_len), 1)

    # Dispersione sillabica (stile Copyleaks)
    if lang == "it":
        syllables = [count_syllables_it(w) for w in words]
        # Formula Gulpease
        letters_count = sum(len(w) for w in words)
        gulpease = 89 + ((300 * num_sentences) - (10 * letters_count)) / num_words
        gulpease_score = round(max(0.0, min(100.0, gulpease)), 1)
        flesch_score = None
        target_eval = "Facile (Scuole medie)" if gulpease_score > 60 else ("Medio (Diploma)" if gulpease_score > 40 else "Complesso / Accademico (Laurea)")
    else:
        syllables = [count_syllables_en(w) for w in words]
        total_syllables = sum(syllables)
        # Flesch Reading Ease = 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
        flesch = 206.835 - 1.015 * (num_words / num_sentences) - 84.6 * (total_syllables / num_words)
        flesch_score = round(max(0.0, min(100.0, flesch)), 1)
        gulpease_score = None
        target_eval = "Standard / Accessible" if flesch_score > 50 else "Difficult / Academic"

    avg_syllables = sum(syllables) / num_words
    var_syllables = sum((s - avg_syllables) ** 2 for s in syllables) / num_words
    std_syllables = round(math.sqrt(var_syllables), 2)

    return {
        "language": lang,
        "sentences_count": num_sentences,
        "words_count": num_words,
        "avg_sentence_length": round(avg_sentence_len, 1),
        "sentence_length_std": std_sentence_len,
        "avg_syllables_per_word": round(avg_syllables, 2),
        "syllable_dispersion": std_syllables,
        "gulpease": gulpease_score,
        "flesch_reading_ease": flesch_score,
        "interpretation": target_eval
    }

def check_anti_bypass(text: str, sentences: list[str]) -> dict:
    """Rileva tecniche artificiali tipiche dei bypasser commerciali (Text2Go / bypass spammers)."""
    if not sentences:
        return {"risk_score": 0.0, "anomalies": []}

    anomalies = []
    # 1. Frammentazione artificiale (troppe micro-frasi sotto 4 parole)
    micro_sentences = [s for s in sentences if len(s.split()) <= 3]
    micro_ratio = len(micro_sentences) / len(sentences)
    if micro_ratio > 0.22:
        anomalies.append(f"Tasso anomalo di micro-frasi ({micro_ratio*100:.1f}%): possibile spezzettamento artificiale.")

    # 2. Aperture artificiosamente informali a stampino
    fake_openers = re.findall(r"(?im)^(?:Honestly|Basically|Look|Listen|To be clear|Real talk),", text)
    if len(fake_openers) >= 3:
        anomalies.append(f"Frequenza anomala di incipit colloquiali forzati ({len(fake_openers)} trovati).")

    risk_score = min(100.0, len(anomalies) * 45.0)
    return {
        "risk_score": round(risk_score, 1),
        "anomalies": anomalies
    }
