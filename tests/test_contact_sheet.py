import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


SCRIPT = Path(__file__).resolve().parents[1] / 'skills/wechat-moments/scripts/contact_sheet.py'


class ContactSheetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / '照片 with spaces'
        self.source.mkdir()
        self.output = self.root / 'preview'

    def run_script(self):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(self.source), str(self.output)],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
        )

    def test_pagination_order_and_source_preservation(self):
        for i in range(19):
            Image.new('RGB', (40, 60), (i * 10, 30, 40)).save(self.source / f'{i:02}.jpg')
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.source.iterdir()}
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        records = json.loads((self.output / 'image-index.json').read_text(encoding='utf-8'))
        self.assertEqual([r['number'] for r in records], list(range(1, 20)))
        self.assertEqual([Path(r['path']).name for r in records], sorted(before))
        for page, size in [('contact-001.jpg', (1200, 1800)), ('contact-002.jpg', (1200, 300))]:
            with Image.open(self.output / page) as im:
                self.assertEqual(im.size, size)
        after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.source.iterdir()}
        self.assertEqual(before, after)

    def test_corrupt_image_is_recorded_and_other_images_survive(self):
        (self.source / 'broken.jpg').write_bytes(b'not an image')
        Image.new('RGBA', (50, 70), (0, 255, 0, 120)).save(self.source / 'transparent.png')
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        records = json.loads((self.output / 'image-index.json').read_text(encoding='utf-8'))
        self.assertIn('error', records[0])
        self.assertNotIn('error', records[1])

    def test_exif_orientation_is_applied(self):
        im = Image.new('RGB', (40, 80), 'red')
        exif = Image.Exif()
        exif[274] = 6
        im.save(self.source / 'rotated.jpg', exif=exif)
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        with Image.open(self.output / 'contact-001.jpg') as sheet:
            # Rotation produces an 80 x 40 preview centered in the first cell.
            self.assertGreater(sheet.getpixel((165, 20))[0], 200)
            self.assertLess(sheet.getpixel((165, 20))[1], 50)
            r, g, b = sheet.getpixel((200, 60))
            self.assertLess(max(r, g, b) - min(r, g, b), 10)
            self.assertGreater(g, 200)

    def test_empty_directory_fails_without_output(self):
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('No supported images', result.stderr)
        self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main()
