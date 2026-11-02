from models.schemas import DailyCheckIn


def generate_plan(checkin: DailyCheckIn):
    """Generate a simple realistic daily plan from a check-in."""

    plan = []

    # Add fixed commitments first
    for commitment in checkin.commitments:
        plan.append({
            "time": extract_time(commitment),
            "activity": commitment
        })

    # Add tasks
    for task in checkin.tasks:
        plan.append({
            "time": "Flexible",
            "activity": task
        })

    # Add recovery depending on energy
    if checkin.energy_level is not None:

        if checkin.energy_level <= 2:
            plan.append({
                "time": "Flexible",
                "activity": "Take extra breaks and keep demanding tasks short"
            })

        elif checkin.energy_level >= 4:
            plan.append({
                "time": "Flexible",
                "activity": "Use your higher energy for focused work"
            })

    return plan


def extract_time(commitment: str):
    """Extract the time portion from a commitment."""

    if ":" in commitment:
        parts = commitment.split(":", 1)

        if len(parts) == 2:
            return parts[1].strip()

    return "Scheduled"