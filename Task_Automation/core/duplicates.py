import hashlib
from pathlib import Path

EXCLUDED = {
    ".git", "__pycache__", ".venv",
    "venv", "backups", "logs"
}

def file_hash(path):
    digest = hashlib.sha256()

    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()

def find_duplicates(folder, progress=None):
    folder = Path(folder)

    if not folder.is_dir():
        raise FileNotFoundError(folder)

    files = [
        path for path in folder.rglob("*")
        if path.is_file()
        and not any(part in EXCLUDED for part in path.parts)
    ]

    sizes = {}

    for path in files:
        try:
            sizes.setdefault(path.stat().st_size, []).append(path)
        except OSError:
            continue

    candidates = [
        path for group in sizes.values()
        if len(group) > 1
        for path in group
    ]

    groups = {}

    for index, path in enumerate(candidates, 1):
        try:
            key = (path.stat().st_size, file_hash(path))
            groups.setdefault(key, []).append(path)
        except OSError:
            continue

        if progress:
            progress(index, len(candidates), path.name)

    return [
        group for group in groups.values()
        if len(group) > 1
    ]
