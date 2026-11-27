import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from transformers import pipeline

MODEL_ID = "IVN-RIN/MedPsyNIT" # Define NER model
MAX_TEXT_CHARS = 5000  # protects the service from huge inputs
STRIDE = 128  # overlap (in tokens) between windows for texts > 512 tokens

# Uvicorn's logger: its messages already show up in the server output.
# On Saturday we'll set up logging properly.
logger = logging.getLogger("uvicorn.error")

# Load the model once, when the app starts.
ner = pipeline(
    "token-classification",
    model=MODEL_ID,
    aggregation_strategy="simple",
    device="cpu",
)

app = FastAPI(title="IVN-RIN NER API")


class NerRequest(BaseModel):
    # Field() adds constraints: Pydantic checks them and FastAPI returns 422
    text: str = Field(min_length=1, max_length=MAX_TEXT_CHARS)

    # Custom check that Field() can't express: reject whitespace-only text.
    # The text is returned unchanged, so entity offsets stay correct.
    @field_validator("text")
    @classmethod
    def text_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be blank")
        return value


class Entity(BaseModel):
    label: str
    text: str
    score: float
    start: int
    end: int


class NerResponse(BaseModel):
    entities: list[Entity]


@app.get("/health")
def health() -> dict:
    # Called by the load balancer / ECS to check the container is alive
    return {"status": "ok", "model": MODEL_ID}


@app.post("/ner", response_model=NerResponse)
def extract_entities(request: NerRequest) -> NerResponse:
    try:
        # stride: split long texts into overlapping 512-token windows
        results = ner(request.text, stride=STRIDE)
    except Exception:
        # Full traceback in the server log, generic message to the client
        logger.exception("NER inference failed")
        raise HTTPException(status_code=500, detail="Model inference failed")

    entities = [
        Entity(
            label=r["entity_group"],
            text=request.text[r["start"] : r["end"]],
            score=round(float(r["score"]), 4),
            start=int(r["start"]),
            end=int(r["end"]),
        )
        for r in results
    ]
    return NerResponse(entities=entities)