from rapidfuzz import fuzz


def similarity(a, b):
    if not a or not b:
        return 0
    return fuzz.ratio(a.lower().strip(), b.lower().strip())


def score_data(old_name, new_name, extracted):
    print("Scoring Agent running...")

    extracted_old = extracted.get("old_name", "")
    extracted_new = extracted.get("new_name", "")

    # 🔥 use precomputed scores if available
    old_score = extracted.get("old_score", similarity(old_name, extracted_old))
    new_score = extracted.get("new_score", similarity(new_name, extracted_new))

    print("Old match score:", old_score)
    print("New match score:", new_score)

    confidence = (old_score + new_score) / 2

    return {
        "confidence": confidence,
        "old_score": old_score,
        "new_score": new_score
    }