import sys
import time
import subprocess

p = subprocess.Popen(
    ["/Users/harriedgemusic/Documents/repos/notebooklm-mcp/.venv/bin/python", "-m", "mcp_notebooklm"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

def send(msg):
    p.stdin.write(msg + '\n')
    p.stdin.flush()

send('{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}')
send('{"jsonrpc": "2.0", "method": "notifications/initialized"}')

print("INIT RECV: ", p.stdout.readline().strip())

send('{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "list_notebooks", "arguments": {}}}')

print("TOOL RECV 1: ", p.stdout.readline().strip())
print("TOOL RECV 2: ", p.stdout.readline().strip())
p.terminate()

out, err = p.communicate()
if err:
    print("STDERR: ", err)
