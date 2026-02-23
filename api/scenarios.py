from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from actions.agent_actions import scenarios, actions  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        scenario_list = []
        for name, action_names in scenarios.items():
            steps = []
            for action_name in action_names:
                if action_name in actions:
                    for step in actions[action_name]:
                        steps.append(
                            {
                                "agent": step["agent"],
                                "message": step["message"],
                            }
                        )
            scenario_list.append(
                {
                    "name": name,
                    "steps": steps,
                }
            )

        self.wfile.write(json.dumps(scenario_list, indent=2).encode())
