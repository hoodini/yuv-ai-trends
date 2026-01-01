"""Utility functions for the Gen AI News Aggregator"""

import re

def strip_emojis(text):
    """Remove emoji characters from text to avoid Windows encoding issues"""
    if not isinstance(text, str):
        return text

    # Pattern to match most emoji characters
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)


def sanitize_dict(data):
    """Recursively sanitize dictionary to remove emojis from all string values"""
    if isinstance(data, dict):
        return {k: sanitize_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_dict(item) for item in data]
    elif isinstance(data, str):
        return strip_emojis(data)
    else:
        return data
