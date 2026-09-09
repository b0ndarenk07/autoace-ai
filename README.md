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
├── create-files.sh
├── pyproject.toml
└── README.md
```

                    AutoAce AI Dashboard
                            │
             ┌──────────────┴──────────────┐
             │                             │
       Single Call                    Batch Evaluation
             │                             │
        .ogg / audio                 ZIP / folder
             │                             │
             ▼                             ▼
       Analyze one                    Validate batch
             │                             │
             └──────────────┬──────────────┘
                            ▼
                     Same prediction
                         pipeline
                            │
                            ▼
                    Required JSON schema
                            │
                            ▼
                       Results UI

Start
↓
POST /batches/:id/process
↓
poll / websocket
↓
progress
↓
results
↓

CSV / JSON download

Browser
│
▼
Next.js
│
▼
FastAPI
│
├── Batch validation
├── Job management
└── Results
│
▼
Python worker
│
├── Audio preprocessing
├── Emotion model
├── Noise detection
└── Quality analysis

BACKEND
POST /auth/login
POST /batches
GET /batches/{batch_id}
GET /batches/{batch_id}/results
GET /batches/{batch_id}/download

POST /single
