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

    def do_POST(self):
        self.send_header("Access-Control-Allow-Origin", "*")

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"error": "Invalid JSON body"}).encode()
            )
            return

        scenario_name = data.get("scenario")
        if not scenario_name or scenario_name not in scenarios:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            available = list(scenarios.keys())
            self.wfile.write(
                json.dumps(
                    {
                        "error": f"Unknown scenario: {scenario_name}",
                        "available_scenarios": available,
                    }
                ).encode()
            )
            return

        # Check that the OpenAI API key is configured
        openai_key = os.environ.get("OPENAI_API_KEY")
        if not openai_key or openai_key == "<OPENAI API KEY>":
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {
                        "error": (
                            "OPENAI_API_KEY is not configured. "
                            "Set it in Vercel environment variables."
                        ),
                    }
                ).encode()
            )
            return

        try:
            from run_agents import run_scenario

            run_scenario(scenario_name)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {
                        "status": "completed",
                        "scenario": scenario_name,
                    }
                ).encode()
            )
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {
                        "error": str(e),
                        "scenario": scenario_name,
                    }
                ).encode()
            )
