import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()


@app.get("/", response_class=PlainTextResponse)
def hello() -> str:
    return "Hello world"


def main() -> None:
    uvicorn.run("saury_backend.main:app", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
