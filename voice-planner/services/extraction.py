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
    """Extract activities that have an associated time or time range."""

    text = text.lower()

    number_words = {
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
        "twelve": "12"
    }

    # Convert written numbers to digits
    for word, number in number_words.items():
        text = re.sub(
            rf"\b{word}\b",
            number,
            text
        )

    # Normalize AM/PM variations
    text = re.sub(r"\ba\.m\.\b", "am", text)
    text = re.sub(r"\bp\.m\.\b", "pm", text)

    commitments = []

    # --------------------------------------------------
    # Time ranges
    # Example:
    # "I have internship from 9 to 5 today"
    # "I have class from 10:30 to 12"
    # --------------------------------------------------

    range_pattern = re.compile(
        r"(?:i\s+have|i\s+need\s+to|i\s+have\s+to|"
        r"i'm\s+going\s+to|i\s+am\s+going\s+to)?\s*"
        r"(.+?)\s+"
        r"(?:from\s+)?"
        r"(\d+(?::\d+)?)\s*"
        r"(?:am|pm)?\s*"
        r"(?:to|-)\s*"
        r"(\d+(?::\d+)?)\s*"
        r"(?:am|pm)?"
    )

    for match in range_pattern.finditer(text):

        activity = match.group(1).strip()
        start = match.group(2)
        end = match.group(3)

        # Remove common trailing words
        activity = re.sub(
            r"\s+(today|tomorrow|tonight)$",
            "",
            activity
        ).strip()

        if activity:
            commitments.append(
                f"{activity}: {start}-{end}"
            )

    # --------------------------------------------------
    # Single times
    # Example:
    # "I have tutoring at 7"
    # "I have a meeting at 2 pm"
    # "I need to go to the dentist at 3"
    # --------------------------------------------------

    single_pattern = re.compile(
        r"(?:i\s+have|i\s+need\s+to|i\s+have\s+to|"
        r"i'm\s+going\s+to|i\s+am\s+going\s+to)\s+"
        r"(.+?)\s+"
        r"(?:at|around)\s+"
        r"(\d+(?::\d+)?)\s*"
        r"(am|pm)?"
    )

    for match in single_pattern.finditer(text):

        activity = match.group(1).strip()
        time = match.group(2)
        period = match.group(3)

        if period:
            time = f"{time} {period}"

        commitments.append(
            f"{activity}: {time}"
        )

    return list(dict.fromkeys(commitments))