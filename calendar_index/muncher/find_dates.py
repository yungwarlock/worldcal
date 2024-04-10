import re

from prefect import task


@task
def text_contain_dates(text):
    matches = []
    # Define the regex pattern to match dates in the formats "MM/DD/YYYY" and "YYYY-MM-DD"
    pattern = r"\b(?:\d{1,2}\/\d{1,2}\/\d{4}|\d{4}-\d{2}-\d{2})\b"
    m = re.findall(pattern, text, re.IGNORECASE)
    matches.extend(m)

    # Define the regex pattern to match dates in the format "Month Day, Year"
    pattern = r"(?i)(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}"
    m = re.findall(pattern, text, re.IGNORECASE)
    matches.extend(m)

    # Define the regex pattern to match dates in the format "Month Day"
    pattern = r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\b"
    matches = re.findall(pattern, text, re.IGNORECASE)

    # Define the regex pattern to match dates in the formats "Month, Year" and "Year"
    pattern = r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)?\s*,?\s*\d{4}\b"
    m = re.findall(pattern, text, re.IGNORECASE)
    matches.extend(m)

    return matches
