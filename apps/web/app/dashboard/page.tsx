"use client";

import {
  Activity,
  CheckCircle2,
  Clock3,
  FileAudio,
  Upload,
} from "lucide-react";

import BatchUploader from "../../components/BatchUploader";
import BatchProgress from "../../components/BatchProgress";
export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
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
        {/* Page heading */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold">Audio Analysis</h2>
          <p className="mt-1 text-sm text-slate-400">
            Upload a batch of production calls to analyze emotional tone,
            background noise, and audio quality.
          </p>
        </div>

        {/* Stats */}
        <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            icon={<FileAudio size={20} />}
            label="Files processed"
            value="0"
          />

          <StatCard
            icon={<CheckCircle2 size={20} />}
            label="Completed"
            value="0"
          />

          <StatCard
            icon={<Clock3 size={20} />}
            label="Processing"
            value="0"
          />

          <StatCard
            icon={<Activity size={20} />}
            label="Avg. confidence"
            value="—"
          />
        </div>

        {/* Upload section */}
        <section className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6">
          <div className="mb-6 flex items-start gap-4">
            <div className="rounded-xl bg-slate-800 p-3">
              <Upload size={22} />
            </div>

            <div>
              <h3 className="text-lg font-medium">Upload a batch</h3>
              <p className="mt-1 text-sm text-slate-400">
                Upload a ZIP containing audio files and a CSV manifest.
              </p>
            </div>
          </div>

          <BatchUploader />
            <div className="mt-6">
                <BatchProgress
                    total={100}
                    processed={42}
                    status="processing"
                />
            </div>
        </section>

        {/* Recent batches */}
        <section className="mt-8">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium">Recent batches</h3>
              <p className="text-sm text-slate-400">
                Your recently submitted audio analysis jobs.
              </p>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/50">
            <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
              <FileAudio
                size={36}
                className="mb-4 text-slate-600"
              />

              <p className="text-sm font-medium text-slate-300">
                No batches yet
              </p>

              <p className="mt-1 max-w-md text-sm text-slate-500">
                Upload your first batch above and its processing status and
                results will appear here.
              </p>
            </div>
          </div>
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