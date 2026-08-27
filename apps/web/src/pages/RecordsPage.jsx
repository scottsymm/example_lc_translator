import { useEffect, useState } from "react";
import { listRecords, deleteRecord } from "../api/records";

export function RecordsPage() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await listRecords({ limit: 50 });
      setRecords(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleDelete(id) {
    if (!confirm("Delete this record?")) return;
    try {
      await deleteRecord(id);
      setRecords((prev) => prev.filter((r) => r.id !== id));
    } catch (err) {
      setError(err.message);
    }
  }

  if (loading) return <p className="p-4">Loading...</p>;
  if (error) return <p className="p-4 text-red-600">{error}</p>;

  return (
    <div className="space-y-4 p-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Saved Records</h1>
        <button
          type="button"
          onClick={load}
          className="rounded bg-gray-200 px-3 py-1 text-sm hover:bg-gray-300"
        >
          Refresh
        </button>
      </div>
      {records.length === 0 ? (
        <p className="text-gray-600">No saved records yet.</p>
      ) : (
        <ul className="divide-y rounded border">
          {records.map((record) => (
            <li key={record.id} className="flex items-center justify-between p-4">
              <div>
                <p className="font-medium">{record.title}</p>
                <p className="text-sm text-gray-600">
                  {record.source_type} · {new Date(record.created_at).toLocaleString()}
                </p>
              </div>
              <button
                type="button"
                onClick={() => handleDelete(record.id)}
                className="text-sm text-red-600 hover:underline"
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
