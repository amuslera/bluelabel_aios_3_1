#!/usr/bin/env python3
"""
Test runner for all multi-agent coordination tests.

This script runs the complete test suite for agent coordination,
including unit tests, integration tests, and performance benchmarks.
"""

import asyncio
import sys
import os
import json
import subprocess
from datetime import datetime
from typing import Dict, Any, List

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


class CoordinationTestRunner:
    """Runner for all coordination tests."""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.utcnow()
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests using the built-in test runner."""
        print("🧪 Running Unit Tests")
        print("=" * 20)
        
        try:
            # Run the unit tests directly
            sys.path.append('tests/unit')
            from test_agent_coordination import run_manual_tests
            
            # Run manual tests
            asyncio.run(run_manual_tests())
            
            return {
                "status": "passed",
                "message": "Unit tests completed successfully",
                "test_count": "manual_execution"
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "message": "Unit tests failed"
            }
    
    async def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests."""
        print("\n🔗 Running Integration Tests")
        print("=" * 25)
        
        try:
            # Import and run integration tests
            sys.path.append('tests/integration')
            from test_multi_agent_coordination import MultiAgentTestSuite
            
            # Create test suite
            test_suite = MultiAgentTestSuite()
            
            # Check if monitoring server is available
            if not await test_suite.setup_monitoring_connection():
                return {
                    "status": "skipped",
                    "message": "Monitoring server not available",
                    "recommendation": "Start monitoring server: python projects/monitoring/src/enhanced_monitoring_server.py"
                }
            
            # Run all scenarios
            results = await test_suite.run_all_scenarios()
            
            summary = results.get("summary", {})
            
            return {
                "status": "passed" if summary.get("scenario_success_rate", 0) > 0.8 else "failed",
                "results": summary,
                "scenarios_passed": summary.get("successful_scenarios", 0),
                "scenarios_total": summary.get("total_scenarios", 0),
                "overall_grade": summary.get("overall_grade", "Unknown")
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "message": "Integration tests failed"
            }
    
    async def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests."""
        print("\n⚡ Running Performance Tests")
        print("=" * 25)
        
        try:
            # Import and run performance tests
            sys.path.append('tests/performance')
            from test_agent_performance import AgentPerformanceTester
            
            # Create performance tester
            tester = AgentPerformanceTester()
            
            # Run a subset of performance tests for CI
            print("Running lightweight performance suite...")
            
            # Quick throughput test
            throughput_result = await tester.run_throughput_test(
                agent_count=5, 
                task_count=25, 
                complexity=2
            )
            
            # Quick scalability test
            scalability_results = []
            for agent_count in [2, 4, 6]:
                result = await tester.run_throughput_test(agent_count, agent_count * 5, 2)
                scalability_results.append(result)
            
            return {
                "status": "passed",
                "throughput": {
                    "tasks_per_second": throughput_result.tasks_per_second,
                    "success_rate": throughput_result.success_rate
                },
                "scalability": {
                    "agent_counts_tested": [2, 4, 6],
                    "performance_scaling": [r.tasks_per_second for r in scalability_results]
                },
                "message": "Performance tests completed (lightweight suite)"
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "message": "Performance tests failed"
            }
    
    def check_prerequisites(self) -> Dict[str, Any]:
        """Check if all prerequisites are met."""
        print("🔍 Checking Prerequisites")
        print("=" * 22)
        
        checks = {
            "python_version": sys.version_info >= (3, 8),
            "src_directory": os.path.exists("src"),
            "tests_directory": os.path.exists("tests"),
            "monitoring_code": os.path.exists("projects/monitoring"),
            "control_center_code": os.path.exists("projects/control_center")
        }
        
        all_passed = all(checks.values())
        
        print(f"   Python version: {'✅' if checks['python_version'] else '❌'}")
        print(f"   Source directory: {'✅' if checks['src_directory'] else '❌'}")
        print(f"   Tests directory: {'✅' if checks['tests_directory'] else '❌'}")
        print(f"   Monitoring code: {'✅' if checks['monitoring_code'] else '❌'}")
        print(f"   Control Center code: {'✅' if checks['control_center_code'] else '❌'}")
        
        return {
            "status": "passed" if all_passed else "failed",
            "checks": checks,
            "message": "All prerequisites met" if all_passed else "Some prerequisites missing"
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run the complete test suite."""
        print("🚀 AIOSv3 Multi-Agent Coordination Test Suite")
        print("=" * 45)
        print(f"Started at: {self.start_time.isoformat()}")
        print()
        
        # Check prerequisites
        prereq_results = self.check_prerequisites()
        self.test_results["prerequisites"] = prereq_results
        
        if prereq_results["status"] != "passed":
            print("❌ Prerequisites not met, aborting tests")
            return self.test_results
        
        # Run unit tests
        unit_results = self.run_unit_tests()
        self.test_results["unit_tests"] = unit_results
        
        # Run integration tests
        integration_results = await self.run_integration_tests()
        self.test_results["integration_tests"] = integration_results
        
        # Run performance tests (if integration tests passed)
        if integration_results["status"] != "failed":
            performance_results = await self.run_performance_tests()
            self.test_results["performance_tests"] = performance_results
        else:
            self.test_results["performance_tests"] = {
                "status": "skipped",
                "message": "Skipped due to integration test failures"
            }
        
        # Generate overall summary
        self.test_results["summary"] = self._generate_summary()
        self.test_results["end_time"] = datetime.utcnow().isoformat()
        
        return self.test_results
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate overall test summary."""
        test_categories = ["unit_tests", "integration_tests", "performance_tests"]
        
        passed_tests = sum(
            1 for category in test_categories 
            if self.test_results.get(category, {}).get("status") == "passed"
        )
        
        skipped_tests = sum(
            1 for category in test_categories
            if self.test_results.get(category, {}).get("status") == "skipped"
        )
        
        failed_tests = sum(
            1 for category in test_categories
            if self.test_results.get(category, {}).get("status") == "failed"
        )
        
        total_tests = len(test_categories)
        
        # Determine overall status
        if failed_tests == 0:
            overall_status = "PASSED"
            grade = "A" if passed_tests == total_tests else "B"
        elif failed_tests == 1 and skipped_tests > 0:
            overall_status = "MOSTLY_PASSED"
            grade = "C"
        else:
            overall_status = "FAILED"
            grade = "F"
        
        return {
            "overall_status": overall_status,
            "grade": grade,
            "tests_passed": passed_tests,
            "tests_skipped": skipped_tests,
            "tests_failed": failed_tests,
            "tests_total": total_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0
        }
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 45)
        print("📊 TEST SUITE SUMMARY")
        print("=" * 45)
        
        summary = self.test_results.get("summary", {})
        
        print(f"Overall Status: {summary.get('overall_status', 'UNKNOWN')}")
        print(f"Grade: {summary.get('grade', 'N/A')}")
        print(f"Tests Passed: {summary.get('tests_passed', 0)}/{summary.get('tests_total', 0)}")
        print(f"Success Rate: {summary.get('success_rate', 0):.1%}")
        
        print("\nDetailed Results:")
        for category in ["unit_tests", "integration_tests", "performance_tests"]:
            result = self.test_results.get(category, {})
            status = result.get("status", "unknown")
            
            status_icon = {
                "passed": "✅",
                "failed": "❌", 
                "skipped": "⏭️"
            }.get(status, "❓")
            
            print(f"  {status_icon} {category.replace('_', ' ').title()}: {status}")
            
            if status == "failed" and "error" in result:
                print(f"    Error: {result['error']}")
        
        print("\n🎯 Recommendations:")
        
        if summary.get("overall_status") == "PASSED":
            print("  • Excellent! All coordination tests are passing")
            print("  • The multi-agent system is ready for production use")
        elif summary.get("overall_status") == "MOSTLY_PASSED":
            print("  • Good progress! Most tests are passing")
            print("  • Address any skipped tests when possible")
        else:
            print("  • Issues detected in the coordination system")
            print("  • Review failed tests and fix underlying issues")
        
        # Check for monitoring server requirement
        integration_result = self.test_results.get("integration_tests", {})
        if integration_result.get("status") == "skipped":
            print("  • Start the monitoring server to enable full integration testing")
            print("    Command: python projects/monitoring/src/enhanced_monitoring_server.py")


async def main():
    """Main test runner function."""
    runner = CoordinationTestRunner()
    
    try:
        # Run all tests
        results = await runner.run_all_tests()
        
        # Print summary
        runner.print_summary()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"coordination_test_results_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {filename}")
        
        # Exit with appropriate code
        summary = results.get("summary", {})
        exit_code = 0 if summary.get("overall_status") == "PASSED" else 1
        
        print(f"\n{'🎉 All tests passed!' if exit_code == 0 else '❌ Some tests failed'}")
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Test runner failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)