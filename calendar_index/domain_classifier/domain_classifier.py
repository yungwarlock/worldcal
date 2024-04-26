import os
import csv
import glob
from pathlib import Path

import nanoid
from prefect import flow, get_run_logger

from storage import get_domains_batch
from extract_labels import batch_get_url_category


WORLDCAL_FS = os.environ.get("WORLDCAL_FS", "")

@flow
def domain_classifier(chunk_name: str):
    logger = get_run_logger()

    batch_files = glob.glob(f"{WORLDCAL_FS}/jobs/domain_classifier/{chunk_name}/*.csv")

    for batch_file in batch_files:
        logger.info(f"Processing batch {batch_file}")

        batch_id = nanoid.generate()
        result_path = Path(batch_file).parent / "results" / f"batch_{batch_id}.csv"
        result_path.parent.mkdir(exist_ok=True, parents=True)

        domain_batches = get_domains_batch(batch_file)

        with open(result_path, "w") as f:
            result_writer = csv.DictWriter(f, fieldnames=["domain", "category"])

            for index, batch in enumerate(domain_batches):
                logger.info(f"Processing batch {index} of {batch_file}")

                urls = [item["domain"] for item in batch]

                batch_get_url_category(urls, result_writer)



if __name__ == "__main__":
    domain_classifier.serve(
        name="domain_classifier",
    ) # type: ignore
