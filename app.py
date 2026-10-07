from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


app = FastAPI(title="Task Manager")

templates = Jinja2Templates(directory="templates")


# Temporary task storage
tasks = []

next_id = 1


@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "tasks": tasks
        }
    )


@app.post("/tasks")
async def add_task(request: Request):

    global next_id

    data = await request.json()

    task_name = data.get("task")

    if not task_name:
        return {
            "error": "Task cannot be empty"
        }

    task = {
        "id": next_id,
        "name": task_name
    }

    tasks.append(task)

    next_id += 1

    return {
        "message": "Task added",
        "task": task
    }


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):

    global tasks

    tasks = [
        task
        for task in tasks
        if task["id"] != task_id
    ]

    return {
        "message": "Task deleted"
    }