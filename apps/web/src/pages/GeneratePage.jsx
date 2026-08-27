import { useState } from "react";
import { generateLc } from "../api/client.js";
import { SaveRecordButton } from "../components/SaveRecordButton.jsx";
import MessageBlock from "../components/MessageBlock.jsx";
import ValidationResult from "../components/ValidationResult.jsx";

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
          <div className="mt-4">
            <SaveRecordButton
              record={{
                source_type: "generated",
                generated_seed: seed ? Number(seed) : null,
                generated_strict: false,
                mx_xml: result.mx_xml,
                validation_result: {
                  mt700_valid: result.mt700_valid,
                  mt700_errors: result.mt700_errors,
                  mt700_warnings: result.mt700_warnings,
                  mx_valid: result.mx_valid,
                  mx_errors: result.mx_errors,
                },
              }}
            />
          </div>
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
    </div>
  );
}
