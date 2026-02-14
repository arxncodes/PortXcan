"""
PortXcan Web UI — Glassmorphism Design System
"""


# ── Service colour classification ─────────────────
def _svc_class(service: str) -> str:
    s = service.lower()
    web = {"http", "https", "http-alt", "http-dev", "https-alt"}
    remote = {"ssh", "ssh-alt", "telnet", "rdp", "vnc", "vnc-1", "vnc-2"}
    share = {"smb", "netbios-ssn", "netbios-ns", "netbios-dgm", "msrpc", "nfs"}
    db = {"mysql", "postgresql", "postgresql-alt", "mssql", "oracle", "oracle-db",
          "mongodb", "redis", "cassandra", "elasticsearch"}
    mail = {"smtp", "pop3", "imap", "smtps", "imaps", "pop3s", "smtp-submission"}
    transfer = {"ftp", "ftp-data", "sftp", "tftp"}
    infra = {"dns", "ldap", "ldaps", "kerberos", "ntp", "snmp"}
    if s in remote:   return "svc-remote"
    if s in web:      return "svc-web"
    if s in share:    return "svc-file"
    if s in db:       return "svc-db"
    if s in mail:     return "svc-mail"
    if s in transfer: return "svc-transfer"
    if s in infra:    return "svc-infra"
    return "svc-other"


# ── Shared CSS ────────────────────────────────────
_CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',system-ui,sans-serif;background:#020617;color:#e2e8f0;
  min-height:100vh;overflow-x:hidden;line-height:1.6}

