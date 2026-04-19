from docx import Document
from rapidfuzz import fuzz


# -------------------------
# DOCX EXTRACTION
# -------------------------
def extract_text_from_docx(file_path):
    text = ""

    try:
        doc = Document(file_path)

        for para in doc.paragraphs:
            text += para.text.strip() + "\n"

    except Exception as e:
        print("DOCX error:", e)

    print("\nExtracted Text:")
    print(text)

    return text


# -------------------------
# NAME EXTRACTION
# -------------------------
def extract_names(text):
    lines = text.split("\n")

    names = []

    for line in lines:
        line = line.strip()

        # Only keep meaningful lines (avoid empty / noise)
        if len(line) > 2:
            names.append(line)

    print("Extracted Names:", names)

    return names


# -------------------------
# FUZZY MATCH
# -------------------------
def find_best_match(input_name, names):
    input_name_clean = input_name.lower().strip()

    best_match = ""
    best_score = 0

    for name in names:
        score = fuzz.ratio(input_name_clean, name.lower().strip())

        if score > best_score:
            best_score = score
            best_match = name

    print(f"[MATCH] {input_name} → {best_match} ({best_score})")

    # 🔥 FIX: don't return empty immediately
    # return best match always, but let scoring decide confidence
    return best_match, best_score


# -------------------------
# MAIN FUNCTION
# -------------------------
def process_document(file_path, old_name, new_name):
    print("\nProcessing:", file_path)

    text = ""

    if file_path.lower().endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        print("Unsupported file type")

    names = extract_names(text)

    extracted_old, old_score = find_best_match(old_name, names)
    extracted_new, new_score = find_best_match(new_name, names)

    print("Matched Old:", extracted_old)
    print("Matched New:", extracted_new)

    # 🔥 NEW: simple forgery simulation
    if old_score > 70 and new_score > 70:
        forgery_flag = "PASS"
    else:
        forgery_flag = "REVIEW"

    return {
        "old_name": extracted_old,
        "new_name": extracted_new,
        "old_score": old_score,
        "new_score": new_score,
        "forgery": forgery_flag
    }