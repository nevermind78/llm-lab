"""Entraîne un adaptateur LoRA sur Llama 3.2 3B à partir de train.jsonl.

Le prompt d'entraînement reproduit exactement le gabarit qu'Ollama applique à llama3.2,
pour que l'adaptateur voie à l'inférence le même texte qu'à l'entraînement.

Usage : python entrainer.py [--base DOSSIER_OU_ID_HF] [--epochs 6] [--sortie adaptateur]
Demande une carte graphique NVIDIA (8 Go de mémoire vidéo au moins).
"""
import argparse
import json
import math
import random
import time

import torch
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

p = argparse.ArgumentParser()
p.add_argument("--base", default="unsloth/Llama-3.2-3B-Instruct")
p.add_argument("--donnees", default="train.jsonl")
p.add_argument("--sortie", default="adaptateur")
p.add_argument("--epochs", type=int, default=6)
p.add_argument("--lot", type=int, default=4)
p.add_argument("--lr", type=float, default=2e-4)
p.add_argument("--rang", type=int, default=16)
args = p.parse_args()

EOT = "<|eot_id|>"


def entete(role):
    return f"<|start_header_id|>{role}<|end_header_id|>\n\n"


def prompt_ollama(messages):
    """Texte que produit le gabarit Ollama de llama3.2, jusqu'au début de la réponse."""
    systeme = next((m["content"] for m in messages if m["role"] == "system"), "")
    texte = entete("system") + "Cutting Knowledge Date: December 2023\n\n" + systeme + EOT
    for m in messages:
        if m["role"] == "user":
            texte += entete("user") + m["content"] + EOT
    return texte + entete("assistant")


tok = AutoTokenizer.from_pretrained(args.base)
tok.pad_token = "<|finetune_right_pad_id|>"


def encoder(ex):
    """Renvoie (ids, labels) : la perte ne porte que sur la réponse de l'assistant."""
    msgs = ex["messages"]
    debut = [tok.bos_token_id] + tok(prompt_ollama(msgs[:-1]), add_special_tokens=False)["input_ids"]
    reponse = tok(msgs[-1]["content"] + EOT, add_special_tokens=False)["input_ids"]
    return debut + reponse, [-100] * len(debut) + reponse


with open(args.donnees, encoding="utf-8") as f:
    exemples = [encoder(json.loads(ligne)) for ligne in f]
print(f"{len(exemples)} exemples, {max(len(i) for i, _ in exemples)} tokens au plus")

modele = AutoModelForCausalLM.from_pretrained(args.base, dtype=torch.bfloat16, device_map={"": 0})
modele = get_peft_model(modele, LoraConfig(
    r=args.rang, lora_alpha=2 * args.rang, lora_dropout=0.05, task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]))
modele.print_trainable_parameters()

optimiseur = torch.optim.AdamW([q for q in modele.parameters() if q.requires_grad], lr=args.lr, weight_decay=0.0)
pas_total = args.epochs * math.ceil(len(exemples) / args.lot)
planificateur = torch.optim.lr_scheduler.OneCycleLR(optimiseur, max_lr=args.lr, total_steps=pas_total, pct_start=0.1)


def lot_tenseurs(lot):
    longueur = max(len(i) for i, _ in lot)
    ids = torch.full((len(lot), longueur), tok.pad_token_id)
    labels = torch.full((len(lot), longueur), -100)
    for k, (i, l) in enumerate(lot):
        ids[k, :len(i)] = torch.tensor(i)
        labels[k, :len(l)] = torch.tensor(l)
    return ids.cuda(), (ids != tok.pad_token_id).cuda(), labels.cuda()


modele.train()
debut, pas = time.time(), 0
for epoch in range(args.epochs):
    random.Random(epoch).shuffle(exemples)
    pertes = []
    for k in range(0, len(exemples), args.lot):
        ids, masque, labels = lot_tenseurs(exemples[k:k + args.lot])
        perte = modele(input_ids=ids, attention_mask=masque, labels=labels).loss
        perte.backward()
        torch.nn.utils.clip_grad_norm_(modele.parameters(), 1.0)
        optimiseur.step()
        planificateur.step()
        optimiseur.zero_grad()
        pertes.append(perte.item())
        pas += 1
    print(f"époque {epoch + 1}/{args.epochs} · perte moyenne {sum(pertes) / len(pertes):.3f} · "
          f"{time.time() - debut:.0f} s · mémoire GPU {torch.cuda.max_memory_allocated() / 2**30:.1f} Go", flush=True)

modele.save_pretrained(args.sortie)
print(f"Adaptateur enregistré dans {args.sortie}/ ({pas} pas, {time.time() - debut:.0f} s)")
