from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Debug server is up"}

if __name__ == "__main__":
    print("Starting minimal debug server on port 8005...")
    uvicorn.run(app, host="0.0.0.0", port=8005)
