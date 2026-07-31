import { useState } from "react";
import { generateLc } from "../api/client.js";
import { saveToHistory } from "../lib/history.js";
import MessageBlock from "../components/MessageBlock.jsx";
import ValidationResult from "../components/ValidationResult.jsx";
import HistoryPanel from "../components/HistoryPanel.jsx";

export default function GeneratePage() {
  const [seed, setSeed] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    try {
      const data = await generateLc(seed ? Number(seed) : undefined);
      setResult(data);
      saveToHistory("generate", {
        lc_number: data.lc_number,
        mt700: data.mt700,
        mx_xml: data.mx_xml,
        mt700_valid: data.mt700_valid,
        mx_valid: data.mx_valid,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900">Generate LC</h2>
      <p className="text-gray-600 mt-1">
        Generate a fake Letter of Credit and run the full MT700 → MX pipeline.
      </p>

      <div className="mt-4 flex flex-wrap items-center gap-3">
        <input
          type="number"
          value={seed}
          onChange={(e) => setSeed(e.target.value)}
          placeholder="Optional seed"
          className="px-3 py-2 border border-gray-300 rounded-md text-sm"
        />
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          type="button"
        >
          {loading ? "Generating..." : "Generate"}
        </button>
      </div>

      {error && <p className="mt-4 text-red-600">{error}</p>}

      {result && (
        <>
          <ValidationResult
            result={{ valid: result.mt700_valid, errors: result.mt700_errors, warnings: result.mt700_warnings }}
            title="MT700 Structure"
          />
          <ValidationResult
            result={{ valid: result.mx_valid, errors: result.mx_errors }}
            title="MX XSD Validation"
          />
          <MessageBlock title="MT700" text={result.mt700} />
          <MessageBlock title="MX XML" text={result.mx_xml} />
        </>
      )}

      <HistoryPanel
        type="generate"
        onSelect={(payload) =>
          setResult({
            lc_number: payload.lc_number,
            mt700: payload.mt700,
            mx_xml: payload.mx_xml,
            mt700_valid: payload.mt700_valid,
            mt700_errors: [],
            mt700_warnings: [],
            mx_valid: payload.mx_valid,
            mx_errors: [],
          })
        }
      />
    </div>
  );
}
