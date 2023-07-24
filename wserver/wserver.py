from typing import List

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from helpers.get_websocket_server_settings import get_websocket_server_settings

app = FastAPI()
templates = Jinja2Templates(directory="templates")
# Mount the 'static' directory to serve static files like CSS and JavaScript
app.mount("/static", StaticFiles(directory="static"), name="static")


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("change_page.html", {"request": request})


@app.get("/change_page", response_class=HTMLResponse)
async def show_change_page(request: Request):
    return templates.TemplateResponse("change_page.html", {"request": request})


@app.post("/switch_page")
async def switch_page(request: Request, page_number: int = Form(..., gt=0)):
    # Broadcast the message with the specified page number to all active WebSocket connections
    await manager.broadcast(f"page_number_{page_number}")
    return JSONResponse(content={"message": f"Broadcast page_number_{page_number}"}, status_code=200)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data is None:
                break
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"{client_id} left the chat")


if __name__ == "__main__":
    data = get_websocket_server_settings()
    uvicorn.run(app, host=data[1], port=data[2], log_level="info")
