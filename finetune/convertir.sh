#!/bin/bash
# Convertit le modèle fusionné (dossier fusionne/) en un fichier GGUF 4 bits pour Ollama.
# Tourne sous Linux, dans un conteneur Docker lancé depuis le dossier du projet :
#   docker run --rm -v "${PWD}/finetune:/work" -w /work python:3.12-slim bash convertir.sh
set -euo pipefail

TAG=${LLAMA_TAG:-b12373}                 # version de llama.cpp dont on prend les outils
SORTIE=${1:-eps-assistant-q4_k_m.gguf}

[ -d fusionne ] || { echo "Dossier fusionne/ introuvable : lancez d'abord fusionner.py"; exit 1; }

# Outils système absents de l'image python:3.12-slim
if ! command -v git >/dev/null || ! ldconfig -p | grep -q libgomp; then
  apt-get update -qq >/dev/null
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq git libgomp1 >/dev/null 2>&1
fi

python3 -m pip install -q --root-user-action=ignore --disable-pip-version-check \
  torch --index-url https://download.pytorch.org/whl/cpu
python3 -m pip install -q --root-user-action=ignore --disable-pip-version-check \
  "transformers<5" sentencepiece protobuf numpy

[ -f llama.cpp/conversion/__init__.py ] || { rm -rf llama.cpp; git clone -q --depth 1 --branch "$TAG" https://github.com/ggml-org/llama.cpp.git llama.cpp; }

echo "== 1/2 conversion en GGUF 16 bits"
python3 llama.cpp/convert_hf_to_gguf.py fusionne --outfile /tmp/f16.gguf --outtype f16 2>&1 | tail -2

echo "== 2/2 quantification en 4 bits (Q4_K_M)"
mkdir -p /tmp/llama-bin
python3 - <<EOF
import tarfile, urllib.request
url = "https://github.com/ggml-org/llama.cpp/releases/download/$TAG/llama-$TAG-bin-ubuntu-x64.tar.gz"
urllib.request.urlretrieve(url, "/tmp/llama.tar.gz")
tarfile.open("/tmp/llama.tar.gz").extractall("/tmp/llama-bin")
EOF
QUANT=$(find /tmp/llama-bin -name llama-quantize -type f | head -1)
LD_LIBRARY_PATH=$(dirname "$QUANT") "$QUANT" /tmp/f16.gguf "$SORTIE" Q4_K_M 2>&1 | tail -3
echo "== terminé"
ls -la "$SORTIE"
