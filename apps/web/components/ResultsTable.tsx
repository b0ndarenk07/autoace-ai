"use client";

export type EmotionalTone =
  | "neutral"
  | "satisfied"
  | "frustrated"
  | "upset"
  | "distressed";

export type EmotionalIntensity = "low" | "medium" | "high";

export type BackgroundNoiseSeverity = "none" | "low" | "medium" | "high";

export type AudioQuality =
  | "clear"
  | "slightly_impaired"
  | "severely_impaired";

export interface AudioResult {
  name: string;

  emotional_tone: EmotionalTone;
  emotional_intensity: EmotionalIntensity;

  background_noise_present: boolean;
  background_noise_type: string;
  background_noise_severity: BackgroundNoiseSeverity;

  audio_quality: AudioQuality;
  speaker_overlap_present: boolean;
  long_silence_present: boolean;

  confidence: number;

  status?: "completed" | "processing" | "error";
  error?: string;
}

interface ResultsTableProps {
  results?: AudioResult[];
  onClear?: () => void;
}

function formatConfidence(value: number) {
  return `${Math.round(value * 100)}%`;
}

function formatLabel(value: string) {
  return value.replace(/_/g, " ");
}

function getToneClass(tone: EmotionalTone) {
  switch (tone) {
    case "satisfied":
      return "text-green-400";
    case "frustrated":
      return "text-yellow-400";
    case "upset":
      return "text-orange-400";
    case "distressed":
      return "text-red-400";
    default:
      return "text-gray-300";
  }
}

function getIntensityClass(intensity: EmotionalIntensity) {
  switch (intensity) {
    case "high":
      return "text-red-400";
    case "medium":
      return "text-yellow-400";
    default:
      return "text-gray-400";
  }
}

function getSeverityClass(
  severity: BackgroundNoiseSeverity
) {
  switch (severity) {
    case "high":
      return "text-red-400";
    case "medium":
      return "text-yellow-400";
    case "low":
      return "text-blue-400";
    default:
      return "text-gray-400";
  }
}

function getQualityClass(quality: AudioQuality) {
  switch (quality) {
    case "clear":
      return "text-green-400";
    case "slightly_impaired":
      return "text-yellow-400";
    case "severely_impaired":
      return "text-red-400";
  }
}

function getStatusClass(status?: AudioResult["status"]) {
  switch (status) {
    case "completed":
      return "bg-green-500/10 text-green-400";

    case "processing":
      return "bg-blue-500/10 text-blue-400";

    case "error":
      return "bg-red-500/10 text-red-400";

    default:
      return "bg-gray-500/10 text-gray-400";
  }
}

export default function ResultsTable({
  results = [],
  onClear,
}: ResultsTableProps) {
  if (results.length === 0) {
    return (
      <div className="rounded-xl border border-gray-800 bg-gray-900/60 p-8 text-center">
        <h3 className="text-sm font-semibold text-white">
          No Results Yet
        </h3>

        <p className="mt-2 text-sm text-gray-500">
          Upload an evaluation batch to begin analyzing audio.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-gray-800 bg-gray-900/60">
      <div className="border-b border-gray-800 px-5 py-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="text-sm font-semibold text-white">
              Analysis Results
            </h3>

            <p className="mt-1 text-sm text-gray-500">
              {results.length} audio clip
              {results.length === 1 ? "" : "s"} analyzed
            </p>
          </div>

          {onClear && (
            <button
              type="button"
              onClick={onClear}
              aria-label="Clear analysis results"
              title="Clear analysis results"
              className="rounded-md p-2 text-gray-500 transition hover:bg-gray-800 hover:text-white"
            >
              <span aria-hidden="true">×</span>
            </button>
          )}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-800">
          <thead className="bg-gray-950/40">
            <tr>
              <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Audio File
              </th>

              <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Emotional Tone
              </th>

              <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Intensity
              </th>

              <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Background Noise
              </th>

              <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Noise Severity
              </th>

              <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Audio Quality
              </th>

              <th className="px-5 py-3 text-center text-xs font-medium uppercase tracking-wider text-gray-500">
                Overlap
              </th>

              <th className="px-5 py-3 text-center text-xs font-medium uppercase tracking-wider text-gray-500">
                Silence
              </th>

              <th className="px-5 py-3 text-center text-xs font-medium uppercase tracking-wider text-gray-500">
                Confidence
              </th>

              <th className="px-5 py-3 text-center text-xs font-medium uppercase tracking-wider text-gray-500">
                Status
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-gray-800">
            {results.map((result) => (
              <tr
                key={result.name}
                className="transition-colors hover:bg-gray-800/40"
              >
                <td className="whitespace-nowrap px-5 py-4">
                  <span className="font-mono text-sm text-white">
                    {result.name}
                  </span>
                </td>

                <td className="whitespace-nowrap px-5 py-4">
                  <span
                    className={`text-sm font-medium capitalize ${getToneClass(
                      result.emotional_tone
                    )}`}
                  >
                    {formatLabel(result.emotional_tone)}
                  </span>
                </td>

                <td className="whitespace-nowrap px-5 py-4">
                  <span
                    className={`text-sm capitalize ${getIntensityClass(
                      result.emotional_intensity
                    )}`}
                  >
                    {result.emotional_intensity}
                  </span>
                </td>

                <td className="max-w-[220px] px-5 py-4">
                  <div className="text-sm text-gray-300">
                    {result.background_noise_present
                      ? result.background_noise_type || "Detected"
                      : "None"}
                  </div>
                </td>

                <td className="whitespace-nowrap px-5 py-4">
                  <span
                    className={`text-sm capitalize ${getSeverityClass(
                      result.background_noise_severity
                    )}`}
                  >
                    {result.background_noise_severity}
                  </span>
                </td>

                <td className="whitespace-nowrap px-5 py-4">
                  <span
                    className={`text-sm capitalize ${getQualityClass(
                      result.audio_quality
                    )}`}
                  >
                    {formatLabel(result.audio_quality)}
                  </span>
                </td>

                <td className="whitespace-nowrap px-5 py-4 text-center">
                  <span
                    className={
                      result.speaker_overlap_present
                        ? "text-orange-400"
                        : "text-gray-500"
                    }
                  >
                    {result.speaker_overlap_present ? "Yes" : "No"}
                  </span>
                </td>

                <td className="whitespace-nowrap px-5 py-4 text-center">
                  <span
                    className={
                      result.long_silence_present
                        ? "text-yellow-400"
                        : "text-gray-500"
                    }
                  >
                    {result.long_silence_present ? "Yes" : "No"}
                  </span>
                </td>

                <td className="whitespace-nowrap px-5 py-4 text-center">
                  <span className="text-sm font-semibold text-white">
                    {formatConfidence(result.confidence)}
                  </span>
                </td>

                <td className="whitespace-nowrap px-5 py-4 text-center">
                  <span
                    className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium capitalize ${getStatusClass(result.status)}`}
                  >
                    {result.status ?? "completed"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
