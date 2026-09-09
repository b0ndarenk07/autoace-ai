"use client";

interface BatchProgressProps {
  total: number;
  processed: number;
  status?: "idle" | "uploading" | "processing" | "completed" | "error";
  currentFile?: string | null;
  currentProgress?: number;
  currentStage?: string;
}

export default function BatchProgress({
  total,
  processed,
  status = "idle",
  currentFile,
  currentProgress = 0,
  currentStage = "",
}: BatchProgressProps) {
  const progress = total > 0
    ? Math.min(Math.round(((processed + currentProgress / 100) / total) * 100), 100)
    : 0;

  const statusText = {
    idle: "Ready",
    uploading: "Uploading...",
    processing: "Processing audio files...",
    completed: "Completed",
    error: "Processing failed",
  }[status];

  if (status === "idle" && total === 0) {
    return null;
  }

  return (
    <div className="w-full rounded-xl border border-gray-800 bg-gray-900/60 p-5">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-white">
            Batch Progress
          </h3>

          <p className="mt-1 text-sm text-gray-400">{statusText}</p>
          {currentFile && status === "processing" && (
            <p className="mt-1 text-xs text-gray-500">
              {currentFile}: {currentStage} ({currentProgress}%)
            </p>
          )}
        </div>

        <span className="text-sm font-medium text-gray-300">
          {processed} / {total}
        </span>
      </div>

      <div className="h-2 w-full overflow-hidden rounded-full bg-gray-800">
        <div
          className="h-full rounded-full bg-blue-500 transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="mt-2 flex justify-between text-xs text-gray-500">
        <span>{progress}%</span>

        {status === "completed" && (
          <span className="text-green-400">All audio files processed</span>
        )}
      </div>
    </div>
  );
}