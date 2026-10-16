#!/usr/bin/env python3
"""
Writing Suite - Modern Automated Test Suite
Unit test e test di regressione sull'architettura a 4 pilastri:
- Cleaner (Typst, LaTeX, Markdown)
- Stylome (Cadenza asimmetrica, MTLD, Burstiness di periodo)
- Citations (Audit bibliografico, claim non supportati)
- Surprisal (SmolLM2 Causal Perplexity & Token Burstiness)
- Modern Evaluator (Verdetto 4-pillar, Heatmap)
"""

import sys
import unittest
import warnings
warnings.simplefilter("ignore", FutureWarning)
warnings.filterwarnings("ignore", message=".*torch.jit.script.*")
warnings.filterwarnings("ignore", category=UserWarning)
from pathlib import Path

# Setup path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "mcp"))

from core.cleaner import clean_markup, extract_sentences, extract_words
from core.stylome import (
    extract_stylometric_features,
    calculate_mtld,
)
from core.citations import audit_citations
from core.modern_evaluator import evaluate_document_modern


class TestWritingSuiteModern(unittest.TestCase):

    def test_cleaner_typst_and_latex(self):
        sample = """
        #figure(image("arch.png"), caption: [Architettura]) <fig1>
        Ecco il testo principale con formula $E = m c^2$ e citazione @nakamoto2008.
        #table(columns: 2, [A], [B])
        La conclusione finale.
        """
        cleaned = clean_markup(sample)
        self.assertNotIn("#figure", cleaned)
        self.assertNotIn("#table", cleaned)
        self.assertNotIn("$E = m c^2$", cleaned)
        self.assertIn("Ecco il testo principale", cleaned)
        self.assertIn("La conclusione finale", cleaned)

    def test_stylome_cadence_and_mtld(self):
        # Testo con forte asimmetria di cadenza (umano autentico)
        sample = (
            "The reaction was immediate. "
            "Within minutes, automated build clusters across thousands of enterprise networks "
            "crashed simultaneously when package resolvers encountered unexpected 404 missing package errors. "
            "Mathematical immutability does not exist on centralized cloud servers."
        )
        words = extract_words(sample)
        sentences = extract_sentences(sample)
        self.assertEqual(len(sentences), 3)

        sty = extract_stylometric_features(sample)
        self.assertGreater(sty["cadence_sigma"], 8.0, "La cadenza deve mostrare elevata varianza asimmetrica (sigma >= 8.0)")

        mtld = calculate_mtld(words)
        self.assertGreater(mtld, 40.0, "Il testo deve mostrare elevata diversità lessicale MTLD")

    def test_citations_audit(self):
        sample = (
            "Secondo recenti ricerche la scalabilità delle blockchain è limitata. "
            "Invece @buterin2014 propone lo sharding per distribuire il consenso."
        )
        res = audit_citations(sample)
        self.assertEqual(res["total_citations_found"], 1)
        self.assertIn("buterin2014", res["citation_keys"])
        # Verifica claim apodittico senza fonte
        self.assertGreater(len(res["unsupported_claims"]), 0)
        self.assertTrue(any("recenti ricerche" in c["matched_text"].lower() for c in res["unsupported_claims"]))

    def test_modern_evaluator_pipeline(self):
        sample_ai = (
            "In today's fast-paced digital landscape, decentralized registries play a pivotal role. "
            "By leveraging smart contracts, organizations ensure seamless deployment and foster trust."
        )
        rep = evaluate_document_modern(sample_ai)
        self.assertIn("overall_ai_risk", rep)
        self.assertIn("avg_perplexity", rep)
        self.assertIn("paragraphs", rep)
        self.assertGreaterEqual(rep["overall_ai_risk"], 50.0, "Testo AI standard deve avere rischio elevato")

    def test_diagnostic_vector_and_syntax_patterns(self):
        from core.engines import evaluate_paragraph_vector
        sample_triad = (
            "When developers invoke package installation, their machines connect to remote edge servers, "
            "mutable relational databases, and institutional administrators."
        )
        res = evaluate_paragraph_vector(sample_triad)
        self.assertIn("vector", res)
        self.assertIn("syntax", res["vector"])
        self.assertIn("cadence", res["vector"])
        self.assertIn("surprisal", res["vector"])
        self.assertIn("lexical", res["vector"])
        self.assertIn("prescriptions", res)
        # Verifica rilevamento triade
        syntax_res = res["vector"]["syntax"]
        self.assertTrue(any("Triadic" in p or "POS Parallelism" in p for p in syntax_res.get("patterns_detected", [])))

    def test_sota_stylometrics_hapax_and_punctuation_entropy(self):
        from core.stylome import (
            calculate_hapax_ratio,
            calculate_dis_legomena_ratio,
            calculate_punctuation_entropy,
            extract_stylometric_features
        )
        sample = (
            "We measure a commit latency of 42.1 ms under 1,000 tx/sec. "
            "Raft maintains quorum; Byzantine nodes drop off without halting state replication. "
            "In our testbed (a 64-node cluster), RocksDB serializes Merkle nodes directly to NVMe storage."
        )

        words = extract_words(sample)
        hapax = calculate_hapax_ratio(words)
        self.assertGreater(hapax, 0.85, "Il testo umano denso deve avere un Hapax Legomena ratio elevato (> 0.85)")

        h_punct = calculate_punctuation_entropy(sample)
        self.assertGreater(h_punct, 1.4, "Il testo con punteggiatura asimmetrica (punto e virgola, virgole, punti) deve avere H_punct >= 1.4")

        sty = extract_stylometric_features(sample)
        self.assertIn("hapax_ratio", sty)
        self.assertIn("punctuation_entropy", sty)
        self.assertIn("dis_legomena_ratio", sty)

    def test_surprisal_binoculars_and_top1_curvature(self):
        from core.surprisal import calculate_token_surprisal
        sample = "We benchmark 10,000 cryptographic SWHID tree nodes on NVMe storage."
        res = calculate_token_surprisal(sample)
        self.assertIn("perplexity", res)
        self.assertIn("binoculars_ratio", res)
        self.assertIn("top1_gap", res)
        self.assertIn("mean_entropy_nats", res)
        self.assertGreater(res["binoculars_ratio"], 0.5, "Il rapporto Binoculars deve essere un valore positivo valido")
        self.assertGreater(res["top1_gap"], 0.0, "Il Top-1 gap deve essere non nullo")


if __name__ == "__main__":
    unittest.main()

