import streamlit as st


def render_student_ai_insights(logs: list, student_name: str):
    """Renders a modern Circular Radial Gauge + AI Smart Insights Card."""
    total = len(logs)
    attended = sum(1 for l in logs if l.get('is_present'))
    pct = (attended / total * 100) if total > 0 else 100.0

    # Calculate stroke offset for SVG circle (circumference = 2 * pi * 40 ≈ 251.2)
    circumference = 251.2
    dashoffset = circumference - (pct / 100.0 * circumference)

    # Risk Tier & Palette
    if pct >= 80.0:
        color = "#10B981"  # Emerald
        bg_color = "rgba(16, 185, 129, 0.1)"
        badge_text = "🛡️ Excellent Standing"
        badge_color = "#047857"
        safe_skips = max(0, int((attended - 0.75 * total) / 0.75))
        ai_tip = f"You are well above the 75% threshold. You can miss up to <strong>{safe_skips} class{'es' if safe_skips != 1 else ''}</strong> and stay safe."
    elif pct >= 75.0:
        color = "#F59E0B"  # Amber
        bg_color = "rgba(245, 158, 11, 0.1)"
        badge_text = "⚠️ Borderline (75% Threshold)"
        badge_color = "#B45309"
        ai_tip = "You are near the 75% boundary. <strong>Do not skip any upcoming classes</strong> to avoid attendance shortages."
    else:
        color = "#EF4444"  # Rose
        bg_color = "rgba(239, 68, 68, 0.1)"
        badge_text = "🚨 Critical Shortage (<75%)"
        badge_color = "#B91C1C"
        classes_needed = max(1, int(np_ceil_needed(attended, total, target=0.75)))
        ai_tip = f"Attendance shortage detected! You must attend the next <strong>{classes_needed} consecutive sessions</strong> to get back to 75%."

    gauge_html = f"""
    <div style="
        background: #FFFFFF;
        border-radius: 1.5rem;
        padding: 1.75rem;
        border: 1.5px solid #E2E8F0;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 2rem;
        flex-wrap: wrap;
    ">
        <!-- SVG Radial Gauge -->
        <div style="position: relative; width: 110px; height: 110px; flex-shrink: 0; margin: 0 auto;">
            <svg viewBox="0 0 100 100" style="transform: rotate(-90deg); width: 100%; height: 100%;">
                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#E2E8F0" stroke-width="8"></circle>
                <circle cx="50" cy="50" r="40" fill="transparent" stroke="{color}" stroke-width="8"
                    stroke-dasharray="{circumference}" stroke-dashoffset="{dashoffset}"
                    stroke-linecap="round" style="transition: stroke-dashoffset 0.8s ease;"></circle>
            </svg>
            <div style="
                position: absolute;
                inset: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            ">
                <span style="font-family: 'Outfit', sans-serif; font-size: 1.6rem; font-weight: 800; color: #1E1B4B; line-height: 1;">
                    {pct:.0f}%
                </span>
                <span style="font-size: 0.68rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.04em;">
                    Overall
                </span>
            </div>
        </div>

        <!-- AI Insights & Tips -->
        <div style="flex: 1; min-width: 240px;">
            <div style="display: inline-flex; align-items: center; gap: 6px; background: {bg_color}; color: {badge_color}; padding: 4px 12px; border-radius: 9999px; font-size: 0.82rem; font-weight: 700; margin-bottom: 0.6rem;">
                {badge_text}
            </div>
            <h3 style="margin: 0 0 0.4rem 0; color: #1E1B4B; font-size: 1.15rem; font-family: 'Outfit', sans-serif;">
                AI Attendance Radar
            </h3>
            <p style="margin: 0; color: #475569; font-size: 0.92rem; line-height: 1.5;">
                {ai_tip}
            </p>
            <div style="display: flex; gap: 1rem; margin-top: 0.75rem; flex-wrap: wrap;">
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 4px 10px; border-radius: 8px; font-size: 0.82rem; color: #334155;">
                    ✅ Attended: <strong>{attended}</strong>
                </div>
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 4px 10px; border-radius: 8px; font-size: 0.82rem; color: #334155;">
                    📅 Total Sessions: <strong>{total}</strong>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(gauge_html, unsafe_allow_html=True)


def np_ceil_needed(attended: int, total: int, target: float = 0.75) -> int:
    """Calculates how many consecutive classes are needed to reach target percentage."""
    if total == 0:
        return 0
    if (attended / total) >= target:
        return 0
    # (attended + x) / (total + x) >= target
    # attended + x >= target*total + target*x
    # x(1 - target) >= target*total - attended
    # x >= (target*total - attended) / (1 - target)
    x = (target * total - attended) / (1.0 - target)
    return max(1, int(x + 0.999))
