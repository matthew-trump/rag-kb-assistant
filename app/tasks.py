from celery import states
from celery.exceptions import Ignore

from app.celery_app import celery
from app.db import SessionLocal, engine, Base
from app.models import Run
from app.rag_chain import build_chain, retrieve, format_context
from app.schemas import Citation

# Ensure tables exist (simple approach for a skeleton; replace with migrations later)
Base.metadata.create_all(bind=engine)


@celery.task(bind=True)
def answer_question(self, run_id: str) -> dict:
    db = SessionLocal()
    try:
        run = db.get(Run, run_id)
        if not run:
            self.update_state(state=states.FAILURE, meta={"error": "run not found"})
            raise Ignore()

        run.status = "running"
        db.commit()

        docs = retrieve(run.question, k=4)
        context = format_context(docs)

        chain = build_chain()
        result = chain.invoke({"question": run.question, "context": context})

        # Build citations from retrieved docs (keep it simple and transparent)
        citations = []
        for d in docs:
            citations.append(
                Citation(
                    source=str(d.metadata.get("source", "unknown")),
                    chunk_id=str(d.metadata.get("chunk_id", "unknown")),
                    excerpt=d.page_content[:240],
                ).model_dump()
            )

        payload = {
            "answer": result.answer,
            "confidence": result.confidence,
            "citations": citations,
        }

        run.status = "completed"
        run.result_json = payload
        db.commit()

        return payload

    except Exception as exc:
        if run_id:
            run = db.get(Run, run_id)
            if run:
                run.status = "failed"
                run.error = str(exc)
                db.commit()

        self.update_state(state=states.FAILURE, meta={"error": str(exc)})
        raise
    finally:
        db.close()
