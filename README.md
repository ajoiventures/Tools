# Tools — ajoiventures

Personal toolbox. Each subfolder is a standalone tool.

## Tools

| Tool | Description | Deploy |
|---|---|---|
| [`fax-web/`](fax-web/) | Mobile web app — scan a document & fax it to the IRS | Netlify |
| [`fax_cli/`](fax_cli/) | Python CLI — send faxes from terminal | Local |

---

## fax-web

Mobile-first web app with camera capture, in-browser OCR (Tesseract.js), and one-tap fax sending via Sinch/Phaxio.

**Deploy to Netlify:** drag the `fax-web/` folder into [app.netlify.com](https://app.netlify.com) — `netlify.toml` handles the rest.

## fax_cli

Lightweight Python script. Requires `pip install requests`.

```bash
python fax_cli/send_fax.py --to 18008290115 --file document.pdf
python fax_cli/send_fax.py --irs-numbers
```
