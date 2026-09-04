from fastapi import FastAPI, Request, Form
from fastapi.responses import Response, HTMLResponse
from fastapi.templating import Jinja2Templates

import aiohttp

from config import UPSTREAM_DOH
from modules.dns_utils import extract_domain, parse_dns_response
from modules.db import (
    log_query,
    get_top_domains,
    get_unique_clients,
    get_client_logs,
)

app = FastAPI(title="GDNS - DNS-over-HTTPS")
templates = Jinja2Templates(directory="templates")

UPSTREAM_HEADERS = {"Content-Type": "application/dns-message", "Accept": "application/dns-message"}


@app.get("/", response_class=HTMLResponse)
def index_visit(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})


@app.post("/")
async def doh_endpoint(request: Request):
    client_ip = request.client.host
    data = await request.body()
    domain = extract_domain(data)

    async with aiohttp.ClientSession() as session:
        async with session.post(UPSTREAM_DOH, data=data, headers=UPSTREAM_HEADERS) as resp:
            if resp.status != 200:
                return Response(b"", status_code=502, media_type="application/dns-message")
            answer = await resp.read()
            ips = parse_dns_response(answer)
            log_query(client_ip, domain, ips)
            return Response(content=answer, media_type="application/dns-message")


@app.get("/dns-query")
async def doh_endpoint_get(request: Request):
    """RFC 8484 GET-based DoH endpoint (?dns= base64url encoded query)."""
    import base64

    client_ip = request.client.host
    b64 = request.query_params.get("dns")
    if not b64:
        return Response(b"", status_code=400, media_type="application/dns-message")
    try:
        data = base64.urlsafe_b64decode(b64 + "=" * (-len(b64) % 4))
    except Exception:
        return Response(b"", status_code=400, media_type="application/dns-message")

    domain = extract_domain(data)

    async with aiohttp.ClientSession() as session:
        async with session.post(UPSTREAM_DOH, data=data, headers=UPSTREAM_HEADERS) as resp:
            if resp.status != 200:
                return Response(b"", status_code=502, media_type="application/dns-message")
            answer = await resp.read()
            ips = parse_dns_response(answer)
            log_query(client_ip, domain, ips)
            return Response(content=answer, media_type="application/dns-message")


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_get(request: Request):
    domains = get_top_domains()                # all clients
    logs = get_client_logs(limit=100)          # recent 100 queries
    total_queries = sum(count for _, count in domains)
    unique_clients = len(get_unique_clients())
    top_domains_count = len(domains)

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "request": request,
            "domains": domains,
            "logs": logs,
            "total_queries": total_queries,
            "unique_clients": unique_clients,
            "top_domains_count": top_domains_count,
        },
    )


@app.post("/dashboard", response_class=HTMLResponse)
def dashboard_post(request: Request, client_ip: str = Form("")):
    domains = get_top_domains(client_ip if client_ip else None)
    logs = get_client_logs(client_ip if client_ip else None, limit=100)
    total_queries = sum(count for _, count in domains)
    unique_clients = len(get_unique_clients())
    top_domains_count = len(domains)

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "request": request,
            "domains": domains,
            "logs": logs,
            "total_queries": total_queries,
            "unique_clients": unique_clients,
            "top_domains_count": top_domains_count,
        },
    )