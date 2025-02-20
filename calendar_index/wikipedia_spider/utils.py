from typing import List

from models import URL


def batch_array(arr, batch_size=4) -> List[List[URL]]:
    items = []
    for i in range(0, len(arr), batch_size):
        items.append(arr[i: i + batch_size])
    return items
