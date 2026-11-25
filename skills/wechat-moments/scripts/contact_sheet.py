"""Create numbered photo previews without changing source images. Requires Pillow."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if not args.source.is_dir():
        parser.error('Source must be an existing directory')
    files = sorted((p for p in args.source.iterdir() if p.is_file() and
                    p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff'}),
                   key=lambda p: p.name.casefold())
    if not files:
        parser.error('No supported images found')
    args.output.mkdir(parents=True, exist_ok=True)
    records = []
    for start in range(0, len(files), 18):
        batch = files[start:start + 18]
        sheet = Image.new('RGB', (1200, ((len(batch) + 2) // 3) * 300), '#eeeeee')
        draw = ImageDraw.Draw(sheet)
        for offset, path in enumerate(batch):
            number = start + offset + 1
            x, y = (offset % 3) * 400, (offset // 3) * 300
            record = {'number': number, 'path': str(path.resolve())}
            try:
                with Image.open(path) as source:
                    record['size'] = list(source.size)
                    preview = ImageOps.exif_transpose(source).convert('RGBA')
                    preview.thumbnail((380, 260))
                    sheet.paste(preview, (x + (400 - preview.width) // 2, y), preview)
                label = f"{number:03d} | {record['size'][0]} x {record['size'][1]}"
            except Exception as error:
                record['error'] = str(error)
                label = f'{number:03d} | unreadable image'
            records.append(record)
            draw.text((x + 10, y + 270), label, fill='black')
        target = args.output / f'contact-{start // 18 + 1:03d}.jpg'
        sheet.save(target, quality=90)
        print(target.resolve())
    mapping = args.output / 'image-index.json'
    mapping.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    print(mapping.resolve())


if __name__ == '__main__':
    main()
