"""Collect five real public service pages, preserving table text and provenance."""
import asyncio
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from bs4 import BeautifulSoup
from .task1_collect_legal_docs import fetch

DATA_DIR = Path(__file__).resolve().parents[1] / 'data' / 'landing' / 'news'
ARTICLES = [
    'https://library.vinuni.edu.vn/services/learning-services/',
    'https://library.vinuni.edu.vn/services/borrow-and-request/undergraduate-and-staff/',
    'https://library.vinuni.edu.vn/help/ask-a-librarian/',
    'https://registrar.vinuni.edu.vn/academics/policy-regulations/',
    'https://vinuni.edu.vn/student-gateway/',
]

async def crawl_article(article_data: dict) -> dict:
    response = await asyncio.to_thread(fetch, article_data['url'])
    soup = BeautifulSoup(response.content, 'html.parser')
    title_node = soup.find('h1') or soup.find('title')
    title = title_node.get_text(' ', strip=True) if title_node else ''
    body = (soup.select_one('.post-detail') or soup.select_one('.entry-content') or soup.select_one('.page-content') or soup.find('main') or soup.find('article') or soup.body)
    if not body:
        raise ValueError('Could not find article body')
    for element in body.select('script, style, nav, header, footer, form'):
        element.decompose()
    for row in body.select('tr'):
        row.replace_with(' | '.join(cell.get_text(' ', strip=True) for cell in row.select('th, td')) + '\n')
    content = body.get_text('\n', strip=True)
    if not title or len(content) < 200:
        raise ValueError('Source extraction is empty or too short')
    return dict(url=article_data['url'], resolved_url=response.url, title=title, date_crawled=datetime.now(timezone.utc).isoformat(), content_markdown=content, verified=True, response_sha256=hashlib.sha256(response.content).hexdigest(), content_sha256=hashlib.sha256(content.encode()).hexdigest())

async def crawl_all() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for index, url in enumerate(ARTICLES, 1):
        article = await crawl_article({'url': url})
        path = DATA_DIR / f'article_{index:02d}.json'
        path.write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"Collected {path.name}: {len(article['content_markdown'])} characters")

if __name__ == '__main__':
    asyncio.run(crawl_all())
