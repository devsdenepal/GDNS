# GDNS

GDNS is a modern, asynchronous DNS resolver server supporting both traditional **UDP DNS** and **DNS-over-HTTPS (DoH)**. It is designed for local network deployment, forwarding DNS queries securely to an upstream DoH provider, logging all queries, and providing a browser-based analytics dashboard.

## Features

- **UDP DNS Server:** Receives standard DNS queries on a configurable UDP port.
- **DNS-over-HTTPS (DoH) Server:** Provides an RFC 8484-compliant DoH endpoint (POST and GET) using FastAPI and Uvicorn.
- **Query Logging:** Logs all DNS queries (domain, client IP, resolved IPs) to an SQLite database.
- **Analytics Dashboard:** Web-based dashboard to view most queried domains, recent queries, client stats, and a chart.
- **TLS/HTTPS Support:** Runs the DoH server over HTTPS with configurable certificates; falls back to HTTP for quick local testing.
- **Modular Codebase:** Clean separation of UDP, DoH, database, and utility modules.
- **Asynchronous and Concurrent:** Built on `asyncio` to handle many clients efficiently.

## Use Cases

- **Home/Office Network Privacy:** Route all DNS queries through GDNS for encrypted, logged, and auditable resolution.
- **Educational Labs:** Monitor DNS usage and analyze domain access patterns.
- **DNS Query Auditing:** Gain insights into network DNS behavior for security or parental control.

## Setup

### Prerequisites

- Python 3.8+

### Installation

```bash
git clone https://github.com/devsdenepal/GDNS.git
cd GDNS
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

All settings can be overridden with environment variables (see `config.py`):

| Env var            | Default                       | Description                          |
| ------------------ | ----------------------------- | ------------------------------------ |
| `GDNS_LISTEN_ADDR` | `0.0.0.0`                     | Address to bind                       |
| `GDNS_UDP_PORT`    | `5350`                        | UDP DNS port                         |
| `GDNS_DOH_PORT`    | `8053`                        | DoH HTTP/HTTPS port                  |
| `GDNS_USE_TLS`     | `0`                           | Set to `1` to enable HTTPS           |
| `GDNS_SSL_CERT`    | `certs/cert.pem`              | Path to your SSL certificate          |
| `GDNS_SSL_KEY`     | `certs/key.pem`               | Path to your SSL key                 |
| `GDNS_UPSTREAM_DOH`| `https://dns.google/dns-query`| Upstream DoH provider                |
| `GDNS_DB_PATH`     | `dns_logs.db`                 | SQLite database path                 |

### Running GDNS

Start both servers (UDP and DoH):

```bash
python app.py
```

- The UDP DNS server listens on `GDNS_LISTEN_ADDR:GDNS_UDP_PORT`.
- The DoH server (FastAPI) listens on `GDNS_LISTEN_ADDR:GDNS_DOH_PORT`.

By default the dashboard runs over **HTTP** for quick local testing:

```text
http://<your-server-ip>:8053/dashboard
```

Point a DNS client (or your router's DNS settings) at `UDP_PORT` (`5350`) to start collecting queries.

### Enabling HTTPS

1. Provide your own `cert.pem`/`key.pem`, or generate self-signed ones:

   ```bash
   openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
   # requires the certs to be at certs/cert.pem and certs/key.pem, or set GDNS_SSL_CERT/KEY
   ```

2. Start with TLS enabled:

   ```bash
   GDNS_USE_TLS=1 python app.py    # Linux/macOS
   $env:GDNS_USE_TLS="1"; python app.py   # PowerShell
   ```

### Accessing the Dashboard

Visit `http://<your-server-ip>:8053/dashboard` (or `https://...` when TLS is enabled) in your browser to view DNS query analytics.

## Testing

Send a test DNS query over UDP using `client.py` (adjust `SERVER` and source IPs in the file):

```bash
python client.py
```

The dashboard should then show the queried domains, recent queries, and top-domain stats.

## Directory Structure

```
app.py                # Main entrypoint, starts UDP and DoH servers
config.py             # Configuration variables (env-var overridable)
client.py             # Simple UDP DNS test client
requirements.txt      # Python dependencies
modules/
  udp_server.py       # UDP DNS server logic
  doh_server.py       # DoH server logic and dashboard endpoints
  dns_utils.py        # DNS packet parsing utilities
  db.py               # Database logging and analytics
templates/
  index.html          # Landing page
  dashboard.html      # Dashboard page
  partials/           # Reusable dashboard sections
```

## Security Notice

- For production use, **provide your own SSL certificate and key** for HTTPS.
- Make sure to restrict access to the dashboard and database files in sensitive environments.
- Allow only trusted clients to query the UDP port if it is exposed beyond a trusted network.

## License

MIT License. See [LICENSE](LICENSE) for full details.

---

**Contributions and feedback welcome!**