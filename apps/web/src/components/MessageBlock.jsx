export default function MessageBlock({ title, text }) {
  if (!text) return null;

  async function handleCopy() {
    await navigator.clipboard.writeText(text);
  }

  return (
    <div className="mt-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-700">{title}</h3>
        <button
          onClick={handleCopy}
          className="text-xs text-blue-600 hover:text-blue-800"
          type="button"
        >
          Copy
        </button>
      </div>
      <pre className="mt-1 p-3 bg-gray-100 border border-gray-300 rounded-md text-xs overflow-auto max-h-96">
        {text}
      </pre>
    </div>
  );
}
