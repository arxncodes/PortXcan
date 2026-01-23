import asyncio
from portxcan.utils import get_service_name


class AsyncPortScanner:
    def __init__(
        self,
        target,
        start_port,
        end_port,
        timeout=1,
        concurrency=200,
        progress_cb=None
    ):
        self.target = target
        self.start_port = start_port
        self.end_port = end_port
        self.timeout = timeout

        self.semaphore = asyncio.Semaphore(concurrency)
        self.results = []

        self.total = end_port - start_port + 1
        self.scanned = 0

        # optional progress callback (CLI or Web UI)
        self.progress_cb = progress_cb

    async def grab_banner(self, reader):
        try:
            data = await asyncio.wait_for(reader.read(1024), timeout=1)
            banner = data.decode(errors="ignore").strip()
            return banner if banner else "Not disclosed"
        except Exception:
            return "Not disclosed"

    async def scan_port(self, port):
        async with self.semaphore:
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(self.target, port),
                    timeout=self.timeout
                )

                service = get_service_name(port)

                # record open port immediately
                entry = {
                    "port": port,
                    "service": service,
                    "banner": "Not disclosed"
                }
                self.results.append(entry)

                # banner is optional
                try:
                    entry["banner"] = await self.grab_banner(reader)
                except Exception:
                    pass

                writer.close()
                await writer.wait_closed()

            except Exception:
                # port closed / filtered
                pass

            finally:
                self.scanned += 1
                if self.progress_cb:
                    try:
                        self.progress_cb(self.scanned, self.total)
                    except Exception:
                        pass


    async def run(self):
        ports = list(range(self.start_port, self.end_port + 1))

        # chunked scheduling prevents FD exhaustion on Windows
        for i in range(0, len(ports), 200):
            chunk = ports[i:i + 200]
            tasks = [self.scan_port(p) for p in chunk]
            await asyncio.gather(*tasks)

        return self.results
