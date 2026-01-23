import socket
import json
import csv
from datetime import datetime
import ipaddress
import sys

def end_progress():
    sys.stdout.write("\n")

def print_progress(current, total, prefix=""):
    bar_length = 30
    filled = int(bar_length * current / total)
    bar = "#" * filled + "-" * (bar_length - filled)
    percent = (current / total) * 100
    sys.stdout.write(
        f"\r{prefix} [{bar}] {current}/{total} ({percent:.1f}%)"
    )
    sys.stdout.flush()
def resolve_target(target):
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        raise ValueError("Unable to resolve target hostname")
    
COMMON_SERVICES = {
    # --- File Transfer ---
    20: "FTP-DATA",
    21: "FTP",
    22: "SSH",
    69: "TFTP",
    115: "SFTP",

    # --- Remote Access ---
    23: "TELNET",
    3389: "RDP",
    5900: "VNC",
    5901: "VNC-1",
    5902: "VNC-2",
    2222: "SSH-ALT",

    # --- Email ---
    25: "SMTP",
    110: "POP3",
    143: "IMAP",
    465: "SMTPS",
    587: "SMTP-Submission",
    993: "IMAPS",
    995: "POP3S",

    # --- Web ---
    80: "HTTP",
    443: "HTTPS",
    8080: "HTTP-ALT",
    8000: "HTTP-DEV",
    8008: "HTTP-ALT",
    8443: "HTTPS-ALT",
    8888: "HTTP-ALT",

    # --- Name / Directory Services ---
    53: "DNS",
    88: "Kerberos",
    389: "LDAP",
    636: "LDAPS",
    3268: "Global-Catalog",
    3269: "Global-Catalog-SSL",

    # --- Windows / SMB ---
    135: "MSRPC",
    137: "NetBIOS-NS",
    138: "NetBIOS-DGM",
    139: "NetBIOS-SSN",
    445: "SMB",
    593: "RPC-over-HTTP",

    # --- Databases ---
    1433: "MSSQL",
    1521: "Oracle",
    1830: "Oracle-DB",
    2049: "NFS",
    2082: "cPanel",
    2083: "cPanel-SSL",
    2086: "WHM",
    2087: "WHM-SSL",
    2095: "Webmail",
    2096: "Webmail-SSL",
    3306: "MySQL",
    5432: "PostgreSQL",
    5433: "PostgreSQL-ALT",
    6379: "Redis",
    27017: "MongoDB",

    # --- Application Servers ---
    7001: "WebLogic",
    7002: "WebLogic-SSL",
    8005: "Tomcat-Shutdown",
    8009: "Tomcat-AJP",
    8081: "HTTP-ALT",
    8181: "HTTP-ALT",
    9000: "PHP-FPM",
    9042: "Cassandra",
    9200: "Elasticsearch",
    9300: "Elasticsearch-Cluster",

    # --- Monitoring / Management ---
    10000: "Webmin",
    9090: "Prometheus",
    3000: "Grafana",
    5601: "Kibana",

    # --- DevOps / Containers ---
    2375: "Docker",
    2376: "Docker-SSL",
    6443: "Kubernetes-API",
    10250: "Kubelet",
    10255: "Kubelet-RO",

    # --- VPN ---
    1194: "OpenVPN",
    500: "IPSec-IKE",
    1701: "L2TP",
    4500: "IPSec-NAT-T",

    # --- Messaging / Queues ---
    5672: "RabbitMQ",
    5671: "RabbitMQ-SSL",
    61616: "ActiveMQ",
    9092: "Kafka",

    # --- Cache / Search ---
    11211: "Memcached",
    8983: "Solr",

    # --- Version Control ---
    9418: "Git",
    3690: "Subversion",

    # --- Time / Infra ---
    123: "NTP",
    161: "SNMP",
    162: "SNMP-TRAP",

    # --- Misc ---
    179: "BGP",
    4433: "HTTPS-ALT",
    5060: "SIP",
    5061: "SIP-TLS",
}


def get_service_name(port: int) -> str:
    return COMMON_SERVICES.get(port, "Unknown")

def write_json_report(filename, target, results):
    report = {
        "target": target,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "results": results
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

def write_csv_report(filename, results):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["host", "port", "service", "banner"])
        for entry in results:
            writer.writerow([
                entry.get("host"),
                entry.get("port"),
                entry.get("service"),
                entry.get("banner")
            ])
def get_service_name(port):
    return COMMON_SERVICES.get(port, "Unknown")

def expand_target(target):
    """
    Returns a list of IP addresses.
    Supports:
    - Single IP
    - Hostname
    - CIDR range
    """
    if "/" in target:
        try:
            network = ipaddress.ip_network(target, strict=False)
            return [str(ip) for ip in network.hosts()]
        except ValueError:
            raise ValueError("Invalid CIDR notation")
    else:
        return [resolve_target(target)]
