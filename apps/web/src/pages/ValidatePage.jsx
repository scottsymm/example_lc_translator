import { useState } from "react";
import { validateMt, validateMx } from "../api/client.js";
import { SaveRecordButton } from "../components/SaveRecordButton.jsx";
import ValidationResult from "../components/ValidationResult.jsx";

export default function ValidatePage() {
  const [mode, setMode] = useState("mt");
  const [input, setInput] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleValidate() {
    setLoading(true);
    setError(null);
    try {
      const data = mode === "mt" ? await validateMt(input) : await validateMx(input);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900">Validate</h2>
      <p className="text-gray-600 mt-1">Validate MT700 structure or MX XML against the tsrv.001 XSD.</p>

      <div className="mt-4 flex gap-2">
        <button
          onClick={() => setMode("mt")}
          className={`px-3 py-2 rounded-md text-sm font-medium ${
            mode === "mt" ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700"
          }`}
          type="button"
        >
          MT700
        </button>
        <button
          onClick={() => setMode("mx")}
          className={`px-3 py-2 rounded-md text-sm font-medium ${
            mode === "mx" ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700"
          }`}
          type="button"
        >
          MX XML
        </button>
      </div>

      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        rows={12}
        className="mt-4 w-full p-3 border border-gray-300 rounded-md font-mono text-xs"
        placeholder={mode === "mt" ? ":20:LC123456..." : "<?xml version=\"1.0\"?>..."}
      />

      <button
        onClick={handleValidate}
        disabled={loading || !input.trim()}
        className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        type="button"
      >
        {loading ? "Validating..." : "Validate"}
      </button>

      {error && <p className="mt-4 text-red-600">{error}</p>}

      {result && (
        <>
          <div className="mt-4">
            <SaveRecordButton
              record={{
                source_type: "validated",
                mt700_input: mode === "mt" ? input : undefined,
                mx_xml: mode === "mx" ? input : undefined,
                validation_result: {
                  mt700_valid: mode === "mt" ? result.valid : undefined,
                  mt700_errors: mode === "mt" ? result.errors : undefined,
                  mt700_warnings: mode === "mt" ? result.warnings : undefined,
                  mx_valid: mode === "mx" ? result.valid : undefined,
                  mx_errors: mode === "mx" ? result.errors : undefined,
                },
              }}
            />
          </div>
          <ValidationResult
            result={{ valid: result.valid, errors: result.errors, warnings: result.warnings }}
            title={mode === "mt" ? "MT700 Validation" : "MX XSD Validation"}
          />
        </>
      )}
    </div>
  );
}
