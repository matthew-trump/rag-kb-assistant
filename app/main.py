from fastapi import FastAPI, HTTPException
from celery.result import AsyncResult

from app.celery_app import celery
from app.db import SessionLocal, engine, Base
from app.models import Run
from app.schemas import AskRequest, AskResponse, RunResponse
from app.tasks import answer_question

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RAG KB Assistant")


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    db = SessionLocal()
    try:
        run = Run(question=req.question, status="queued")
        db.add(run)
        db.commit()
        db.refresh(run)

        async_result = answer_question.delay(run.id)
        return AskResponse(task_id=async_result.id, run_id=run.id)
    finally:
        db.close()


@app.get("/result/{task_id}")
def get_result(task_id: str):
    res = AsyncResult(task_id, app=celery)
    if res.state == "PENDING":
        return {"status": "pending"}
    if res.state == "STARTED":
        return {"status": "started"}
    if res.state == "FAILURE":
        return {"status": "failure", "error": str(res.info)}
    if res.state == "SUCCESS":
        return {"status": "success", "result": res.result}
    return {"status": res.state}


@app.get("/runs/{run_id}", response_model=RunResponse)
def get_run(run_id: str) -> RunResponse:
    db = SessionLocal()
    try:
        run = db.get(Run, run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        return RunResponse(
            run_id=run.id,
            status=run.status,
            question=run.question,
            result=run.result_json,
            error=run.error,
        )
    finally:
        db.close()
