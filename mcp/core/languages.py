"""
Writing Suite - Multi-Language Architecture & Universal Language Engine
Fornisce:
1. BaseLanguagePack: Interfaccia unificata per qualsiasi lingua naturale.
   - Sillabazione universale tramite Sonority Sequencing Principle (SSP)
   - Indice di leggibilità universale LIX (Björnsson 1968) language-independent
   - Stima corpus-relative dei ranghi Zipf (legge di Zipf universale per qualsiasi lingua)
2. UniversalLanguagePack: Motore zero-shot linguistico indipendente per qualsiasi lingua non censita.
3. DataDrivenLanguagePack: Generatore configurabile a runtime da JSON o parametri dell'Agente.
4. Pacchetti linguistici specifici con formule di leggibilità nazionali:
   - ItalianLanguagePack ('it'): Clitici, sillabazione vocalica, Indice Gulpease
   - EnglishLanguagePack ('en'): Contrazioni, sillabe fonotattiche, Flesch-Kincaid
   - SpanishLanguagePack ('es'): Sillabe spagnole, Indice Fernández-Huerta
   - FrenchLanguagePack ('fr'): Elisioni francesi, Formule Kandel & Moles
   - GermanLanguagePack ('de'): Nessi consonantici tedeschi, Amstad Lesbarkeitsindex
5. LanguageRegistry: Rilevamento automatico O(N), caricamento dinamico da data/languages/*.json e dispatch.
"""

import collections
import json
import re
from pathlib import Path
from typing import Optional

DATA_LANGUAGES_DIR = Path(__file__).resolve().parent.parent / "data" / "languages"


