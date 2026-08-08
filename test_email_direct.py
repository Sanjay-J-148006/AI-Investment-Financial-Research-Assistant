import unittest
from agents.email_agent import get_email_agent_response
from agents.coordinator import route_and_execute

class TestEmailAgentDirect(unittest.TestCase):

    def test_get_email_agent_response_with_gmail_user(self):
        """Test calling get_email_agent_response with explicit gmail_user and gmail_password kwargs"""
        res = get_email_agent_response(
            query="Send report to test@example.com",
            last_report_text="Sample Report Text",
            provider="groq",
            api_key="test_key",
            gmail_user="myemail@gmail.com",
            gmail_password="app_password_123",
            attachment_path=""
        )
        self.assertIsNotNone(res)
        self.assertIn("Email Composition Cover Letter", res)

    def test_coordinator_route_email(self):
        """Test coordinator routing email queries"""
        res = route_and_execute(
            query="Send email report to client@example.com",
            last_report_text="Sample Report Text",
            provider="groq",
            api_key="test_key"
        )
        self.assertIsNotNone(res)
        self.assertEqual(res.get("agent_name"), "Email Agent")

if __name__ == "__main__":
    unittest.main()
