"""Small end-to-end smoke test for the local server and saved demo."""
import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import ProxyHandler, build_opener

ROOT = Path(__file__).resolve().parents[1]
snapshot = json.loads((ROOT / "dist/snapshot.json").read_text())
assert len(snapshot["portfolio"]) == 18
assert len(snapshot["prices"]) == 18
assert snapshot["filings"]
assert "TCS" in snapshot["research"]
assert any(d["type"] == "annual" for d in snapshot["research"]["TCS"]["documents"])
assert any(d["type"] == "transcript" for d in snapshot["research"]["TCS"]["documents"])

proc = subprocess.Popen([sys.executable, "server.py"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
open_local = build_opener(ProxyHandler({})).open
try:
    for _ in range(30):
        try:
            with open_local("http://127.0.0.1:8008/") as response:
                assert b"The signal" in response.read()
            break
        except OSError:
            time.sleep(0.1)
    else:
        raise AssertionError("local server did not start")
    with open_local("http://127.0.0.1:8008/api/research?symbol=TCS") as response:
        data = json.load(response)
    assert data["symbol"] == "TCS"
    assert data["quarters"]["rows"]["Sales"][-1] > 0
    print("PASS: 18 prices, filings, primary document links, web page, live TCS research")
finally:
    proc.terminate()
    proc.wait(timeout=5)
