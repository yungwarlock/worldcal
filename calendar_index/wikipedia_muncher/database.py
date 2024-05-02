import os
from typing import Dict, Sequence, Any, TypedDict

import duckdb
from prefect import task
from nanoid import generate


MOTHERDUCK_TOKEN = os.environ.get("MOTHERDUCK_TOKEN", "")


class Event(TypedDict):
    year: int
    month: int
    day: int
    title: str
    summary: str
    url: str
    context: Dict[str, Any]



@task(
    name="Extract batch from dataset",
    task_run_name="extract-batch-from-dataset",
)
def extract_batch(batch_size: int = 5):
    """Extract batch from dataset"""

    dataset_name = "common_crawl.pending_extract"
    con = duckdb.connect(f"md:?motherduck_token={MOTHERDUCK_TOKEN}")

    query = f"""
SELECT url
FROM {dataset_name}
LIMIT {batch_size}
	"""
    res = con.execute(query).fetchdf()

    return res["url"]


@task(
    name="Save batch to database",
    task_run_name="save-batch-to-database",
)
def save_batch_to_database(data: Sequence[Event]):
    """Save batch to database"""

    dataset_name = "common_crawl.events"
    con = duckdb.connect(f"md:?motherduck_token={MOTHERDUCK_TOKEN}")

    query = f"""
INSERT INTO {dataset_name} (
    id,
    title,
    summary,
    context,
    url,
    day,
    month,
    year
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    con.executemany(
        query,
        (
            (
                generate(size=10),
                event["title"],
                event["summary"],
                event["context"],
                event["url"],
                event["day"],
                event["month"],
                event["year"],
            )
            for event in data
        ),
    )
