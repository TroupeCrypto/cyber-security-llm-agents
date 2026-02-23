from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        response = {
            "status": "ok",
            "project": "cyber-security-llm-agents",
            "description": (
                "A collection of agents that use Large Language Models "
                "(LLMs) to perform tasks common in cyber security."
            ),
            "endpoints": {
                "/api": "Project information (this endpoint)",
                "/api/scenarios": "List available scenarios",
                "/api/run": "Run a scenario (POST)",
            },
        }
        self.wfile.write(json.dumps(response, indent=2).encode())
