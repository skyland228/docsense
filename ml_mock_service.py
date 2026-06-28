from pathlib import Path
import shutil
import zipfile
import requests

BACKEND_URL = "http://127.0.0.1:8000"

DOCUMENTS_DOWNLOAD_URL = f"{BACKEND_URL}/api/v1/documents/download"
DOCUMENTS_ANALYSIS_URL = f"{BACKEND_URL}/api/v1/documents/analysis"

WORK_DIR = Path("ml_mock_temp")
ZIP_PATH = WORK_DIR / "documents.zip"
EXTRACT_DIR = WORK_DIR / "documents"

def download_documents_zip() -> bool:
    WORK_DIR.mkdir(parents = True, exist_ok=True)
    response = requests.get(DOCUMENTS_DOWNLOAD_URL)
    
    if response.status_code == 404:
        print("No documents to analyze")
        return False
    
    response.raise_for_status()

    ZIP_PATH.write_bytes(response.content)
    return True

def extract_documents_zip() -> None:
    if EXTRACT_DIR.exists():
        shutil.rmtree(EXTRACT_DIR)
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_file:
        zip_file.extractall(EXTRACT_DIR)
        
def analyze_documents() -> list[dict]:
    result = []
    
    for file_path in EXTRACT_DIR.iterdir():
        if not file_path.is_file():
            continue
        text = file_path.read_text(encoding='utf-8')
        words = text.split()
        
        if words:
            topic = words[0]
        else:
            topic = 'empty'
        document_id = int(file_path.name.split("__")[0])

        result.append({
            "document_ids": [document_id],
            "topic": topic,
        })
    return result

def send_analysis_result(data: list[dict]) -> None:
    response = requests.patch(DOCUMENTS_ANALYSIS_URL,json = data)
    response.raise_for_status()
    print(response.json())
    
def main() -> None:
    is_downloaded = download_documents_zip()

    if not is_downloaded:
        return

    extract_documents_zip()
    
    analysis_result = analyze_documents()
    send_analysis_result(analysis_result)
    
if __name__ == "__main__":
    main()