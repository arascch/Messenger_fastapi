from fastapi import FastAPI , WebSocket , WebSocketDisconnect , Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory = "templates")

class ConnectionManager:
    def __init__(self):
        self.active_connection : list[WebSocket] = []

    async def connect(self , websocket:WebSocket):
        await websocket.accept()
        self.active_connection.append(websocket)

    def disconnect(self , websocket:WebSocket):
        self.active_connection.remove(websocket)

    async def broadcast(self , message:str):
        for connection in self.active_connection:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
def get_chat_page(request:Request):
    return templates.TemplateResponse(request=request,  name = "chat.html")

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket:WebSocket , username : str):
    await manager.connect(websocket)
    await manager.broadcast(f"{username} joined the chat")

    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{username}:{data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"{username} left the chat")
