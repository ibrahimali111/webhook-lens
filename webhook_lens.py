#!/usr/bin/env python3
"""
webhook-lens
Zero-dependency local webhook catcher and HTTP request inspector.
Pretty-prints incoming webhook requests, headers, and JSON payloads with colored terminal formatting.
"""

import sys
import os
import json
import time
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ANSI Terminal Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

HISTORY_FILE = "webhooks_history.json"


def save_to_history(entry):
    """Save received webhook payload to a local history JSON file."""
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []
            
    history.append(entry)
    # Keep last 100 requests
    if len(history) > 100:
        history = history[-100:]
        
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"{YELLOW}[!] Failed to write to {HISTORY_FILE}: {e}{RESET}")


class WebhookHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(204)

    def handle_request(self, method):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length) if content_length > 0 else b""
        body_str = body_bytes.decode("utf-8", errors="replace")

        # Try parsing JSON
        is_json = False
        parsed_json = None
        if body_str:
            try:
                parsed_json = json.loads(body_str)
                is_json = True
            except Exception:
                is_json = False

        # Format Headers
        headers_dict = {k: v for k, v in self.headers.items()}

        # Print Visual Card
        print(f"\n{BOLD}{MAGENTA}┌─────────────────────────────────────────────────────────────{RESET}")
        print(f"{BOLD}{MAGENTA}│{RESET} {BOLD}{GREEN}{method:<6}{RESET} {BOLD}{self.path}{RESET}")
        print(f"{BOLD}{MAGENTA}│{RESET} {DIM}Time:{RESET}   {timestamp} | {DIM}Client:{RESET} {self.client_address[0]}")
        
        if query_params:
            print(f"{BOLD}{MAGENTA}├─ {YELLOW}Query Parameters:{RESET}")
            for k, v in query_params.items():
                print(f"{BOLD}{MAGENTA}│{RESET}   {CYAN}{k}{RESET}: {v if len(v) > 1 else v[0]}")

        print(f"{BOLD}{MAGENTA}├─ {YELLOW}Headers:{RESET}")
        for k, v in headers_dict.items():
            print(f"{BOLD}{MAGENTA}│{RESET}   {CYAN}{k}{RESET}: {v}")

        print(f"{BOLD}{MAGENTA}├─ {YELLOW}Payload ({content_length} bytes):{RESET}")
        if is_json:
            formatted_json = json.dumps(parsed_json, indent=2)
            for line in formatted_json.splitlines():
                print(f"{BOLD}{MAGENTA}│{RESET}   {line}")
        elif body_str:
            for line in body_str.splitlines():
                print(f"{BOLD}{MAGENTA}│{RESET}   {line}")
        else:
            print(f"{BOLD}{MAGENTA}│{RESET}   {DIM}(empty body){RESET}")

        print(f"{BOLD}{MAGENTA}└─────────────────────────────────────────────────────────────{RESET}\n")

        # Save to history file
        save_to_history({
            "timestamp": timestamp,
            "method": method,
            "path": path,
            "query": query_params,
            "headers": headers_dict,
            "body": parsed_json if is_json else body_str
        })

        # Respond to webhook sender
        self._set_headers(200)
        response_payload = {
            "status": "success",
            "message": "Webhook captured by webhook-lens",
            "timestamp": timestamp
        }
        self.wfile.write(json.dumps(response_payload).encode("utf-8"))

    def do_GET(self):
        self.handle_request("GET")

    def do_POST(self):
        self.handle_request("POST")

    def do_PUT(self):
        self.handle_request("PUT")

    def do_DELETE(self):
        self.handle_request("DELETE")

    def do_PATCH(self):
        self.handle_request("PATCH")

    def log_message(self, format, *args):
        # Suppress standard http.server log lines to keep terminal clean
        return


def replay_webhooks(target_url):
    """Replay captured requests from history to a target URL."""
    import urllib.request
    
    if not os.path.exists(HISTORY_FILE):
        print(f"{RED}[!] No history file found at {HISTORY_FILE}.{RESET}")
        sys.exit(1)
        
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    except Exception as e:
        print(f"{RED}[!] Failed to read {HISTORY_FILE}: {e}{RESET}")
        sys.exit(1)
        
    if not history:
        print(f"{YELLOW}[!] History file is empty.{RESET}")
        sys.exit(0)
        
    print(f"\n{BOLD}{CYAN}Replaying last webhook to: {target_url}{RESET}")
    last_req = history[-1]
    
    body = last_req.get("body")
    payload = json.dumps(body).encode("utf-8") if isinstance(body, (dict, list)) else (body or "").encode("utf-8")
    
    req = urllib.request.Request(
        target_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method=last_req.get("method", "POST")
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            print(f"{GREEN}[✓] Replay successful! Status: {res.getcode()}{RESET}\n")
    except Exception as e:
        print(f"{RED}[!] Replay failed: {e}{RESET}\n")


def main():
    parser = argparse.ArgumentParser(
        description="webhook-lens: Zero-dependency local webhook catcher and HTTP request inspector."
    )
    parser.add_argument("-p", "--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("-b", "--bind", type=str, default="0.0.0.0", help="Address to bind to (default: 0.0.0.0)")
    parser.add_argument("--replay", type=str, metavar="URL", help="Replay the last captured webhook to a target URL")

    args = parser.parse_args()

    if args.replay:
        replay_webhooks(args.replay)
        return

    print(f"\n{BOLD}{CYAN}======================================================={RESET}")
    print(f"{BOLD}{CYAN}   🔍 webhook-lens: Local Webhook & API Inspector      {RESET}")
    print(f"{BOLD}{CYAN}======================================================={RESET}")
    print(f"📡 Listening for webhooks on: {BOLD}http://{args.bind}:{args.port}{RESET}")
    print(f"📁 Saving requests to:        {BOLD}{HISTORY_FILE}{RESET}")
    print(f"{DIM}Press Ctrl+C to stop.{RESET}\n")

    server = HTTPServer((args.bind, args.port), WebhookHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n{CYAN}[*] Shutting down webhook-lens server.{RESET}")
        server.server_close()


if __name__ == "__main__":
    main()
