import sqlite3, time

conn = sqlite3.connect("new_dns_logs.db", check_same_thread=False)
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

def log_query(client_ip, domain, ips):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    for ip in ips or ["N/A"]:
        cur.execute(
            "INSERT INTO logs (timestamp, client_ip, domain, ip) VALUES (?, ?, ?, ?)",
            (timestamp, client_ip, domain, ip)
        )
    conn.commit()
    print(f"[LOG] {timestamp} | {client_ip} | {domain} -> {ips or 'N/A'}")
def get_top_domains(ip=None, limit=10):
    """
    Return top visited domains.
    If ip is given, returns top domains for that IP.
    Otherwise, returns top domains overall.
    """
    if ip:
        cur.execute(
            """
            SELECT domain, COUNT(*) as count
            FROM logs
            WHERE client_ip = ?
            GROUP BY domain
            ORDER BY count DESC
            LIMIT ?
            """,
            (ip, limit)
        )
    else:
        cur.execute(
            """
            SELECT domain, COUNT(*) as count
            FROM logs
            GROUP BY domain
            ORDER BY count DESC
            LIMIT ?
            """,
            (limit,)
        )
    return cur.fetchall()
def get_unique_clients():
    cur.execute("SELECT DISTINCT client_ip FROM logs")
    return [row[0] for row in cur.fetchall()]

def get_client_logs(client_ip=None, limit=50):
    if client_ip:
        cur.execute("SELECT timestamp, client_ip, domain, ip FROM logs WHERE client_ip=? ORDER BY id DESC LIMIT ?", (client_ip, limit))
    else:
        cur.execute("SELECT timestamp, client_ip, domain, ip FROM logs ORDER BY id DESC LIMIT ?", (limit,))
    return cur.fetchall()
