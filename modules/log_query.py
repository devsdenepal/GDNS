def log_query(client_ip, domain, ips): 
    import sqlite3
    import time
    # -------------------
    # Logging function
    # -------------------
    conn = sqlite3.connect("dns_logs.db")
    cur = conn.cursor()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    for ip in ips or ["N/A"]:
        cur.execute(
            "INSERT INTO logs (timestamp, client_ip, domain, ip) VALUES (?, ?, ?, ?)",
            (timestamp, client_ip, domain, ip)
        )
    conn.commit()
    print(f"[LOG] {timestamp} | {client_ip} | {domain} -> {ips or 'N/A'}")
