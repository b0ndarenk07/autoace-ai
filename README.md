## Repository Structure

```text
autoace-ai/
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   ├── auth.py
│   │   │   │   ├── batches.py
│   │   │   │   ├── results.py
│   │   │   │   └── single.py
│   │   │   ├── schemas/
│   │   │   │   ├── batch.py
│   │   │   │   └── prediction.py
│   │   │   ├── services/
│   │   │   │   ├── batch_service.py
│   │   │   │   └── result_service.py
│   │   │   ├── config.py
│   │   │   └── main.py
│   │   └── requirements.txt
│   │
│   └── web/
│       ├── app/
│       │   ├── dashboard/page.tsx
│       │   ├── login/page.tsx
│       │   ├── globals.css
│       │   ├── layout.tsx
│       │   └── page.tsx
│       ├── components/
│       │   ├── BatchProgress.tsx
│       │   ├── BatchUploader.tsx
│       │   ├── ErrorList.tsx
│       │   └── ResultsTable.tsx
│       ├── .env.local
│       ├── package.json
│       ├── postcss.config.mjs
│       ├── tailwind.config.ts
│       └── tsconfig.json
│
├── data/
├── experiments/
│   ├── baseline/README.md
│   ├── foundation_model/README.md
│   ├── hybrid/README.md
│   ├── calibration.py
│   ├── confusion_matrix.py
│   └── evaluate.py
│
├── scripts/
│   ├── evaluate.py
│   ├── process_batch.py
│   └── train.py
│
├── tests/
│   ├── api/
│   ├── fixtures/
│   ├── models/
│   ├── preprocessing/
│   └── test_audio_pipeline.py
│
├── workers/
│   └── audio/
│       ├── features/
│       │   ├── acoustic.py
│       │   ├── quality.py
│       │   └── silence.py
│       ├── fusion/classifier.py
│       ├── models/
│       │   ├── baseline.py
│       │   ├── emotion.py
│       │   └── noise.py
│       ├── preprocessing/
│       │   ├── decoder.py
│       │   ├── normalizer.py
│       │   └── vad.py
│       ├── validation/output.py
│       ├── pipeline.py
│       └── worker.py
│
├── startup.sh
├── pyproject.toml
└── README.md
```

## Getting Started

### Requirements

- Python 3
- Node.js and npm
- `ffmpeg` available on the system PATH for audio decoding

### Install Everything

From the repository root, run:

```bash
./startup.sh
```

The script creates the backend virtual environment, installs Python dependencies, installs frontend dependencies, and creates `apps/web/.env.local` if it does not already exist.

### Frontend Environment

The frontend reads the backend URL from `apps/web/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Restart the Next.js development server after changing this file.

### Start the Backend

In one terminal:

```bash
cd apps/api
./.venv/bin/python -m uvicorn app.main:app \
	--reload \
	--host 0.0.0.0 \
	--port 8000
```

The API is available at `http://localhost:8000`.

Interactive API documentation is available at:

```text
http://localhost:8000/docs
```

Open that URL in a browser to view the Swagger documentation and try the API endpoints.

### Start the Frontend

In a second terminal:

```bash
cd apps/web
npm run dev
```

The dashboard is available at `http://localhost:3000`.

### Main API Routes

```text
POST /single                 Analyze one .ogg or .wav file
POST /batches                Upload a ZIP of audio files
GET  /batches/{batch_id}     Get batch progress and current results
GET  /results/{batch_id}     Get batch results
GET  /results/{batch_id}/download?format=json
GET  /results/{batch_id}/download?format=csv
```
