import pandas as pd
import io
from fastapi import UploadFile

async def process_excel_file(file: UploadFile):
    """Reads an Excel file and converts it to a structured JSON format."""
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))
    return df.to_dict(orient="records")  # Convert to JSON-like format
