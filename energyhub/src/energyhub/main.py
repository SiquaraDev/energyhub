from fastapi import FastAPI

app = FastAPI(title="EnergyHub", version="0.1.0")


@app.get("/")
def read_root():
    return {"message": "EnergyHub API está rodando 🚀"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