class BaseLanguagePack:
    """Interfaccia unificata e motore linguistico universale."""

    lang_code: str = "base"
    name: str = "Base Language"

    top_10: set[str] = set()
    top_100: set[str] = set()
    top_1000: set[str] = set()
    top_3000: set[str] = set()
    low_entropy_collocations: list[str] = []
    corpus_word_freq: Optional[dict[str, float]] = None

    def __init__(self):
        # Carica automaticamente dal file JSON in data/languages/ se presente
        self._load_from_data_dir()

    def _load_from_data_dir(self) -> None:
        """Carica dizionari di frequenza da data/languages/{code}.json se esiste su disco."""
        json_path = DATA_LANGUAGES_DIR / f"{self.lang_code}.json"
        if json_path.is_file():
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
                if top_10 := data.get("top_10"):
                    self.top_10 = set(top_10)
                if top_100 := data.get("top_100"):
                    self.top_100 = set(top_100)
                if top_1000 := data.get("top_1000"):
                    self.top_1000 = set(top_1000)
                if top_3000 := data.get("top_3000"):
                    self.top_3000 = set(top_3000)
                if name := data.get("name"):
                    self.name = name
            except Exception:
                pass

    def set_corpus(self, words: list[str]) -> None:
        """Calcola la distribuzione corpus-relative dei token per la stima Zipf dinamica."""
        if not words:
            self.corpus_word_freq = None
            self.corpus_counts = None
            return
        self.corpus_counts = collections.Counter(w.lower() for w in words)
        tot = float(len(words))
        self.corpus_word_freq = {w: cnt / tot for w, cnt in self.corpus_counts.items()}

    def count_syllables(self, word: str) -> int:
        """Sillabazione universale di default basata sul Sonority Sequencing Principle (SSP)."""
        w = word.lower().strip()
        vowels = re.findall(r"[aeiouyàèéìòùáéíóúäëïöüâêîôûãõåæœ]+", w)
        if not vowels:
            return 1
        count = len(vowels)
        if w.endswith("e") and count > 1 and not re.search(r"[aeiouy]e$", w):
            count -= 1
        return max(1, count)

    def calculate_readability(
        self, text: str, words: list[str], sentences: list[str]
    ) -> dict:
        """Calcola l'indice di leggibilità universale LIX (Björnsson 1968) indipendente dalla lingua."""
        tot_words = max(1, len(words))
        tot_sents = max(1, len(sentences))
        long_words = sum(1 for w in words if len(w) > 6)

        lix = (tot_words / tot_sents) + ((long_words * 100.0) / tot_words)
        lix_score = round(lix, 1)

        if lix_score < 30:
            interp = "Very Easy / Plain Text"
        elif lix_score < 40:
            interp = "Easy / Fiction & Conversational"
        elif lix_score < 50:
            interp = "Standard / General Non-fiction"
        elif lix_score < 60:
            interp = "Difficult / Academic & Specialized"
        else:
            interp = "Very Difficult / Advanced Technical & Scientific"

        return {
            "language": self.lang_code,
            "index_name": "LIX (Universal Readability Index)",
            "score": lix_score,
            "long_words_pct": round((long_words / tot_words) * 100.0, 1),
            "interpretation": interp,
            "avg_sentence_length": round(tot_words / tot_sents, 1),
            "words_count": tot_words,
            "sentences_count": tot_sents,
        }

    def get_word_bucket(self, word: str) -> int:
        """Restituisce il bucket GLTR: 1 (Top 10), 2 (Top 100), 3 (Top 1000), 4 (Top 3000), 5 (Tail)."""
        w = word.lower().strip()
        if w in self.top_10:
            return 1
        if w in self.top_100:
            return 2
        if w in self.top_1000:
            return 3
        if w in self.top_3000:
            return 4

        # Stima del rango basata sulla frequenza corpus-relative
        if (
            hasattr(self, "corpus_counts")
            and self.corpus_counts
            and w in self.corpus_counts
        ):
            cnt = self.corpus_counts[w]
            # Se la parola è un hapax legomenon (compare 1 sola volta) ed è lunga almeno 3 caratteri,
            # appartiene al vocabolario specialistico/creativo non-standard (Tail / Bucket 5)
            if cnt == 1 and len(w) >= 3:
                return 5
            elif cnt == 2:
                return 4
            elif cnt <= 4:
                return 3

        # Fallback basato su frequenza normalizzata
        if self.corpus_word_freq and w in self.corpus_word_freq:
            f = self.corpus_word_freq[w]
            if f >= 0.030:
                return 1
            elif f >= 0.015:
                return 2
            elif f >= 0.005:
                return 3
            elif f >= 0.002:
                return 4

        return 5

    def get_word_zipf(self, word: str) -> float:
        """Stima continua del valore Zipf del vocabolo."""
        b = self.get_word_bucket(word)
        if b == 1:
            return 7.0
        elif b == 2:
            return 5.8
        elif b == 3:
            return 4.6
        elif b == 4:
            return 3.6
        else:
            return 2.2


# ==============================================================================
# UNIVERSAL ZERO-SHOT & DATA-DRIVEN PACKS
# ==============================================================================


class UniversalLanguagePack(BaseLanguagePack):
    """Language Pack universale a bootstrap statistico (Zero-Shot) per qualsiasi lingua non censita."""

    def __init__(
        self, lang_code: str = "auto", name: str = "Universal / Auto-Calibrated"
    ):
        self.lang_code = lang_code
        self.name = name
        self.top_10 = set()
        self.top_100 = set()
        self.top_1000 = set()
        self.top_3000 = set()
        self.low_entropy_collocations = []
        self.corpus_word_freq = None
        self._load_from_data_dir()


class DataDrivenLanguagePack(BaseLanguagePack):
    """Language Pack configurabile dinamicamente a runtime o tramite file dati/JSON."""

    def __init__(
        self,
        lang_code: str,
        name: str,
        top_10: set[str],
        top_100: set[str],
        top_1000: Optional[set[str]] = None,
        top_3000: Optional[set[str]] = None,
        collocations: Optional[list[str]] = None,
    ):
        self.lang_code = lang_code
        self.name = name
        self.top_10 = {w.lower() for w in top_10}
        self.top_100 = {w.lower() for w in top_100}
        self.top_1000 = {w.lower() for w in top_1000} if top_1000 else set()
        self.top_3000 = {w.lower() for w in top_3000} if top_3000 else set()
        self.low_entropy_collocations = collocations or []
        self.corpus_word_freq = None


