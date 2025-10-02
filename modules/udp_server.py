import asyncio
import socket
import aiohttp
from config import LISTEN_ADDR, UDP_PORT, UPSTREAM_DOH
from modules.dns_utils import extract_domain, parse_dns_response
from modules.db import log_query

async def handle_udp_query(loop, sock, session):
    while True:
        try:
            data, addr = await loop.sock_recvfrom(sock, 4096)
        except Exception as e:
            print(f"[ERROR] Receiving data failed: {e}")
            continue

        client_ip, _ = addr
        domain = extract_domain(data)

        try:
            headers = {"Content-Type": "application/dns-message"}
            async with session.post(UPSTREAM_DOH, data=data, headers=headers) as resp:
                if resp.status == 200:
                    answer = await resp.read()

                   
                    try:
                        await loop.sock_sendto(sock, answer, addr)
                    except ConnectionResetError:
                 
                        print(f"[WARN] Client {client_ip} disconnected before receiving answer")
                    except Exception as e:
                        print(f"[ERROR] Sending response failed: {e}")

            
                    ips = parse_dns_response(answer)
                    log_query(client_ip, domain, ips)
                else:
                    print(f"[ERROR] Upstream returned {resp.status}")
        except Exception as e:
            print(f"[ERROR] Upstream request failed: {e}")

async def udp_server():
    loop = asyncio.get_running_loop()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((LISTEN_ADDR, UDP_PORT))
    sock.setblocking(False)

    print(f"[INFO] UDP server listening on {LISTEN_ADDR}:{UDP_PORT}")

    async with aiohttp.ClientSession() as session:
        await handle_udp_query(loop, sock, session)

if __name__ == "__main__":
    try:
        asyncio.run(udp_server())
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user")
