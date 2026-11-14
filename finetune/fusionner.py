"""Fusionne l'adaptateur LoRA dans le modèle de base et enregistre un modèle complet.

Ollama n'accepte plus les adaptateurs LoRA séparés : il lui faut un modèle entier.

Usage : python fusionner.py [--base DOSSIER_OU_ID_HF] [--adaptateur adaptateur] [--sortie fusionne]
"""
import argparse

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

p = argparse.ArgumentParser()
p.add_argument("--base", default="unsloth/Llama-3.2-3B-Instruct")
p.add_argument("--adaptateur", default="adaptateur")
p.add_argument("--sortie", default="fusionne")
args = p.parse_args()

modele = AutoModelForCausalLM.from_pretrained(args.base, dtype=torch.float16)
modele = PeftModel.from_pretrained(modele, args.adaptateur).merge_and_unload()
modele.save_pretrained(args.sortie, safe_serialization=True)
AutoTokenizer.from_pretrained(args.base).save_pretrained(args.sortie)
print(f"Modèle fusionné enregistré dans {args.sortie}/")