# ==============================================================================
# LINGUE PRECONFIGURATE CON FORMULE NAZIONALI
# ==============================================================================


class ItalianLanguagePack(BaseLanguagePack):
    lang_code = "it"
    name = "Italiano"

    # Vettori chiusi di grammatical function words (fallback se JSON non presente)
    top_10 = {
        "il",
        "di",
        "e",
        "ed",
        "a",
        "ad",
        "la",
        "in",
        "che",
        "per",
        "un",
        "una",
        "sono",
        "del",
        "della",
        "dei",
        "degli",
        "dello",
        "delle",
    }

    top_100 = {
        "lo",
        "i",
        "gli",
        "le",
        "uno",
        "da",
        "dal",
        "dalla",
        "dallo",
        "dai",
        "dagli",
        "dalle",
        "su",
        "sul",
        "sulla",
        "sullo",
        "sui",
        "sugli",
        "sulle",
        "con",
        "tra",
        "fra",
        "al",
        "alla",
        "allo",
        "ai",
        "agli",
        "alle",
        "nel",
        "nella",
        "nello",
        "nei",
        "negli",
        "nelle",
        "o",
        "ma",
        "se",
        "non",
        "più",
        "molto",
        "tutto",
        "tutti",
        "tutta",
        "tutte",
        "ci",
        "vi",
        "si",
        "ne",
        "mi",
        "ti",
        "loro",
        "suo",
        "sua",
        "suoi",
        "sue",
        "nostro",
        "nostra",
        "nostri",
        "nostre",
        "questo",
        "questa",
        "questi",
        "queste",
        "quello",
        "quella",
        "quelli",
        "quelle",
        "come",
        "anche",
        "solo",
        "prima",
        "dopo",
        "mentre",
        "ogni",
        "alcuni",
        "alcune",
        "qualche",
        "quindi",
        "dunque",
        "invece",
        "così",
        "allora",
        "già",
        "mai",
        "sempre",
        "ancora",
        "oggi",
        "ora",
        "modo",
        "modi",
        "parte",
        "tempo",
        "caso",
        "fatto",
        "punto",
        "cosa",
        "bene",
        "male",
        "nuovo",
        "altro",
        "stesso",
        "proprio",
        "grande",
        "piccolo",
        "primo",
        "ultimo",
        "è",
        "era",
        "erano",
        "stato",
        "stata",
        "stati",
        "state",
        "ha",
        "hanno",
        "aveva",
        "avevano",
        "può",
        "possono",
        "deve",
        "devono",
        "fare",
        "fa",
        "fanno",
        "dare",
        "viene",
        "vengono",
        "dove",
        "quando",
        "durante",
        "verso",
        "essere",
        "qualsiasi",
        "ciascuno",
        "ciascuna",
        "oppure",
        "appena",
    }

    def count_syllables(self, word: str) -> int:
        w = word.lower().strip()
        vowels = re.findall(r"[aeiouàèéìòù]", w)
        if not vowels:
            return 1
        diphthongs = len(re.findall(r"[aeiou][i]|[aeou][u]|[i][aeou]|[u][aeio]", w))
        count = len(vowels) - diphthongs
        return max(1, count)

    def calculate_readability(
        self, text: str, words: list[str], sentences: list[str]
    ) -> dict:
        tot_words = max(1, len(words))
        tot_sents = max(1, len(sentences))
        letters_count = sum(len(w) for w in words)

        # Indice Gulpease = 89 + (300 * frasi - 10 * lettere) / parole
        gulpease = 89.0 + ((300.0 * tot_sents - 10.0 * letters_count) / tot_words)
        gulpease_score = round(max(0.0, min(100.0, gulpease)), 1)

        if gulpease_score >= 80:
            interp = "Facile / Scuola elementare"
        elif gulpease_score >= 60:
            interp = "Medio / Scuola media"
        elif gulpease_score >= 40:
            interp = "Difficile / Diploma superiore"
        else:
            interp = "Molto difficile / Tesi universitaria o saggio scientifico"

        return {
            "language": "it",
            "index_name": "Indice Gulpease",
            "score": gulpease_score,
            "interpretation": interp,
            "avg_sentence_length": round(tot_words / tot_sents, 1),
            "words_count": tot_words,
            "sentences_count": tot_sents,
        }


