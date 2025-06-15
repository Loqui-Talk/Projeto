from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients = {}

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    if not username or len(username.strip()) == 0:
        await websocket.close(code=4001)
        return

    await websocket.accept()
    clients[username] = websocket
    print(f"{username} conectou.")

    try:
        while True:
            data = await websocket.receive_text()
            # Envia a mensagem para todos os outros usuários
            for user, client in clients.items():
                if client != websocket:
                    await client.send_text(data)
    except WebSocketDisconnect:
        clients.pop(username, None)
        print(f"{username} desconectou.")
