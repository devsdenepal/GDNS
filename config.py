import os

# Server bind address
LISTEN_ADDR = os.getenv("GDNS_LISTEN_ADDR", "0.0.0.0")

# UDP DNS port
UDP_PORT = int(os.getenv("GDNS_UDP_PORT", "5350"))

# Port for the DoH (HTTP/HTTPS) server
DOH_PORT = int(os.getenv("GDNS_DOH_PORT", "8053"))

# Set to "1" to enable HTTPS (requires certs), otherwise plain HTTP is used
USE_TLS = os.getenv("GDNS_USE_TLS", "0") == "1"

if USE_TLS:
    SSL_CERT = os.getenv("GDNS_SSL_CERT", "certs/cert.pem")
    SSL_KEY = os.getenv("GDNS_SSL_KEY", "certs/key.pem")
else:
    SSL_CERT = None
    SSL_KEY = None

# Upstream DNS-over-HTTPS provider
UPSTREAM_DOH = os.getenv("GDNS_UPSTREAM_DOH", "https://dns.google/dns-query")

# SQLite database path
DB_PATH = os.getenv("GDNS_DB_PATH", "dns_logs.db")