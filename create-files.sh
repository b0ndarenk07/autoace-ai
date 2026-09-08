#!/usr/bin/env bash

set -e

echo "Creating project structure..."

# -------------------------
# Directories
# -------------------------

mkdir -p \
  apps/web/app/login \
  apps/web/app/dashboard \
  apps/web/components \
  \
  apps/api/app/api \
  apps/api/app/services \
  apps/api/app/schemas \
  \
  workers/audio/preprocessing \
  workers/audio/features \
  workers/audio/models \
  workers/audio/fusion \
  workers/audio/validation \
  \
  experiments/baseline \
  experiments/foundation_model \
  experiments/hybrid \
  \
  tests/api \
  tests/preprocessing \
  tests/models \
  tests/fixtures \
  \
  scripts \
  data

# -------------------------
# Web
# -------------------------

touch \
  apps/web/package.json \
  apps/web/app/page.tsx \
  apps/web/app/layout.tsx \
  apps/web/app/login/page.tsx \
  apps/web/app/dashboard/page.tsx \
  apps/web/components/BatchUploader.tsx \
  apps/web/components/BatchProgress.tsx \
  apps/web/components/ResultsTable.tsx \
  apps/web/components/ErrorList.tsx

# -------------------------
# API
# -------------------------

touch \
  apps/api/requirements.txt \
  apps/api/app/main.py \
  apps/api/app/config.py \
  apps/api/app/api/auth.py \
  apps/api/app/api/batches.py \
  apps/api/app/api/results.py \
  apps/api/app/services/batch_service.py \
  apps/api/app/services/result_service.py \
  apps/api/app/schemas/batch.py \
  apps/api/app/schemas/prediction.py

# -------------------------
# Audio Worker
# -------------------------

touch \
  workers/audio/worker.py \
  workers/audio/pipeline.py \
  workers/audio/preprocessing/decoder.py \
  workers/audio/preprocessing/normalizer.py \
  workers/audio/preprocessing/vad.py \
  workers/audio/features/acoustic.py \
  workers/audio/features/quality.py \
  workers/audio/features/silence.py \
  workers/audio/models/baseline.py \
  workers/audio/models/emotion.py \
  workers/audio/models/noise.py \
  workers/audio/fusion/classifier.py \
  workers/audio/validation/output.py

# -------------------------
# Experiments
# -------------------------

touch \
  experiments/evaluate.py \
  experiments/confusion_matrix.py \
  experiments/calibration.py \
  experiments/baseline/README.md \
  experiments/foundation_model/README.md \
  experiments/hybrid/README.md

# -------------------------
# Tests
# -------------------------

touch \
  tests/api/test_batches.py \
  tests/api/test_results.py \
  tests/preprocessing/test_decoder.py \
  tests/preprocessing/test_vad.py \
  tests/models/test_emotion.py \
  tests/models/test_noise.py

# -------------------------
# Scripts
# -------------------------

touch \
  scripts/process_batch.py \
  scripts/train.py \
  scripts/evaluate.py

# -------------------------
# Root files
# -------------------------

touch \
  .env.example \
  .gitignore \
  README.md \
  pyproject.toml \
  data/.gitkeep

echo "AutoAce AI project structure created successfully."