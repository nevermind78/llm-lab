"""Compare des modèles Ollama sur test.jsonl (questions jamais vues à l'entraînement).

Pour chaque question, on mesure le « rappel » : la part des mots importants de la réponse
de référence (mots de 4 lettres ou plus, nombres) que l'on retrouve dans la réponse du modèle.

Usage : python evaluer.py MODELE [MODELE ...] [--url http://localhost:11434] [--n 58]
"""
import argparse
import json
import re
import time
import unicodedata
import urllib.request

p = argparse.ArgumentParser()
p.add_argument("modeles", nargs="+")
p.add_argument("--url", default="http://localhost:11434")
p.add_argument("--donnees", default="test.jsonl")
p.add_argument("--n", type=int, default=0, help="nombre de questions (0 = toutes)")
p.add_argument("--sortie", default="evaluation.json")
args = p.parse_args()


def mots(texte):
    texte = unicodedata.normalize("NFKD", texte.lower()).encode("ascii", "ignore").decode()
    texte = re.sub(r"(?<=\d)[   ](?=\d)", "", texte)          # « 7 849 » -> « 7849 »
    return {m for m in re.findall(r"[a-z0-9@._-]+", texte) if len(m) >= 4 or m.isdigit()}


def demander(modele, messages):
    corps = json.dumps({"model": modele, "messages": messages, "stream": False,
                        "options": {"temperature": 0, "num_predict": 200}}).encode()
    req = urllib.request.Request(f"{args.url}/api/chat", data=corps, headers={"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        rep = json.load(r)
    return rep["message"]["content"].strip(), rep.get("eval_count", 0) / max(rep.get("eval_duration", 1) / 1e9, 1e-9)


with open(args.donnees, encoding="utf-8") as f:
    tests = [json.loads(ligne)["messages"] for ligne in f]
if args.n:
    tests = tests[:args.n]

resultats = []
for modele in args.modeles:
    debut, rappels, debits = time.time(), [], []
    for msgs in tests:
        reference = msgs[-1]["content"]
        reponse, debit = demander(modele, msgs[:-1])
        attendus = mots(reference)
        rappel = len(attendus & mots(reponse)) / len(attendus)
        rappels.append(rappel)
        debits.append(debit)
        resultats.append({"modele": modele, "question": msgs[1]["content"], "reference": reference,
                          "reponse": reponse, "rappel": round(rappel, 2)})
    print(f"{modele:28s} rappel moyen {100 * sum(rappels) / len(rappels):5.1f} % · "
          f"réponses à plus de 80 % : {sum(r >= 0.8 for r in rappels)}/{len(rappels)} · "
          f"{sum(debits) / len(debits):.1f} tokens/s · {time.time() - debut:.0f} s", flush=True)

with open(args.sortie, "w", encoding="utf-8") as f:
    json.dump(resultats, f, ensure_ascii=False, indent=1)
print(f"Détail des réponses dans {args.sortie}")
