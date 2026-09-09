from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Cloud configuration
MIN_SERVERS = 1
MAX_SERVERS = 10

SCALE_DOWN_THRESHOLD = 30
SCALE_UP_THRESHOLD = 70

# Initial cloud state
cloud = {
    "cpu": 68,
    "servers": 4,
    "status": "ONLINE",
    "last_action": "No Scaling Required"
}


def auto_scale(cpu):
    """
    Automatically increase or decrease
    the number of cloud server instances.
    """

    if cpu > SCALE_UP_THRESHOLD:

        if cloud["servers"] < MAX_SERVERS:
            cloud["servers"] += 1
            cloud["last_action"] = "Scaled UP"
        else:
            cloud["last_action"] = "Maximum capacity reached"

    elif cpu < SCALE_DOWN_THRESHOLD:

        if cloud["servers"] > MIN_SERVERS:
            cloud["servers"] -= 1
            cloud["last_action"] = "Scaled DOWN"
        else:
            cloud["last_action"] = "Minimum capacity reached"

    else:
        cloud["last_action"] = "No Scaling Required"


@app.route("/")
def home():
    return render_template(
        "index.html",
        cpu=cloud["cpu"],
        servers=cloud["servers"]
    )


@app.route("/simulate", methods=["POST"])
def simulate():

    try:
        data = request.get_json()

        cpu = int(data.get("cpu", 0))

        # Validate CPU value
        if cpu < 0 or cpu > 100:
            return jsonify({
                "error": "CPU must be between 0 and 100"
            }), 400

        # Update CPU
        cloud["cpu"] = cpu

        # Run auto scaling
        auto_scale(cpu)

        # Determine workload
        if cpu < 30:
            workload = "Low Load"

        elif cpu <= 70:
            workload = "Normal Load"

        else:
            workload = "High Load"

        return jsonify({
            "success": True,
            "cpu": cloud["cpu"],
            "servers": cloud["servers"],
            "status": cloud["status"],
            "action": cloud["last_action"],
            "workload": workload,
            "minimum_servers": MIN_SERVERS,
            "maximum_servers": MAX_SERVERS
        })

    except (ValueError, TypeError):

        return jsonify({
            "success": False,
            "error": "Invalid CPU value"
        }), 400


@app.route("/status")
def status():

    return jsonify({
        "cpu": cloud["cpu"],
        "servers": cloud["servers"],
        "status": cloud["status"],
        "action": cloud["last_action"]
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )