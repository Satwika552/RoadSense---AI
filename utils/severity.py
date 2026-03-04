# utils/severity.py
# Summarizes all detections into statistics for dashboard and report

def summarize_detections(detections):
    """
    Takes list of detections, returns a summary dictionary
    with counts, percentages and overall road health score.
    """

    if not detections:
        return {
            "total": 0,
            "severe": 0,
            "moderate": 0,
            "minor": 0,
            "severe_pct": 0,
            "moderate_pct": 0,
            "minor_pct": 0,
            "health_score": 100,
            "health_label": "Good",
            "damage_types": {},
            "recommendation": "No damage detected. Road is in good condition."
        }

    total = len(detections)

    # Count severities
    severe   = sum(1 for d in detections if d["severity"] == "Severe")
    moderate = sum(1 for d in detections if d["severity"] == "Moderate")
    minor    = sum(1 for d in detections if d["severity"] == "Minor")

    # Calculate percentages
    severe_pct   = round((severe / total) * 100)
    moderate_pct = round((moderate / total) * 100)
    minor_pct    = round((minor / total) * 100)

    # Count damage types
    damage_types = {}
    for d in detections:
        dtype = d["type"]
        damage_types[dtype] = damage_types.get(dtype, 0) + 1

    # Calculate road health score (100 = perfect, 0 = destroyed)
    health_score = max(0, 100 - (severe * 15) - (moderate * 7) - (minor * 3))
    health_score = min(100, health_score)

    # Health label
    if health_score >= 75:
        health_label = "Good"
    elif health_score >= 50:
        health_label = "Fair"
    elif health_score >= 25:
        health_label = "Poor"
    else:
        health_label = "Critical"

    # Recommendation
    if health_label == "Critical":
        recommendation = "URGENT: Immediate road repair required. Risk to vehicles and pedestrians."
    elif health_label == "Poor":
        recommendation = "Road repair should be scheduled within 2 weeks."
    elif health_label == "Fair":
        recommendation = "Road maintenance recommended within 1 month."
    else:
        recommendation = "Road is in acceptable condition. Monitor regularly."

    return {
        "total": total,
        "severe": severe,
        "moderate": moderate,
        "minor": minor,
        "severe_pct": severe_pct,
        "moderate_pct": moderate_pct,
        "minor_pct": minor_pct,
        "health_score": health_score,
        "health_label": health_label,
        "damage_types": damage_types,
        "recommendation": recommendation
    }