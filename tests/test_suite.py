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

    def test_domain_terms_calibration(self):
        text = (
            "L'architettura decentralizzata utilizza zkTLS, zk-SNARKs, Sepolia e Merkle DAG per convalidare "
            "le transazioni nello stato globale, garantendo un'infrastruttura crittografica ad alte prestazioni e privacy."
        )
        # Senza termini di dominio
        res_raw = evaluate_document(text, domain_terms=[])
        # Con termini di dominio
        res_calibrated = evaluate_document(
            text,
            domain="blockchain",
            domain_terms=["zkTLS", "zk-SNARKs", "Sepolia", "Merkle DAG"],
            target_style="technical_documentation"
        )
        self.assertEqual(res_calibrated["context_calibration"]["domain"], "blockchain")
        self.assertGreater(res_calibrated["lenses"]["gltr_forensics"]["domain_terms_pct"], 0.0)
        self.assertEqual(res_calibrated["context_calibration"]["domain_terms_count"], 4)

    def test_multilingual_and_universal_pack(self):
        from core.languages import LanguageRegistry, UniversalLanguagePack

        # 1. Spanish Detection & Evaluation
        es_sample = (
            "El sistema descentralizado utiliza contratos inteligentes en la red de pruebas para garantizar "
            "la seguridad y la transparencia de todas las transacciones financieras en tiempo real."
        )
        res_es = evaluate_document(es_sample)
        self.assertEqual(res_es["language"], "es")
        self.assertIn("Fernández-Huerta", res_es["lenses"]["readability"]["index_name"])

        # 2. French Detection & Evaluation
        fr_sample = (
            "Le système décentralisé utilise des protocoles cryptographiques pour valider les blocs "
            "dans le grand livre distribué, avec une haute performance et une résilience prouvée."
        )
        res_fr = evaluate_document(fr_sample)
        self.assertEqual(res_fr["language"], "fr")
        self.assertIn("Kandel & Moles", res_fr["lenses"]["readability"]["index_name"])

        # 3. German Detection & Evaluation
        de_sample = (
            "Das dezentrale System verwendet kryptographische Protokolle und intelligente Verträge, "
            "um die Sicherheit und Integrität der Daten in dem verteilten Netzwerk zu gewährleisten."
        )
        res_de = evaluate_document(de_sample)
        self.assertEqual(res_de["language"], "de")
        self.assertIn("Amstad", res_de["lenses"]["readability"]["index_name"])

        # 4. Unknown Language Fallback -> Universal Zero-Shot Pack (LIX)
        la_sample = (
            "Gallia est omnis divisa in partes tres, quarum unam incolunt Belgae, aliam Aquitani, "
            "tertiam qui ipsorum lingua Celtae, nostra Galli appellantur."
        )
        res_la = evaluate_document(la_sample)
        self.assertEqual(res_la["language"], "auto")
        self.assertIn("LIX", res_la["lenses"]["readability"]["index_name"])

        # 5. Dynamic Agent-injected language
        LanguageRegistry.register_dynamic(
            lang_code="pt",
            name="Português",
            top_10=["o", "a", "de", "que", "e", "do", "da", "em", "um", "para"]
        )
        pt_sample = (
            "O sistema descentralizado utiliza contratos inteligentes para validar as transações financeiras "
            "na rede global de nós distribuídos, garantindo a integridade dos dados sem intermediários."
        )
        res_pt = evaluate_document(pt_sample, language="pt")
        self.assertEqual(res_pt["language"], "pt")

    def test_calibration_and_separation(self):
        # 1. Synthetic AI technical document with list, contrast, and robotic cadence
        ai_sample = (
            "# Architettura di Batching e Multicall\n\n"
            "Il progetto non è solo un esercizio di stile, ma una risposta architetturale necessaria.\n\n"
            "Negli ultimi anni, gli sviluppatori hanno affrontato colli di bottiglia critici.\n\n"
            "Tuttavia, un'analisi approfondita condotta sui sistemi decentralizzati dimostra che il batching è vitale:\n\n"
            "1. **Latenza Ridotta:** Il Relayer aggrega tutte le chiamate in una sola transazione atomica.\n"
            "2. **Risparmio Gas:** Si riducono le fee di rete drasticamente, eliminando i costi fissi per transazione.\n"
            "3. **Atomicità:** O tutte le registrazioni vanno a buon fine, o nessuna viene confermata.\n\n"
            "Questo approccio cattura l'essenza pura del software e funge da pilastro per la scalabilità."
        )
        res_ai = evaluate_document(ai_sample)
        self.assertGreaterEqual(res_ai["overall_ai_score"], 70.0)
        self.assertEqual(res_ai["verdict_badge"], "🔴")

        # 2. Authentic human academic paragraph with rich vocabulary, bursty cadence, and no formulas
        human_sample = (
            "Abbiamo condotto gli esperimenti su un cluster eterogeneo di tre macchine fisiche connesse "
            "tramite uno switch a 10 Gbps. A differenza delle simulazioni sintetiche comunemente riportate "
            "nella letteratura precedente, dove i ritardi di propagazione della rete vengono spesso trascurati "
            "oppure modellati tramite distribuzioni gaussiane stazionarie, le nostre misurazioni sul campo "
            "hanno registrato variazioni empiriche significative e picchi intermittenti di latenza che dipendono "
            "direttamente dal carico concorrente del garbage collector della macchina virtuale. Questi rilievi "
            "smentiscono parzialmente le ipotesi iniziali."
        )
        res_human = evaluate_document(human_sample)
        self.assertLessEqual(res_human["overall_ai_score"], 30.0)
        self.assertEqual(res_human["verdict_badge"], "🟢")

if __name__ == "__main__":
    unittest.main()
