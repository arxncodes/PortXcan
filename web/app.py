from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from collections import defaultdict
import csv
import io
import uuid
import asyncio

from portxcan.async_scanner import AsyncPortScanner
from portxcan.utils import expand_target
from web.templates import index_page

app = FastAPI(title="PortXcan Web")

# ---------------------------
# In-memory scan state
# ---------------------------
SCAN_STATE = {}


# ---------------------------
# Helper: service color class
# ---------------------------
def service_class(service: str) -> str:
    s = service.lower()
    if s == "ssh":
        return "ssh"
    if s in ("http", "https"):
        return "http"
    if s in ("smb", "netbios"):
        return "smb"
    return "unknown"


# ---------------------------
# Home page
# ---------------------------
@app.get("/", response_class=HTMLResponse)
def index():
    return index_page()


# ---------------------------
# Start scan (with live progress)
# ---------------------------
@app.post("/scan", response_class=HTMLResponse)
async def start_scan(
    target: str = Form(...),
    start: int = Form(1),
    end: int = Form(1024)
):
    scan_id = str(uuid.uuid4())

    try:
        targets = expand_target(target)
    except ValueError as e:
        return HTMLResponse(f"<h3>Error: {e}</h3>")

    total_ports = len(targets) * (end - start + 1)

    SCAN_STATE[scan_id] = {
        "done": False,
        "scanned": 0,
        "total": total_ports,
        "results": defaultdict(list)
    }

    async def run_scan():
        for host in targets:
            def progress_cb(scanned, total):
                SCAN_STATE[scan_id]["scanned"] += 1

            scanner = AsyncPortScanner(
                target=host,
                start_port=start,
                end_port=end,
                timeout=1,
                progress_cb=progress_cb
            )
            results = await scanner.run()
            for r in results:
                SCAN_STATE[scan_id]["results"][host].append(r)

        SCAN_STATE[scan_id]["done"] = True

    asyncio.create_task(run_scan())

    # Progress page
    return HTMLResponse(f"""
<!DOCTYPE html>
<html>
<head>
    <title>PortXcan | Scanning</title>
    <style>
        body {{
            background: radial-gradient(circle at top, #0f172a, #020617);
            color: #e5e7eb;
            font-family: "Segoe UI", Arial;
            padding: 40px;
        }}
        .bar {{
            width: 100%;
            background: #1e293b;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 20px;
        }}
        .fill {{
            height: 20px;
            width: 0%;
            background: linear-gradient(90deg, #2563eb, #38bdf8);
            transition: width 0.4s ease;
        }}
    </style>
</head>
<body>

<h1>Scanning in progress...</h1>
<p id="status">Initializing scan...</p>

<div class="bar">
    <div class="fill" id="fill"></div>
</div>

<script>
async function poll() {{
    const res = await fetch("/progress/{scan_id}");
    const data = await res.json();

    const percent = Math.floor((data.scanned / data.total) * 100);
    document.getElementById("fill").style.width = percent + "%";
    document.getElementById("status").innerText =
        "Scanned " + data.scanned + " / " + data.total + " ports";

    if (data.done) {{
        window.location = "/results/{scan_id}";
    }}
}}

setInterval(poll, 1000);
</script>

</body>
</html>
""")

@app.get("/export/json/{scan_id}")
def export_json(scan_id: str):
    state = SCAN_STATE.get(scan_id)
    if not state:
        return JSONResponse({"error": "Invalid scan ID"}, status_code=404)

    data = []
    for host, entries in state["results"].items():
        for e in entries:
            data.append({
                "host": host,
                "port": e["port"],
                "service": e["service"],
                "banner": e["banner"]
            })

    return JSONResponse(data)

@app.get("/export/csv/{scan_id}")
def export_csv(scan_id: str):
    state = SCAN_STATE.get(scan_id)
    if not state:
        return HTMLResponse("Invalid scan ID", status_code=404)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["host", "port", "service", "banner"])

    for host, entries in state["results"].items():
        for e in entries:
            writer.writerow([
                host,
                e["port"],
                e["service"],
                e["banner"]
            ])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=portxcan_results.csv"
        }
    )

# ---------------------------
# Progress endpoint
# ---------------------------
@app.get("/progress/{scan_id}")
def progress(scan_id: str):
    return SCAN_STATE.get(scan_id, {})


# ---------------------------
# Results page
# ---------------------------
@app.get("/results/{scan_id}", response_class=HTMLResponse)
def results(scan_id: str):
    state = SCAN_STATE.get(scan_id)
    if not state:
        return HTMLResponse("<h3>Invalid scan ID</h3>")

    html = """
<!DOCTYPE html>
<html>
<head>
    <title>PortXcan | Scan Results</title>
    <style>
        body {
            background: radial-gradient(circle at top, #0f172a, #020617);
            color: #e5e7eb;
            font-family: "Segoe UI", Arial;
            padding: 30px;
        }
        h1 { color: #38bdf8; }
        .host { margin-top: 40px; color: #7dd3fc; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px; border-bottom: 1px solid #1e293b; }
        th { background: #020617; color: #93c5fd; text-align: left; }
        .badge { background: #1e293b; padding: 4px 10px; border-radius: 12px; }
        .ssh { color: #38bdf8; }
        .http { color: #22c55e; }
        .smb { color: #ef4444; }
        .unknown { color: #9ca3af; }
        a { color: #60a5fa; text-decoration: none; display: inline-block; margin-top: 30px; }
    </style>
</head>
<body>

<h1>Scan Results</h1>
"""

    if not state["results"]:
        html += "<p>No open ports detected.</p>"

    for host, entries in state["results"].items():
        html += f"<div class='host'>Host: {host}</div>"
        html += """
        <table>
            <tr>
                <th>Port</th>
                <th>Service</th>
                <th>Banner</th>
            </tr>
        """
        for e in entries:
            cls = service_class(e["service"])
            html += f"""
            <tr>
                <td><span class="badge">{e['port']}</span></td>
                <td class="{cls}">{e['service']}</td>
                <td>{e['banner']}</td>
            </tr>
            """
        html += "</table>"

    html += f"""
<div style="margin-top:30px;">
    <a href="/export/json/{scan_id}">⬇ Download JSON</a> |
    <a href="/export/csv/{scan_id}">⬇ Download CSV</a>
</div>

<a href="/">← New Scan</a>
"""
    return HTMLResponse(html)


# ---------------------------
# JSON API
# ---------------------------
@app.get("/api/scan")
async def api_scan(target: str, start: int = 1, end: int = 1024):
    targets = expand_target(target)
    all_results = []

    for host in targets:
        scanner = AsyncPortScanner(
            target=host,
            start_port=start,
            end_port=end,
            timeout=1
        )
        results = await scanner.run()
        for r in results:
            r["host"] = host
        all_results.extend(results)

    return JSONResponse(all_results)


# ---------------------------
# CSV Export
# ---------------------------
@app.get("/export/csv")
async def export_csv(target: str, start: int = 1, end: int = 1024):
    targets = expand_target(target)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["host", "port", "service", "banner"])

    for host in targets:
        scanner = AsyncPortScanner(
            target=host,
            start_port=start,
            end_port=end,
            timeout=1
        )
        results = await scanner.run()
        for r in results:
            writer.writerow([host, r["port"], r["service"], r["banner"]])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=portxcan_results.csv"}
    )
