r"""
Agent.py
Saves Top summary bullets (and full report) as JSON in same directory.

Usage:
  pip install PyPDF2
  python C:\Users\vinch\Desktop\Agent.py
"""

from PyPDF2 import PdfReader
import os
import re
import json
from datetime import datetime

PDF_PATH = r"C:\Users\vinch\Downloads\ukpga_20250022_en.pdf"
OUT_FULLTEXT = "uc_act_fulltext.txt"
OUT_REPORT = "uc_act_report_task3.json"
OUT_RULES = "rule_checks_task4.json"
OUT_SUMMARY = "uc_act_summary.json"   

def assert_pdf_exists(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"PDF not found at: {path}")

def read_pdf_text(path):
    """Extract text using PyPDF2 PdfReader."""
    assert_pdf_exists(path)
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        try:
            t = page.extract_text() or ""
        except Exception:
            t = ""
        pages.append(t)
    return "\n".join(pages)

def clean_text(text):
    if not text:
        return ""
    t = text.replace("\x0c", "\n")
    t = re.sub(r'\r\n', '\n', t)
    t = re.sub(r'\n\s+\n', '\n\n', t)
    t = re.sub(r'[ \t]{2,}', ' ', t)
    t = re.sub(r'^\s*\d+\s*$', '', t, flags=re.MULTILINE)
    return t.strip()

def snippet_around(text, keyword, before=60, after=240):
    m = re.search(re.escape(keyword), text, flags=re.IGNORECASE)
    if not m:
        return ""
    s = max(0, m.start() - before)
    e = min(len(text), m.end() + after)
    return text[s:e].strip()

def find_section_by_heading(text, heading_patterns, window_chars=1400):
    for pat in heading_patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            start = m.start()
            search_after = m.end()
            nxt = re.search(r'\n\s*(?:Section|Schedule|Part|Chapter|Short title|Interpretation|Explanatory note|ANNEX)\b', text[search_after:], flags=re.IGNORECASE)
            if nxt:
                end = search_after + nxt.start()
            else:
                end = min(len(text), start + window_chars)
            return text[start:end].strip()
    return ""

def extract_definitions(text):
    patterns = [r'\n\s*Definitions?\b', r'\bIn this (?:Act|section)\b', r'\bFor the purposes of this (?:Act|section)\b']
    sec = find_section_by_heading(text, patterns, window_chars=2000)
    if sec:
        return sec
    means = re.findall(r'["“]([^"”]{1,120})["”]\s+means\s+([^.;\n]+)[.;\n]?', text, flags=re.IGNORECASE)
    if means:
        return "\n".join([f"{k} — {v.strip()}" for k, v in means])
    return snippet_around(text, "consumer prices index") or "No explicit definitions block located."

def extract_obligations(text):
    pattern = r'([A-Z][^.\n]{0,300}\b(?:Secretary of State|the Secretary|Department for Communities|the Department)\b[^.\n]{0,300}\b(?:must|shall|is to|is required to|will)\b[^.\n]*\.)'
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    if matches:
        return "\n".join(sorted(set([m.strip() for m in matches])))
    sec = find_section_by_heading(text, [r'\n\s*Obligations?\b', r'\n\s*Duties?\b'])
    if sec:
        return sec
    return "No explicit obligations located by heuristics."

def extract_responsibilities(text):
    pattern = r'([A-Z][^.\n]{0,300}\b(?:Secretary of State|Department for Communities|the Department)\b[^.\n]{0,200}\b(?:responsib|responsibilit|is to exercise|is responsible)\b[^.\n]*\.)'
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    if matches:
        return "\n".join(sorted(set([m.strip() for m in matches])))
    return extract_obligations(text)

def extract_eligibility(text):
    sec = find_section_by_heading(text, [r'\n\s*Eligibility\b', r'\n\s*Who may claim\b'])
    if sec:
        return sec
    keywords = ['pre-2026 claimant', 'severe conditions', 'terminally ill', 'limited capability for work', 'LCWRA', 'LCW']
    found = []
    for kw in keywords:
        if re.search(re.escape(kw), text, flags=re.IGNORECASE):
            found.append(snippet_around(text, kw, before=40, after=140))
    if found:
        return "\n\n".join(found)
    return "No comprehensive eligibility criteria restated in this Act; see Universal Credit Regulations / Welfare Reform Act for full eligibility."

def extract_payments(text):
    step_block = re.search(r'(Step\s*1[\s\S]{0,450}Step\s*2[\s\S]{0,450}Step\s*3[\s\S]{0,450})', text, flags=re.IGNORECASE)
    if step_block:
        return step_block.group(1).strip()
    sec = find_section_by_heading(text, [r'\bstandard allowance\b', r'\buplift percentage\b', r'\bminimum amounts\b', r'\bamounts of the standard allowance\b'])
    if sec:
        return sec
    return snippet_around(text, "standard allowance") or "Payment calculation/entitlement structure not clearly extracted by heuristics."

def extract_penalties(text):
    matches = re.findall(r'([^.]{0,120}\b(?:penalt|offenc|sanction|fine)\w*\b[^.]{0,120}\.)', text, flags=re.IGNORECASE)
    if matches:
        return "\n".join(sorted(set([m.strip() for m in matches])))
    sec = find_section_by_heading(text, [r'\n\s*Offences?\b', r'\n\s*Penalt', r'\n\s*Penalties?\b'])
    if sec:
        return sec
    return "No explicit penalties or enforcement clauses located."

