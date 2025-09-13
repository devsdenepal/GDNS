import asyncio
import socket
import struct
import sqlite3
import time
from fastapi import FastAPI, Request
from fastapi.responses import Response
import uvicorn
import aiohttp

# -------------------
# Config
# -------------------
LISTEN_ADDR = "0.0.0.0"
UDP_PORT = 5350          # For devices that use UDP
DOH_PORT = 443       # HTTPS port for DoH (use 443 in production with cert)
UPSTREAM_DOH = "https://dns.google/dns-query"  # Upstream Google DoH

# -------------------
# SQLite Setup
# -------------------
conn = sqlite3.connect("dns_logs.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    client_ip TEXT,
    domain TEXT,
    ip TEXT
)
""")
conn.commit()

# -------------------
# Helper: parse DNS response
# -------------------
def parse_dns_response(data):
    """Extract IPs from DNS response (only A records)."""
    results = []
    try:
        tid, flags, qdcount, ancount, _, _ = struct.unpack(">HHHHHH", data[:12])
        offset = 12
        while data[offset] != 0:
            offset += data[offset] + 1
        offset += 5
        for _ in range(ancount):
            offset += 2
            atype, aclass, ttl, rdlength = struct.unpack(">HHIH", data[offset:offset+10])
            offset += 10
            rdata = data[offset:offset+rdlength]
            offset += rdlength
            if atype == 1 and len(rdata) == 4:
                ip = ".".join(map(str, rdata))
                results.append(ip)
    except Exception:
        pass
    return results

def extract_domain(data):
    """Extract queried domain from DNS query."""
    domain = []
    offset = 12
    length = data[offset]
    while length > 0:
        domain.append(data[offset+1:offset+1+length].decode())
        offset += length + 1
        length = data[offset]
    return ".".join(domain)

def log_query(client_ip, domain, ips):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    for ip in ips or ["N/A"]:
        cur.execute(
            "INSERT INTO logs (timestamp, client_ip, domain, ip) VALUES (?, ?, ?, ?)",
            (timestamp, client_ip, domain, ip)
        )
    conn.commit()
    print(f"[LOG] {timestamp} | {client_ip} | {domain} -> {ips or 'N/A'}")

# -------------------
# UDP DNS server
# -------------------
async def handle_udp_query(loop, sock, session):
    while True:
        data, addr = await loop.sock_recvfrom(sock, 4096)
        client_ip, _ = addr
        domain = extract_domain(data)
        try:
            headers = {"Content-Type": "application/dns-message"}
            async with session.post(UPSTREAM_DOH, data=data, headers=headers) as resp:
                if resp.status == 200:
                    answer = await resp.read()
                    await loop.sock_sendto(sock, answer, addr)
                    ips = parse_dns_response(answer)
                    log_query(client_ip, domain, ips)
                else:
                    print(f"[ERROR] Upstream returned {resp.status}")
        except Exception as e:
            print(f"[ERROR] {e}")

async def udp_server():
    loop = asyncio.get_running_loop()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((LISTEN_ADDR, UDP_PORT))
    sock.setblocking(False)

    async with aiohttp.ClientSession() as session:
        await handle_udp_query(loop, sock, session)

# -------------------
# DoH (HTTPS) server
# -------------------
app = FastAPI()

@app.post("/")
async def doh_endpoint(request: Request):
    client_ip = request.client.host
    data = await request.body()
    domain = extract_domain(data)

    # Forward query to upstream DoH
    async with aiohttp.ClientSession() as session:
        headers = {"Content-Type": "application/dns-message"}
        async with session.post(UPSTREAM_DOH, data=data, headers=headers) as resp:
            answer = await resp.read()
            ips = parse_dns_response(answer)
            log_query(client_ip, domain, ips)
            return Response(content=answer, media_type="application/dns-message")

# -------------------
# Main runner
# -------------------
async def main():
    udp_task = asyncio.create_task(udp_server())
    # Run DoH server in background
    config = uvicorn.Config(
        app, host="192.168.1.8",
        port=DOH_PORT,
        log_level="info",
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem"
        )
    server = uvicorn.Server(config)
    doh_task = asyncio.create_task(server.serve())
    await asyncio.gather(udp_task, doh_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")
        conn.close()
