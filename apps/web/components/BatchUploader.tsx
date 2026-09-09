"use client";

import { UploadCloud } from "lucide-react";
import { useRef, useState } from "react";
import type { AudioResult } from "./ResultsTable";

interface BatchUploaderProps {
  onUploadSuccess?: (batchId: string, total: number) => void;
  onSingleResult?: (result: AudioResult) => void;
}

export default function BatchUploader({
  onUploadSuccess,
  onSingleResult,
}: BatchUploaderProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");

  async function handleFile(file?: File) {
    if (!file) return;

    const extension = file.name.split(".").pop()?.toLowerCase();

    if (!extension) {
      setError("Could not detect the file extension.");
      return;
    }

    setFileName(file.name);
    setError("");
    setIsUploading(true);

    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL;
      const formData = new FormData();
      formData.append("file", file);

      const endpoint =
        extension === "zip" ? `${apiBaseUrl}/batches` : `${apiBaseUrl}/single`;

      const response = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          data?.detail ?? "Upload failed. Please try again.",
        );
      }

      if (extension === "zip") {
        onUploadSuccess?.(data.batch_id, data.total);
      } else {
        onSingleResult?.({
          ...data,
          status: "completed",
        });
      }
    } catch (uploadError) {
      setFileName("");
      setError(
        uploadError instanceof Error
          ? uploadError.message
          : "Upload failed. Please try again.",
      );
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        accept=".zip,.ogg,.wav,audio/ogg,audio/wav"
        className="hidden"
        onChange={(event) => handleFile(event.target.files?.[0])}
      />

      <button
        type="button"
        disabled={isUploading}
        onClick={() => inputRef.current?.click()}
        className="flex w-full flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-700 bg-slate-950/50 px-6 py-14 transition hover:border-slate-500 hover:bg-slate-950 disabled:cursor-not-allowed disabled:opacity-70"
      >
        <UploadCloud
          size={40}
          className="mb-4 text-slate-500"
        />

        <span className="text-sm font-medium">
          {isUploading ? "Uploading..." : fileName || "Choose a ZIP file"}
        </span>

        <span className="mt-2 text-xs text-slate-500">
          Upload a ZIP batch or a single .ogg/.wav call
        </span>
      </button>

      {error && <p className="mt-3 text-sm text-red-400">{error}</p>}

      {fileName && !isUploading && (
        <div className="mt-4 flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950 px-4 py-3">
          <span className="truncate text-sm text-slate-300">
            {fileName}
          </span>

          <button
            type="button"
            onClick={() => {
              setFileName("");
              setError("");
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