import struct

def parse_dns_response(data):
    """Extract IPs from DNS response (A records only)."""
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
