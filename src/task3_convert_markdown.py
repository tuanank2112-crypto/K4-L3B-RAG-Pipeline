"""Convert only provenance-verified sources; legacy synthetic files stay excluded."""
import hashlib
import json
from pathlib import Path
import pypdf

LANDING_DIR = Path(__file__).resolve().parents[1] / 'data' / 'landing'
OUTPUT_DIR = Path(__file__).resolve().parents[1] / 'data' / 'standardized'

def write_markdown(kind: str, name: str, info: dict, content: str) -> None:
    if len(content.strip()) < 200:
        raise ValueError(f'Empty/short extraction: {name}')
    directory = OUTPUT_DIR / kind
    directory.mkdir(parents=True, exist_ok=True)
    header = (f"# {info['title']}\n\n**Source:** {info['url']}\n\n"
              f"**File:** {name}\n\n**Verified:** true\n\n"
              f"**Crawled:** {info['date_crawled']}\n\n---\n\n")
    (directory / f'{Path(name).stem}.md').write_text(header + content, encoding='utf-8')
    print(f'Converted {kind}/{name}: {len(content)} characters')

def convert_legal_docs() -> None:
    directory = LANDING_DIR / 'legal'
    manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
    for info in manifest:
        path = directory / info['filename']
        if not info.get('verified') or hashlib.sha256(path.read_bytes()).hexdigest() != info['sha256']:
            raise ValueError(f'Provenance mismatch: {path.name}')
        reader = pypdf.PdfReader(path)
        content = '\n\n'.join(f"## Page {i}\n\n{page.extract_text() or ''}" for i, page in enumerate(reader.pages, 1))
        write_markdown('legal', path.name, info, content)

def convert_news_articles() -> None:
    for path in sorted((LANDING_DIR / 'news').glob('*.json')):
        info = json.loads(path.read_text(encoding='utf-8'))
        if not info.get('verified'):
            continue
        content = info['content_markdown']
        if hashlib.sha256(content.encode()).hexdigest() != info['content_sha256']:
            raise ValueError(f'Provenance mismatch: {path.name}')
        write_markdown('news', path.name, info, content)

def convert_all() -> None:
    convert_legal_docs()
    convert_news_articles()

if __name__ == '__main__':
    convert_all()
