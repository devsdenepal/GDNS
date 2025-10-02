
<img width="1366" height="2144" alt="screencapture-192-168-1-8-dashboard-2025-09-13-22_52_08" src="https://github.com/user-attachments/assets/4bbb8116-9a9f-493c-9909-11da4d052a25" />
# GDNS

GDNS is a modern, asynchronous DNS resolver server supporting both traditional UDP-based DNS and DNS-over-HTTPS (DoH). It is designed for local network deployment, forwarding DNS queries securely to an upstream DoH provider, logging all queries, and providing a browser-based analytics dashboard.

## Features

- **UDP DNS Server:** Receives standard DNS queries on a configurable UDP port.
- **DNS-over-HTTPS (DoH) Server:** Provides an RFC 8484-compliant DoH endpoint using FastAPI and Uvicorn.
- **Query Logging:** Logs all DNS queries (domain, client IP, resolved IPs) to an SQLite database.
- **Analytics Dashboard:** Web-based dashboard to view most queried domains, recent queries, and client statistics.
- **TLS/HTTPS Support:** Runs the DoH server over HTTPS with configurable certificates.
- **Modular Codebase:** Clean separation of UDP, DoH, database, and utility modules.
- **Asynchronous and Concurrent:** Built on `asyncio` to handle many clients efficiently.

## Use Cases

- **Home/Office Network Privacy:** Route all DNS queries through GDNS for encrypted, logged, and auditable resolution.
- **Educational Labs:** Monitor DNS usage and analyze domain access patterns.
- **DNS Query Auditing:** Gain insights into network DNS behavior for security or parental control.

## Setup

### Prerequisites

- Python 3.8+
- (Optional) TLS certificate and key files (`cert.pem`, `key.pem`)

### Installation

Clone the repository:

```bash
git clone https://github.com/devsdenepal/GDNS.git
cd GDNS
```

Install requirements:

```bash
pip install -r requirements.txt
```

### Configuration

Edit `config.py` to set your desired listen address, ports, DoH upstream, and TLS certificates.

```python
LISTEN_ADDR = "0.0.0.0"           # Listen on all interfaces
UDP_PORT = 5350                   # UDP DNS port
DOH_PORT = 443                    # HTTPS port for DoH
UPSTREAM_DOH = "https://dns.google/dns-query"
SSL_CERT = "cert.pem"             # Path to your SSL certificate
SSL_KEY = "key.pem"               # Path to your SSL key
```

### Running GDNS

Start both servers (UDP and DoH) with:

```bash
python app.py
```

- The UDP DNS server listens on `LISTEN_ADDR:UDP_PORT`.
- The DoH server (FastAPI) listens on HTTPS `LISTEN_ADDR:DOH_PORT`.

### Accessing the Dashboard

Visit `https://<your-server-ip>/dashboard` in your browser to view DNS query analytics.

## Directory Structure

```
app.py                # Main entrypoint, starts UDP and DoH servers
config.py             # Configuration variables
modules/
  udp_server.py       # UDP DNS server logic
  doh_server.py       # DoH server logic and dashboard endpoints
  dns_utils.py        # DNS packet parsing utilities (not shown here)
  db.py               # Database logging and analytics (not shown here)
templates/
  dashboard.html      # HTML template for dashboard
```

## Security Notice

- For production use, **provide your own SSL certificate and key** for HTTPS.
- Make sure to restrict access to the dashboard and database files in sensitive environments.

## License

MIT License. See [LICENSE](LICENSE) for full details.

---

**Contributions and feedback welcome!**
