import { describe, it, expect, beforeEach } from "vitest";
import { saveToHistory, getHistory, clearHistory } from "../lib/history.js";

describe("history", () => {
  beforeEach(() => {
    clearHistory();
  });

  it("saves and retrieves entries", () => {
    saveToHistory("generate", { lc_number: "LC123" });
    const history = getHistory();
    expect(history).toHaveLength(1);
    expect(history[0].type).toBe("generate");
    expect(history[0].payload.lc_number).toBe("LC123");
  });

  it("clears entries", () => {
    saveToHistory("generate", { lc_number: "LC123" });
    clearHistory();
    expect(getHistory()).toHaveLength(0);
  });
});