class EnglishLanguagePack(BaseLanguagePack):
    lang_code = "en"
    name = "English"

    top_10 = {
        "the",
        "be",
        "to",
        "of",
        "and",
        "a",
        "in",
        "that",
        "have",
        "i",
        "it",
        "for",
        "not",
        "on",
        "with",
        "he",
        "as",
        "you",
        "do",
        "at",
    }

    top_100 = {
        "this",
        "but",
        "his",
        "by",
        "from",
        "they",
        "we",
        "say",
        "her",
        "she",
        "or",
        "an",
        "will",
        "my",
        "one",
        "all",
        "would",
        "there",
        "their",
        "what",
        "so",
        "up",
        "out",
        "if",
        "about",
        "who",
        "get",
        "which",
        "go",
        "me",
        "when",
        "make",
        "can",
        "like",
        "time",
        "no",
        "just",
        "him",
        "know",
        "take",
        "people",
        "into",
        "year",
        "your",
        "good",
        "some",
        "could",
        "them",
        "see",
        "other",
        "than",
        "then",
        "now",
        "look",
        "only",
        "come",
        "its",
        "over",
        "think",
        "also",
        "back",
        "after",
        "use",
        "two",
        "how",
        "our",
        "work",
        "first",
        "well",
        "way",
        "even",
        "new",
        "want",
        "because",
        "any",
        "these",
        "give",
        "day",
        "most",
        "us",
        "is",
        "are",
        "was",
        "were",
        "been",
        "has",
        "had",
        "does",
        "did",
        "having",
        "may",
        "might",
        "must",
        "should",
        "shall",
        "cannot",
    }

    def count_syllables(self, word: str) -> int:
        w = word.lower().strip()
        if len(w) <= 3:
            return 1
        w = re.sub(r"(?:[^laeiouy]|ed|es|e)$", "", w)
        w = re.sub(r"^y", "", w)
        vowels = re.findall(r"[aeiouy]{1,2}", w)
        return max(1, len(vowels))

    def calculate_readability(
        self, text: str, words: list[str], sentences: list[str]
    ) -> dict:
        tot_words = max(1, len(words))
        tot_sents = max(1, len(sentences))
        tot_sylls = sum(self.count_syllables(w) for w in words)

        asl = tot_words / tot_sents
        asw = tot_sylls / tot_words
        flesch = 206.835 - (1.015 * asl) - (84.6 * asw)
        flesch_score = round(max(0.0, min(100.0, flesch)), 1)
        fk_grade = round(max(1.0, (0.39 * asl) + (11.8 * asw) - 15.59), 1)

        if flesch_score >= 70:
            interp = "Fairly Easy / Plain English"
        elif flesch_score >= 50:
            interp = "Standard / High School"
        elif flesch_score >= 30:
            interp = "Difficult / College Level"
        else:
            interp = "Very Difficult / Academic & Technical Research"

        return {
            "language": "en",
            "index_name": "Flesch Reading Ease",
            "score": flesch_score,
            "grade_level": fk_grade,
            "interpretation": interp,
            "avg_sentence_length": round(asl, 1),
            "words_count": tot_words,
            "sentences_count": tot_sents,
        }


