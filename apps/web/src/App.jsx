import { useState } from "react";
import { Routes, Route } from "react-router-dom";
import Header from "./components/Header.jsx";
import GeneratePage from "./pages/GeneratePage.jsx";
import TranslatePage from "./pages/TranslatePage.jsx";
import ValidatePage from "./pages/ValidatePage.jsx";

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="max-w-6xl mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<GeneratePage />} />
          <Route path="/translate" element={<TranslatePage />} />
          <Route path="/validate" element={<ValidatePage />} />
        </Routes>
      </main>
    </div>
  );
}
