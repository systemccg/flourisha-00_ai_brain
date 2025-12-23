#!/usr/bin/env python3
"""
Flourisha API Test Agent
Tests the backend API from a user/client perspective
Simulates what the frontend does and validates all endpoints work
"""

import asyncio
import sys
import httpx
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

class FlourishaAPITestAgent:
    def __init__(self, api_url: str = "http://100.66.28.67:8001"):
        self.api_url = api_url
        self.test_results: List[Dict[str, Any]] = []
        self.base_headers = {
            "Content-Type": "application/json",
            "User-Agent": "Flourisha-Test-Agent/1.0"
        }

    def add_result(self, test_name: str, passed: bool, message: str = "", details: Dict = None):
        """Add test result"""
        result = {
            "test": test_name,
            "passed": passed,
            "timestamp": datetime.now().isoformat(),
            "message": message
        }
        if details:
            result["details"] = details
        self.test_results.append(result)

        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}: {message}")

    async def test_health_endpoint(self, client: httpx.AsyncClient) -> bool:
        """Test if API is healthy"""
        try:
            response = await client.get(f"{self.api_url}/health")
            passed = response.status_code == 200
            data = response.json() if passed else {}

            self.add_result(
                "API Health Check",
                passed,
                f"Status: {response.status_code}",
                data
            )
            return passed
        except Exception as e:
            self.add_result("API Health Check", False, str(e))
            return False

    async def test_unauthenticated_access(self, client: httpx.AsyncClient) -> bool:
        """Test that protected endpoints reject unauthenticated requests"""
        try:
            response = await client.get(f"{self.api_url}/api/v1/projects")

            # Should return 401 or 403
            protected = response.status_code in [401, 403]

            self.add_result(
                "Unauthenticated Access Protection",
                protected,
                f"Status: {response.status_code} (expected 401/403)",
                {"response": response.json() if protected else response.text}
            )
            return protected
        except Exception as e:
            self.add_result("Unauthenticated Access Protection", False, str(e))
            return False

    async def test_cors_headers(self, client: httpx.AsyncClient) -> bool:
        """Test CORS headers are present"""
        try:
            # CORS headers are only sent when Origin header is present
            headers = {"Origin": "http://100.66.28.67:5174"}
            response = await client.get(f"{self.api_url}/health", headers=headers)

            has_cors = any(key.lower() == "access-control-allow-origin" for key in response.headers.keys())

            self.add_result(
                "CORS Headers",
                has_cors,
                "CORS headers present" if has_cors else "Missing CORS headers",
                {"headers": {k: v for k, v in response.headers.items() if "access-control" in k.lower()}}
            )
            return has_cors
        except Exception as e:
            self.add_result("CORS Headers", False, str(e))
            return False

    async def test_invalid_token(self, client: httpx.AsyncClient) -> bool:
        """Test that invalid tokens are rejected"""
        try:
            headers = {**self.base_headers}
            headers["Authorization"] = "Bearer invalid_token_12345"

            response = await client.get(
                f"{self.api_url}/api/v1/projects",
                headers=headers
            )

            # Should reject invalid token
            rejected = response.status_code in [401, 403]

            self.add_result(
                "Invalid Token Rejection",
                rejected,
                f"Status: {response.status_code} (expected 401/403)",
            )
            return rejected
        except Exception as e:
            self.add_result("Invalid Token Rejection", False, str(e))
            return False

    async def test_api_endpoints_exist(self, client: httpx.AsyncClient) -> bool:
        """Test that key API endpoints exist (return non-404 or proper error)"""
        endpoints = [
            "/api/v1/projects",
            "/api/v1/content",
            "/api/v1/youtube/subscriptions",
        ]

        all_exist = True
        for endpoint in endpoints:
            try:
                response = await client.get(f"{self.api_url}{endpoint}")
                # Endpoint exists if we don't get 404 (auth errors are fine)
                exists = response.status_code != 404
                if not exists:
                    all_exist = False
                    self.add_result(f"Endpoint Exists: {endpoint}", False, f"Status: {response.status_code}")
                else:
                    self.add_result(f"Endpoint Exists: {endpoint}", True, f"Status: {response.status_code}")
            except Exception as e:
                all_exist = False
                self.add_result(f"Endpoint Exists: {endpoint}", False, str(e))

        return all_exist

    async def test_error_response_format(self, client: httpx.AsyncClient) -> bool:
        """Test that error responses are properly formatted"""
        try:
            response = await client.get(f"{self.api_url}/api/v1/nonexistent")

            # Should return error (not crash)
            has_response = response.status_code in [400, 404, 405]

            self.add_result(
                "Error Response Format",
                has_response,
                f"Status: {response.status_code}",
                {"response": response.json() if has_response else response.text}
            )
            return has_response
        except Exception as e:
            self.add_result("Error Response Format", False, str(e))
            return False

    async def test_project_endpoints_structure(self, client: httpx.AsyncClient) -> bool:
        """Test that project endpoints follow REST structure"""
        endpoints = [
            ("GET", "/api/v1/projects"),
            ("POST", "/api/v1/projects"),
        ]

        all_ok = True
        for method, endpoint in endpoints:
            try:
                if method == "GET":
                    response = await client.get(f"{self.api_url}{endpoint}")
                elif method == "POST":
                    response = await client.post(
                        f"{self.api_url}{endpoint}",
                        json={"name": "test-project"}
                    )

                # Should not be 404 (auth rejection is fine)
                ok = response.status_code != 404
                if not ok:
                    all_ok = False

                self.add_result(
                    f"REST Endpoint: {method} {endpoint}",
                    ok,
                    f"Status: {response.status_code}"
                )
            except Exception as e:
                all_ok = False
                self.add_result(f"REST Endpoint: {method} {endpoint}", False, str(e))

        return all_ok

    async def test_youtube_endpoints(self, client: httpx.AsyncClient) -> bool:
        """Test YouTube API endpoints exist"""
        endpoints = [
            ("GET", "/api/v1/youtube/subscriptions"),
            ("POST", "/api/v1/youtube/playlists/subscribe"),
        ]

        all_ok = True
        for method, endpoint in endpoints:
            try:
                if method == "GET":
                    response = await client.get(f"{self.api_url}{endpoint}")
                elif method == "POST":
                    response = await client.post(
                        f"{self.api_url}{endpoint}",
                        json={"playlist_id": "test-playlist"}
                    )

                ok = response.status_code != 404
                if not ok:
                    all_ok = False

                self.add_result(
                    f"YouTube Endpoint: {method} {endpoint}",
                    ok,
                    f"Status: {response.status_code}"
                )
            except Exception as e:
                all_ok = False
                self.add_result(f"YouTube Endpoint: {method} {endpoint}", False, str(e))

        return all_ok

    async def test_content_endpoints(self, client: httpx.AsyncClient) -> bool:
        """Test Content API endpoints"""
        endpoints = [
            ("GET", "/api/v1/content"),
        ]

        all_ok = True
        for method, endpoint in endpoints:
            try:
                if method == "GET":
                    response = await client.get(f"{self.api_url}{endpoint}")

                ok = response.status_code != 404
                if not ok:
                    all_ok = False

                self.add_result(
                    f"Content Endpoint: {method} {endpoint}",
                    ok,
                    f"Status: {response.status_code}"
                )
            except Exception as e:
                all_ok = False
                self.add_result(f"Content Endpoint: {method} {endpoint}", False, str(e))

        return all_ok

    async def test_response_time(self, client: httpx.AsyncClient) -> bool:
        """Test that API responds in reasonable time"""
        try:
            import time
            start = time.time()
            response = await client.get(f"{self.api_url}/health")
            elapsed = (time.time() - start) * 1000  # milliseconds

            # Should respond in under 5 seconds
            ok = elapsed < 5000

            self.add_result(
                "Response Time",
                ok,
                f"{elapsed:.0f}ms (expected <5000ms)"
            )
            return ok
        except Exception as e:
            self.add_result("Response Time", False, str(e))
            return False

    async def run_all_tests(self):
        """Run all tests"""
        print("=" * 70)
        print("🔌 Flourisha API Test Suite")
        print("=" * 70)
        print(f"Testing: {self.api_url}")
        print(f"Started: {datetime.now().isoformat()}\n")

        async with httpx.AsyncClient(timeout=10.0) as client:
            # Run all tests
            await self.test_health_endpoint(client)
            await self.test_cors_headers(client)
            await self.test_unauthenticated_access(client)
            await self.test_invalid_token(client)
            await self.test_api_endpoints_exist(client)
            await self.test_error_response_format(client)
            await self.test_project_endpoints_structure(client)
            await self.test_youtube_endpoints(client)
            await self.test_content_endpoints(client)
            await self.test_response_time(client)

        # Print summary
        print("\n" + "=" * 70)
        print("📊 Test Summary")
        print("=" * 70)
        passed = sum(1 for r in self.test_results if r["passed"])
        failed = sum(1 for r in self.test_results if not r["passed"])
        total = len(self.test_results)

        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        print("\n" + "=" * 70)

        # Return results
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "success_rate": passed / total * 100 if total > 0 else 0,
            "tests": self.test_results
        }


async def main():
    agent = FlourishaAPITestAgent()
    results = await agent.run_all_tests()

    # Print JSON for integration
    print("\n🔍 Detailed Results (JSON):")
    print(json.dumps(results, indent=2))

    # Exit with proper code
    sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
