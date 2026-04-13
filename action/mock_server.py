from fastapi import FastAPI

app = FastAPI()

@app.post("/alert")
def alert(data: dict):
    print(" ALERT RECEIVED:", data)
    return {"status": "ok"}
