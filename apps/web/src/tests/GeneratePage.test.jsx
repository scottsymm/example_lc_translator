import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import GeneratePage from "../pages/GeneratePage.jsx";

describe("GeneratePage", () => {
  it("renders the generate button", () => {
    render(<GeneratePage />);
    expect(screen.getByRole("button", { name: /generate/i })).toBeInTheDocument();
  });
});
