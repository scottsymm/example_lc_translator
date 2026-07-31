import { Link, useLocation } from "react-router-dom";

export default function Header() {
  const location = useLocation();
  const linkClass = (path) =>
    `px-3 py-2 rounded-md text-sm font-medium ${
      location.pathname === path
        ? "bg-blue-700 text-white"
        : "text-gray-300 hover:bg-blue-600 hover:text-white"
    }`;

  return (
    <header className="bg-blue-800 text-white shadow">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold">
          LC Translator
        </Link>
        <nav className="flex gap-2">
          <Link to="/" className={linkClass("/")}>
            Generate
          </Link>
          <Link to="/translate" className={linkClass("/translate")}>
            Translate
          </Link>
          <Link to="/validate" className={linkClass("/validate")}>
            Validate
          </Link>
        </nav>
      </div>
    </header>
  );
}
