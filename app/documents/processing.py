


import asyncio
from pathlib import Path

import aiofiles
from pypdf import PdfReader

from app.documents import exceptions


async def extract_document_text(file_path: Path, media_type: str) -> str:
    if media_type == 'text/plain':
        return await extract_txt(file_path)
    elif media_type == 'application/pdf':
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(extract_pdf, file_path),
                timeout=10,
            )
        except TimeoutError as e:
            raise exceptions.DocumentProcessingTimeoutError from e
    else:
        raise exceptions.UnsupportedDocumentTypeError(media_type)
    

async def extract_txt(file_path: Path) -> str:
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            text = await file.read()
    except UnicodeDecodeError as e:
        raise exceptions.DocumentDecodeError from e
    except (FileNotFoundError, PermissionError, OSError) as e:
        raise exceptions.DocumentReadError from e
    return text


def extract_pdf(file_path: Path) -> str:
    reader = PdfReader(file_path)
    parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    return '\n'.join(parts)