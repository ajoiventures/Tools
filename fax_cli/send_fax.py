#!/usr/bin/env python3
"""
IRS Fax Sender — powered by Sinch (Phaxio) API
Usage:
    python send_fax.py --to 18008290115 --file document.pdf
    python send_fax.py --to 18008290115 --file doc.pdf --cover "John Doe, SSN ending 1234"
    python send_fax.py --status <fax_id>
    python send_fax.py --irs-numbers
"""

import argparse
import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

# ── Sinch / Phaxio credentials ───────────────────────────────────────────────
# Override via env vars if needed: SINCH_KEY_ID, SINCH_KEY_SECRET

_DEFAULT_KEY_ID     = "d633c79a-c3db-40ce-8298-8b385d0799cb"
_DEFAULT_KEY_SECRET = "q_IyRpb3MqmGB5rJY2bGnXt-dG"
_PROJECT_ID         = "12de7a17-948a-4f8d-9e20-815207f0aee7"

PHAXIO_API_URL = "https://api.phaxio.com/v2.1"

# ── Common IRS fax numbers ───────────────────────────────────────────────────

IRS_FAX_NUMBERS = {
    "general":       "18008290115",  # General correspondence
    "cp2000":        "18009783706",  # CP2000 notices
    "lien-release":  "18558027636",  # Lien release requests
    "form-4506":     "18555870934",  # Transcript requests
    "taxpayer-adv":  "18777778242",  # Taxpayer Advocate Service
}

# ── Core functions ───────────────────────────────────────────────────────────

def get_credentials():
    key_id     = os.environ.get("SINCH_KEY_ID",     _DEFAULT_KEY_ID)
    key_secret = os.environ.get("SINCH_KEY_SECRET", _DEFAULT_KEY_SECRET)
    return key_id, key_secret


def send_fax(to_number: str, file_path: str, cover_text: str = None) -> dict:
    """Send a fax via Sinch/Phaxio. Returns the API response dict."""
    api_key, api_secret = get_credentials()

    # Normalize — strip non-digits, ensure leading 1 for US
    digits = "".join(c for c in to_number if c.isdigit())
    if len(digits) == 10:
        digits = "1" + digits
    if len(digits) != 11 or digits[0] != "1":
        raise ValueError(f"Invalid US fax number: {to_number!r} → {digits!r}")

    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if file_path.suffix.lower() not in {".pdf", ".tiff", ".tif", ".docx", ".doc"}:
        print(f"WARNING: {file_path.suffix} may not be supported. PDF is recommended.")

    data = {"to[0]": f"+{digits}"}
    if cover_text:
        data["cover_page_text"] = cover_text

    print(f"\nSending fax to +{digits}...")
    print(f"  File : {file_path} ({file_path.stat().st_size // 1024} KB)")
    if cover_text:
        print(f"  Cover: {cover_text[:80]}")

    with open(file_path, "rb") as f:
        resp = requests.post(
            f"{PHAXIO_API_URL}/faxes",
            data=data,
            files={"file[0]": (file_path.name, f, _mime_type(file_path))},
            auth=(api_key, api_secret),
            timeout=60,
        )

    result = resp.json()
    if not result.get("success"):
        raise RuntimeError(f"API error: {result.get('message', result)}")

    fax_id = result["data"]["id"]
    print(f"\n✓ Fax queued — ID: {fax_id}")
    print(f"  Check status: python send_fax.py --status {fax_id}")
    _save_log(fax_id, digits, str(file_path), cover_text)
    return result


def check_status(fax_id: str) -> dict:
    """Check status of a previously sent fax."""
    api_key, api_secret = get_credentials()
    resp = requests.get(
        f"{PHAXIO_API_URL}/faxes/{fax_id}",
        auth=(api_key, api_secret),
        timeout=30,
    )
    result = resp.json()
    if not result.get("success"):
        raise RuntimeError(f"API error: {result.get('message', result)}")

    fax  = result["data"]
    cost = fax.get("cost", "?")

    print(f"\nFax {fax_id}")
    print(f"  Status : {fax.get('status', 'unknown')}")
    print(f"  Pages  : {fax.get('num_pages', '?')}")
    print(f"  Cost   : ${cost / 100:.2f}" if isinstance(cost, int) else f"  Cost   : {cost}")
    print(f"  To     : {fax.get('recipients', [{}])[0].get('phone_number', '?')}")
    for r in fax.get("recipients", []):
        print(f"  Result : {r.get('status')} — {r.get('error_type', 'OK')}")

    return result


def list_irs_numbers():
    print("\nCommon IRS fax numbers:")
    for name, number in IRS_FAX_NUMBERS.items():
        print(f"  {name:<18} +{number}")
    print("\nAlways verify at irs.gov — numbers change frequently.")


# ── Helpers ──────────────────────────────────────────────────────────────────

def _mime_type(path: Path) -> str:
    return {
        ".pdf":  "application/pdf",
        ".tiff": "image/tiff",
        ".tif":  "image/tiff",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".doc":  "application/msword",
    }.get(path.suffix.lower(), "application/octet-stream")


def _save_log(fax_id, to_number, file_path, cover_text):
    log_file = Path(__file__).parent / "fax_log.jsonl"
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "fax_id": fax_id,
        "to": to_number,
        "file": file_path,
        "cover": cover_text,
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Send faxes to the IRS (or anywhere) via Sinch/Phaxio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python send_fax.py --to 18008290115 --file response.pdf
  python send_fax.py --to 18008290115 --file response.pdf --cover "Re: CP2000, John Doe"
  python send_fax.py --status 12345678
  python send_fax.py --irs-numbers
        """
    )
    parser.add_argument("--to",          help="Recipient fax number (digits, e.g. 18008290115)")
    parser.add_argument("--file",        help="Path to PDF or TIFF to fax")
    parser.add_argument("--cover",       help="Optional cover page note")
    parser.add_argument("--status",      metavar="FAX_ID", help="Check status of a sent fax")
    parser.add_argument("--irs-numbers", action="store_true", help="List common IRS fax numbers")

    args = parser.parse_args()

    if args.irs_numbers:
        list_irs_numbers()
    elif args.status:
        check_status(args.status)
    elif args.to and args.file:
        send_fax(args.to, args.file, args.cover)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
