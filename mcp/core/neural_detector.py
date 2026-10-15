"""
Writing Suite - Neural AI Detector Module
Utilizza il modello SOTA DeBERTa-v3-large (desklib/ai-text-detector-v1.01, #1 su RAID Benchmark)
per stimare la probabilità neurale che il testo sia generato da LLM (ChatGPT, Claude, Llama).
Sfrutta nativamente l'accelerazione Apple Silicon Metal (MPS) su Mac M-series (~35ms per inferenza).
"""

import os
import sys
import glob
import logging
import warnings
from typing import Optional, List, Dict, Union, Any
from pathlib import Path

# Silenzia warning innocui di deprecazione JIT e avvisi di download da HF Hub
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
warnings.filterwarnings("ignore", category=FutureWarning)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)

_MODEL = None
_TOKENIZER = None
_DEVICE = None
_MODEL_NAME = "desklib/ai-text-detector-v1.01"


def get_device():
    """Rileva il miglior dispositivo di calcolo disponibile (MPS per Mac, CUDA per GPU, altrimenti CPU)."""
    global _DEVICE
    if _DEVICE is not None:
        return _DEVICE
    
    try:
        import torch
        if torch.backends.mps.is_available():
            _DEVICE = torch.device("mps")
        elif torch.cuda.is_available():
            _DEVICE = torch.device("cuda")
        else:
            _DEVICE = torch.device("cpu")
    except Exception:
        _DEVICE = "cpu"
    return _DEVICE


class DesklibAIDetectionModel:
    """Implementazione pura PyTorch compatibile con i pesi safetensors di desklib."""
    pass


def load_model(model_name: Optional[str] = None):
    """Carica il modello e il tokenizer nella memoria unificata (in cache singleton)."""
    global _MODEL, _TOKENIZER, _MODEL_NAME
    if model_name:
        _MODEL_NAME = model_name
        
    if _MODEL is not None and _TOKENIZER is not None:
        return _MODEL, _TOKENIZER
        
    try:
        import torch
        import torch.nn as nn
        from transformers import AutoTokenizer, AutoConfig, AutoModel
        from huggingface_hub import hf_hub_download
        from safetensors.torch import load_file
        
        device = get_device()
        try:
            _TOKENIZER = AutoTokenizer.from_pretrained(_MODEL_NAME, local_files_only=True)
        except Exception:
            _TOKENIZER = AutoTokenizer.from_pretrained(_MODEL_NAME)
        
        if "desklib" in _MODEL_NAME:
            try:
                config = AutoConfig.from_pretrained(_MODEL_NAME, local_files_only=True)
            except Exception:
                config = AutoConfig.from_pretrained(_MODEL_NAME)
            
            class CustomDesklibModel(nn.Module):
                def __init__(self, cfg):
                    super().__init__()
                    self.model = AutoModel.from_config(cfg)
                    self.classifier = nn.Linear(cfg.hidden_size, 1)

                def forward(self, input_ids, attention_mask=None):
                    outputs = self.model(input_ids, attention_mask=attention_mask)
                    last_hidden_state = outputs[0]
                    input_mask_expanded = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
                    sum_embeddings = torch.sum(last_hidden_state * input_mask_expanded, dim=1)
                    sum_mask = torch.clamp(input_mask_expanded.sum(dim=1), min=1e-9)
                    pooled_output = sum_embeddings / sum_mask
                    logits = self.classifier(pooled_output)
                    return logits

            _MODEL = CustomDesklibModel(config)
            
            # Carica file safetensors in modalità offline locale
            try:
                safetensors_path = hf_hub_download(repo_id=_MODEL_NAME, filename="model.safetensors", local_files_only=True)
            except Exception:
                safetensors_path = hf_hub_download(repo_id=_MODEL_NAME, filename="model.safetensors")
            state_dict = load_file(safetensors_path)
            _MODEL.load_state_dict(state_dict)
            _MODEL.to(device)
            _MODEL.eval()
        else:
            try:
                from transformers import AutoModelForSequenceClassification
                _MODEL = AutoModelForSequenceClassification.from_pretrained(_MODEL_NAME, local_files_only=True)
            except Exception:
                _MODEL = AutoModelForSequenceClassification.from_pretrained(_MODEL_NAME)
            _MODEL.to(device)
            _MODEL.eval()
            
        return _MODEL, _TOKENIZER
    except Exception as e:
        print(f"[Neural Detector Error]: {e}", file=sys.stderr)
        return None, None


def is_neural_available() -> bool:
    """Verifica se il motore neurale è pronto per l'inferenza."""
    try:
        import torch
        import transformers
        return True
    except ImportError:
        return False


