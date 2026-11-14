"""Évalue un modèle Hugging Face (base ou fusionné) sur test.jsonl, directement sur la carte graphique.

Même mesure que evaluer.py : part des mots importants de la référence retrouvés dans la réponse.

Usage : python evaluer_hf.py DOSSIER_MODELE [--sortie evaluation-hf.json]
"""
import argparse
import json
import re
import time
import unicodedata

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

p = argparse.ArgumentParser()
p.add_argument("modele")
p.add_argument("--donnees", default="test.jsonl")
p.add_argument("--sortie", default="evaluation-hf.json")
args = p.parse_args()

EOT = "<|eot_id|>"


def entete(role):
    return f"<|start_header_id|>{role}<|end_header_id|>\n\n"


def prompt_ollama(messages):
    systeme = next((m["content"] for m in messages if m["role"] == "system"), "")
    texte = entete("system") + "Cutting Knowledge Date: December 2023\n\n" + systeme + EOT
    for m in messages:
        if m["role"] == "user":
            texte += entete("user") + m["content"] + EOT
    return texte + entete("assistant")


def mots(texte):
    texte = unicodedata.normalize("NFKD", texte.lower()).encode("ascii", "ignore").decode()
    texte = re.sub(r"(?<=\d)[   ](?=\d)", "", texte)
    return {m for m in re.findall(r"[a-z0-9@._-]+", texte) if len(m) >= 4 or m.isdigit()}


tok = AutoTokenizer.from_pretrained(args.modele)
modele = AutoModelForCausalLM.from_pretrained(args.modele, dtype=torch.bfloat16, device_map={"": 0}).eval()
fin = tok.convert_tokens_to_ids(EOT)

with open(args.donnees, encoding="utf-8") as f:
    tests = [json.loads(ligne)["messages"] for ligne in f]

debut, resultats = time.time(), []
for msgs in tests:
    ids = torch.tensor([[tok.bos_token_id] + tok(prompt_ollama(msgs[:-1]), add_special_tokens=False)["input_ids"]]).cuda()
    with torch.no_grad():
        sortie = modele.generate(ids, attention_mask=torch.ones_like(ids), max_new_tokens=200, do_sample=False,
                                 eos_token_id=fin, pad_token_id=fin)
    reponse = tok.decode(sortie[0, ids.shape[1]:], skip_special_tokens=True).strip()
    attendus = mots(msgs[-1]["content"])
    resultats.append({"question": msgs[1]["content"], "reference": msgs[-1]["content"], "reponse": reponse,
                      "rappel": round(len(attendus & mots(reponse)) / len(attendus), 2)})

rappels = [r["rappel"] for r in resultats]
print(f"{args.modele}: rappel moyen {100 * sum(rappels) / len(rappels):.1f} % · "
      f"réponses à plus de 80 % : {sum(r >= 0.8 for r in rappels)}/{len(rappels)} · {time.time() - debut:.0f} s")
with open(args.sortie, "w", encoding="utf-8") as f:
    json.dump(resultats, f, ensure_ascii=False, indent=1)
