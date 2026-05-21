#!/usr/bin/env python3
"""
Log4j2 RCE Attack Simulation Test Client
=========================================

This module simulates the CVE-2021-44228 Log4Shell exploitation attack
to test firewall detection and mitigation effectiveness.

The simulated attack sends specially crafted HTTP requests with malicious
headers that would trigger RCE on unpatched Apache Tomcat servers.

Usage:
    python test_client.py
"""

import requests
import json
import sys
from typing import Dict, List, Tuple


class Log4j2AttackSimulator:
    """Simulates Log4j2 RCE attacks for testing firewall effectiveness."""

    def __init__(self, target_url: str = "http://localhost:8000"):
        """
        Initialize the attack simulator.
        
        Args:
            target_url: Base URL of the target firewall server
        """
        self.target_url = target_url
        self.vulnerable_endpoint = "/tomcatwar.jsp"
        self.test_results: List[Dict] = []

    def test_case_1_attack_with_all_signatures(self) -> Tuple[bool, str]:
        """
        Test Case 1: Complete attack with all malicious headers.
        
        Expected: Request should be BLOCKED (403)
        """
        print("\n[TEST 1] Full Log4j2 RCE attack with all signature headers...")
        
        headers = {
            "suffix": "%>//",
            "c1": "Runtime",
            "c2": "<%",
            "DNT": "1",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        payload = (
            "class.module.classLoader.resources.context.parent.pipeline.first"
            ".pattern=%25%7Bc2%7Di%20if(%22j%22.equals(request.getParameter(%22pwd%22)))"
            "%7B%20java.io.InputStream%20in%20%3D%20%25%7Bc1%7Di.getRuntime()"
            ".exec(request.getParameter(%22cmd%22)).getInputStream()%3B"
        )
        
        try:
            response = requests.post(
                self.target_url + self.vulnerable_endpoint,
                headers=headers,
                data=payload,
                timeout=5
            )
            
            is_blocked = response.status_code == 403
            result = "BLOCKED ✓" if is_blocked else "ALLOWED ✗"
            expected = "BLOCKED"
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Result: {result} (Expected: {expected})")
            print(f"   Response: {response.json()}")
            
            return is_blocked, "Complete attack with all signatures"
        except Exception as e:
            print(f"   ERROR: {str(e)}")
            return False, f"Error: {str(e)}"

    def test_case_2_missing_signature(self) -> Tuple[bool, str]:
        """
        Test Case 2: Attack with missing signature header.
        
        Expected: Request should be ALLOWED (200)
        """
        print("\n[TEST 2] Attack with missing signature header...")
        
        headers = {
            "suffix": "%>//",
            "c1": "Runtime",
            # Missing "c2" header
            "DNT": "1",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        try:
            response = requests.post(
                self.target_url + self.vulnerable_endpoint,
                headers=headers,
                timeout=5
            )
            
            is_allowed = response.status_code == 200
            result = "ALLOWED ✓" if is_allowed else "BLOCKED ✗"
            expected = "ALLOWED"
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Result: {result} (Expected: {expected})")
            print(f"   Response: {response.json()}")
            
            return is_allowed, "Attack with missing signature"
        except Exception as e:
            print(f"   ERROR: {str(e)}")
            return False, f"Error: {str(e)}"

    def test_case_3_safe_request(self) -> Tuple[bool, str]:
        """
        Test Case 3: Safe request with legitimate headers.
        
        Expected: Request should be ALLOWED (200)
        """
        print("\n[TEST 3] Safe request to vulnerable endpoint...")
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        }
        
        try:
            response = requests.post(
                self.target_url + self.vulnerable_endpoint,
                headers=headers,
                timeout=5
            )
            
            is_allowed = response.status_code == 200
            result = "ALLOWED ✓" if is_allowed else "BLOCKED ✗"
            expected = "ALLOWED"
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Result: {result} (Expected: {expected})")
            print(f"   Response: {response.json()}")
            
            return is_allowed, "Safe request"
        except Exception as e:
            print(f"   ERROR: {str(e)}")
            return False, f"Error: {str(e)}"

    def test_case_4_safe_endpoint(self) -> Tuple[bool, str]:
        """
        Test Case 4: Attack headers but safe endpoint.
        
        Expected: Request should be ALLOWED (200)
        """
        print("\n[TEST 4] Attack headers sent to safe endpoint...")
        
        headers = {
            "suffix": "%>//",
            "c1": "Runtime",
            "c2": "<%",
            "DNT": "1",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        try:
            response = requests.post(
                self.target_url + "/safe",
                headers=headers,
                timeout=5
            )
            
            is_allowed = response.status_code == 200
            result = "ALLOWED ✓" if is_allowed else "BLOCKED ✗"
            expected = "ALLOWED"
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Result: {result} (Expected: {expected})")
            print(f"   Response: {response.json()}")
            
            return is_allowed, "Attack headers on safe endpoint"
        except Exception as e:
            print(f"   ERROR: {str(e)}")
            return False, f"Error: {str(e)}"

    def run_all_tests(self) -> None:
        """Run all firewall tests and display results."""
        print("=" * 70)
        print("Log4j2 RCE Firewall Test Suite")
        print("=" * 70)
        
        tests = [
            self.test_case_1_attack_with_all_signatures,
            self.test_case_2_missing_signature,
            self.test_case_3_safe_request,
            self.test_case_4_safe_endpoint,
        ]
        
        results = []
        for test_func in tests:
            passed, description = test_func()
            results.append({
                "test": description,
                "passed": passed,
            })
            self.test_results.append({
                "test": description,
                "passed": passed,
            })
        
        # Print summary
        print("\n" + "=" * 70)
        print("Test Summary")
        print("=" * 70)
        
        passed_count = sum(1 for r in results if r["passed"])
        total_count = len(results)
        
        for i, result in enumerate(results, 1):
            status = "✓ PASS" if result["passed"] else "✗ FAIL"
            print(f"[{i}] {result['test']}: {status}")
        
        print(f"\nTotal: {passed_count}/{total_count} tests passed")
        
        if passed_count == total_count:
            print("\n✓ All firewall tests passed!")
            return 0
        else:
            print(f"\n✗ {total_count - passed_count} test(s) failed")
            return 1


if __name__ == "__main__":
    simulator = Log4j2AttackSimulator()
    exit_code = simulator.run_all_tests()
    sys.exit(exit_code)
