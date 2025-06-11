# routes/code.py
import asyncio

import httpx
from core.config import code_settings
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

code_router = APIRouter(prefix="/code", tags=["code"])

JUDGE0_URL = f"https://{code_settings.RAPIDAPI_HOST}/submissions"

LANGUAGE_MAP = {
    "python": 71,
    "javascript": 63,
    "java": 62,
    "cpp": 54,
}


class CodeIn(BaseModel):
    code: str
    language: str | int
    stdin: str | None = ""


class CodeOut(BaseModel):
    stdout: str | None
    stderr: str | None
    status: str


@code_router.post("/", response_model=CodeOut)
async def run_code(body: CodeIn):
    lang_id = (
        LANGUAGE_MAP.get(body.language.lower())
        if isinstance(body.language, str)
        else body.language
    )
    if not lang_id:
        raise HTTPException(status_code=400, detail="Unsupported language")

    headers = {
        "X-RapidAPI-Key": code_settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": code_settings.RAPIDAPI_HOST,
        "content-type": "application/json",
    }
    payload = {
        "language_id": lang_id,
        "source_code": body.code,
        "stdin": body.stdin or "",
    }

    async with httpx.AsyncClient() as client:
        create = await client.post(JUDGE0_URL, json=payload, headers=headers)
        if create.status_code >= 400:
            raise HTTPException(status_code=502, detail="Judge0 error (create)")

        token = create.json()["token"]

        while True:
            res = await client.get(f"{JUDGE0_URL}/{token}", headers=headers)
            data = res.json()
            status_id = data["status"]["id"]
            if status_id in (1, 2):
                await asyncio.sleep(1)
                continue
            break

    return CodeOut(
        stdout=data.get("stdout"),
        stderr=data.get("stderr"),
        status=data["status"]["description"],
    )
