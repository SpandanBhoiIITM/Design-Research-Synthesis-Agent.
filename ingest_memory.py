"""
Load every .txt file in past_studies/ into the ChromaDB research memory.

Run this ONCE (or whenever you add new studies):
    python ingest_memory.py
"""

import os
from dotenv import load_dotenv
from research_memory.memory import add_study, get_collection

load_dotenv()

STUDIES_DIR = os.path.join(os.path.dirname(__file__), "past_studies")


def main():
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not set. Add it to your .env first.")
        return

    files = [f for f in os.listdir(STUDIES_DIR) if f.endswith(".txt")]
    if not files:
        print("No .txt studies found in past_studies/")
        return

    total = 0
    for fname in sorted(files):
        with open(os.path.join(STUDIES_DIR, fname), "r", encoding="utf-8") as f:
            text = f.read()
        n = add_study(study_name=fname.replace(".txt", ""), text=text)
        total += n
        print(f"  added {n} chunks from {fname}")

    print(f"\nDone. Research memory now holds {get_collection().count()} chunks "
          f"from {len(files)} studies.")


if __name__ == "__main__":
    main()
