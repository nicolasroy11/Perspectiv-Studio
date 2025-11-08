from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from web.backend.routers import eval, ohlcv, eval_stats

app = FastAPI(title="LLM Trader Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # replace "*" with your client URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(eval.router, prefix="/api", tags=["Evaluation"])
app.include_router(ohlcv.router, prefix="/api", tags=["Price Data"])
app.include_router(eval_stats.router)


@app.get("/")
def root():
    return {"message": "Perspectiv LLM Trader backend is running."}


if __name__ == "__main__":
    uvicorn.run("web.backend.main:app", host="0.0.0.0", port=8000, reload=True)