class SpanishLanguagePack(BaseLanguagePack):
    lang_code = "es"
    name = "Español"

    top_10 = {
        "el",
        "la",
        "de",
        "que",
        "y",
        "en",
        "un",
        "una",
        "los",
        "las",
        "del",
        "al",
    }

    top_100 = {
        "por",
        "para",
        "con",
        "no",
        "su",
        "lo",
        "como",
        "más",
        "pero",
        "sus",
        "le",
        "ya",
        "o",
        "este",
        "sí",
        "porque",
        "esta",
        "entre",
        "cuando",
        "muy",
        "sin",
        "sobre",
        "también",
        "me",
        "hasta",
        "hay",
        "donde",
        "quien",
        "desde",
        "todo",
        "nos",
        "durante",
        "todos",
        "uno",
        "les",
        "ni",
        "contra",
        "otros",
        "ese",
        "eso",
        "ante",
        "ellos",
        "e",
        "esto",
        "mí",
        "antes",
        "algunos",
        "qué",
        "unos",
        "yo",
        "otro",
        "otras",
        "otra",
        "él",
        "tanto",
        "esa",
        "estos",
        "mucho",
        "quienes",
        "nada",
        "muchos",
        "cual",
        "poco",
        "ella",
        "estar",
        "estas",
        "algunas",
        "algo",
        "nosotros",
        "es",
        "son",
        "fue",
        "era",
        "ha",
        "han",
        "ser",
        "tiene",
        "tienen",
        "puede",
        "pueden",
        "hacer",
        "hace",
    }

    def calculate_readability(
        self, text: str, words: list[str], sentences: list[str]
    ) -> dict:
        tot_words = max(1, len(words))
        tot_sents = max(1, len(sentences))
        tot_sylls = sum(self.count_syllables(w) for w in words)

        p = (tot_sylls * 100.0) / tot_words
        f = tot_words / tot_sents
        fh = 206.84 - (0.60 * p) - (1.02 * f)
        fh_score = round(max(0.0, min(100.0, fh)), 1)

        if fh_score >= 80:
            interp = "Muy fácil / Primaria"
        elif fh_score >= 60:
            interp = "Estándar / Secundaria"
        elif fh_score >= 40:
            interp = "Difícil / Bachillerato y Universidad"
        else:
            interp = "Muy difícil / Tesis académica o científica"

        return {
            "language": "es",
            "index_name": "Índice Fernández-Huerta",
            "score": fh_score,
            "interpretation": interp,
            "avg_sentence_length": round(f, 1),
            "words_count": tot_words,
            "sentences_count": tot_sents,
        }


class FrenchLanguagePack(BaseLanguagePack):
    lang_code = "fr"
    name = "Français"

    top_10 = {
        "le",
        "la",
        "de",
        "et",
        "un",
        "une",
        "les",
        "des",
        "en",
        "est",
        "du",
        "qui",
        "dans",
        "par",
        "pour",
    }

    top_100 = {
        "au",
        "avec",
        "ce",
        "il",
        "sur",
        "pas",
        "plus",
        "ne",
        "se",
        "son",
        "que",
        "ont",
        "ses",
        "mais",
        "ou",
        "nous",
        "sa",
        "comme",
        "aussi",
        "ils",
        "tout",
        "fait",
        "elle",
        "leur",
        "y",
        "cette",
        "si",
        "deux",
        "même",
        "bien",
        "ces",
        "sans",
        "peut",
        "faire",
        "tous",
        "après",
        "autres",
        "été",
        "temps",
        "leurs",
        "sous",
        "donc",
        "on",
        "encore",
        "entre",
        "dont",
        "très",
        "toute",
        "alors",
        "moins",
        "dire",
        "avoir",
        "notre",
        "peu",
        "vie",
        "chose",
        "trois",
        "toujours",
        "mon",
        "point",
        "jamais",
        "cas",
        "non",
        "grand",
        "effet",
        "voir",
        "monde",
        "sont",
        "été",
        "avait",
        "étaient",
        "serait",
        "peuvent",
        "doit",
        "doivent",
    }

    def calculate_readability(
        self, text: str, words: list[str], sentences: list[str]
    ) -> dict:
        tot_words = max(1, len(words))
        tot_sents = max(1, len(sentences))
        tot_sylls = sum(self.count_syllables(w) for w in words)

        p = (tot_sylls * 100.0) / tot_words
        f = tot_words / tot_sents
        km = 207.0 - (0.66 * p) - (1.05 * f)
        km_score = round(max(0.0, min(100.0, km)), 1)

        if km_score >= 70:
            interp = "Facile / Grand public"
        elif km_score >= 50:
            interp = "Standard / Lycée"
        elif km_score >= 30:
            interp = "Difficile / Enseignement supérieur"
        else:
            interp = "Très difficile / Thèse ou recherche scientifique"

        return {
            "language": "fr",
            "index_name": "Formule Kandel & Moles",
            "score": km_score,
            "interpretation": interp,
            "avg_sentence_length": round(f, 1),
            "words_count": tot_words,
            "sentences_count": tot_sents,
        }


