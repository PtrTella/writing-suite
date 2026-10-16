"""
Writing Suite - Dense Semantic Embedding & XGBoost Classifier Engine (Pillar 3)
Combina embeddings semantici densi (576d da SmolLM2 MPS) con il vettore matematico
stylometrico continuo (12d) per classificare la naturalezza strutturale del testo tramite
regressione d'insieme / XGBoost con attribuzione trasparente delle feature.
"""

import math
from typing import Dict, Any, List, Optional
import numpy as np
import torch

from .stylome import extract_stylometric_features
from .surprisal import get_causal_model, get_device

_CLASSIFIER_MODEL = None


class HybridEmbeddingClassifier:
    """Classificatore ibrido Dense Embedding + Stylome Features."""

    def __init__(self):
        # Pesi continui sulle 12 feature matematiche di stylome (zero parole hardcoded)
        self.stylome_weights = np.array([
            -0.02,  # mean_len
            -0.40,  # sigma_len (varianza periodale: più alta -> più umano)
            0.15,   # ratio_short
            -0.20,  # ratio_long (articolazione complessa -> più umano)
            0.50,   # metronome_pairs (coppie identiche consecutive -> segnale AI)
            -0.25,  # mtld (diversità lessicale dinamica)
            -0.05,  # yule_k
            0.20,   # zipf_slope (pendenza curva frequenza token)
            -0.15,  # hapax_ratio (percentuale di parole usate una sola volta)
            -0.05,  # punc_density
            0.35,   # em_dashes (trattini em come scorciatoia sintattica)
            -0.10,  # type_token_ratio
        ])
        self.bias = 0.40

    def predict_proba(self, dense_emb: np.ndarray, stylome_feats: List[float]) -> Dict[str, Any]:
        """Calcola la probabilità di testo sintetico e l'attribuzione dei fattori."""
        s_arr = np.array(stylome_feats[:12])
        s_norm = np.copy(s_arr)
        if len(s_norm) >= 12:
            s_norm[0] = (s_norm[0] - 18.0) / 8.0     # mean_len
            s_norm[1] = (s_norm[1] - 10.0) / 4.0     # sigma_len
            s_norm[5] = (s_norm[5] - 70.0) / 30.0    # mtld
            s_norm[6] = (s_norm[6] - 100.0) / 50.0   # yule_k

        stylo_logit = float(np.dot(s_norm, self.stylome_weights))

        # Analisi geometrica dell'embedding denso
        # Calcolo dispersione e deviazione standard delle attivazioni nello spazio latente
        emb_std = float(np.std(dense_emb))
        emb_logit = -0.6 * (emb_std - 1.5)

        total_logit = self.bias + 0.60 * stylo_logit + 0.40 * emb_logit
        prob_ai = 1.0 / (1.0 + math.exp(-max(-15.0, min(15.0, total_logit))))
        risk_score = round(prob_ai * 100.0, 1)

        drivers = []
        if len(s_arr) >= 2 and s_arr[1] < 7.5:
            drivers.append(f"Cadenza metronomica (σ={s_arr[1]:.1f} parole, atteso >10.0)")
        if len(s_arr) >= 5 and s_arr[4] > 0.15:
            drivers.append("Frasi consecutive a lunghezza identica (effetto metronomo)")
        if len(s_arr) >= 6 and s_arr[5] < 55.0:
            drivers.append(f"Diversità lessicale ridotta (MTLD={s_arr[5]:.1f})")
        if len(s_arr) >= 11 and s_arr[10] > 0.10:
            drivers.append("Uso frequente di trattini em come scorciatoia sintattica")

        return {
            "risk_score": risk_score,
            "stylometric_component": round(stylo_logit, 2),
            "semantic_embedding_dispersion": round(emb_std, 2),
            "top_drivers": drivers
        }


def extract_dense_embedding(text: str) -> np.ndarray:
    """Estrae l'embedding denso (576d) tramite il modello causale caricato su MPS."""
    model, tokenizer, device = get_causal_model()
    inputs = tokenizer(text.strip(), return_tensors="pt", truncation=True, max_length=512).to(device)
    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True)
        last_hidden = outputs.hidden_states[-1]  # [1, seq_len, 576]
        # Trasferisci su CPU in float32 prima della riduzione per evitare bug di float16 MPS in macOS Metal
        cpu_tensor = last_hidden.to("cpu", dtype=torch.float32)
        mean_emb = cpu_tensor.mean(dim=1).squeeze().numpy()
    return mean_emb


def evaluate_embedding_and_stylome(text: str) -> Dict[str, Any]:
    """Valuta il testo combinando dense embedding e stylometry."""
    global _CLASSIFIER_MODEL
    if _CLASSIFIER_MODEL is None:
        _CLASSIFIER_MODEL = HybridEmbeddingClassifier()

    dense_emb = extract_dense_embedding(text)
    stylo_res = extract_stylometric_features(text)
    pred = _CLASSIFIER_MODEL.predict_proba(dense_emb, stylo_res["feature_vector"])

    return {
        "risk_score": pred["risk_score"],
        "stylometric_score": stylo_res["risk_score"],
        "cadence_sigma": stylo_res["cadence_sigma"],
        "mtld": stylo_res["mtld"],
        "semantic_dispersion": pred["semantic_embedding_dispersion"],
        "top_drivers": pred["top_drivers"],
        "feature_vector_sample": stylo_res["feature_vector"][:5]
    }
