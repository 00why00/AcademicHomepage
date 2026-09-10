"""Fetch complete Scholar snapshots with bounded retries and atomic writes."""
import argparse
import json
import multiprocessing
import os
from pathlib import Path
import tempfile
import time
from datetime import datetime, timezone


def normalize_author(author, author_id):
    if not isinstance(author, dict) or not author.get("name"):
        raise ValueError("Missing author name")
    if type(author.get("citedby")) is not int or author["citedby"] < 0:
        raise ValueError("Invalid total citation count")
    papers = author.get("publications")
    if not isinstance(papers, list) or not papers:
        raise ValueError("No complete publication list returned")
    publications = {}
    for paper in papers:
        paper_id = paper.get("author_pub_id", "")
        count = paper.get("num_citations")
        if not paper_id.startswith(author_id + ":") or type(count) is not int or count < 0:
            raise ValueError("Invalid publication or citation count")
        if paper_id in publications:
            raise ValueError("Duplicate publication ID")
        publications[paper_id] = paper
    return {
        **author,
        "publications": publications,
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def _fetch_worker(connection, author_id, use_proxy):
    try:
        from scholarly import scholarly, ProxyGenerator

        scholarly.set_timeout(30)
        if use_proxy:
            proxy = ProxyGenerator()
            if not proxy.FreeProxies(timeout=2, wait_time=5):
                raise RuntimeError("No working proxy available")
            scholarly.use_proxy(proxy)
        author = scholarly.search_author_id(author_id)
        scholarly.fill(author, sections=["basics", "indices", "counts", "publications"])
        connection.send((True, author))
    except Exception as error:
        connection.send((False, f"{type(error).__name__}: {error}"))
    finally:
        connection.close()


def fetch_with_timeout(author_id, timeout, use_proxy):
    # Isolate third-party retries so even a stalled proxy cannot run indefinitely.
    context = multiprocessing.get_context("spawn")
    receiver, sender = context.Pipe(duplex=False)
    worker = context.Process(target=_fetch_worker, args=(sender, author_id, use_proxy))
    worker.start()
    sender.close()
    try:
        if not receiver.poll(timeout):
            raise TimeoutError(f"Scholar attempt exceeded {timeout} seconds")
        success, result = receiver.recv()
        if not success:
            raise RuntimeError(result)
        return result
    finally:
        receiver.close()
        worker.join(timeout=1)
        if worker.is_alive():
            worker.terminate()
            worker.join(timeout=5)
        if worker.is_alive():
            worker.kill()
            worker.join()
        worker.close()


def collect_author(author_id, attempts=3, timeout=120, wait_seconds=15,
                   fetch=fetch_with_timeout, sleep=time.sleep):
    if attempts < 1 or timeout <= 0 or wait_seconds < 0:
        raise ValueError("Invalid retry configuration")
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            author = fetch(author_id, timeout=timeout, use_proxy=attempt > 1)
            return normalize_author(author, author_id)
        except Exception as error:
            last_error = error
            print(f"Attempt {attempt}/{attempts} failed: {error}", flush=True)
            if attempt < attempts:
                sleep(wait_seconds)
    raise RuntimeError(f"All {attempts} Scholar attempts failed") from last_error


def write_json_atomic(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                         dir=path.parent, delete=False) as output:
            temp_path = Path(output.name)
            json.dump(value, output, ensure_ascii=False, indent=2)
            output.write("\n")
        temp_path.replace(path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "results")
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--wait-seconds", type=int, default=15)
    args = parser.parse_args()
    author_id = os.environ.get("GOOGLE_SCHOLAR_ID", "").strip()
    if not author_id:
        parser.error("GOOGLE_SCHOLAR_ID must be set")
    try:
        author = collect_author(author_id, args.attempts, args.timeout, args.wait_seconds)
    except Exception as error:
        parser.exit(1, f"Citation refresh failed; previous data remains unchanged: {error}\n")
    write_json_atomic(args.output_dir / "gs_data.json", author)
    write_json_atomic(args.output_dir / "gs_data_shieldsio.json", {
        "schemaVersion": 1, "label": "citations", "message": str(author["citedby"]),
    })
    print(f"Updated {len(author['publications'])} publications at {author['updated']}")


if __name__ == "__main__":
    main()
