from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="IVN-RIN MedPsyNIT API")


# 1) Simplest possible endpoint
@app.get("/")
def root():
    return {"message": "hello"}


# 2) Path parameter ({name}) + query parameter (?times=3)
@app.get("/greet/{name}")
def greet(name: str, times: int = 1):
    return {"greeting": f"Hello {name}! " * times}


# 3) Request body described with a Pydantic model
class TextRequest(BaseModel):
    text: str
    language: str = "it"  # optional, with a default value


@app.post("/echo")
def echo(request: TextRequest):
    return {"length": len(request.text), "language": request.language}