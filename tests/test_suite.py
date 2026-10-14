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

    def test_project_auditor(self):
        from core.project_auditor import audit_directory
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_p = Path(tmpdir)
            (tmp_p / "ch1.typ").write_text("This is an authentic human test file.")
            (tmp_p / "ch2.typ").write_text("In today's fast-paced world, AI plays a crucial role.")
            res = audit_directory(tmpdir)
            self.assertEqual(res["total_files"], 2)
            self.assertIn("summary_table", res)
            self.assertGreater(res["total_words"], 0)

    def test_technical_ai_patterns(self):
        tech_ai_sample = (
            "Un approccio ingenuo suggerirebbe di salvare questo albero direttamente on-chain.\n"
            "Tuttavia, questo approccio porta a pura follia architetturale per tre ragioni fondamentali:\n"
            "1. **Architectural Security:** Qualitative mapping against threat taxonomies.\n"
            "2. **Smart Contract Robustness:** Formal verification using static analysis.\n"
            "3. **Economic Feasibility:** State bloat projections across blockchains.\n"
            "Il componente funge da indice, garantendo al contempo un'infrastruttura resiliente."
        )
        findings = lint_text(tech_ai_sample)
        rule_ids = {f["id"] for f in findings}
        self.assertIn("WS-SYN-006", rule_ids)  # Un approccio ingenuo suggerirebbe
        self.assertIn("WS-STR-002", rule_ids)  # per tre ragioni fondamentali
        self.assertIn("WS-LEX-003", rule_ids)  # pura follia architetturale
        self.assertIn("WS-FMT-001", rule_ids)  # Bold list items cluster
        self.assertIn("WS-RID-004", rule_ids)  # funge da indice
        self.assertIn("WS-RID-003", rule_ids)  # , garantendo

if __name__ == "__main__":
    unittest.main()
