"""
TestY Pytest Plugin - Standalone Version

Поместите этот файл в папку с тестами и создайте conftest.py с содержимым:
pytest_plugins = ["testy_plugin"]
"""

import os
import requests
from typing import Dict, List, Optional, Any
import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TestYConfig:
    """Configuration for TestY integration"""

    def __init__(self):
        self.url = os.getenv("TESTY_URL")
        self.project_id = os.getenv("TESTY_PROJECT_ID")
        self.username = os.getenv("TESTY_USERNAME")
        self.password = os.getenv("TESTY_PASSWORD")
        self.token = None
        self.plan_id = None
        self.enabled = False

    def validate(self):
        """Validate required configuration"""
        required_fields = ["url", "project_id", "username", "password"]
        missing = [field for field in required_fields if not getattr(self, field)]

        if missing:
            raise ValueError(
                f"Missing required configuration in .env: {', '.join(missing)}"
            )

        if not self.plan_id:
            raise ValueError("Test plan ID is required (use --testy-plan)")


class TestYClient:
    """Client for TestY API interactions"""

    def __init__(self, config: TestYConfig):
        self.config = config
        self.session = requests.Session()

    def authenticate(self) -> bool:
        """Authenticate with TestY and get access token"""
        url = f"{self.config.url}/api/token/obtain/"
        data = {"username": self.config.username, "password": self.config.password}

        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()

            token_data = response.json()
            self.config.token = token_data["token"]

            # Set authorization header for future requests
            self.session.headers.update({"Authorization": f"Token {self.config.token}"})

            print(f"TestY: Successfully authenticated as {self.config.username}")
            return True

        except requests.RequestException as e:
            print(f"TestY authentication failed: {e}")
            return False

    def get_tests(self) -> Dict[str, Any]:
        """Get tests from TestY plan"""
        url = f"{self.config.url}/api/v2/tests/"
        params = {
            "project": self.config.project_id,
            "plan": self.config.plan_id,
            "page_size": 1000,
        }

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"Failed to get tests from TestY: {e}")
            return {}

    def send_result(
        self, test_id: int, status_id: int, comment: str = ""
    ) -> Optional[Dict[str, Any]]:
        """Send test result to TestY"""
        url = f"{self.config.url}/api/v2/results/"
        params = {"project": self.config.project_id}
        data = {"test": test_id, "status": status_id, "comment": comment}

        try:
            response = self.session.post(url, params=params, json=data)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"Failed to send result for test {test_id}: {e}")
            return None


class TestYDecorator:
    """Decorator for marking tests with TestY IDs"""

    def __init__(self):
        self.test_ids: Dict[str, List[int]] = {}

    def id(self, *ids: int):
        """Mark test with TestY test case IDs"""

        def decorator(func):
            self.test_ids[func.__name__] = list(ids)
            return func

        return decorator


# Global decorator instance
testy = TestYDecorator()


