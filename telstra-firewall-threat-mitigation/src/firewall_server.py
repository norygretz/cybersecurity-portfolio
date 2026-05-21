#!/usr/bin/env python3
"""
Apache Log4j2 Vulnerability Firewall Mitigation Server
=========================================================

This module implements a firewall server that detects and blocks requests
containing the CVE-2021-44228 (Log4Shell) exploitation payload targeting
Apache Tomcat and Spring Framework environments.

The vulnerability allows remote code execution (RCE) through JNDI injection
via specially crafted HTTP headers and request parameters.

Usage:
    python firewall_server.py
    
    Then test with:
    python test_client.py
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
from typing import Dict, Any

# Configure logging for security audit trail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Server configuration
HOST = "localhost"
PORT = 8000

# Malicious payload signatures known to exploit Log4j2 RCE
ATTACK_SIGNATURES = {
    "suffix": "%>//",
    "c1": "Runtime",
    "c2": "<%",
    "DNT": "1",
    "Content-Type": "application/x-www-form-urlencoded",
}

# Vulnerable Spring Framework endpoint
VULNERABLE_ENDPOINT = "/tomcatwar.jsp"


class FirewallHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler that implements Log4j2 RCE mitigation.
    
    This handler intercepts HTTP requests and analyzes headers and request
    body for known exploitation signatures. Malicious requests are blocked
    with a 403 Forbidden response.
    """

    def do_GET(self) -> None:
        """Handle GET requests."""
        self._handle_request()

    def do_POST(self) -> None:
        """Handle POST requests."""
        self._handle_request()

    def _handle_request(self) -> None:
        """
        Core firewall logic: analyze request and block if attack detected.
        
        Detection Strategy:
        1. Check if request targets vulnerable endpoint (/tomcatwar.jsp)
        2. Iterate through known attack signatures
        3. Match signature headers against request headers
        4. Block request if all attack signature headers detected
        """
        client_ip = self.client_address[0]
        logger.info(f"Incoming request from IP: {client_ip}")
        logger.info(f"Request path: {self.path}")
        logger.info(f"Request headers: {dict(self.headers)}")

        # Check if request targets vulnerable endpoint
        if self.path == VULNERABLE_ENDPOINT:
            logger.warning(f"Request to vulnerable endpoint detected: {self.path}")
            
            # Check for attack signatures in request headers
            attack_detected = self._detect_attack_headers()
            
            if attack_detected:
                logger.critical(f"Log4j2 RCE attack blocked from IP: {client_ip}")
                self._send_blocked_response()
                return

        # Request passed all security checks
        logger.info("Request allowed through firewall")
        self._send_success_response()

    def _detect_attack_headers(self) -> bool:
        """
        Detect if request contains all required attack signature headers.
        
        Returns:
            bool: True if attack signatures detected, False otherwise
        """
        for signature_header, signature_value in ATTACK_SIGNATURES.items():
            if signature_header in self.headers:
                if self.headers[signature_header] == signature_value:
                    logger.debug(
                        f"Attack signature detected - {signature_header}: "
                        f"{signature_value}"
                    )
                    continue
            else:
                # Missing signature header, not a complete attack
                return False
        
        # All attack signatures detected
        return True

    def _send_blocked_response(self) -> None:
        """Send 403 Forbidden response for blocked requests."""
        response_body = {
            "status": "blocked",
            "message": "Request blocked by WAF",
            "reason": "Potential Log4j2 RCE attack detected",
            "timestamp": str(__import__('datetime').datetime.utcnow())
        }
        
        self.send_response(403)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps(response_body, indent=2).encode('utf-8')
        )

    def _send_success_response(self) -> None:
        """Send 200 OK response for allowed requests."""
        response_body = {
            "status": "allowed",
            "message": "Request passed security checks",
            "timestamp": str(__import__('datetime').datetime.utcnow())
        }
        
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps(response_body, indent=2).encode('utf-8')
        )

    def log_message(self, format, *args):
        """Suppress default HTTP server logging."""
        pass


def start_firewall_server() -> None:
    """
    Initialize and start the firewall server.
    
    The server listens on localhost:8000 and blocks requests containing
    Log4j2 RCE exploitation signatures.
    """
    server = HTTPServer((HOST, PORT), FirewallHandler)
    server_address = f"{HOST}:{PORT}"
    
    print("=" * 70)
    print("Log4j2 RCE Firewall Server")
    print("=" * 70)
    print(f"[+] Server starting on http://{server_address}")
    print(f"[+] Vulnerable endpoint protection: {VULNERABLE_ENDPOINT}")
    print(f"[+] Attack signatures being monitored: {len(ATTACK_SIGNATURES)}")
    print("[+] Press Ctrl+C to stop the server")
    print("=" * 70)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[+] Server shutting down...")
    finally:
        server.server_close()
        print("[+] Server terminated. Exiting.")


if __name__ == "__main__":
    start_firewall_server()
