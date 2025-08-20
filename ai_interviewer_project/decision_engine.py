def final_decision(predicted_role, selected_role, sentiment_score, threshold=0.5):
    # Skill match score: 1 if roles match, 0 otherwise
    skill_match = int(predicted_role == selected_role)
    reasons = []
    if skill_match:
        reasons.append(f"Strong {selected_role.lower()} skills")
    else:
        reasons.append(f"Resume does not match the selected role ({selected_role})")

    if sentiment_score > threshold:
        reasons.append("Good communication/confidence")
    else:
        reasons.append("Low confidence in communication")

    # Combine scores for decision
    if skill_match and sentiment_score > threshold:
        result = "✅ Selected"
    elif not skill_match and sentiment_score > threshold + 0.1:
        result = "🤔 Maybe (good interview, but skill mismatch)"
    else:
        result = "❌ Rejected"

    reason_str = "; ".join(reasons)
    return result, reason_str
