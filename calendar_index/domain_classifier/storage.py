import csv


def get_domains_batch(file_name: str, batch_size: int = 4):
    with open(file_name, "r") as file:
        reader = csv.DictReader(file)
        while True:
            batch = []
            try:
                for _ in range(batch_size):
                    batch.append(next(reader))
                yield batch
            except StopIteration:
                yield batch
                break
