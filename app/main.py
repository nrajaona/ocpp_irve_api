from fastapi import FastAPI, WebSocket
from app.api import router as api_router
from app.websocket import websocket_endpoint

app = FastAPI()

app.include_router(api_router)

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    await websocket_endpoint(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)