def predict_sliding_window_chunks(text: str, chunk_size: int = 384, stride: int = 192) -> Dict[str, Any]:
    """
    Scansiona il documento continuo in finestre scorrevoli sovrapposte (sliding window 50% overlap).
    Cattura transizioni tra paragrafi, ripetizioni di parole e coerenza macroscopica.
    """
    model, tokenizer = load_model()
    if model is None or tokenizer is None or not text.strip():
        return {
            "chunks": [],
            "worst_chunk_score": 0.0,
            "mean_chunk_score": 0.0,
            "p80_chunk_score": 0.0,
            "hotspots": [],
            "hotspots_count": 0
        }

    import torch
    device = get_device()

    full_tokens = tokenizer(text, return_tensors="pt", truncation=False)
    input_ids = full_tokens["input_ids"][0]
    total_tokens = len(input_ids)

    if total_tokens <= 40:
        return {
            "chunks": [],
            "worst_chunk_score": 0.0,
            "mean_chunk_score": 0.0,
            "p80_chunk_score": 0.0,
            "hotspots": [],
            "hotspots_count": 0
        }

    chunks = []
    chunk_meta = []
    for start in range(0, total_tokens, stride):
        end = min(start + chunk_size, total_tokens)
        c_ids = input_ids[start:end]
        if len(c_ids) < 30:
            continue
        chunks.append(c_ids)
        snippet = tokenizer.decode(c_ids[:45], skip_special_tokens=True).strip()
        chunk_meta.append({
            "start_token": start,
            "end_token": end,
            "snippet": snippet + "...",
            "tokens_count": len(c_ids)
        })
        if end >= total_tokens:
            break

    if not chunks:
        return {
            "chunks": [],
            "worst_chunk_score": 0.0,
            "mean_chunk_score": 0.0,
            "p80_chunk_score": 0.0,
            "hotspots": [],
            "hotspots_count": 0
        }

    # Batch padding e inferenza su Metal MPS
    batch_ids = torch.nn.utils.rnn.pad_sequence(chunks, batch_first=True, padding_value=tokenizer.pad_token_id).to(device)
    mask = (batch_ids != tokenizer.pad_token_id).long().to(device)

    with torch.no_grad():
        if "desklib" in _MODEL_NAME:
            logits = model(batch_ids, attention_mask=mask)
            probs = (torch.sigmoid(logits).squeeze(-1) * 100.0).cpu().tolist()
        else:
            outputs = model(batch_ids, attention_mask=mask)
            probs = (torch.softmax(outputs.logits, dim=-1)[:, 1] * 100.0).cpu().tolist()

    if not isinstance(probs, list):
        probs = [probs]

    evaluated_chunks = []
    hotspots = []
    for meta, p in zip(chunk_meta, probs):
        p_val = round(float(p), 1)
        badge = "🔴" if p_val >= 65.0 else ("🟡" if p_val >= 35.0 else "🟢")
        item = {
            **meta,
            "ai_probability": p_val,
            "badge": badge,
            "is_hotspot": p_val >= 60.0
        }
        evaluated_chunks.append(item)
        if p_val >= 60.0:
            hotspots.append(item)

    sorted_probs = sorted(probs)
    worst = round(float(max(probs)), 1)
    mean_chunk = round(float(sum(probs) / len(probs)), 1)
    p80_idx = int(len(sorted_probs) * 0.80)
    p80_chunk = round(float(sorted_probs[min(p80_idx, len(sorted_probs) - 1)]), 1)

    return {
        "total_chunks": len(evaluated_chunks),
        "worst_chunk_score": worst,
        "mean_chunk_score": mean_chunk,
        "p80_chunk_score": p80_chunk,
        "hotspots_count": len(hotspots),
        "hotspots": hotspots,
        "chunks": evaluated_chunks
    }


