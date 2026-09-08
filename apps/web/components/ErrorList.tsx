"use client";

export interface BatchError {
  name: string;
  error: string;
}

interface ErrorListProps {
  errors?: BatchError[];
}

export default function ErrorList({
  errors = [],
}: ErrorListProps) {
  if (errors.length === 0) {
    return null;
  }

  return (
    <div className="rounded-xl border border-red-900/50 bg-red-950/20">
      <div className="border-b border-red-900/50 px-5 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-red-400">
              Processing Errors
            </h3>

            <p className="mt-1 text-sm text-gray-500">
              {errors.length} file
              {errors.length === 1 ? "" : "s"} could not be processed.
            </p>
          </div>

          <span className="rounded-full bg-red-500/10 px-2.5 py-1 text-xs font-medium text-red-400">
            {errors.length} error{errors.length === 1 ? "" : "s"}
          </span>
        </div>
      </div>

      <div className="divide-y divide-red-900/30">
        {errors.map((item, index) => (
          <div
            key={`${item.name}-${index}`}
            className="flex items-start gap-4 px-5 py-4"
          >
            <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-red-500/10">
              <span className="text-sm font-semibold text-red-400">
                !
              </span>
            </div>

            <div className="min-w-0 flex-1">
              <p className="break-all font-mono text-sm font-medium text-white">
                {item.name}
              </p>

              <p className="mt-1 text-sm text-red-300/80">
                {item.error}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

