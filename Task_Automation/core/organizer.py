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
    return sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )

def organize_images(source, destination, move=False, progress=None):
    source = Path(source)
    destination = Path(destination)

    if not source.is_dir():
        raise FileNotFoundError(source)

    destination.mkdir(parents=True, exist_ok=True)
    files = scan_images(source)
    results = []

    for index, file in enumerate(files, 1):
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

        if progress:
            progress(index, len(files), file.name)

    return results