class TestYPlugin:
    """Main pytest plugin class"""

    # TestY status IDs
    STATUS_PASSED = 2
    STATUS_FAILED = 1
    STATUS_SKIPPED = 3
    STATUS_BROKEN = 4
    STATUS_BLOCKED = 5
    STATUS_RETEST = 6

    def __init__(self):
        self.config = TestYConfig()
        self.client: Optional[TestYClient] = None
        self.tests_data: Dict[int, Dict[str, Any]] = {}
        self.case_to_instance: Dict[int, int] = {}  # Maps case ID to instance ID

    def pytest_addoption(self, parser):
        """Add command line options"""
        group = parser.getgroup("testy", "TestY TMS Integration")

        group.addoption(
            "--testy",
            action="store_true",
            default=False,
            help="Enable TestY TMS integration",
        )

        group.addoption(
            "--testy-plan",
            action="store",
            type=str,
            help="TestY test plan ID (required when --testy is used)",
        )

    def pytest_configure(self, config):
        """Configure the plugin"""
        if not config.option.testy:
            return

        self.config.enabled = True
        self.config.plan_id = config.option.testy_plan

        try:
            self.config.validate()
            self.client = TestYClient(self.config)

            # Authenticate with TestY
            if not self.client.authenticate():
                print("TestY authentication failed. Disabling integration.")
                self.config.enabled = False
                return

            # Load tests data from plan
            print(f"TestY: Loading tests from plan {self.config.plan_id}...")
            tests_response = self.client.get_tests()

            if "results" in tests_response:
                for test in tests_response["results"]:
                    instance_id = test["id"]
                    case_id = test["case"]
                    self.case_to_instance[case_id] = instance_id
                    self.tests_data[instance_id] = test

            print(
                f"TestY: Integration enabled. Loaded {len(self.tests_data)} tests from plan {self.config.plan_id}"
            )

        except Exception as e:
            print(f"TestY configuration error: {e}")
            self.config.enabled = False

    def pytest_runtest_logreport(self, report):
        """Handle test reports including skipped tests"""
        if not self.config.enabled or not self.client:
            return

        # Only process the 'call' phase for regular tests, but also handle 'setup' for skipped tests
        if report.when == "call" or (report.when == "setup" and report.skipped):
            self._send_test_result(report)

    def pytest_runtest_makereport(self, item, call):
        """Generate test report (keeping for backward compatibility)"""
        # This method is kept for any additional processing if needed
        pass

    def _send_test_result(self, report):
        """Send test result to TestY based on report"""
        # Get test IDs from decorator
        test_name = report.nodeid.split("::")[-1]  # Extract function name from nodeid
        test_case_ids = testy.test_ids.get(test_name, [])

        if not test_case_ids:
            # No TestY IDs specified for this test
            return

        # Determine test status and comment based on report
        status_id, comment = self._get_test_result_from_report(report)

        # Send results for all associated test case IDs
        for case_id in test_case_ids:
            instance_id = self.case_to_instance.get(case_id)
            if instance_id:
                result = self.client.send_result(instance_id, status_id, comment)
                if result:
                    status_text = result.get("status_text", "Unknown")
                    print(
                        f"TestY: Result sent for test {instance_id} (case {case_id}): {status_text}"
                    )
                else:
                    print(
                        f"TestY: Failed to send result for test {instance_id} (case {case_id})"
                    )
            else:
                print(
                    f"TestY Warning: Test case {case_id} not found in plan {self.config.plan_id}"
                )

    def _get_test_result_from_report(self, report) -> tuple:
        """Determine test status and comment from test report"""
        if report.passed:
            # Test passed
            return self.STATUS_PASSED, "Автотест выполнен успешно"
        elif report.skipped:
            # Test was skipped
            skip_reason = (
                report.longrepr
                if hasattr(report, "longrepr") and report.longrepr
                else "Нет причины"
            )
            # Handle different types of skip reasons
            if hasattr(skip_reason, "reprcrash") and skip_reason.reprcrash:
                reason = str(skip_reason.reprcrash.message)
            elif isinstance(skip_reason, tuple) and len(skip_reason) >= 2:
                reason = str(skip_reason[1])
            elif hasattr(skip_reason, "reason"):
                reason = str(skip_reason.reason)
            else:
                reason = str(skip_reason) if skip_reason else "Нет причины"
            return self.STATUS_SKIPPED, f"Тест пропущен: {reason}"
        elif report.failed:
            # Test failed
            error_msg = "Неизвестная ошибка"
            if hasattr(report, "longrepr") and report.longrepr:
                if hasattr(report.longrepr, "reprcrash") and report.longrepr.reprcrash:
                    error_msg = str(report.longrepr.reprcrash.message)
                else:
                    error_msg = str(report.longrepr)
            return self.STATUS_FAILED, f"Тест завершился с ошибкой: {error_msg}"
        else:
            # Unknown status - treat as broken
            return self.STATUS_BROKEN, "Неопределенный статус теста"


# Create plugin instance
_plugin = TestYPlugin()


def pytest_addoption(parser):
    """Pytest hook for adding command line options"""
    _plugin.pytest_addoption(parser)


def pytest_configure(config):
    """Pytest hook for plugin configuration"""
    _plugin.pytest_configure(config)


def pytest_runtest_makereport(item, call):
    """Pytest hook for test result reporting"""
    return _plugin.pytest_runtest_makereport(item, call)


def pytest_runtest_logreport(report):
    """Pytest hook for processing test reports including skipped tests"""
    return _plugin.pytest_runtest_logreport(report)
