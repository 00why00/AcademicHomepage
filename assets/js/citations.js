/** A missing publication must not interrupt the remaining citation counts. */
export function citationCount(data, paperId) {
  const count = data?.publications?.[paperId]?.num_citations;
  return Number.isSafeInteger(count) && count >= 0 ? count : null;
}

export async function loadCitations(root, source, fetchData = globalThis.fetch) {
  const papers = [...root.querySelectorAll("[data-scholar-id]")];
  const total = root.getElementById("total_cit");
  if (!source || (!papers.length && !total)) return;

  try {
    let data;
    const sources = (Array.isArray(source) ? source : [source]).filter(Boolean);
    for (const url of sources) {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 8000);
      try {
        const response = await fetchData(url, { signal: controller.signal, cache: "no-cache" });
        if (!response.ok) throw new Error(`Citation data HTTP ${response.status}`);
        const candidate = await response.json();
        if (!candidate || !candidate.publications || typeof candidate.publications !== "object") {
          throw new Error("Invalid citation data");
        }
        data = candidate;
        break;
      } catch {
        // Try the alternate host before hiding unavailable counts.
      } finally {
        clearTimeout(timeout);
      }
    }
    if (!data) throw new Error("Citation sources unavailable");
    const format = new Intl.NumberFormat("en-US");
    if (total && Number.isSafeInteger(data.citedby) && data.citedby >= 0) {
      total.textContent = format.format(data.citedby);
    }
    for (const paper of papers) {
      const count = citationCount(data, paper.dataset.scholarId);
      paper.textContent = count === null ? "" : `Citations: ${format.format(count)}`;
      if (count !== null && data.updated) {
        paper.title = `Google Scholar; data updated ${data.updated}`;
      }
    }
  } catch {
    // Publications and their Scholar links remain usable if the service is down.
    for (const paper of papers) paper.textContent = "";
    if (total) total.textContent = "—";
  }
}
