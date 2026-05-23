import unicodedata


def normalize_text(value: str | None) -> str:
    if value is None:
        return ''
    clean = value.strip().lower()
    normalized = unicodedata.normalize('NFD', clean)
    return ''.join(ch for ch in normalized if unicodedata.category(ch) != 'Mn')
