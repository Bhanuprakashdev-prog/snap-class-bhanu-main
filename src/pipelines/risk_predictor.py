"""Hybrid attendance risk predictor (T7 + T8).

SMA trend on last 5 classes → primary signal.
LogisticRegression trained on history → secondary signal when >= 10 rows.
# ponytail: LR skipped if <10 rows of history, SMA only until data accumulates.
"""

import numpy as np
import pandas as pd


def _attendance_percentage(attended: int, total: int) -> float:
    return (attended / total * 100) if total > 0 else 100.0


def _sma_slope(series: list[int]) -> float:
    """Returns trend slope of the last 5 values (positive = improving)."""
    tail = series[-5:]
    if len(tail) < 2:
        return 0.0
    x = np.arange(len(tail), dtype=float)
    slope = np.polyfit(x, tail, 1)[0]
    return float(slope)


def _lr_risk_prob(total: int, attended: int, pct: float, all_rows: pd.DataFrame) -> float | None:
    """Logistic Regression risk probability; None if insufficient history."""
    if len(all_rows) < 10:
        return None  # ponytail: fall back to SMA
    try:
        from sklearn.linear_model import LogisticRegression
        X = all_rows[["total", "attended", "pct"]].values
        # Label: 1 = at risk (pct < 75)
        y = (all_rows["pct"] < 75).astype(int).values
        if len(set(y)) < 2:
            return None  # only one class — LR meaningless
        clf = LogisticRegression(max_iter=200)
        clf.fit(X, y)
        prob = clf.predict_proba([[total, attended, pct]])[0][1]
        return float(prob)
    except Exception:
        return None


def compute_risk(student_logs: list[dict]) -> dict:
    """
    Args:
        student_logs: list of {'subject_id': ..., 'is_present': bool}
    Returns:
        {'pct': float, 'tier': str, 'label': str, 'color': str, 'recommendation': str}
    """
    total = len(student_logs)
    attended = sum(1 for l in student_logs if l.get("is_present"))
    pct = _attendance_percentage(attended, total)

    presence_series = [1 if l.get("is_present") else 0 for l in student_logs]
    slope = _sma_slope(presence_series)

    # Build a dataframe for LR from per-session rolling state
    rows = []
    for i in range(1, total + 1):
        att = sum(presence_series[:i])
        rows.append({"total": i, "attended": att, "pct": _attendance_percentage(att, i)})
    df = pd.DataFrame(rows)

    lr_prob = _lr_risk_prob(total, attended, pct, df)

    # Determine risk tier
    if lr_prob is not None:
        # Hybrid: weight LR 60%, SMA-slope signal 40%
        slope_risk = max(0.0, min(1.0, 0.5 - slope * 2))
        combined = lr_prob * 0.6 + slope_risk * 0.4
        at_risk = combined > 0.5
    else:
        # SMA only
        at_risk = pct < 80 or (pct < 85 and slope < -0.2)

    if pct >= 85 and not at_risk:
        tier, color = "SAFE", "#2ecc71"
        label = "✅ Safe"
        rec = "Keep it up!"
    elif pct >= 75 or not at_risk:
        tier, color = "AT RISK", "#f39c12"
        label = "⚠️ At Risk"
        classes_needed = max(0, int((0.75 * (total + 5) - attended)))
        rec = f"Attend the next {classes_needed} sessions to stay above 75%."
    else:
        tier, color = "CRITICAL", "#e74c3c"
        label = "🚨 Critical"
        rec = "Attendance is critically low. Talk to your teacher immediately."

    return {
        "pct": round(pct, 1),
        "tier": tier,
        "color": color,
        "label": label,
        "recommendation": rec,
        "slope": round(slope, 3),
        "lr_prob": round(lr_prob, 3) if lr_prob is not None else None,
    }
