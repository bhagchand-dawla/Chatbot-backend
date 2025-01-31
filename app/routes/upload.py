from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.file_processor import process_excel_file
from app.services.database import insert_data, cache_data

router = APIRouter()

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        data = await process_excel_file(file)
        insert_result = await insert_data(data)  # Store in MongoDB
        await cache_data("latest_excel_data", data)  # Cache in Redis

        return {"message": "File uploaded successfully", "inserted_count": len(insert_result.inserted_ids)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
