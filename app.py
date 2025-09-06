from flask import Flask, render_template, request, Response
import subprocess, socket, requests, time, json
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ping")
def ping():
    target = request.args.get("target")
    mode = request.args.get("mode")
    port = request.args.get("port", type=int)

    # Fix HTTP scheme
    if mode == "http" and not target.startswith("http://") and not target.startswith("https://"):
        target = "http://" + target

    def generate():
        while True:
            try:
                now = datetime.now().strftime("%H:%M:%S")
                status_text = ""
                is_up = False

                if mode == "icmp":
                    result = subprocess.run(["ping", "-c", "1", target.split("//")[-1]], capture_output=True)
                    if result.returncode == 0:
                        status_text = f"{target} is reachable"
                        is_up = True
                    else:
                        status_text = "Bitch is Down XD🥶🤡"

                elif mode == "tcp":
                    try:
                        sock = socket.create_connection((target.split("//")[-1], port), timeout=2)
                        sock.close()
                        status_text = f"TCP {target}:{port} is reachable"
                        is_up = True
                    except:
                        status_text = "Bitch is Down XD🥶🤡"

                elif mode == "http":
                    try:
                        r = requests.get(target, timeout=5)
                        if r.status_code == 200:
                            status_text = f"HTTP {target} is UP (200)"
                            is_up = True
                        else:
                            status_text = f"HTTP {target} returned {r.status_code}"
                    except:
                        status_text = "Bitch is Down XD🥶🤡"

                yield f"data: {json.dumps({'time': now, 'status': status_text, 'up': is_up})}\n\n"
                time.sleep(1)
            except GeneratorExit:
                break
            except:
                yield f"data: {json.dumps({'time': now, 'status': 'Error occured', 'up': False})}\n\n"

    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
