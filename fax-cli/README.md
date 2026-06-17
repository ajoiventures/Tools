# IRS Fax Sender

Lightweight CLI tool for sending faxes to the IRS via [Phaxio](https://www.phaxio.com/).

## Setup

**1. Get a Phaxio account**
- Sign up at phaxio.com (~$0.07/page, pay-as-you-go, no monthly fee)
- Grab your API Key and API Secret from the dashboard

**2. Install dependency**
```powershell
pip install requests
```

**3. Set credentials**
```powershell
# PowerShell (current session)
$env:PHAXIO_API_KEY = "your_key_here"
$env:PHAXIO_API_SECRET = "your_secret_here"

# Or add to your profile for persistence:
# Add to $PROFILE file
```

## Usage

```powershell
# Send a fax
python send_fax.py --to 18008290115 --file my_response.pdf

# Send with a cover page note
python send_fax.py --to 18008290115 --file response.pdf --cover "Re: CP2000 Notice, John Doe, SSN ending 1234"

# Check delivery status
python send_fax.py --status 12345678

# List common IRS fax numbers
python send_fax.py --irs-numbers
```

## Common IRS Fax Numbers

| Purpose | Number |
|---|---|
| General correspondence | +1-800-829-0115 |
| CP2000 notices | +1-800-978-3706 |
| Lien release requests | +1-855-802-7636 |
| Form 4506 (transcripts) | +1-855-587-0934 |
| Taxpayer Advocate | +1-877-777-8242 |

> **Always verify numbers at [irs.gov](https://www.irs.gov)** — they change without notice.

## Logs

Every sent fax is appended to `fax_log.jsonl` in this directory (timestamp, fax ID, recipient, file).

## Supported File Types

- **PDF** (recommended — always use PDF for IRS)
- TIFF
- DOCX / DOC

## Cost Estimate

| Pages | Cost |
|---|---|
| 1 page | ~$0.07 |
| 5 pages | ~$0.35 |
| 10 pages | ~$0.70 |

Phaxio charges per page sent, billed in US cents. No subscription required.
