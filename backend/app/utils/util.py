import re


def slugify(text: str) -> str:
    """Return a filename‑safe version of any string."""
    text = re.sub(
        r'[\\/:"*?<>|]+', "_", text
    )  # replace path separators and illegal chars
    text = re.sub(r"\s+", "_", text.strip())  # collapse whitespace
    return text
