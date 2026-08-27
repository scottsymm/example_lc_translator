import { useState } from "react";
import { translateMtToMx } from "../api/client.js";
import { SaveRecordButton } from "../components/SaveRecordButton.jsx";
import MessageBlock from "../components/MessageBlock.jsx";
import ValidationResult from "../components/ValidationResult.jsx";

export default function TranslatePage() {
  const [mt700, setMt700] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleTranslate() {
    setLoading(true);
    setError(null);
    try {
      const data = await translateMtToMx(mt700);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900">Translate MT700 → MX</h2>
      <p className="text-gray-600 mt-1">Paste a raw MT700 message to convert it to ISO 20022 XML.</p>

      <textarea
        value={mt700}
        onChange={(e) => setMt700(e.target.value)}
        rows={12}
        className="mt-4 w-full p-3 border border-gray-300 rounded-md font-mono text-xs"
        placeholder=":20:LC123456..."
      />

      <button
        onClick={handleTranslate}
        disabled={loading || !mt700.trim()}
        className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        type="button"
      >
        {loading ? "Translating..." : "Translate"}
      </button>

      {error && <p className="mt-4 text-red-600">{error}</p>}

      {result && (
        <>
          <div className="mt-4">
            <SaveRecordButton
              record={{
                source_type: "translated",
                mt700_input: mt700,
                mx_xml: result.mx_xml,
                validation_result: {
                  mx_valid: result.mx_valid,
                  mx_errors: result.mx_errors,
                },
              }}
            />
          </div>
          <ValidationResult result={{ valid: result.mx_valid, errors: result.mx_errors }} title="MX XSD Validation" />
          {result.errors?.length > 0 && (
            <ValidationResult result={{ valid: false, errors: result.errors }} title="Translation Errors" />
          )}
          {result.warnings?.length > 0 && (
            <ValidationResult result={{ valid: true, warnings: result.warnings }} title="Translation Warnings" />
          )}
          <MessageBlock title="MX XML" text={result.mx_xml} />
        </>
      )}
    </div>
  );
}
