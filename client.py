import socket
import struct
import random

SERVER = ("192.168.1.8", 5350)  # Your DNS/DoH UDP server port (must support UDP)
CLIENT_IPS = ["192.168.1.88","192.168.1.89","192.168.1.90"]  # Simulated client IPs

def build_query(domain: str):
    # Build a simple A record DNS query
    parts = domain.split(".")
    qname = b"".join([bytes([len(p)]) + p.encode() for p in parts]) + b"\x00"
    header = b"\xaa\xbb\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00"  # Transaction ID + flags + QDCOUNT=1
    question = qname + b"\x00\x01\x00\x01"  # QTYPE=A, QCLASS=IN
    return header + question

def send_query(domain: str, source_ip: str):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((source_ip, 0))  # Bind to chosen source IP, ephemeral port
    query = build_query(domain)
    sock.sendto(query, SERVER)
    
    try:
        data, _ = sock.recvfrom(4096)
    except socket.timeout:
        print(f"{source_ip} -> {domain} : Timeout")
        return
    finally:
        sock.close()
    
    # Parse DNS response
    tid, flags, qdcount, ancount, nscount, arcount = struct.unpack(">HHHHHH", data[:12])
    print(f"{source_ip} -> {domain} : {ancount} answer(s)")
    
    offset = 12
    # Skip question section
    while data[offset] != 0:
        offset += data[offset] + 1
    offset += 5  # null byte + qtype(2) + qclass(2)
    
    for i in range(ancount):
        offset += 2  # name pointer
        atype, aclass, ttl, rdlength = struct.unpack(">HHIH", data[offset:offset+10])
        offset += 10
        rdata = data[offset:offset+rdlength]
        offset += rdlength
        if atype == 1:  # A record
            ip = ".".join(map(str, rdata))
            print(f"Answer {i+1}: {ip}")

if __name__ == "__main__":
    domains = ["google.com", "youtube.com","facebook.com"]
    for domain in domains:
        # Pick a random client IP to simulate multiple clients
        src_ip = random.choice(CLIENT_IPS)
        send_query(domain, src_ip)
