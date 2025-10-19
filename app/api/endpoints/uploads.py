import os
import tempfile

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from app.core.file_upload import secure_file_save
from app.core.security import ENDPOINT_LIMITS, limiter

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", tempfile.gettempdir())


@router.post(
    "/upload",
    summary="Загрузить файл",
    responses={
        400: {"description": "Invalid file"},
        413: {"description": "File too large"},
        415: {"description": "Unsupported media type"},
    },
)
@limiter.limit(ENDPOINT_LIMITS.get("upload_file", "5 per minute"))
async def upload_file(request: Request, file: UploadFile = File(...)) -> dict:
    try:
        content = await file.read()

        success, result = secure_file_save(UPLOAD_DIR, file.filename, content)

        if not success:
            if "exceeds maximum size" in result:
                raise HTTPException(status_code=413, detail=result)
            elif "File type not allowed" in result:
                raise HTTPException(status_code=415, detail=result)
            else:
                raise HTTPException(status_code=400, detail=result)

        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "saved_path": result,
            "size": len(content),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
