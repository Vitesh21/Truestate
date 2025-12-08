from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn
from contextlib import asynccontextmanager
# Force reload 5
try:
    from src.data_processor import load_data, get_transactions, get_filter_options
except ImportError:
    from data_processor import load_data, get_transactions, get_filter_options

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_data()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/transactions/filter-options")
def route_filter_options():
    try:
        return get_filter_options()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/transactions")
def route_transactions(
    page: int = 1,
    pageSize: int = 10,
    q: str = "",
    sortField: str = "Date",
    sortDir: str = "desc",
    filters: Optional[str] = None
):
    try:
        return get_transactions(
            page=page,
            page_size=pageSize,
            q=q,
            sort_field=sortField,
            sort_dir=sortDir,
            filters=filters
        )
    except Exception as e:
        print(f"Error processing transactions: {e}")
        return {"error": str(e), "data": [], "total": 0}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
