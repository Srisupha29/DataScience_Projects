import re

from models.schemas import DailyCheckIn, Commitment


NUMBER_WORDS = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
}


def extract_checkin(transcript: str) -> DailyCheckIn:
    """Extract structured information from a daily check-in."""

    sleep_hours = extract_sleep_hours(transcript)
    energy_level = extract_energy_level(transcript)

    tasks = extract_tasks(transcript)
    commitments = extract_commitments(transcript)

    return DailyCheckIn(
        sleep_hours=sleep_hours,
        energy_level=energy_level,
        tasks=tasks,
        commitments=commitments,
        notes=transcript
    )


def extract_sleep_hours(text: str):
    """Extract the number of hours slept."""

    text = text.lower()

    for word, number in NUMBER_WORDS.items():
        text = re.sub(rf"\b{word}\b", number, text)

    match = re.search(
        r"slept\s+(?:about\s+|around\s+)?"
        r"(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)",
        text
    )

    if match:
        return float(match.group(1))

    return None


def extract_energy_level(text: str):
    """Extract energy level from 1–5."""

    text = text.lower()

    for word, number in NUMBER_WORDS.items():
        text = re.sub(rf"\b{word}\b", number, text)

    match = re.search(
        r"energy\s+(?:is|level\s+is|of)?\s*"
        r"(\d+)(?:\s*(?:out\s+of|/)\s*5)?",
        text
    )

    if match:
        energy = int(match.group(1))

        if 1 <= energy <= 5:
            return energy

    return None


def extract_tasks(text: str):
    """Extract tasks that the user says they need or want to do."""

    text = text.lower()

    pattern = (
        r"(?:need to|have to|want to|should|must)\s+"
        r"(.+?)"
        r"(?=\s+(?:need to|have to|want to|should|must)\s+|[.!?]|$)"
    )

    matches = re.findall(pattern, text)

    tasks = []

    for match in matches:

        parts = re.split(
            r"\s+and\s+(?="
            r"(?:spend|work|finish|complete|do|study|call|go|"
            r"exercise|work out)\b"
            r")",
            match
        )

        for part in parts:
            task = part.strip()

            if task:
                tasks.append(task)

    return list(dict.fromkeys(tasks))


def extract_commitments(text: str):
    """
    Extract activities that have an associated time.

    This function is intentionally generic.
    It does not depend on specific activity names.
    """

    text = text.lower()

    # Convert common number words to digits.
    for word, number in NUMBER_WORDS.items():
        text = re.sub(rf"\b{word}\b", number, text)

    # Normalize written AM/PM.
    text = re.sub(r"\ba\.m\.\b", "am", text)
    text = re.sub(r"\bp\.m\.\b", "pm", text)

    commitments = []

    # TIME RANGES
   
    range_pattern = re.compile(
        r"(?:"
        r"(?:i\s+have|i\s+need\s+to|i\s+have\s+to|"
        r"i'm\s+going\s+to|i\s+am\s+going\s+to)\s+"
        r")?"
        r"(.+?)\s+"
        r"(?:from\s+)?"
        r"(\d{1,2}(?::\d{2})?)\s*(am|pm)?"
        r"\s*(?:to|-)\s*"
        r"(\d{1,2}(?::\d{2})?)\s*(am|pm)?"
    )

    for match in range_pattern.finditer(text):

        activity = match.group(1).strip()

        start = match.group(2)
        start_period = match.group(3)

        end = match.group(4)
        end_period = match.group(5)

        if start_period:
            start = f"{start} {start_period}"

        if end_period:
            end = f"{end} {end_period}"

        activity = clean_activity(activity)

        if activity:
            commitments.append(
                Commitment(
                    activity=activity,
                    start_time=start,
                    end_time=end
                )
            )

    single_pattern = re.compile(
        r"(?:"
        r"(?:i\s+have|i\s+need\s+to|i\s+have\s+to|"
        r"i'm\s+going\s+to|i\s+am\s+going\s+to)\s+"
        r")?"
        r"(.+?)\s+"
        r"(?:at|around)\s+"
        r"(\d{1,2}(?::\d{2})?)\s*(am|pm)?"
    )

    for match in single_pattern.finditer(text):

        activity = match.group(1).strip()

        time = match.group(2)
        period = match.group(3)

        if period:
            time = f"{time} {period}"

        activity = clean_activity(activity)

        if activity:
            commitments.append(
                Commitment(
                    activity=activity,
                    start_time=time
                )
            )

    # Remove duplicate commitments.
    unique = []

    for commitment in commitments:

        if commitment not in unique:
            unique.append(commitment)

    return unique


def clean_activity(activity: str):
    """Clean unnecessary words from an extracted activity."""

    activity = activity.strip()

    activity = re.sub(
        r"\s+(today|tomorrow|tonight)$",
        "",
        activity
    )

    activity = re.sub(
        r"^(today|tomorrow|tonight)\s+",
        "",
        activity
    )

    return activity.strip()