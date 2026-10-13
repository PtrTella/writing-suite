#!/usr/bin/env python3
"""
Writing Suite - Automated Test Suite
Esegue test di regressione e unit test su tutti i componenti core di writing-suite.
"""

import sys
import unittest
from pathlib import Path

# Setup path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "mcp"))

from core.cleaner import clean_markup, extract_sentences, extract_words
from core.linter import lint_text
from core.metrics import calculate_perplexity_and_burstiness, calculate_stylometrics, calculate_readability
from core.citations import audit_citations
from core.evaluator_engine import evaluate_document

class TestWritingSuite(unittest.TestCase):

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

    def test_linter_detection(self):
        sample = (
            "In today's fast-paced world, artificial intelligence plays a crucial role in society, "
            "underscoring the importance of innovation.\n"
            "Non è solo uno strumento, ma rappresenta il futuro.\n"
            "That is the real win."
        )
        findings = lint_text(sample)
        rule_ids = {f["id"] for f in findings}
        self.assertIn("WS-SYN-004", rule_ids)  # In today's fast-paced world
        self.assertIn("WS-RID-001", rule_ids)  # underscoring the importance
        self.assertIn("WS-LEX-001", rule_ids)  # plays a crucial role
        self.assertIn("WS-SYN-001", rule_ids)  # Non è solo uno strumento, ma rappresenta
        self.assertIn("WS-SYN-002", rule_ids)  # That is the real win

    def test_readability_gulpease(self):
        sample_it = "Questo è un testo semplice e chiaro per verificare l'indice Gulpease in lingua italiana."
        res = calculate_readability(sample_it, lang="it")
        self.assertIsNotNone(res["gulpease"])
        self.assertGreater(res["gulpease"], 0)
        self.assertEqual(res["language"], "it")

    def test_citations_audit(self):
        sample = "Secondo recenti ricerche la scalabilità delle blockchain è limitata. Invece @buterin2014 propone lo sharding."
        res = audit_citations(sample)
        self.assertEqual(res["unsupported_claims_count"], 1)
        self.assertIn("buterin2014", res["citation_keys"])

    def test_evaluator_engine(self):
        ai_sample = (
            "In today's digital landscape, modern cloud computing stands as a testament to modern engineering. "
            "Furthermore, it plays a pivotal role in enterprise scalability, underscoring the importance of reliability. "
            "In conclusion, we must embrace this paradigm shift."
        )
        res = evaluate_document(ai_sample)
        self.assertGreater(res["overall_ai_score"], 40.0)
        self.assertIn("lenses", res)
        self.assertIn("heatmap", res)

if __name__ == "__main__":
    unittest.main()
