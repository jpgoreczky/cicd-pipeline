from fastapi import FastAPI

app = FastAPI(title="Automated CI/CD Pipeline API")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Automated FastAPI Deployment"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
