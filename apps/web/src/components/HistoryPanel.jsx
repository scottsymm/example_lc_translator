import { useEffect, useState } from "react";
import { clearHistory, getHistory } from "../lib/history.js";

export default function HistoryPanel({ type, onSelect }) {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    setEntries(getHistory().filter((e) => !type || e.type === type));
  }, [type]);

  if (entries.length === 0) return null;

  return (
    <div className="mt-6 border border-gray-200 rounded-md p-4 bg-white">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-gray-700">Recent {type || ""} results</h3>
        <button
          onClick={() => {
            clearHistory();
            setEntries([]);
          }}
          className="text-xs text-red-600 hover:text-red-800"
          type="button"
        >
          Clear
        </button>
      </div>
      <ul className="space-y-2">
        {entries.map((entry, idx) => (
          <li key={idx}>
            <button
              onClick={() => onSelect(entry.payload)}
              className="text-left w-full text-xs text-blue-600 hover:text-blue-800 truncate"
              type="button"
            >
              {new Date(entry.createdAt).toLocaleString()} —{" "}
              {entry.payload.lc_number || entry.payload.type || entry.type}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
