import asyncio
import difflib
from pathlib import Path

import aiofiles
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.documents import exceptions


async def extract_document_text(file_path: Path, media_type: str) -> str:
    if media_type.startswith("text/"):
        return await extract_txt(file_path)
    elif media_type == "application/pdf":
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
        async with aiofiles.open(file_path, "r", encoding="utf-8") as file:
            text = await file.read()
    except UnicodeDecodeError as e:
        raise exceptions.DocumentDecodeError from e
    except (FileNotFoundError, PermissionError, OSError) as e:
        raise exceptions.DocumentReadError from e
    return text


def extract_pdf(file_path: Path) -> str:
    try:
        reader = PdfReader(file_path)
        parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                parts.append(text)
    except PdfReadError as e:
        raise exceptions.InvalidPdfError
    return "\n".join(parts)


def compute_text_diff(text_v1: str, text_v2: str) -> str | None:
    diff_result = list(difflib.ndiff(text_v1.splitlines(), text_v2.splitlines()))
    delta_lines = [line for line in diff_result if line.startswith(("+", "-"))]
    if delta_lines:
        return "\n".join(delta_lines)
    return None


def calculate_similarity(old_text: str, new_text: str) -> float:
    old_words = old_text.lower().split()
    new_words = new_text.lower().split()

    return difflib.SequenceMatcher(None, old_words, new_words).ratio()
