from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routes.pojects import router as projectrouter

app = FastAPI()

app.include_router(projectrouter,tags=["project"])

# Allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Include routers


# Test endpoint
@app.get("/")
async def main():
    return {"message": "Hello World"}

# Run application
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