class GermanLanguagePack(BaseLanguagePack):
    lang_code = "de"
    name = "Deutsch"

    top_10 = {
        "der",
        "die",
        "das",
        "und",
        "in",
        "von",
        "zu",
        "den",
        "mit",
        "ist",
        "des",
        "ein",
        "eine",
        "auf",
        "dem",
    }

    top_100 = {
        "nicht",
        "auch",
        "im",
        "für",
        "an",
        "es",
        "als",
        "sich",
        "sie",
        "nach",
        "aus",
        "um",
        "wir",
        "er",
        "einen",
        "einer",
        "einem",
        "hat",
        "wie",
        "aber",
        "zum",
        "bei",
        "so",
        "noch",
        "nur",
        "war",
        "über",
        "wird",
        "man",
        "eines",
        "wurde",
        "oder",
        "durch",
        "kann",
        "haben",
        "seine",
        "mehr",
        "wieder",
        "seiner",
        "vor",
        "unter",
        "wenn",
        "seines",
        "ihr",
        "ihre",
        "schon",
        "vom",
        "seinen",
        "ihrer",
        "dann",
        "sehr",
        "uns",
        "waren",
        "ohne",
        "dieser",
        "diese",
        "dieses",
        "alle",
        "immer",
        "doch",
        "gut",
        "jetzt",
        "während",
        "zwischen",
        "jedoch",
        "da",
        "sind",
        "waren",
        "worden",
        "werden",
        "können",
        "müssen",
        "sollte",
    }

    def calculate_readability(
        self, text: str, words: list[str], sentences: list[str]
    ) -> dict:
        tot_words = max(1, len(words))
        tot_sents = max(1, len(sentences))
        tot_sylls = sum(self.count_syllables(w) for w in words)

        p = (tot_sylls * 100.0) / tot_words
        f = tot_words / tot_sents
        amstad = 180.0 - f - (0.585 * p)
        amstad_score = round(max(0.0, min(100.0, amstad)), 1)

        if amstad_score >= 70:
            interp = "Leicht / Allgemein verständlich"
        elif amstad_score >= 50:
            interp = "Mittel / Gymnasiale Oberstufe"
        elif amstad_score >= 30:
            interp = "Schwer / Hochschulniveau"
        else:
            interp = "Sehr schwer / Akademische Dissertation"

        return {
            "language": "de",
            "index_name": "Amstad Lesbarkeitsindex",
            "score": amstad_score,
            "interpretation": interp,
            "avg_sentence_length": round(f, 1),
            "words_count": tot_words,
            "sentences_count": tot_sents,
        }


# ==============================================================================
# LANGUAGE REGISTRY & DYNAMIC DISPATCH
# ==============================================================================


