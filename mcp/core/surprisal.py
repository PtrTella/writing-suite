"""
Writing Suite - Causal Surprisal & Perplexity Engine (Pillar 1)
Calcola perplessità, surprisal token-by-token e burstiness statistica
utilizzando un modello linguistico causale ultra-leggero su Apple Silicon Metal (MPS).
Basato sui principi scientifici di Binoculars, Fast-DetectGPT e GLTR.
"""

import math
import os
import time
from typing import Dict, Any, List, Optional, Tuple

os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

import torch

_CAUSAL_MODEL = None
_CAUSAL_TOKENIZER = None
_DEVICE = None
DEFAULT_CAUSAL_MODEL_ID = "HuggingFaceTB/SmolLM2-135M"


def get_device() -> str:
    global _DEVICE
    if _DEVICE is None:
        if torch.backends.mps.is_available():
            _DEVICE = "mps"
        elif torch.cuda.is_available():
            _DEVICE = "cuda"
        else:
            _DEVICE = "cpu"
    return _DEVICE


def get_causal_model(model_id: str = DEFAULT_CAUSAL_MODEL_ID):
    """Caricamento singleton del modello causale compatto su MPS."""
    global _CAUSAL_MODEL, _CAUSAL_TOKENIZER
    if _CAUSAL_MODEL is None or _CAUSAL_TOKENIZER is None:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        device = get_device()
        _CAUSAL_TOKENIZER = AutoTokenizer.from_pretrained(model_id)
        dtype = torch.float16 if device == "mps" else torch.float32
        _CAUSAL_MODEL = AutoModelForCausalLM.from_pretrained(
            model_id,
            dtype=dtype,
            low_cpu_mem_usage=True
        ).to(device)
        _CAUSAL_MODEL.eval()
    return _CAUSAL_MODEL, _CAUSAL_TOKENIZER, get_device()


def is_causal_available() -> bool:
    """Verifica se PyTorch e le dipendenze per il modello causale sono disponibili."""
    try:
        import transformers
        return True
    except ImportError:
        return False


def calculate_token_surprisal(text: str, model_id: str = DEFAULT_CAUSAL_MODEL_ID) -> Dict[str, Any]:
    """
    Calcola perplessità e distribuzione del surprisal token-by-token per un testo.
    Surprisal: s(w_t) = -log2 P(w_t | w_<t)
    """
    cleaned = text.strip()
    if not cleaned or len(cleaned.split()) < 3:
        return {
            "perplexity": 0.0,
            "mean_surprisal": 0.0,
            "burstiness": 0.0,
            "token_count": 0,
            "tokens": [],
            "surprisal_tokens": [],
            "risk_score": 50.0
        }

    model, tokenizer, device = get_causal_model(model_id)
    inputs = tokenizer(cleaned, return_tensors="pt").to(device)
    input_ids = inputs["input_ids"]
    
    if input_ids.shape[1] < 2:
        return {
            "perplexity": 100.0,
            "mean_surprisal": 8.0,
            "burstiness": 0.0,
            "token_count": input_ids.shape[1],
            "tokens": [],
            "surprisal_tokens": [],
            "risk_score": 10.0
        }

    with torch.no_grad():
        outputs = model(input_ids)
        logits = outputs.logits[:, :-1, :]  # [1, seq_len-1, vocab_size]
        targets = input_ids[:, 1:]           # [1, seq_len-1]

        # Calcolo CrossEntropy (in base 2 per avere i bit di informazione / surprisal)
        loss_fct = torch.nn.CrossEntropyLoss(reduction="none")
        token_losses = loss_fct(logits.reshape(-1, logits.size(-1)), targets.reshape(-1))
        
        # Surprisal in bit (log2)
        log2_e = math.log2(math.e)
        surprisal_bits = (token_losses * log2_e).cpu().tolist()
        
        # Perplessità naturale standard exp(loss)
        mean_nats = token_losses.mean().item()
        ppl = float(math.exp(min(50.0, mean_nats)))
        mean_surprisal = float(sum(surprisal_bits) / max(1, len(surprisal_bits)))
        
        # Burstiness: deviazione standard del surprisal sui token
        if len(surprisal_bits) > 1:
            var_surprisal = sum((s - mean_surprisal) ** 2 for s in surprisal_bits) / (len(surprisal_bits) - 1)
            burstiness = math.sqrt(max(0.0, var_surprisal))
        else:
            burstiness = 0.0

    # Decodifica token per token per evidenziare i punti piatti (basso surprisal)
    tokens_decoded = []
    flat_sequences = []  # sequenze di 3+ token a bassissimo surprisal (< 2.5 bit)
    current_flat = []

    target_tokens = targets[0].cpu().tolist()
    for idx, (tok_id, s_val) in enumerate(zip(target_tokens, surprisal_bits)):
        tok_str = tokenizer.decode([tok_id])
        tokens_decoded.append({
            "token": tok_str,
            "surprisal_bits": round(s_val, 2)
        })
        if s_val < 2.5:
            current_flat.append(tok_str)
        else:
            if len(current_flat) >= 4:
                flat_sequences.append("".join(current_flat).strip())
            current_flat = []
    if len(current_flat) >= 4:
        flat_sequences.append("".join(current_flat).strip())

    # Calibrazione rischio AI basata su Perplessità e Burstiness:
    # - Testo AI cliché: PPL < 25 (log < 3.2), Burstiness < 3.2 -> Rischio AI > 75%
    # - Testo misto: PPL 25-60 -> Rischio 35-70%
    # - Testo umano autentico denso: PPL > 75 (log > 4.3), Burstiness > 4.0 -> Rischio < 20%
    log_ppl = math.log(max(1.0, ppl))
    # Se log_ppl è basso (bassa sorpresa -> AI), z_ppl è negativo -> exp(z) è piccolo -> base_risk è alto
    z_ppl = 1.8 * (log_ppl - 3.70)
    base_risk = 100.0 / (1.0 + math.exp(max(-20.0, min(20.0, z_ppl))))
    
    # Modulazione burstiness: se la burstiness è molto alta (> 4.5), abbassa ulteriormente il rischio
    if burstiness >= 4.5:
        base_risk = max(5.0, base_risk - 15.0)
    elif burstiness <= 3.2:
        base_risk = min(98.0, base_risk + 15.0)

    risk_score = round(max(0.0, min(100.0, base_risk)), 1)

    return {
        "perplexity": round(ppl, 2),
        "mean_surprisal_bits": round(mean_surprisal, 2),
        "burstiness": round(burstiness, 2),
        "token_count": len(surprisal_bits),
        "flat_predictable_segments": flat_sequences[:5],
        "risk_score": risk_score
    }


def analyze_sentences_surprisal(sentences: List[str]) -> List[Dict[str, Any]]:
    """Analizza una lista di frasi calcolando surprisal e perplessità per ciascuna."""
    results = []
    for s in sentences:
        s_clean = s.strip()
        if len(s_clean.split()) < 3:
            continue
        stats = calculate_token_surprisal(s_clean)
        results.append({
            "sentence": s_clean,
            "word_count": len(s_clean.split()),
            "perplexity": stats["perplexity"],
            "burstiness": stats["burstiness"],
            "risk_score": stats["risk_score"],
            "flat_segments": stats["flat_predictable_segments"]
        })
    return results
