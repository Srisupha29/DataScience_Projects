import re

from models.schemas import DailyCheckIn


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
    """Extract sleep duration from the transcript."""

    text = text.lower()

    number_words = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12
    }

    # Numeric format: "slept 8 hours"
    match = re.search(
        r"(?:slept|sleep)\s+(?:about\s+)?(\d+(?:\.\d+)?)\s*hours?",
        text
    )

    if match:
        return float(match.group(1))

    # Word format: "slept eight hours" / "sleep eight hours"
    for word, number in number_words.items():
        pattern = rf"(?:slept|sleep)\s+(?:about\s+)?{word}\s*hours?"

        if re.search(pattern, text):
            return float(number)

    return None


def extract_energy_level(text: str):
    """Extract energy level from a 1-5 rating."""

    text = text.lower()

    number_words = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5
    }

    # Numeric format:
    # "energy 5 out of 5"
    # "energy is 5"
    match = re.search(
        r"energy\s+(?:level\s+)?(?:is\s+)?(?:about\s+)?(\d)\s*(?:out\s+of\s+5)?",
        text
    )

    if match:
        energy = int(match.group(1))

        if 1 <= energy <= 5:
            return energy

    # Word format:
    # "energy five out of five"
    # "energy is five"
    for word, number in number_words.items():
        pattern = (
            rf"energy\s+(?:level\s+)?"
            rf"(?:is\s+)?(?:about\s+)?{word}"
            rf"(?:\s+out\s+of\s+five)?"
        )

        if re.search(pattern, text):
            return number

    return None


def extract_tasks(text: str):
    """Extract individual tasks from the transcript."""

    text = text.lower()

    # Find phrases beginning with a task indicator.
    pattern = (
        r"(?:need to|have to|want to|should|must)\s+"
        r"(.+?)"
        r"(?=\s+(?:need to|have to|want to|should|must)\s+|[.!?]|$)"
    )

    matches = re.findall(pattern, text)

    tasks = []

    for match in matches:
        # Split combined tasks connected by "and"
        parts = re.split(
            r"\s+and\s+(?=(?:spend|work|finish|complete|do|study|call|go|exercise|work out)\b)",
            match
        )

        for part in parts:
            task = part.strip()

            if task:
                tasks.append(task)

    return list(dict.fromkeys(tasks))


def extract_commitments(text: str):
    """Extract commitments with their labels and times."""

    text = text.lower()

    commitments = []

    # Internship / work: "internship from 9 am to 5 pm"
    internship_pattern = (
        r"(internship|work)\s+"
        r"(?:from\s+)?"
        r"(\d+(?::\d+)?\s*(?:am|pm)?)\s*"
        r"(?:to|-)\s*"
        r"(\d+(?::\d+)?\s*(?:am|pm)?)"
    )

    matches = re.findall(internship_pattern, text)

    for _, start, end in matches:
        commitments.append(
            f"Internship: {start}-{end}"
        )

    # Handle transcripts where Whisper removes "am/pm":
    # "internship from 9 to 5"
    if not matches:
        internship_simple = re.search(
            r"internship\s+(?:from\s+)?"
            r"(\d+(?::\d+)?)\s*(?:to|-)\s*"
            r"(\d+(?::\d+)?)",
            text
        )

        if internship_simple:
            start, end = internship_simple.groups()

            commitments.append(
                f"Internship: {start}-{end}"
            )

    # Tutoring: "tutoring at 7 pm"
    tutoring_match = re.search(
        r"tutoring\s+(?:at\s+)?"
        r"(\d+(?::\d+)?\s*(?:am|pm)?)",
        text
    )

    if tutoring_match:
        commitments.append(
            f"Tutoring: {tutoring_match.group(1)}"
        )

    # Remove duplicates
    return list(dict.fromkeys(commitments))