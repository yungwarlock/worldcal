import re


banned_urls = [
    "google.com",
    "facebook.com",
    "twitter.com",
    "instagram.com",
    "youtube.com",
    "linkedin.com",
    "pinterest.com",
    "reddit.com",
    "whatsapp.com",
]


def check_is_banned_url(url: str):
    if any(re.search(banned_url, url) for banned_url in banned_urls):
        return True
    return False


def batch_array(arr, batch_size=10):
    items = []
    for i in range(0, len(arr), batch_size):
        items.append(arr[i : i + batch_size])
    return items
