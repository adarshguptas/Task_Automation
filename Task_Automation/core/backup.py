import zipfile
from pathlib import Path, PurePosixPath
from datetime import datetime

EXCLUDED = {
    ".git", "__pycache__", ".venv",
    "venv", "backups"
}

def create_backup(project_root):
    root = Path(project_root).resolve()
    backup_dir = root / "backups"
    backup_dir.mkdir(exist_ok=True)

    filename = "TaskAutomation_" + datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    ) + ".zip"

    archive = backup_dir / filename

    with zipfile.ZipFile(
        archive, "w", zipfile.ZIP_DEFLATED
    ) as zip_file:

        for path in root.rglob("*"):
            if not path.is_file() or path == archive:
                continue

            relative = path.relative_to(root)

            if any(part in EXCLUDED for part in relative.parts):
                continue

            if "logs" in relative.parts:
                continue

            zip_file.write(path, relative)

    return archive


def restore_backup(archive, destination):
    archive = Path(archive).resolve()
    destination = Path(destination).resolve()

    if not archive.is_file():
        raise FileNotFoundError(archive)

    if destination.exists():
        if not destination.is_dir():
            raise NotADirectoryError(destination)

        if any(destination.iterdir()):
            raise FileExistsError(
                "Restore destination must be empty."
            )
    else:
        destination.mkdir(parents=True)

    with zipfile.ZipFile(archive, "r") as zip_file:
        validated = []

        for member in zip_file.infolist():
            normalized = member.filename.replace("\\", "/")
            name = PurePosixPath(normalized)

            if name.is_absolute() or ".." in name.parts:
                raise ValueError("Unsafe archive path detected.")

            if name.parts and ":" in name.parts[0]:
                raise ValueError("Invalid archive path detected.")

            target = (destination / Path(*name.parts)).resolve()

            if target != destination and destination not in target.parents:
                raise ValueError("Archive path escapes restore folder.")

            validated.append(member)

        for member in validated:
            zip_file.extract(member, destination)

    return destination
