from fastapi import FastAPI


app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "yeah.. maybe.. who cares.."}

