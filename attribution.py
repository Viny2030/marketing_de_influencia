from datetime import timedelta

def run_attribution(data):
    events = data["events"]
    conversions = data["conversions"]

    results = []

    for conv in conversions:
        for ev in events:
            if ev["device_id"] == conv["user_id"]:
                if ev["timestamp"] <= conv["timestamp"] <= ev["timestamp"] + timedelta(days=7):
                    results.append({
                        "campaign_id": ev["campaign_id"],
                        "conversion_value": conv["value"]
                    })

    # agregación simple
    summary = {}
    for r in results:
        summary.setdefault(r["campaign_id"], 0)
        summary[r["campaign_id"]] += r["conversion_value"]

    return summary
