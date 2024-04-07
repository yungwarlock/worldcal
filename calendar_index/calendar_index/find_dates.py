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


if __name__ == "__main__":
    # Test the function with some example text
    text = "The deadline is 12/31/2023 and today is 2024-04-01."
    dates = text_contain_dates(text)
    print("Dates found:", dates)

    text = "The event will take place on JUNE 15, 2026 and January 8, 2009."
    dates = text_contain_dates(text)
    print("Dates found:", dates)

    text = "The event is scheduled for JUNE 19"
    dates = text_contain_dates(text)
    print("Dates found:", dates)

    text = "The report was published in May 2020, May, 2020 and the project started in 2020."
    dates = text_contain_dates(text)
    print("Dates found:", dates)
