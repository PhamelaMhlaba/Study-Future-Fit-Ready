from fastapi import FastAPI

app = FastAPI(title="Study Future Fit API")


@app.get("/")
def root():
    return {"message": "Study Future Fit API is running!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}