/* Background */
.bg{position:fixed;inset:0;z-index:-1;
  background:radial-gradient(ellipse at 20% 0%,rgba(37,99,235,.15) 0%,transparent 60%),
  radial-gradient(ellipse at 80% 100%,rgba(56,189,248,.1) 0%,transparent 60%),
  radial-gradient(ellipse at 50% 50%,rgba(129,140,248,.08) 0%,transparent 60%),#020617}
.orb{position:absolute;border-radius:50%;filter:blur(80px);opacity:.35;animation:drift 20s ease-in-out infinite}
.orb-1{width:500px;height:500px;background:#1d4ed8;top:-10%;left:-5%;animation-duration:28s}
.orb-2{width:350px;height:350px;background:#0ea5e9;bottom:-5%;right:-5%;animation-duration:22s;animation-delay:-7s}
.orb-3{width:250px;height:250px;background:#7c3aed;top:40%;left:45%;animation-duration:18s;animation-delay:-12s}
@keyframes drift{0%,100%{transform:translate(0,0) scale(1)}33%{transform:translate(60px,-40px) scale(1.08)}66%{transform:translate(-40px,50px) scale(.92)}}

/* Glass */
.glass{background:rgba(15,23,42,.55);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);
  border:1px solid rgba(148,163,184,.1);border-radius:20px;
  box-shadow:0 8px 32px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.04)}
.glass-sm{background:rgba(15,23,42,.35);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
  border:1px solid rgba(148,163,184,.07);border-radius:16px}

/* Nav */
nav{position:fixed;top:0;left:0;right:0;z-index:1000;height:64px;display:flex;align-items:center;
  justify-content:space-between;padding:0 36px;background:rgba(2,6,23,.75);
  backdrop-filter:blur(20px);border-bottom:1px solid rgba(56,189,248,.08)}
.logo{font-size:1.35rem;font-weight:700;letter-spacing:-.5px;
  background:linear-gradient(135deg,#38bdf8,#818cf8);-webkit-background-clip:text;
  -webkit-text-fill-color:transparent;background-clip:text}
.nav-links{display:flex;gap:28px}
.nav-links a{color:#64748b;text-decoration:none;font-weight:500;font-size:.9rem;
  transition:color .3s;position:relative}
.nav-links a::after{content:'';position:absolute;bottom:-4px;left:0;width:0;height:2px;
  background:#38bdf8;transition:width .3s}
.nav-links a:hover,.nav-links a.active{color:#e2e8f0}
.nav-links a:hover::after,.nav-links a.active::after{width:100%}

/* Layout */
.page{padding:88px 24px 40px;max-width:960px;margin:0 auto}
.center-page{display:flex;align-items:center;justify-content:center;
  min-height:calc(100vh - 64px);padding:88px 24px 40px}

/* Typography */
.grad{background:linear-gradient(135deg,#38bdf8,#818cf8);-webkit-background-clip:text;
  -webkit-text-fill-color:transparent;background-clip:text}
h1{font-size:2.2rem;font-weight:700;letter-spacing:-.5px}
.sub{color:#475569;font-size:.9rem;margin-top:6px}

/* Buttons */
.btn{display:inline-flex;align-items:center;gap:8px;padding:14px 28px;
  background:linear-gradient(135deg,rgba(37,99,235,.55),rgba(56,189,248,.55));
  backdrop-filter:blur(12px);border:1px solid rgba(56,189,248,.25);border-radius:12px;
  color:#f1f5f9;font-weight:600;font-family:'Inter',sans-serif;font-size:.95rem;
  cursor:pointer;transition:all .35s cubic-bezier(.4,0,.2,1);text-decoration:none}
.btn:hover{background:linear-gradient(135deg,rgba(37,99,235,.75),rgba(56,189,248,.75));
  box-shadow:0 0 40px rgba(56,189,248,.25),0 4px 20px rgba(0,0,0,.3);
  transform:translateY(-2px);border-color:rgba(56,189,248,.45)}
.btn-sm{padding:10px 20px;font-size:.85rem;border-radius:10px}
.btn-ghost{background:transparent;border:1px solid rgba(148,163,184,.2);color:#94a3b8}
.btn-ghost:hover{background:rgba(56,189,248,.08);border-color:rgba(56,189,248,.3);
  color:#e2e8f0;box-shadow:0 0 20px rgba(56,189,248,.1);transform:translateY(-1px)}

/* Inputs */
.gi{width:100%;padding:14px 18px;background:rgba(2,6,23,.5);
  border:1px solid rgba(148,163,184,.12);border-radius:10px;color:#e2e8f0;
  font-family:'Inter',sans-serif;font-size:.95rem;outline:none;transition:all .3s}
.gi:focus{border-color:rgba(56,189,248,.4);box-shadow:0 0 0 3px rgba(56,189,248,.08),0 0 20px rgba(56,189,248,.06)}
.gi::placeholder{color:#374151}
label{display:block;font-size:.8rem;font-weight:500;color:#64748b;
  text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px}

/* Tables */
.gt{width:100%;border-collapse:collapse}
.gt th{padding:14px 16px;text-align:left;color:#64748b;font-weight:600;font-size:.75rem;
  text-transform:uppercase;letter-spacing:1px;border-bottom:1px solid rgba(148,163,184,.1)}
.gt td{padding:14px 16px;border-bottom:1px solid rgba(148,163,184,.05);font-size:.9rem}
.gt tr{transition:background .25s}
.gt tbody tr:hover{background:rgba(56,189,248,.04)}

/* Badges & Services */
.badge{display:inline-block;padding:4px 14px;background:rgba(56,189,248,.1);
  border:1px solid rgba(56,189,248,.2);border-radius:8px;
  font-family:'JetBrains Mono',monospace;font-size:.8rem;color:#38bdf8}
.svc-remote{color:#22d3ee}.svc-web{color:#34d399}.svc-file{color:#f87171}
.svc-db{color:#a78bfa}.svc-mail{color:#fbbf24}.svc-transfer{color:#2dd4bf}
.svc-infra{color:#60a5fa}.svc-other{color:#64748b}

/* Stats */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px;margin-bottom:32px}
.sc{padding:24px;text-align:center}
.sv{font-size:2.2rem;font-weight:700}
.sl{color:#475569;font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-top:4px}

/* Progress */
.pt{width:100%;height:10px;background:rgba(15,23,42,.8);border-radius:5px;overflow:hidden;
  border:1px solid rgba(56,189,248,.08)}
.pf{height:100%;width:0%;background:linear-gradient(90deg,#2563eb,#38bdf8,#818cf8);
  background-size:200% 100%;border-radius:5px;transition:width .5s cubic-bezier(.4,0,.2,1);
  animation:shimmer 2s linear infinite}
@keyframes shimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}

/* Animations */
@keyframes fadeUp{from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:translateY(0)}}
.fu{animation:fadeUp .5s ease forwards}
.fu1{animation:fadeUp .5s ease .08s forwards;opacity:0}
.fu2{animation:fadeUp .5s ease .16s forwards;opacity:0}
.fu3{animation:fadeUp .5s ease .24s forwards;opacity:0}
.fu4{animation:fadeUp .5s ease .32s forwards;opacity:0}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
.pulse{animation:pulse 2s ease-in-out infinite}

/* Spinner */
.spin{width:40px;height:40px;margin:0 auto;border:3px solid rgba(56,189,248,.15);
  border-top-color:#38bdf8;border-radius:50%;animation:sp .8s linear infinite}
@keyframes sp{to{transform:rotate(360deg)}}

/* Footer */
footer{text-align:center;padding:32px 24px;margin-top:40px;color:#334155;
  font-size:.8rem;letter-spacing:.5px;border-top:1px solid rgba(148,163,184,.06)}
footer a{color:#475569;text-decoration:none}footer a:hover{color:#38bdf8}

/* Scrollbar */
::-webkit-scrollbar{width:8px}::-webkit-scrollbar-track{background:#0f172a}
::-webkit-scrollbar-thumb{background:#1e293b;border-radius:4px}
::-webkit-scrollbar-thumb:hover{background:#334155}

/* Responsive */
@media(max-width:640px){nav{padding:0 16px}.page,.center-page{padding-left:16px;padding-right:16px}
  h1{font-size:1.6rem}.stats{grid-template-columns:1fr 1fr}}
"""


# ── Page wrapper ──────────────────────────────────
def _page(title, body, active="home", extra_css="", extra_js=""):
    links = [("home", "/", "⚡ Home"), ("history", "/history", "📋 History")]
    nav = "".join(
        f'<a href="{h}"{" class=active" if k == active else ""}>{l}</a>'
        for k, h, l in links
    )
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>{_CSS}{extra_css}</style></head><body>
<div class="bg"><div class="orb orb-1"></div><div class="orb orb-2"></div><div class="orb orb-3"></div></div>
<nav><div class="logo">⚡ PortXcan</div><div class="nav-links">{nav}</div></nav>
{body}
<footer>Made with ❤️ by <a href="#">arxncodes</a> &bull; PortXcan v1.0</footer>
{extra_js}</body></html>"""


# ── Home page ─────────────────────────────────────
def index_page():
    body = """
<div class="center-page">
<div class="glass fu" style="padding:48px;width:100%;max-width:500px">
  <div style="text-align:center;margin-bottom:32px">
    <h1 class="grad" style="font-size:2.5rem;margin-bottom:4px">PortXcan</h1>
    <p class="sub">Advanced Network Port Scanner</p>
  </div>
  <form method="post" action="/scan" onsubmit="document.getElementById('ld').style.display='block'">
    <div style="margin-bottom:16px" class="fu1">
      <label>Target</label>
      <input class="gi" name="target" placeholder="IP / Hostname / CIDR" required>
    </div>
    <div style="display:flex;gap:12px;margin-bottom:28px" class="fu2">
      <div style="flex:1"><label>Start Port</label><input class="gi" name="start" value="1" type="number"></div>
      <div style="flex:1"><label>End Port</label><input class="gi" name="end" value="1024" type="number"></div>
    </div>
    <button type="submit" class="btn fu3" style="width:100%;justify-content:center;font-size:1rem">⚡ Start Scan</button>
  </form>
  <div id="ld" style="display:none;text-align:center;margin-top:24px">
    <div class="spin"></div>
    <p style="color:#64748b;margin-top:12px;font-size:.85rem">Initializing scan...</p>
  </div>
</div>
</div>"""
    return _page("PortXcan | Network Scanner", body, "home")


# ── Scan progress page ───────────────────────────
def progress_page(scan_id, total):
    body = f"""
<div class="center-page">
<div class="glass fu" style="padding:48px;width:100%;max-width:520px;text-align:center">
  <div class="spin" style="margin-bottom:24px"></div>
  <h2 style="margin-bottom:8px;color:#cbd5e1">Scanning in progress</h2>
  <p class="sub pulse" id="st">Initializing scan...</p>
  <div style="margin:32px 0"><div class="sv grad" id="pct" style="font-size:3.5rem">0%</div></div>
  <div class="pt" style="margin-bottom:16px"><div class="pf" id="fill"></div></div>
  <p style="color:#334155;font-size:.8rem" id="det">0 / {total} ports</p>
</div>
</div>"""

    js = """
<script>
const SID="__SID__",TOT=__TOT__;
async function poll(){try{
const r=await fetch("/progress/"+SID),d=await r.json(),
p=Math.min(100,Math.floor((d.scanned/TOT)*100));
document.getElementById("fill").style.width=p+"%";
document.getElementById("pct").textContent=p+"%";
document.getElementById("st").textContent="Scanning ports...";
document.getElementById("det").textContent=d.scanned+" / "+TOT+" ports";
if(d.done){document.getElementById("st").textContent="Complete! Redirecting...";
document.getElementById("st").classList.remove("pulse");
setTimeout(()=>window.location="/results/"+SID,800)}}catch(e){}}
setInterval(poll,800);poll();
</script>""".replace("__SID__", scan_id).replace("__TOT__", str(total))

    return _page("PortXcan | Scanning", body, "", "", js)


# ── Results page ──────────────────────────────────
def results_page(scan_id, state):
    entries = []
    for host, items in state["results"].items():
        for e in items:
            entries.append({**e, "host": host})

    total = state["total"]
    opened = len(entries)
    services = len(set(e["service"] for e in entries)) if entries else 0

    stats = f"""
<div class="stats fu">
  <div class="glass-sm sc"><div class="sv grad">{total:,}</div><div class="sl">Ports Scanned</div></div>
  <div class="glass-sm sc"><div class="sv grad">{opened}</div><div class="sl">Open Ports</div></div>
  <div class="glass-sm sc"><div class="sv grad">{services}</div><div class="sl">Services</div></div>
</div>"""

    if not entries:
        tables = '<div class="glass fu1" style="padding:40px;text-align:center"><p class="sub">No open ports detected.</p></div>'
    else:
        tables = ""
        delay = 1
        for host, items in state["results"].items():
            rows = ""
            for e in items:
                cls = _svc_class(e["service"])
                banner = e["banner"] if e["banner"] != "Not disclosed" else '<span style="color:#334155">—</span>'
                rows += f'<tr><td><span class="badge">{e["port"]}</span></td><td class="{cls}" style="font-weight:500">{e["service"]}</td><td style="color:#94a3b8">{banner}</td></tr>'
            tables += f"""
<div class="glass fu{delay}" style="padding:28px;margin-bottom:20px">
  <h2 style="margin-bottom:16px;font-size:1.1rem;color:#7dd3fc">🖥️ {host}</h2>
  <div style="overflow-x:auto"><table class="gt">
    <thead><tr><th>Port</th><th>Service</th><th>Banner</th></tr></thead>
    <tbody>{rows}</tbody></table></div>
</div>"""
            delay = min(delay + 1, 4)

    export = f"""
<div class="fu4" style="display:flex;gap:12px;flex-wrap:wrap;margin-top:24px">
  <a href="/export/json/{scan_id}" class="btn-sm btn-ghost">⬇ JSON</a>
  <a href="/export/csv/{scan_id}" class="btn-sm btn-ghost">⬇ CSV</a>
  <a href="/" class="btn-sm btn">⚡ New Scan</a>
</div>"""

    body = f"""
<div class="page">
  <h1 class="fu" style="margin-bottom:24px">Scan Results</h1>
  {stats}{tables}{export}
</div>"""
    return _page("PortXcan | Results", body, "home")


# ── History page ──────────────────────────────────
def history_page(scans):
    if not scans:
        cards = """
<div class="glass fu1" style="padding:48px;text-align:center">
  <p style="font-size:1.1rem;color:#64748b;margin-bottom:20px">No scans yet</p>
  <a href="/" class="btn">⚡ Start a Scan</a>
</div>"""
    else:
        cards = '<div style="display:grid;gap:16px">'
        delay = 1
        for s in reversed(scans):
            sid = s["id"]
            target = s.get("target", "N/A")
            ts = s.get("timestamp", "")
            ports = f'{s.get("start_port", "?")}-{s.get("end_port", "?")}'
            opened = s.get("open_count", 0)
            done = s.get("done", False)
            status = f'<span style="color:#34d399">✓ {opened} open</span>' if done else '<span class="pulse" style="color:#fbbf24">⏳ In progress</span>'
            cards += f"""
<div class="glass-sm fu{delay}" style="padding:24px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px">
  <div>
    <div style="font-weight:600;font-size:1.05rem;color:#e2e8f0;margin-bottom:4px">🎯 {target}</div>
    <div style="color:#475569;font-size:.8rem">Ports {ports} &bull; {ts}</div>
  </div>
  <div style="display:flex;align-items:center;gap:16px">
    {status}
    {'<a href="/results/'+sid+'" class="btn-sm btn-ghost">View</a>' if done else ''}
  </div>
</div>"""
            delay = min(delay + 1, 4)
        cards += "</div>"

    body = f"""
<div class="page">
  <h1 class="fu" style="margin-bottom:8px">Scan History</h1>
  <p class="sub fu" style="margin-bottom:32px">All your recent scans in one place</p>
  {cards}
</div>"""
    return _page("PortXcan | History", body, "history")
