#!/bin/sh
# À exécuter DANS le conteneur Ollama. Crée le modèle « eps-assistant » à partir du fichier
# /tmp/eps-assistant.gguf, en reprenant le gabarit de prompt et les paramètres de llama3.2:3b.
set -e
GGUF=${1:-/tmp/eps-assistant.gguf}
NOM=${2:-eps-assistant}

[ -f "$GGUF" ] || { echo "Fichier $GGUF introuvable dans le conteneur"; exit 1; }
ollama show --modelfile llama3.2:3b \
  | grep -v '^#' \
  | sed "s|^FROM .*|FROM $GGUF|" \
  | awk '/^LICENSE/{exit} {print}' > /tmp/Modelfile
ollama create "$NOM" -f /tmp/Modelfile
rm -f "$GGUF" /tmp/Modelfile
ollama list