def predict_sentences_batch(
    sentences: List[str], with_context: bool = True
) -> List[Dict[str, Union[str, float, bool]]]:
    """
    Analizza una lista di frasi in batch su GPU Metal MPS.
    Se with_context=True, valuta sia la frase isolata sia la frase nel trigramma [S_{i-1}, S_i, S_{i+1}],
    intercettando ripetizioni lessicali e flussi transizionali tra periodi adiacenti.
    """
    model, tokenizer = load_model()
    if model is None or tokenizer is None or not sentences:
        return []

    import torch
    device = get_device()

    single_texts = []
    context_texts = []
    valid_indices = []

    for idx, s in enumerate(sentences):
        stripped = s.strip()
        if len(stripped.split()) >= 3:
            single_texts.append(stripped)
            valid_indices.append(idx)
            
            # Trigramma di contesto [precedente, attuale, successiva]
            prev_s = sentences[idx - 1].strip() if idx > 0 else ""
            next_s = sentences[idx + 1].strip() if idx + 1 < len(sentences) else ""
            ctx_parts = [p for p in [prev_s, stripped, next_s] if p]
            context_texts.append(" ".join(ctx_parts))

    if not valid_indices:
        return [
            {
                "text": s,
                "ai_probability": 0.0,
                "standalone_probability": 0.0,
                "context_probability": 0.0,
                "context_penalty": 0.0,
                "context_anomaly": False,
                "label": "TOO_SHORT",
                "badge": "⚪"
            }
            for s in sentences
        ]

    def _score_text_list(texts: List[str], max_len: int = 256) -> List[float]:
        out = []
        batch_size = 32
        for b_idx in range(0, len(texts), batch_size):
            b_texts = texts[b_idx : b_idx + batch_size]
            toks = tokenizer(b_texts, padding=True, truncation=True, max_length=max_len, return_tensors="pt").to(device)
            with torch.no_grad():
                if "desklib" in _MODEL_NAME:
                    logits = model(toks["input_ids"], attention_mask=toks["attention_mask"])
                    p_list = (torch.sigmoid(logits).squeeze(-1) * 100.0).cpu().tolist()
                else:
                    outs = model(**toks)
                    p_list = (torch.softmax(outs.logits, dim=-1)[:, 1] * 100.0).cpu().tolist()
                if not isinstance(p_list, list):
                    p_list = [p_list]
                out.extend(p_list)
        return out

    single_probs = _score_text_list(single_texts, max_len=256)
    if with_context and len(context_texts) > 1:
        context_probs = _score_text_list(context_texts, max_len=384)
    else:
        context_probs = single_probs

    prob_map = {}
    for j, orig_idx in enumerate(valid_indices):
        p_sing = round(float(single_probs[j]), 1)
        p_ctx = round(float(context_probs[j]), 1)
        # Blend bilanciato: 40% isolata, 60% nel contesto discorsivo del paragrafo
        p_final = round(0.40 * p_sing + 0.60 * p_ctx, 1)
        penalty = round(max(0.0, p_ctx - p_sing), 1)
        prob_map[orig_idx] = {
            "ai_probability": p_final,
            "standalone_probability": p_sing,
            "context_probability": p_ctx,
            "context_penalty": penalty,
            "context_anomaly": penalty >= 15.0
        }

    results = []
    for orig_idx, s in enumerate(sentences):
        if orig_idx in prob_map:
            info = prob_map[orig_idx]
            p = info["ai_probability"]
            badge = "🔴" if p >= 65.0 else ("🟡" if p >= 35.0 else "🟢")
            label = "AI" if p >= 65.0 else ("MIXED" if p >= 35.0 else "HUMAN")
            results.append({
                "text": s,
                "ai_probability": p,
                "standalone_probability": info["standalone_probability"],
                "context_probability": info["context_probability"],
                "context_penalty": info["context_penalty"],
                "context_anomaly": info["context_anomaly"],
                "label": label,
                "badge": badge
            })
        else:
            results.append({
                "text": s,
                "ai_probability": 0.0,
                "standalone_probability": 0.0,
                "context_probability": 0.0,
                "context_penalty": 0.0,
                "context_anomaly": False,
                "label": "TOO_SHORT",
                "badge": "⚪"
            })

    return results


def predict_text_score(text: str) -> Optional[float]:
    """
    Predice la probabilità complessiva che il testo sia generato da AI (0.0 - 100.0%)
    usando l'aggregazione non-lineare multi-scala di livello industriale (stile Copyleaks):
      Composite = 0.45 * Mean_Frasi_Ponderata + 0.35 * P80_Frasi + 0.20 * Worst_Chunk
    """
    model, tokenizer = load_model()
    if model is None or tokenizer is None:
        return None

    import re
    raw_sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip().split()) >= 3]
    if len(raw_sents) >= 2:
        sent_scores = predict_sentences_batch(raw_sents, with_context=True)
        if sent_scores:
            total_words = sum(len(s["text"].split()) for s in sent_scores)
            if total_words > 0:
                weighted_prob = sum(s["ai_probability"] * len(s["text"].split()) for s in sent_scores) / total_words

                all_probs = sorted([s["ai_probability"] for s in sent_scores])
                p80_idx = int(len(all_probs) * 0.80)
                p80_val = all_probs[min(p80_idx, len(all_probs) - 1)]

                chunk_res = predict_sliding_window_chunks(text)
                worst_chunk = chunk_res.get("worst_chunk_score", weighted_prob)

                # Composite score multi-scala Copyleaks
                composite = (0.45 * weighted_prob) + (0.35 * p80_val) + (0.20 * worst_chunk)
                return round(float(composite), 1)

    import torch
    tokens = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True
    ).to(get_device())

    with torch.no_grad():
        if "desklib" in _MODEL_NAME:
            logits = model(tokens["input_ids"], attention_mask=tokens["attention_mask"])
            ai_prob = torch.sigmoid(logits).item() * 100.0
        else:
            outputs = model(**tokens)
            probs = torch.softmax(outputs.logits, dim=-1)
            ai_prob = probs[0][1].item() * 100.0

    return round(float(ai_prob), 1)

