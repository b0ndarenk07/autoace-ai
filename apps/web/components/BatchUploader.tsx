"use client";

import { UploadCloud } from "lucide-react";
import { useRef, useState } from "react";

export default function BatchUploader() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState("");

  function handleFile(file?: File) {
    if (!file) return;

    setFileName(file.name);
  }

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        accept=".zip"
        className="hidden"
        onChange={(event) => handleFile(event.target.files?.[0])}
      />

      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        className="flex w-full flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-700 bg-slate-950/50 px-6 py-14 transition hover:border-slate-500 hover:bg-slate-950"
      >
        <UploadCloud
          size={40}
          className="mb-4 text-slate-500"
        />

        <span className="text-sm font-medium">
          {fileName || "Choose a ZIP file"}
        </span>

        <span className="mt-2 text-xs text-slate-500">
          ZIP containing audio files and manifest.csv
        </span>
      </button>

      {fileName && (
        <div className="mt-4 flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950 px-4 py-3">
          <span className="truncate text-sm text-slate-300">
            {fileName}
          </span>

          <button
            type="button"
            onClick={() => {
              setFileName("");
              if (inputRef.current) {
                inputRef.current.value = "";
              }
            }}
            className="ml-4 text-xs text-slate-500 hover:text-white"
          >
            Remove
          </button>
        </div>
      )}
    </div>
  );
}