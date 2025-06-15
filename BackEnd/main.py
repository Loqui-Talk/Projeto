from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients: Dict[str, WebSocket] = {}
# ✅ Função global para enviar a lista de usuários online pra todo mundo
async def broadcast_online_users():
    user_list = list(clients.keys())
    for user, client in clients.items():
        await client.send_json({
            "type": "online-users",
            "users": user_list
        })

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    if not username or len(username.strip()) == 0:
        await websocket.close(code=4001)
        return

    await websocket.accept()
    clients[username] = websocket
    
    print(f"{username} conectou.")
    
    await broadcast_online_users()

    


    # Notifica todos (inclusive o próprio) que esse usuário entrou
    for user, client in clients.items():
        await client.send_json({"type": "user-joined", "username": username})


    try:
        while True:
            data = await websocket.receive_json()
            target = data.get("target")
            sender = username
            data["from"] = sender

            # Se for uma mensagem para alguém específico (offer, answer, candidate)
            if target and target in clients:
                await clients[target].send_json(data)
            else:
                # Mensagens de broadcast (ex: notificações)
                for user, client in clients.items():
                    if user != sender:
                        await client.send_json(data)

    except WebSocketDisconnect:
        clients.pop(username, None)
        print(f"{username} desconectou.")

        # Notifica os outros que esse usuário saiu
        for user, client in clients.items():
            await client.send_json({"type": "user-left", "username": username})
