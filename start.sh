#!/usr/bin/env bash
set -e
export AI_PATH=${AI_PATH:-./IA_BRENO}
cd SITE_AI
pip install -r requirements.txt
exec gunicorn app:app -b 0.0.0.0:${PORT:-5000}