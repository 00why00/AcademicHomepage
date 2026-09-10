import test from "node:test";
import assert from "node:assert/strict";
import { citationCount, loadCitations } from "../assets/js/citations.js";

const data = { citedby: 12, publications: { valid: { num_citations: 7 }, zero: { num_citations: 0 } } };
const element = (id) => ({ dataset: { scholarId: id }, textContent: "" });
function page(elements, total = null) {
  return { querySelectorAll: () => elements, getElementById: () => total };
}
const response = (value) => async () => ({ ok: true, json: async () => value });

test("missing total and an unknown first paper do not block valid papers", async () => {
  const elements = [element("removed"), element("valid"), element("zero")];
  await loadCitations(page(elements), "https://example.test/data.json", response(data));
  assert.deepEqual(elements.map((item) => item.textContent), ["", "Citations: 7", "Citations: 0"]);
});

test("an optional total is updated when present", async () => {
  const total = { textContent: "" };
  await loadCitations(page([], total), "https://example.test/data.json", response(data));
  assert.equal(total.textContent, "12");
});

test("network, invalid JSON and HTTP errors leave the page usable", async () => {
  for (const fetcher of [
    async () => { throw new Error("offline"); },
    async () => ({ ok: false, status: 503 }),
    async () => ({ ok: true, json: async () => { throw new SyntaxError("bad JSON"); } }),
    response(null),
  ]) {
    const paper = element("valid");
    const total = { textContent: "old" };
    await loadCitations(page([paper], total), "https://example.test/data.json", fetcher);
    assert.equal(paper.textContent, "");
    assert.equal(total.textContent, "—");
  }
});

test("untrusted or malformed citation values are never rendered", () => {
  for (const count of [-1, 0.5, "7", "<img onerror=alert(1)>", null]) {
    assert.equal(citationCount({ publications: { p: { num_citations: count } } }, "p"), null);
  }
});

test("alternate host recovers when the primary source is unavailable", async () => {
  const calls = [];
  const paper = element("valid");
  await loadCitations(page([paper]), ["primary", "fallback"], async (url) => {
    calls.push(url);
    if (url === "primary") throw new Error("unavailable");
    return { ok: true, json: async () => data };
  });
  assert.deepEqual(calls, ["primary", "fallback"]);
  assert.equal(paper.textContent, "Citations: 7");
});
