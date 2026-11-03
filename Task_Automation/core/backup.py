import zipfile
from pathlib import Path
from datetime import datetime

EXCLUDED = {
    ".git", "__pycache__", ".venv", "venv", "backups"
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

            if relative.parts[0] == "backups":
                continue

            zip_file.write(path, relative)

    return archive
