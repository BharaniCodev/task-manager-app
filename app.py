from fastapi import FastAPI, Request, Form, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from typing import Optional

app = FastAPI(title="Task Manager")
app.add_middleware(SessionMiddleware, secret_key="super-secret-key-change-in-production")

templates = Jinja2Templates(directory="templates")

# Temporary task storage
tasks = []
next_id = 1

# Simple hardcoded credentials
USER_DB = {"admin": "password123"}

def get_current_user(request: Request) -> Optional[str]:
    return request.session.get("user")

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if USER_DB.get(username) == password:
        request.session["user"] = username
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="login.html", context={"error": "Invalid credentials"})

@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"tasks": tasks, "user": user}
    )

@app.post("/tasks")
async def add_task(request: Request):
    if not get_current_user(request):
        return {"error": "Unauthorized"}
    global next_id
    data = await request.json()
    task_name = data.get("task")
    if not task_name:
        return {"error": "Task cannot be empty"}
    task = {"id": next_id, "name": task_name}
    tasks.append(task)
    next_id += 1
    return {"message": "Task added", "task": task}

@app.put("/tasks/{task_id}")
async def edit_task(task_id: int, request: Request):
    if not get_current_user(request):
        return {"error": "Unauthorized"}
    data = await request.json()
    new_name = data.get("task")
    if not new_name:
        return {"error": "Task cannot be empty"}
    for task in tasks:
        if task["id"] == task_id:
            task["name"] = new_name
            return {"message": "Task updated", "task": task}
    return {"error": "Task not found"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, request: Request):
    if not get_current_user(request):
        return {"error": "Unauthorized"}
    global tasks
    tasks = [task for task in tasks if task["id"] != task_id]
    return {"message": "Task deleted"}