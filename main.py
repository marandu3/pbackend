from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from routes.profile import router as profile_router
from routes.education import router as education_router
from routes.skill import router as skill_router
from routes.timeline import router as timeline_router
from routes.project import router as project_router
from routes.user import router as user_router

app = FastAPI()

# Allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Include routers
app.include_router(profile_router, tags=["profile"])
app.include_router(education_router, tags=["education"])
app.include_router(skill_router, tags=["skills"])
app.include_router(timeline_router, tags=["timeline"])
app.include_router(project_router, tags=["projects"])
app.include_router(user_router, tags=["user"])

# Test endpoint
@app.get("/")
async def main():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
