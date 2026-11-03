import unittest
import tempfile
from pathlib import Path

from core.organizer import scan_images, organize_images
from core.duplicates import find_duplicates


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


if __name__ == "__main__":
    unittest.main()
