banned_urls = [
    "https://www.google.com",
    "https://www.facebook.com",
    "https://www.twitter.com",
    "https://www.instagram.com",
    "https://www.youtube.com",
    "https://www.linkedin.com",
    "https://www.pinterest.com",
    "https://www.reddit.com",
]


def check_is_banned_url(url: str):
    for banned_url in banned_urls:
        if url.find(banned_url) == 0:
            return True
    return False


def batch_array(arr, batch_size=10):
    items = []
    for i in range(0, len(arr), batch_size):
        items.append(arr[i : i + batch_size])
    return items
