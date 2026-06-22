#!/usr/bin/env python3
"""Batch generate highlights for all books. Runs books sequentially but you can launch multiple instances."""
import subprocess, sys

BOOKS = list(range(1, 37))

for book_id in BOOKS:
    print(f"\n{'='*50}")
    print(f"Starting book {book_id}")
    print(f"{'='*50}")
    result = subprocess.run(
        [sys.executable, 'scripts/generate_highlights.py', f'--book={book_id}'],
        capture_output=False, timeout=3600
    )
    if result.returncode != 0:
        print(f"Book {book_id} failed with code {result.returncode}")
    else:
        print(f"Book {book_id} done")

print("\nAll books processed!")
