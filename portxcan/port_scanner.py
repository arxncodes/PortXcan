import socket
import threading
from queue import Queue
from portxcan.utils import get_service_name, print_progress, end_progress

class PortScanner:
    def __init__(self, target, start_port, end_port, threads=100, timeout=1):
        self.target = target
        self.start_port = start_port
        self.end_port = end_port
        self.threads = threads
        self.timeout = timeout
        self.queue = Queue()
        self.lock = threading.Lock()
        self.results = []
        self.scanned = 0
        self.total = end_port - start_port + 1

    def grab_banner(self, sock):
        try:
            sock.settimeout(1)
            banner = sock.recv(1024).decode(errors="ignore").strip()
            return banner if banner else "Not disclosed"
        except:
            return "Not disclosed"

    def scan_port(self, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                if sock.connect_ex((self.target, port)) == 0:
                    service = get_service_name(port)
                    banner = self.grab_banner(sock)
                    with self.lock:
                        self.results.append({
                            "port": port,
                            "service": service,
                            "banner": banner
                        })
                        print(
                            f"\n[OPEN] {self.target}:{port} | {service} | {banner}"
                        )
        finally:
            with self.lock:
                self.scanned += 1
                print_progress(self.scanned, self.total, f"Scanning {self.target}")

    def worker(self):
        while not self.queue.empty():
            port = self.queue.get()
            self.scan_port(port)
            self.queue.task_done()

    def run(self):
        for port in range(self.start_port, self.end_port + 1):
            self.queue.put(port)

        for _ in range(self.threads):
            t = threading.Thread(target=self.worker, daemon=True)
            t.start()

        self.queue.join()
        end_progress()
        return self.results
