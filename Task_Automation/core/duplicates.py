import hashlib
from pathlib import Path

def file_hash(path):
    digest = hashlib.sha256()

    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()

def find_duplicates(folder):
    folder = Path(folder)
    if not folder.is_dir():
        raise FileNotFoundError(folder)

    groups = {}
    for path in folder.rglob("*"):
        if path.is_file():
            try:
                key = (path.stat().st_size, file_hash(path))
                groups.setdefault(key, []).append(path)
            except (PermissionError, OSError):
                continue

    return [
        files for files in groups.values()
        if len(files) > 1
    ]
