
from pathlib import Path
from uuid import uuid4
import math

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile

from loader import load_dataset
from profiler import profile_dataset
from analyzer import analyze_dataset
from visualizer import generate_charts


# Project folders
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
CHART_DIR = BASE_DIR / "charts"

UPLOAD_DIR.mkdir(exist_ok=True)
CHART_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="AI Data Intelligence Agent",
    description="Upload datasets for automatic profiling, analysis, and chart generation.",
    version="1.0.0",
)


def make_json_safe(value):
    """Convert analysis results into JSON-compatible values."""

    if isinstance(value, dict):
        return {
            str(key): make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [make_json_safe(item) for item in value]

    if hasattr(value, "item"):
        return make_json_safe(value.item())

    if isinstance(value, float) and not math.isfinite(value):
        return None

    return value


@app.get("/")
def home():
    return {
        "message": "AI Data Intelligence Agent is running!",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/analyze")
async def analyze_uploaded_dataset(file: UploadFile = File(...)):
    """Upload a CSV or Excel file and automatically analyze it."""

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please select a file.",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in [".csv", ".xlsx", ".xls"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file. Please upload CSV or Excel.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File is too large. Maximum size is 20 MB.",
        )

    upload_id = uuid4().hex
    saved_file = UPLOAD_DIR / f"{upload_id}{extension}"
    chart_folder = CHART_DIR / upload_id

    try:
        saved_file.write_bytes(content)

        # 1. Load the uploaded dataset
        df = load_dataset(str(saved_file))

        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="The uploaded dataset contains no rows.",
            )

        # 2. Profile the dataset
        profile = profile_dataset(df)

        # 3. Analyze patterns and outliers
        analysis = analyze_dataset(df)

        # 4. Generate charts
        chart_files = generate_charts(
            df,
            output_dir=str(chart_folder),
        )

        # Return one combined report
        return make_json_safe({
            "message": "Dataset analyzed successfully.",
            "filename": Path(file.filename).name,
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "profile": profile,
            "analysis": analysis,
            "charts": [
                str(Path(path).relative_to(BASE_DIR)).replace("\\", "/")
                for path in chart_files
            ],
        })

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Could not analyze the dataset: {error}",
        ) from error

    finally:
        await file.close()
        saved_file.unlink(missing_ok=True)
