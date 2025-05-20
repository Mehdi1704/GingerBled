"""
convert_openstax.py
-------------------
Convert all PDFs in rag_build/raw/openstax/ to plain-text files in
rag_build/txt/openstax/.

• If `pdftotext` is available, use it (fast, preserves layout).
• Otherwise, auto-install and use pdfminer.six (slower, pure Python).

Run:  python convert_openstax.py
"""

import subprocess, shutil, sys, os
from pathlib import Path
from typing import Optional

RAW_DIR = Path("rag_build/raw/openstax")
TXT_DIR = Path("rag_build/txt/openstax")
TXT_DIR.mkdir(parents=True, exist_ok=True)


# ----------------------------------------------------------------------
def have_pdftotext() -> bool:
    return shutil.which("pdftotext") is not None


def convert_with_pdftotext(pdf_path: Path, txt_path: Path) -> None:
    subprocess.run(
        ["pdftotext", "-layout", "-nopgbrk", str(pdf_path), str(txt_path)],
        check=True,
    )


# ----------------------------------------------------------------------
def ensure_pdfminer() -> None:
    try:
        import pdfminer  # noqa: F401
    except ImportError:
        print("[INFO] pdfminer.six not found – installing …")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfminer.six"])


def convert_with_pdfminer(pdf_path: Path, txt_path: Path) -> None:
    from pdfminer.high_level import extract_text

    txt = extract_text(str(pdf_path))
    txt_path.write_text(txt, encoding="utf-8")


# ----------------------------------------------------------------------
def convert_pdf(pdf_path: Path) -> None:
    base = pdf_path.stem
    out_path = TXT_DIR / f"{base}.txt"
    print(f"  → {pdf_path.name}")
    if have_pdftotext():
        convert_with_pdftotext(pdf_path, out_path)
    else:
        ensure_pdfminer()
        convert_with_pdfminer(pdf_path, out_path)


def main() -> None:
    if not RAW_DIR.exists():
        sys.exit(f"[ERROR] Source directory {RAW_DIR} does not exist.")

    pdf_files = list(RAW_DIR.glob("*.pdf"))
    if not pdf_files:
        sys.exit(f"[ERROR] No PDF files found in {RAW_DIR}.")

    print(f"[INFO] Converting {len(pdf_files)} PDF(s) …")
    for pdf in pdf_files:
        convert_pdf(pdf)

    print(f"[INFO] Done. Text files are in {TXT_DIR}")


if __name__ == "__main__":
    main()
