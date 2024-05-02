import os
from typing import Dict

import duckdb
from prefect import task

MOTHERDUCK_TOKEN = os.environ.get("MOTHERDUCK_TOKEN", "")


@task(name="Extract batch from dataset",
      task_run_name="extract-batch-from-dataset",)
def extract_batch(batch_size: int = 5):
	""" Extract batch from dataset """

	dataset_name = "common_crawl.wikipedia_en"
	con = duckdb.connect(f"md:?motherduck_token={MOTHERDUCK_TOKEN}")

	query = f"""
SELECT fetch_redirect
FROM {dataset_name}
WHERE category = 'Unknown'
LIMIT {batch_size}
	"""
	res = con.execute(query).fetchdf()

	return res["fetch_redirect"]


@task(
    name="Save batch to database",
    task_run_name="save-batch-to-database",
)
def save_batch_to_database(data: Dict[str, str]):
    """ Save batch to database """

    dataset_name = "common_crawl.wikipedia_en"
    con = duckdb.connect(f"md:?motherduck_token={MOTHERDUCK_TOKEN}")

    for url, category in data.items():
        query = f"""
    UPDATE {dataset_name}
    SET category = ?
    WHERE fetch_redirect = ?
        """
        con.execute(query, (
            category,
            url,
        ))
