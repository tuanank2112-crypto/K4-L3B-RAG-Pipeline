"""Download unmodified public VinUni policy PDFs with provenance."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DATA_DIR = Path(__file__).resolve().parents[1] / 'data' / 'landing' / 'legal'
DOCUMENTS = [
    ('academic_regulations.pdf', 'Academic Regulations for Full-Time Undergraduate Programs (2024-10-30)', 'https://policy.vinuni.edu.vn/wp-content/uploads/2023/05/VU_HT03.EN_Academic-Regulations-For-Full-Time-Undergraduate-Programs_30102024.pdf'),
    ('assessment_guidelines.pdf', 'Assessment Guidelines for Undergraduate Programs (2024-06-12)', 'https://policy.vinuni.edu.vn/wp-content/uploads/2023/05/VUNI.39_240612_Assessment-policy-for-Undergrade_CHS.pdf'),
    ('student_handbook.pdf', 'VinUni Undergraduate Student Handbook (2020 historical edition)', 'https://vinuni.edu.vn/wp-content/uploads/2020/10/201001_VinUni_Undergraduate_Student_Handbook.pdf'),
]

def fetch(url: str) -> requests.Response:
    with requests.Session() as session:
        session.mount('https://', HTTPAdapter(max_retries=Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])))
        response = session.get(url, timeout=(10, 60))
        response.raise_for_status()
        return response

def download_documents() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    for filename, title, url in DOCUMENTS:
        response = fetch(url)
        if not response.content.startswith(b'%PDF-') or len(response.content) <= 1024:
            raise ValueError(f'Invalid PDF: {filename}')
        (DATA_DIR / filename).write_bytes(response.content)
        manifest.append(dict(filename=filename, title=title, url=url, resolved_url=response.url, date_crawled=datetime.now(timezone.utc).isoformat(), sha256=hashlib.sha256(response.content).hexdigest(), bytes=len(response.content), verified=True))
        print(f'Downloaded {filename}: {len(response.content)} bytes')
    (DATA_DIR / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

if __name__ == '__main__':
    download_documents()
