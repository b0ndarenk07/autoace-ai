Structure AutoAce AI
│
├── apps/
│ │
│ ├── web/ ← Next.js frontend
│ │ ├── app/
│ │ │ ├── dashboard/
│ │ │ │ └── page.tsx
│ │ │ ├── login/
│ │ │ │ └── page.tsx
│ │ │ ├── globals.css
│ │ │ ├── layout.tsx
│ │ │ └── page.tsx
│ │ │
│ │ └── components/
│ │ ├── BatchUploader.tsx
│ │ ├── BatchProgress.tsx
│ │ ├── ResultsTable.tsx
│ │ └── ErrorList.tsx
│ │
│ └── api/ ← Python API
│ └── app/
│ ├── api/
│ │ ├── auth.py
│ │ ├── batches.py
│ │ └── results.py
│ │
│ ├── schemas/
│ │ ├── batch.py
│ │ └── prediction.py
│ │
│ ├── services/
│ │ ├── batch_service.py
│ │ └── result_service.py
│ │
│ ├── config.py
│ └── main.py
│
└── ...



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
GET  /batches/{batch_id}
GET  /batches/{batch_id}/results
GET  /batches/{batch_id}/download

POST /single