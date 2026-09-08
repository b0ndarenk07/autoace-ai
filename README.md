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

<!-- /Processing Results -->

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
