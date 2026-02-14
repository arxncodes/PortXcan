from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from collections import defaultdict
import csv
import io
import uuid
import asyncio
from datetime import datetime

from portxcan.async_scanner import AsyncPortScanner
from portxcan.utils import expand_target
from web.templates import index_page, progress_page, results_page, history_page

app = FastAPI(title="PortXcan Web")

# ---------------------------
# In-memory scan state
# ---------------------------
SCAN_STATE = {}


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
        "id": scan_id,
        "done": False,
        "scanned": 0,
        "total": total_ports,
        "results": defaultdict(list),
        "target": target,
        "start_port": start,
        "end_port": end,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "open_count": 0,
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
        # Compute open port count for history
        count = sum(len(v) for v in SCAN_STATE[scan_id]["results"].values())
        SCAN_STATE[scan_id]["open_count"] = count

    asyncio.create_task(run_scan())

    return HTMLResponse(progress_page(scan_id, total_ports))


# ---------------------------
# Progress endpoint
# ---------------------------
@app.get("/progress/{scan_id}")
def progress(scan_id: str):
    state = SCAN_STATE.get(scan_id)
    if not state:
        return JSONResponse({"error": "Invalid scan ID"}, status_code=404)
    return JSONResponse({
        "scanned": state["scanned"],
        "total": state["total"],
        "done": state["done"],
    })


# ---------------------------
# Results page
# ---------------------------
@app.get("/results/{scan_id}", response_class=HTMLResponse)
def results(scan_id: str):
    state = SCAN_STATE.get(scan_id)
    if not state:
        return HTMLResponse("<h3>Invalid scan ID</h3>")
    return HTMLResponse(results_page(scan_id, state))


# ---------------------------
# History page
# ---------------------------
@app.get("/history", response_class=HTMLResponse)
def history():
    scans = list(SCAN_STATE.values())
    return HTMLResponse(history_page(scans))


# ---------------------------
# Export JSON
# ---------------------------
@app.get("/export/json/{scan_id}")
def export_json_by_id(scan_id: str):
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


# ---------------------------
# Export CSV
# ---------------------------
@app.get("/export/csv/{scan_id}")
def export_csv_by_id(scan_id: str):
    state = SCAN_STATE.get(scan_id)
    if not state:
        return HTMLResponse("Invalid scan ID", status_code=404)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["host", "port", "service", "banner"])

    for host, entries in state["results"].items():
        for e in entries:
            writer.writerow([host, e["port"], e["service"], e["banner"]])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=portxcan_results.csv"}
    )


# ---------------------------
# JSON API (standalone)
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
