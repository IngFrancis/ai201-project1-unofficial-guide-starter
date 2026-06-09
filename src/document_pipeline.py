import json
import random
import re
from html import unescape
from pathlib import Path

RAW_DIR = Path("documents/raw")
OUTPUT_DIR = Path("documents/chunks")
OUTPUT_FILE = OUTPUT_DIR / "chunks.jsonl"
SAMPLE_FILE = OUTPUT_DIR / "sample_chunks.txt"

CHUNK_WORDS = 400
OVERLAP_WORDS = 75
MIN_WORDS = 40


def clean_text(text):
    """
    Clean raw document text by removing basic HTML, common web artifacts,
    and extra whitespace while keeping the useful student-facing content.
    """
    text = unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)

    bad_phrases = [
        "cookie",
        "privacy policy",
        "terms of use",
        "advertisement",
        "read more",
    ]

    cleaned_lines = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        lower_line = line.lower()

        if any(phrase in lower_line for phrase in bad_phrases):
            continue

        cleaned_lines.append(line)

    text = " ".join(cleaned_lines)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def load_document(path):
    """
    Load one raw .txt file and extract:
    - title
    - url
    - source type
    - main text after the Text: marker
    """
    raw = path.read_text(encoding="utf-8-sig", errors="ignore")

    title = ""
    url = ""
    source_type = ""

    for line in raw.splitlines():
        clean_line = line.strip().lstrip("\ufeff")

        if clean_line.startswith("Title:"):
            title = clean_line.replace("Title:", "", 1).strip()
        elif clean_line.startswith("URL:"):
            url = clean_line.replace("URL:", "", 1).strip()
        elif clean_line.startswith("Source type:"):
            source_type = clean_line.replace("Source type:", "", 1).strip()

    if "Text:" in raw:
        text = raw.split("Text:", 1)[1].strip()
    else:
        text = raw

    text = clean_text(text)

    return {
        "file": path.name,
        "title": title,
        "url": url,
        "source_type": source_type,
        "text": text,
    }


def chunk_text(text):
    """
    Split text into overlapping word-based chunks.
    This follows the planning.md strategy:
    about 350-500 words per chunk with about 75 words overlap.
    """
    words = text.split()

    if len(words) < MIN_WORDS:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = min(start + CHUNK_WORDS, len(words))
        chunk_words = words[start:end]
        chunk = " ".join(chunk_words).strip()

        if len(chunk.split()) >= MIN_WORDS:
            chunks.append(chunk)

        if end == len(words):
            break

        start = end - OVERLAP_WORDS

    return chunks


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    raw_files = sorted(RAW_DIR.glob("*.txt"))
    all_chunks = []

    print(f"Found {len(raw_files)} raw document files.")

    for path in raw_files:
        doc = load_document(path)

        if not doc["text"]:
            print(f"Skipping empty file: {path.name}")
            continue

        if "Paste the relevant copied text" in doc["text"]:
            print(f"Skipping empty/template file: {path.name}")
            continue

        chunks = chunk_text(doc["text"])

        print(f"{path.name}: {len(chunks)} chunks")

        for i, chunk in enumerate(chunks):
            all_chunks.append(
                {
                    "id": f"{path.stem}_chunk_{i}",
                    "source_file": doc["file"],
                    "title": doc["title"],
                    "url": doc["url"],
                    "source_type": doc["source_type"],
                    "chunk_index": i,
                    "word_count": len(chunk.split()),
                    "text": chunk,
                }
            )

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print("\n==============================")
    print(f"Total chunks created: {len(all_chunks)}")
    print(f"Saved chunks to: {OUTPUT_FILE}")
    print("==============================\n")

    if not all_chunks:
        print("No chunks were created. Check that your raw documents contain real text.")
        return

    random.seed(42)
    sample_chunks = random.sample(all_chunks, min(5, len(all_chunks)))

    with SAMPLE_FILE.open("w", encoding="utf-8") as f:
        for chunk in sample_chunks:
            f.write("=" * 80 + "\n")
            f.write(f"Source: {chunk['title']}\n")
            f.write(f"File: {chunk['source_file']}\n")
            f.write(f"URL: {chunk['url']}\n")
            f.write(f"Source type: {chunk['source_type']}\n")
            f.write(f"Word count: {chunk['word_count']}\n\n")
            f.write(chunk["text"] + "\n\n")

    print("5 sample chunks:\n")

    for chunk in sample_chunks:
        print("=" * 80)
        print(f"Source: {chunk['title']}")
        print(f"File: {chunk['source_file']}")
        print(f"Word count: {chunk['word_count']}")
        print(chunk["text"][:700])
        print()

    print(f"Saved sample chunks to: {SAMPLE_FILE}")


if __name__ == "__main__":
    main()