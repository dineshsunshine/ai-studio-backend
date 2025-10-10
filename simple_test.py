"""
Simple test API server - No database required!
This is a quick test to verify your FastAPI setup works.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="AI Studio Backend - Test API",
    version="1.0.0",
    description="Simple test API to verify everything works!"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory data store for testing
tasks_db = []
task_id_counter = {"value": 1}


# Pydantic models
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    created_at: datetime


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint - Welcome message"""
    return {
        "message": "🎉 Welcome to AI Studio Backend!",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "tasks": "/tasks"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "API is running perfectly! ✅"
    }


@app.get("/tasks", response_model=List[Task])
async def get_tasks():
    """Get all tasks"""
    return tasks_db


@app.post("/tasks", response_model=Task, status_code=201)
async def create_task(task: TaskCreate):
    """Create a new task"""
    new_task = Task(
        id=task_id_counter["value"],
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=datetime.now()
    )
    task_id_counter["value"] += 1
    tasks_db.append(new_task)
    return new_task


@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: int):
    """Get a specific task by ID"""
    for task in tasks_db:
        if task.id == task_id:
            return task
    return {"error": "Task not found"}


@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task_update: TaskCreate):
    """Update a task"""
    for i, task in enumerate(tasks_db):
        if task.id == task_id:
            updated_task = Task(
                id=task_id,
                title=task_update.title,
                description=task_update.description,
                completed=task_update.completed,
                created_at=task.created_at
            )
            tasks_db[i] = updated_task
            return updated_task
    return {"error": "Task not found"}


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    """Delete a task"""
    for i, task in enumerate(tasks_db):
        if task.id == task_id:
            tasks_db.pop(i)
            return {"message": f"Task {task_id} deleted successfully"}
    return {"error": "Task not found"}


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 Starting AI Studio Test API Server...")
    print("=" * 60)
    print("📍 Local URL:  http://localhost:8000")
    print("📚 API Docs:   http://localhost:8000/docs")
    print("❤️  Health:     http://localhost:8000/health")
    print("=" * 60)
    print("✨ Press Ctrl+C to stop the server\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

