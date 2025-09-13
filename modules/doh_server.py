from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import aiohttp
from config import UPSTREAM_DOH
from modules.dns_utils import extract_domain, parse_dns_response
from modules.db import *

app = FastAPI()
# Templates & static files for dashboard
templates = Jinja2Templates(directory="templates")
# app.mount("/static", StaticFiles(directory="static"), name="static")
          
@app.post("/")
async def doh_endpoint(request: Request):
    client_ip = request.client.host
    data = await request.body()
    domain = extract_domain(data)

    async with aiohttp.ClientSession() as session:
        headers = {"Content-Type": "application/dns-message"}
        async with session.post(UPSTREAM_DOH, data=data, headers=headers) as resp:
            answer = await resp.read()
            ips = parse_dns_response(answer)
            log_query(client_ip, domain, ips)
            return Response(content=answer, media_type="application/dns-message")

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_get(request: Request):
    domains = get_top_domains()         # all clients
    logs = get_client_logs(limit=100)   # recent 100 queries
    # Compute summary stats
    total_queries = sum(count for _, count in domains)
    unique_clients = len(set(log[1] for log in logs))
    top_domains_count = len(domains)

    # Render template
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "domains": domains,
            "logs": logs,
            "total_queries": total_queries,
            "unique_clients": unique_clients,
            "top_domains_count": top_domains_count
        }
    )

@app.post("/dashboard", response_class=HTMLResponse)
def dashboard_post(request: Request, client_ip: str = Form("")):
    domains = get_top_domains(client_ip if client_ip else None)
    return templates.TemplateResponse("dashboard.html", {"request": request, "domains": domains, "ip": client_ip})