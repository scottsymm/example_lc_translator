import { useState } from "react";
import { createRecord } from "../api/records";

export function SaveRecordButton({ record, onSaved, label = "Save" }) {
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState(null);

  async function handleSave() {
    if (saved) return;
    setSaving(true);
    setError(null);
    try {
      const savedRecord = await createRecord(record);
      setSaved(true);
      onSaved?.(savedRecord);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="flex flex-col items-start gap-1">
      <button
        type="button"
        onClick={handleSave}
        disabled={saving || saved}
        className="rounded bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700 disabled:opacity-50"
      >
        {saved ? "Saved ✓" : saving ? "Saving..." : label}
      </button>
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );
}
