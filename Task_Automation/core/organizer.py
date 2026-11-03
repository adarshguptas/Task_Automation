import shutil
from pathlib import Path

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif",
    ".bmp", ".webp", ".tiff"
}

def scan_images(folder):
    folder = Path(folder)
    if not folder.is_dir():
        return []
    return [
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    ]

def organize_images(source, destination, move=False):
    source = Path(source)
    destination = Path(destination)

    if not source.is_dir():
        raise FileNotFoundError(f"Source folder not found: {source}")

    destination.mkdir(parents=True, exist_ok=True)
    results = []

    for file in scan_images(source):
        target = destination / file.name
        counter = 1

        while target.exists():
            target = destination / f"{file.stem}_{counter}{file.suffix}"
            counter += 1

        if move:
            shutil.move(str(file), str(target))
            action = "MOVED"
        else:
            shutil.copy2(file, target)
            action = "COPIED"

        results.append((file.name, action, str(target)))

    return results
