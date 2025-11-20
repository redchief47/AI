# VIDEO 
https://www.dropbox.com/scl/fi/11dwqebez13rxj9r425po/2025-11-21-00-23-32.mkv?rlkey=bbsrclddb5jok9qcvbwv9hmvi&st=k27jwlqr&dl=0

# Universal Credit Act 2025 – AI Agent
**Made by Shreyash Vinchurkar**

## 📌 Overview
This project implements a mini AI agent that reads, analyses, and extracts structured information from the **Universal Credit Act 2025**.  
It completes **Tasks 1–4** of the assignment, fully locally, using Python.

## 🛠️ Approach
The solution follows a deterministic, rule-driven architecture designed for reliability and reproducibility without external APIs.

### 1. PDF Extraction
- Used PyPDF2 to load and extract text from the Act PDF.
- Combined text from all pages and cleaned formatting noise.

### 2. Text Cleaning
- Removed page numbers, form feed characters, irregular spacing, and broken lines.
- Produced a clean, analysis-ready text file.

### 3. Summary Generation
- Created a 7-point structured summary covering:
  - Purpose  
  - Definitions  
  - Eligibility  
  - Obligations  
  - Payments  
  - Enforcement  
  - Record-keeping  

### 4. Key Legislative Section Extraction (Task 3)
Extracts:
- definitions  
- obligations  
- responsibilities  
- eligibility  
- payments  
- penalties  
- record_keeping  

Using:
1. Heading-based detection  
2. Regex heuristics  
3. Keyword-based fallback  

### 5. Rule-Based Checks (Task 4)
Evaluates the Act against 6 required legislative rules and saves:
- status  
- evidence  
- confidence score  

## 📂 Output Files
Generated after running the script:
- uc_act_fulltext.txt
- uc_act_summary.json
- uc_act_report_task3.json
- rule_checks_task3.json

## 🚀 How to Run
1. Install:
   ```
   pip install PyPDF2
   ```
2. Place the PDF:
   ```
   C:\Users\vinch\Downloads\ukpga_20250022_en.pdf
   ```
3. Run:
   ```
   python Agent.py
   ```

## 👨‍💻 Author
Made by Shreyash Vinchurkar
