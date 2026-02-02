
from __future__ import annotations

import argparse
import json
import os
from typing import Dict, Any

from .ingest import load_documents
from .classify import classify
from .extract import extract_fields
from .retrieve import Retriever

def build_output(data_dir: str) -> Dict[str, Any]:
    docs = load_documents(data_dir)
    out: Dict[str, Any] = {}
    for d in docs:
        cls = classify(d)
        out[d.filename] = extract_fields(d, cls)
    return out

def run_search(data_dir: str, query: str, top_k: int = 5, backend: str = "auto") -> None:
    docs = load_documents(data_dir)
    filenames = [d.filename for d in docs]
    texts = [d.text if d.text else "" for d in docs]

    retriever = Retriever(backend=backend)
    used_backend = retriever.fit(filenames, texts)
    print(f"[retrieval] backend={used_backend}")

    results = retriever.search(query, top_k=top_k)
    if not results:
        print("No results.")
        return
    for r in results:
        print(f"- {r.filename} | score={r.score:.4f}")
        print(f"  {r.snippet}")

def cli():
    p = argparse.ArgumentParser(description="Local Document AI pipeline (offline)")
    p.add_argument("--data", required=True, help="Folder containing .pdf/.txt documents")
    p.add_argument("--output", default="output.json", help="Path to write output.json")
    p.add_argument("--query", default=None, help="Optional semantic search query")
    p.add_argument("--top_k", type=int, default=5, help="Top-K results for search")
    p.add_argument("--retrieval_backend", default="auto", choices=["auto","sentence-transformers","tfidf"], help="Retrieval backend")
    args = p.parse_args()

    out = build_output(args.data)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"Wrote: {os.path.abspath(args.output)}")

    if args.query:
        print()
        run_search(args.data, args.query, top_k=args.top_k, backend=args.retrieval_backend)

if __name__ == "__main__":
    cli()
