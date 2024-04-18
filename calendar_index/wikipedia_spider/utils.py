


def batch_array(arr, batch_size=10):
    items = []
    for i in range(0, len(arr), batch_size):
        items.append(arr[i : i + batch_size])
    return items
