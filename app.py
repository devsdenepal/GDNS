import asyncio, uvicorn
from modules.udp_server import udp_server
from modules.doh_server import app
from config import DOH_PORT, SSL_KEY, SSL_CERT

async def main():
    udp_task = asyncio.create_task(udp_server())

    config = uvicorn.Config(
        app, host="0.0.0.0", port=DOH_PORT, log_level="info",
        ssl_keyfile=SSL_KEY, ssl_certfile=SSL_CERT
    )
    server = uvicorn.Server(config)
    doh_task = asyncio.create_task(server.serve())

    await asyncio.gather(udp_task, doh_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")
