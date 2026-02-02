# Local Document AI (Offline) — Technical Assessment Solution

This project ingests a folder of **PDF/TXT documents**, performs:
1. **Text extraction + cleaning**
2. **Document classification** into: Invoice / Resume / Utility Bill / Other / Unclassifiable
3. **Structured field extraction** for the required classes
4. **Local retrieval (semantic search)** using:
   - **SentenceTransformers** if the model is available locally
   - **TF‑IDF fallback** (always offline) if the embedding model is not available

> No hosted/paid AI services are used. Everything runs locally.

---

## Folder Structure

```
AI-Document-Intelligence-System/
  app/
    ingest.py
    classify.py
    extract.py
    retrieve.py
    utils.py
    main.py
  requirements.txt
  output.json               # generated after running
```

---

## Install

```bash
python -m venv .venv
# Linux / Mac:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
```

### Note about offline embeddings
If you want **SentenceTransformers embeddings offline**, download/cache the model beforehand (on a machine with internet),
then run offline using the cached model directory.

This solution also supports a fully-offline **TF‑IDF** backend.

---

## Run (Generate `output.json`)

```bash
python -m app.main --data /path/to/dataset --output output.json
```

---

## Run Retrieval / Semantic Search

```bash
python -m app.main --data /path/to/dataset --output output.json \
  --query "Find all documents mentioning payments due in January" \
  --top_k 5 \
  --retrieval_backend auto
```

Backends:
- `auto` (tries SentenceTransformers; falls back to TF‑IDF)
- `sentence-transformers`
- `tfidf`

---

## Libraries & Methods Used

- **PyPDF2**: PDF text extraction
- **Regex-based rules**: Classification + field extraction (fast, reliable offline)
- **SentenceTransformers (optional)**: Local embeddings if model is available
- **scikit-learn TF‑IDF (fallback)**: Always offline search
- **Cosine similarity**: ranking documents for retrieval

---

## Output Format

Produces a single JSON mapping each filename to its classification and extracted fields, e.g.:

```json
{
  "invoice_1.pdf": {
    "class": "Invoice",
    "invoice_number": "1001",
    "date": "2025-06-16",
    "company": "Pioneer Ltd",
    "total_amount": 2073.0
  }
}
```
