from flask import Flask, render_template, request, Response
import subprocess
import socket
import requests
import time

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ping")
def ping():
    target = request.args.get("target")
    mode = request.args.get("mode")
    port = request.args.get("port", type=int)

    def generate():
        while True:
            try:
                if mode == "icmp":
                    result = subprocess.run(["ping", "-c", "1", target], capture_output=True)
                    if result.returncode == 0:
                        yield f"data: {target} is reachable\n\n"
                    else:
                        yield f"data: Bitch is Down XD\n\n"

                elif mode == "tcp":
                    try:
                        sock = socket.create_connection((target, port), timeout=2)
                        sock.close()
                        yield f"data: TCP {target}:{port} is reachable\n\n"
                    except:
                        yield f"data: Bitch is Down XD\n\n"

                elif mode == "http":
                    try:
                        r = requests.get(f"http://{target}", timeout=3)
                        if r.status_code == 200:
                            yield f"data: HTTP {target} is UP (200)\n\n"
                        else:
                            yield f"data: HTTP {target} returned {r.status_code}\n\n"
                    except:
                        yield f"data: Bitch is Down XD\n\n"

                time.sleep(1)
            except GeneratorExit:
                break

    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
