export default function ValidationResult({ result, title = "Validation Result" }) {
  if (!result) return null;

  return (
    <div className="mt-4 p-3 rounded-md border">
      <h3 className="text-sm font-semibold text-gray-700">{title}</h3>
      <p className="mt-1">
        <span
          className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
            result.valid ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
          }`}
        >
          {result.valid ? "Valid" : "Invalid"}
        </span>
      </p>
      {result.errors?.length > 0 && (
        <ul className="mt-2 text-sm text-red-700 list-disc list-inside">
          {result.errors.map((err, idx) => (
            <li key={idx}>{err}</li>
          ))}
        </ul>
      )}
      {result.warnings?.length > 0 && (
        <ul className="mt-2 text-sm text-yellow-700 list-disc list-inside">
          {result.warnings.map((warn, idx) => (
            <li key={idx}>{warn}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