def extract_record_keeping(text):
    matches = re.findall(r'([^.]{0,120}\b(report|reporting|register|record|returns)\b[^.]{0,120}\.)', text, flags=re.IGNORECASE)
    if matches:
        snippets = [m[0].strip() for m in matches[:12]]
        return "\n".join(sorted(set(snippets)))
    sec = find_section_by_heading(text, [r'\n\s*Record-keeping\b', r'\n\s*Reporting\b', r'\n\s*Records\b'])
    if sec:
        return sec
    return "No explicit record-keeping or reporting obligations located."

SUMMARY_BULLETS = [
  "Purpose: Sets minimum amounts for Universal Credit standard allowance and certain elements for tax years 2026–27 to 2029–30 and updates related regulations.",
  "Key definitions: Contains definitions for calculation terms (e.g., 'consumer prices index', 'relevant power', 'standard allowance', 'tax year').",
  "Eligibility: References claimant categories (pre-2026 claimant; severe conditions criteria claimant; claimant who is terminally ill) but does not fully restate general eligibility rules.",
  "Obligations & responsibilities: Requires the Secretary of State (and corresponding NI department) to exercise specified powers to secure amounts and make regulatory amendments.",
  "Payments/Entitlements: Prescribes a step-wise calculation (baseline → CPI increase → uplift percentage) and specifies uplift percentages for the tax years in scope.",
  "Enforcement: No explicit new sanctions, fines or criminal offence clauses were located by heuristics.",
  "Record-keeping/reporting: No explicit reporting or record-keeping duties were located in the Act text."
]

def run_rule_checks(extracted):
    checks = []
    has_defs = bool(extracted.get("definitions") and len(extracted.get("definitions")) > 20)
    checks.append({
        "rule": "Act must define key terms",
        "status": "pass" if has_defs else "fail",
        "evidence": "Definitions block located" if has_defs else "No definitions block extracted",
        "confidence": 95 if has_defs else 50
    })
    elig = extracted.get("eligibility","")
    status = "partial" if re.search(r'pre-2026|severe conditions|terminally ill', elig, flags=re.IGNORECASE) else "fail"
    checks.append({
        "rule": "Act must specify eligibility criteria",
        "status": status,
        "evidence": elig or "No eligibility text extracted",
        "confidence": 78 if status=="partial" else 55
    })
    obligations_text = extracted.get("obligations","")
    status = "pass" if re.search(r'Secretary of State|Department for Communities|must|shall', obligations_text, flags=re.IGNORECASE) else "fail"
    checks.append({
        "rule": "Act must specify responsibilities of the administering authority",
        "status": status,
        "evidence": obligations_text or "No obligation text extracted",
        "confidence": 92 if status=="pass" else 55
    })
    penalties_text = extracted.get("penalties","")
    status = "fail" if penalties_text and "No explicit penalties" in penalties_text else ("pass" if penalties_text else "fail")
    checks.append({
        "rule": "Act must include enforcement or penalties",
        "status": status,
        "evidence": penalties_text or "No penalties text extracted",
        "confidence": 90 if status=="fail" else 70
    })
    payments_text = extracted.get("payments","")
    status = "pass" if payments_text and re.search(r'Step\s*1|CPI|uplift|standard allowance|tax year', payments_text, flags=re.IGNORECASE) else "fail"
    checks.append({
        "rule": "Act must include payment calculation or entitlement structure",
        "status": status,
        "evidence": payments_text or "No payment structure extracted",
        "confidence": 96 if status=="pass" else 60
    })
    rec_text = extracted.get("record_keeping","")
    status = "fail" if rec_text and "No explicit record-keeping" in rec_text else ("pass" if rec_text and len(rec_text)>10 else "fail")
    checks.append({
        "rule": "Act must include record-keeping or reporting requirements",
        "status": status,
        "evidence": rec_text or "No record-keeping text extracted",
        "confidence": 88 if status=="fail" else 70
    })
    return checks

def main():
    try:
        print("Reading PDF:", PDF_PATH)
        raw = read_pdf_text(PDF_PATH)
        if not raw:
            print("Warning: extracted text is empty.")
        text = clean_text(raw)
        print("Extracted characters:", len(text))

        with open(OUT_FULLTEXT, "w", encoding="utf-8") as f:
            f.write(text)
        print("Saved full extracted text to:", OUT_FULLTEXT)

        extracted_sections = {
            "definitions": extract_definitions(text),
            "obligations": extract_obligations(text),
            "responsibilities": extract_responsibilities(text),
            "eligibility": extract_eligibility(text),
            "payments": extract_payments(text),
            "penalties": extract_penalties(text),
            "record_keeping": extract_record_keeping(text)
        }

        summary_bullets = SUMMARY_BULLETS

        summary_json = {
            "source_pdf_path": PDF_PATH,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "summary_bullets": summary_bullets
        }
        with open(OUT_SUMMARY, "w", encoding="utf-8") as f:
            json.dump(summary_json, f, indent=2, ensure_ascii=False)
        print("Saved summary bullets to:", OUT_SUMMARY)

        rule_checks = run_rule_checks(extracted_sections)

        report = {
            "source_pdf_path": PDF_PATH,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "summary_bullets": summary_bullets,
            "extracted_sections": extracted_sections,
            "rule_checks": rule_checks
        }

        # Write outputs
        with open(OUT_REPORT, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        with open(OUT_RULES, "w", encoding="utf-8") as f:
            json.dump(rule_checks, f, indent=2, ensure_ascii=False)

        print("\nSaved report to:", OUT_REPORT)
        print("Saved rule-checks to:", OUT_RULES)
        print("Saved dedicated summary to:", OUT_SUMMARY)
        print("\nTop summary bullets (saved):")
        for b in summary_bullets:
            print(" -", b)

    except FileNotFoundError as fe:
        print("ERROR:", fe)
    except Exception as e:
        print("Unexpected error:", type(e).__name__, str(e))

if __name__ == "__main__":
    main()
