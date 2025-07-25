from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pipeline import run_research_pipeline
import uvicorn

app = FastAPI()

class ResearchRequest(BaseModel):
    topic: str

@app.post("/research")
async def research_topic(req: ResearchRequest):
    try:
        output = run_research_pipeline(req.topic)
        return {
            "topic": req.topic,
            "summary_and_sources": output
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Optional: run with `python main.py`
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
