from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from actions.agent_actions import scenarios  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            self._send_json(400, {"error": "Invalid JSON body"})
            return

        scenario_name = data.get("scenario")
        if not scenario_name or scenario_name not in scenarios:
            self._send_json(
                400,
                {
                    "error": f"Unknown scenario: {scenario_name}",
                    "available_scenarios": list(scenarios.keys()),
                },
            )
            return

        # Check that the OpenAI API key is configured
        openai_key = os.environ.get("OPENAI_API_KEY")
        if not openai_key or openai_key == "<OPENAI API KEY>":
            self._send_json(
                500,
                {
                    "error": (
                        "OPENAI_API_KEY is not configured. "
                        "Set it in Vercel environment variables."
                    ),
                },
            )
            return

        try:
            from run_agents import run_scenario

            run_scenario(scenario_name)

            self._send_json(
                200, {"status": "completed", "scenario": scenario_name}
            )
        except Exception as e:
            self._send_json(
                500, {"error": str(e), "scenario": scenario_name}
            )
