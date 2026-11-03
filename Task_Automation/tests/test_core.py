import unittest
import tempfile
import zipfile
from pathlib import Path

from core.organizer import scan_images, organize_images
from core.duplicates import find_duplicates
from core.backup import create_backup, restore_backup


class TestTaskAutomation(unittest.TestCase):

    def test_scan_images(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "photo.jpg").write_bytes(b"image")
            (root / "notes.txt").write_text("test")

            self.assertEqual(len(scan_images(root)), 1)

    def test_copy_images(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source"
            destination = root / "destination"
            source.mkdir()

            original = source / "photo.png"
            original.write_bytes(b"image-data")

            result = organize_images(source, destination)

            self.assertEqual(len(result), 1)
            self.assertTrue(original.exists())
            self.assertTrue((destination / "photo.png").exists())

    def test_duplicate_detection(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "a.txt").write_text("same content")
            (root / "b.txt").write_text("same content")

            duplicates = find_duplicates(root)
            self.assertEqual(len(duplicates), 1)

    def test_backup_and_restore(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "project"
            root.mkdir()
            (root / "main.py").write_text("print('hello')")

            archive = create_backup(root)
            destination = Path(temp) / "restored"

            restore_backup(archive, destination)

            self.assertTrue(
                (destination / "main.py").exists()
            )

    def test_restore_rejects_unsafe_path(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / "unsafe.zip"

            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("../outside.txt", "unsafe")

            destination = root / "restore"
            destination.mkdir()

            with self.assertRaises(ValueError):
                restore_backup(archive, destination)


if __name__ == "__main__":
    unittest.main()
