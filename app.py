import asyncio, uvicorn
from modules.udp_server import udp_server
from modules.doh_server import app
from config import DOH_PORT, SSL_KEY, SSL_CERT, USE_TLS

async def main():
    udp_task = asyncio.create_task(udp_server())

    ssl_kwargs = {}
    if USE_TLS:
        ssl_kwargs = {"ssl_keyfile": SSL_KEY, "ssl_certfile": SSL_CERT}

    config = uvicorn.Config(
        app, host="0.0.0.0", port=DOH_PORT, log_level="info", **ssl_kwargs
    )
    server = uvicorn.Server(config)
    doh_task = asyncio.create_task(server.serve())

    await asyncio.gather(udp_task, doh_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")