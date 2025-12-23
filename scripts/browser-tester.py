#!/usr/bin/env python3
"""
Flourisha Browser Test Agent
Tests the frontend application from a user perspective using Playwright
"""

import asyncio
import sys
from playwright.async_api import async_playwright, expect, Page
import json
from datetime import datetime
from typing import Dict, List, Any

class FlourishaTestAgent:
    def __init__(self, base_url: str = "http://100.66.28.67:5174"):
        self.base_url = base_url
        self.test_results: List[Dict[str, Any]] = []
        self.test_email = f"tester-{datetime.now().timestamp()}@test.local"
        self.test_password = "TestPassword123!"
        
    def add_result(self, test_name: str, passed: bool, message: str = ""):
        """Add test result"""
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "timestamp": datetime.now().isoformat(),
            "message": message
        })
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}: {message}")
    
    async def test_page_load(self, page: Page, path: str, expected_title: str = None) -> bool:
        """Test if a page loads without errors"""
        try:
            await page.goto(f"{self.base_url}{path}", wait_until="domcontentloaded", timeout=10000)
            # Check for common error patterns
            content = await page.content()
            has_errors = any(err in content.lower() for err in ["error", "500", "404", "failed"])
            
            if expected_title:
                title = await page.title()
                if expected_title not in title:
                    self.add_result(f"Page Load: {path}", False, f"Expected title '{expected_title}', got '{title}'")
                    return False
            
            self.add_result(f"Page Load: {path}", not has_errors, f"Loaded successfully" if not has_errors else "Page contains errors")
            return not has_errors
        except Exception as e:
            self.add_result(f"Page Load: {path}", False, str(e))
            return False
    
    async def test_login_page(self, page: Page) -> bool:
        """Test login page elements and functionality"""
        try:
            await page.goto(f"{self.base_url}/login", wait_until="domcontentloaded")
            
            # Check elements exist
            email_input = page.locator('input[type="email"]')
            password_input = page.locator('input[type="password"]')
            signin_button = page.locator('button:has-text("Sign In")')
            signup_link = page.locator('a:has-text("Sign Up")')
            google_button = page.locator('button:has-text("Google")')
            
            all_exist = (
                await email_input.count() > 0 and
                await password_input.count() > 0 and
                await signin_button.count() > 0 and
                await signup_link.count() > 0 and
                await google_button.count() > 0
            )
            
            self.add_result("Login Page Elements", all_exist, "All required elements present" if all_exist else "Missing elements")
            
            # Test invalid login
            await email_input.fill("invalid@test.local")
            await password_input.fill("wrongpassword")
            await signin_button.click()
            
            # Wait for error or rejection
            try:
                await page.wait_for_selector('text=/invalid|error|failed/i', timeout=5000)
                self.add_result("Login Validation", True, "Error shown for invalid credentials")
                return True
            except:
                self.add_result("Login Validation", False, "No error shown for invalid credentials")
                return False
                
        except Exception as e:
            self.add_result("Login Page Test", False, str(e))
            return False
    
    async def test_signup_page(self, page: Page) -> bool:
        """Test signup page"""
        try:
            await page.goto(f"{self.base_url}/signup", wait_until="domcontentloaded")
            
            # Check elements
            email_input = page.locator('input[type="email"]')
            password_input = page.locator('input[type="password"]')
            signup_button = page.locator('button:has-text("Sign Up")')
            login_link = page.locator('a:has-text("Sign In")')
            
            all_exist = (
                await email_input.count() > 0 and
                await password_input.count() > 0 and
                await signup_button.count() > 0 and
                await login_link.count() > 0
            )
            
            self.add_result("Signup Page Elements", all_exist, "All required elements present")
            return all_exist
            
        except Exception as e:
            self.add_result("Signup Page Test", False, str(e))
            return False
    
    async def test_api_connectivity(self, page: Page) -> bool:
        """Test if frontend can reach backend API"""
        try:
            # Go to dashboard (will fail without auth)
            await page.goto(f"{self.base_url}/dashboard", wait_until="domcontentloaded")
            
            # Should redirect to login if not authenticated
            await page.wait_for_url(f"{self.base_url}/login", timeout=5000)
            self.add_result("Auth Redirect", True, "Redirects to login when not authenticated")
            return True
            
        except Exception as e:
            self.add_result("API Connectivity", False, f"Could not test auth flow: {str(e)}")
            return False
    
    async def test_responsive_ui(self, page: Page) -> bool:
        """Test responsive UI elements"""
        try:
            await page.goto(f"{self.base_url}/login", wait_until="domcontentloaded")
            
            # Check button clickability
            buttons = await page.locator("button").all()
            clickable_count = 0
            
            for button in buttons[:3]:  # Test first 3 buttons
                try:
                    is_enabled = await button.is_enabled()
                    if is_enabled:
                        clickable_count += 1
                except:
                    pass
            
            self.add_result("UI Responsiveness", clickable_count > 0, f"{clickable_count} buttons are clickable")
            return clickable_count > 0
            
        except Exception as e:
            self.add_result("UI Responsiveness", False, str(e))
            return False
    
    async def test_error_boundaries(self, page: Page) -> bool:
        """Test error handling and boundaries"""
        try:
            # Try to access non-existent routes
            await page.goto(f"{self.base_url}/nonexistent-page", wait_until="domcontentloaded")
            
            # Should either redirect or show error gracefully
            current_url = page.url
            has_error_or_redirect = current_url != f"{self.base_url}/nonexistent-page" or "error" in page.url.lower()
            
            self.add_result("Error Boundaries", has_error_or_redirect, "App handles invalid routes gracefully")
            return has_error_or_redirect
            
        except Exception as e:
            self.add_result("Error Boundaries", False, str(e))
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("=" * 70)
        print("🌐 Flourisha Frontend Browser Test Suite")
        print("=" * 70)
        print(f"Testing: {self.base_url}")
        print(f"Started: {datetime.now().isoformat()}\n")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Run all tests
                await self.test_page_load(page, "/login", "Flourisha")
                await self.test_login_page(page)
                await self.test_signup_page(page)
                await self.test_api_connectivity(page)
                await self.test_responsive_ui(page)
                await self.test_error_boundaries(page)
                
            finally:
                await browser.close()
        
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
    agent = FlourishaTestAgent()
    results = await agent.run_all_tests()
    
    # Print JSON for integration
    print("\n🔍 Detailed Results (JSON):")
    print(json.dumps(results, indent=2))
    
    # Exit with proper code
    sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
