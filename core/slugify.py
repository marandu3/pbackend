import re


def slugify(text: str) -> str:
    """Turn a title into a clean, URL-safe slug: 'My Project!' -> 'my-project'."""
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "project"


def unique_slug(base_slug: str, slug_exists) -> str:
    """Append -2, -3, ... until slug_exists(candidate) is False."""
    if not slug_exists(base_slug):
        return base_slug
    suffix = 2
    while slug_exists(f"{base_slug}-{suffix}"):
        suffix += 1
    return f"{base_slug}-{suffix}"
