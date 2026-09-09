"use client";

import { useEffect, useState } from "react";
import {
  Activity,
  CheckCircle2,
  Clock3,
  FileAudio,
  Upload,
} from "lucide-react";

import BatchUploader from "../../components/BatchUploader";
import BatchProgress from "../../components/BatchProgress";
import ResultsTable, {
  type AudioResult,
} from "../../components/ResultsTable";

const apiBaseUrl =process.env.NEXT_PUBLIC_API_URL;
export default function DashboardPage() {
  const [batchId, setBatchId] = useState<string | null>(null);
  const [batchStatus, setBatchStatus] = useState<
    "idle" | "uploading" | "processing" | "completed" | "error"
  >("idle");
  const [batchTotal, setBatchTotal] = useState(0);
  const [batchProcessed, setBatchProcessed] = useState(0);
  const [currentFile, setCurrentFile] = useState<string | null>(null);
  const [currentProgress, setCurrentProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState("waiting");
  const [results, setResults] = useState<AudioResult[]>([]);

  useEffect(() => {
    if (!batchId) return;

    let timer: ReturnType<typeof setInterval> | undefined;

    const pollBatch = async () => {
      try {
        const response = await fetch(`${apiBaseUrl}/batches/${batchId}`);
        if (!response.ok) return;

        const data = await response.json();
        setBatchTotal(data.total ?? 0);
        setBatchProcessed(data.processed ?? 0);
        setCurrentFile(data.current_file ?? null);
        setCurrentProgress(data.current_progress ?? 0);
        setCurrentStage(data.current_stage ?? "waiting");

        const completedResults = (data.results ?? []).filter(
          (result: AudioResult & { status?: string }) =>
            result.status === "completed",
        );
        setResults(completedResults);

        if (data.status === "processing") {
          setBatchStatus("processing");
          return;
        }

        const isFinished =
          data.status === "completed" ||
          data.status === "completed_with_errors" ||
          data.status === "error";

        setBatchStatus(
          data.status === "error"
            ? "error"
            : isFinished
              ? "completed"
              : "processing",
        );

        if (isFinished) {
          if (timer) clearInterval(timer);
        }
      } catch {
        setBatchStatus("error");
        if (timer) clearInterval(timer);
      }
    };

    pollBatch();
    timer = setInterval(pollBatch, 1500);

    return () => {
      if (timer) clearInterval(timer);
    };
  }, [batchId]);

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-slate-800 bg-slate-950/90">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-xl font-semibold tracking-tight">
              AutoAce AI
            </h1>
            <p className="text-sm text-slate-400">
              Production Call Audio Analysis
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900 px-3 py-1.5 text-xs text-slate-300">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              System online
            </div>

            <button className="rounded-lg border border-slate-800 px-4 py-2 text-sm text-slate-300 transition hover:bg-slate-900">
              Sign out
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-6 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-semibold">Audio Analysis</h2>
          <p className="mt-1 text-sm text-slate-400">
            Upload a batch of production calls to analyze emotional tone,
            background noise, and audio quality.
          </p>
        </div>

        <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            icon={<FileAudio size={20} />}
            label="Files processed"
            value={String(batchProcessed || 0)}
          />

          <StatCard
            icon={<CheckCircle2 size={20} />}
            label="Completed"
            value={
              batchStatus === "completed"
                ? String(batchProcessed || 0)
                : "0"
            }
          />

          <StatCard
            icon={<Clock3 size={20} />}
            label="Processing"
            value={
              batchStatus === "processing"
                ? String(Math.max(batchTotal - batchProcessed, 0))
                : "0"
            }
          />

          <StatCard
            icon={<Activity size={20} />}
            label="Avg. confidence"
            value="—"
          />
        </div>

        <section className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6">
          <div className="mb-6 flex items-start gap-4">
            <div className="rounded-xl bg-slate-800 p-3">
              <Upload size={22} />
            </div>

            <div>
              <h3 className="text-lg font-medium">Upload a batch</h3>
              <p className="mt-1 text-sm text-slate-400">
                Upload a ZIP containing audio files.
              </p>
            </div>
          </div>

          <BatchUploader
            onSingleResult={(result) => {
              setResults([result]);
              setBatchId(null);
              setBatchStatus("completed");
              setBatchTotal(1);
              setBatchProcessed(1);
            }}
            onUploadSuccess={(nextBatchId, total) => {
              setResults([]);
              setBatchId(nextBatchId);
              setBatchStatus("processing");
              setBatchTotal(total);
              setBatchProcessed(0);
            }}
          />

          {batchId && (
            <div className="mt-6">
              <BatchProgress
                total={batchTotal}
                processed={batchProcessed}
                status={batchStatus}
                currentFile={currentFile}
                currentProgress={currentProgress}
                currentStage={currentStage}
              />
            </div>
          )}
        </section>

        <section className="mt-8">
          <ResultsTable
            results={results}
            onClear={() => setResults([])}
          />
        </section>

      </div>
    </main>
  );
}

function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-5">
      <div className="mb-4 flex items-center justify-between">
        <div className="rounded-lg bg-slate-800 p-2 text-slate-300">
          {icon}
        </div>
      </div>

      <p className="text-sm text-slate-400">{label}</p>

      <p className="mt-1 text-2xl font-semibold">{value}</p>
    </div>
  );
}