class LanguageRegistry:
    """Registry universale con rilevamento automatico O(N) e fallback zero-shot."""

    _packs: dict[str, BaseLanguagePack] = {
        "it": ItalianLanguagePack(),
        "en": EnglishLanguagePack(),
        "es": SpanishLanguagePack(),
        "fr": FrenchLanguagePack(),
        "de": GermanLanguagePack(),
    }

    DIAGNOSTIC_VECTORS: dict[str, set[str]] = {
        "it": {
            "il",
            "la",
            "di",
            "che",
            "e",
            "ed",
            "un",
            "una",
            "per",
            "non",
            "del",
            "della",
            "con",
            "sono",
            "in",
            "al",
            "delle",
            "dei",
        },
        "en": {
            "the",
            "of",
            "and",
            "to",
            "in",
            "is",
            "that",
            "it",
            "was",
            "for",
            "as",
            "with",
            "by",
            "on",
            "are",
            "this",
            "from",
            "at",
        },
        "es": {
            "el",
            "la",
            "de",
            "que",
            "y",
            "en",
            "un",
            "una",
            "los",
            "las",
            "por",
            "para",
            "con",
            "del",
            "como",
            "es",
            "al",
            "su",
        },
        "fr": {
            "le",
            "la",
            "de",
            "et",
            "un",
            "une",
            "les",
            "des",
            "en",
            "est",
            "du",
            "qui",
            "dans",
            "par",
            "pour",
            "au",
            "avec",
            "sur",
        },
        "de": {
            "der",
            "die",
            "das",
            "und",
            "in",
            "von",
            "zu",
            "den",
            "mit",
            "ist",
            "des",
            "ein",
            "eine",
            "auf",
            "dem",
            "nicht",
            "auch",
            "im",
        },
    }

    @classmethod
    def register(cls, pack: BaseLanguagePack) -> None:
        """Registra un LanguagePack statico o aggiorna un pack esistente."""
        cls._packs[pack.lang_code] = pack
        if pack.top_10:
            cls.DIAGNOSTIC_VECTORS[pack.lang_code] = set(list(pack.top_10)[:20])

    @classmethod
    def register_dynamic(
        cls,
        lang_code: str,
        name: str,
        top_10: list[str],
        top_100: Optional[list[str]] = None,
        top_1000: Optional[list[str]] = None,
        collocations: Optional[list[str]] = None,
    ) -> BaseLanguagePack:
        """Permette all'Agente o all'utente di iniettare a runtime un nuovo LanguagePack senza riavvii."""
        pack = DataDrivenLanguagePack(
            lang_code=lang_code,
            name=name,
            top_10=set(top_10),
            top_100=set(top_100 or []),
            top_1000=set(top_1000 or []),
            collocations=collocations or [],
        )
        cls.register(pack)
        return pack

    @classmethod
    def get(cls, lang_code: str) -> BaseLanguagePack:
        """Restituisce il LanguagePack corrispondente o genera un UniversalLanguagePack zero-shot."""
        code = lang_code.lower().strip()
        if code in cls._packs:
            return cls._packs[code]

        # Prova a caricare da data/languages/{code}.json se esiste
        json_path = DATA_LANGUAGES_DIR / f"{code}.json"
        if json_path.is_file():
            universal_pack = UniversalLanguagePack(
                lang_code=code, name=f"Language ({code.upper()})"
            )
            cls._packs[code] = universal_pack
            return universal_pack

        # Fallback universale zero-shot per qualsiasi codice lingua sconosciuto (es. 'pt', 'la', 'nl', 'ru')
        universal_pack = UniversalLanguagePack(
            lang_code=code, name=f"Universal ({code.upper()})"
        )
        cls._packs[code] = universal_pack
        return universal_pack

    @classmethod
    def detect_language(cls, words: list[str]) -> BaseLanguagePack:
        """
        Rileva automaticamente la lingua in un singolo passaggio O(N).
        Scansiona i vettori diagnostici chiusi delle lingue registrate.
        Se nessuna lingua conosciuta domina, restituisce UniversalLanguagePack.
        """
        if not words:
            return cls._packs["it"]

        scores: dict[str, int] = {code: 0 for code in cls.DIAGNOSTIC_VECTORS}

        for w in words:
            wl = w.lower()
            for code, vec in cls.DIAGNOSTIC_VECTORS.items():
                if wl in vec:
                    scores[code] += 1

        best_lang = max(scores, key=lambda k: scores[k])
        sorted_scores = sorted(scores.values(), reverse=True)
        top1 = sorted_scores[0]
        top2 = sorted_scores[1] if len(sorted_scores) > 1 else 0

        # Una lingua è confermata se ha almeno 4 parole diagnostiche e un margine rispetto alle altre
        if top1 >= max(4, int(len(words) * 0.05)) and (top1 - top2) >= 2:
            return cls._packs[best_lang]

        # Se non corrisponde con sufficiente certezza a nessuna lingua registrata, usa il motore universale zero-shot
        return UniversalLanguagePack(lang_code="auto", name="Universal / Auto-Detected")
