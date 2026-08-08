import os
import unittest
from models.report_schema import InvestmentReport
from tools.financial_calculator import calculate_cagr, calculate_roi, calculate_growth_rate
from memory.long_term import save_investor_profile, get_investor_profile, log_conversation_turn, get_recent_conversation_logs
from utils.formatter import export_report_as_txt, export_report_as_pdf
from agents.coordinator import route_and_execute

class TestFinancialAssistantSystem(unittest.TestCase):

    def test_pydantic_schema(self):
        report = InvestmentReport(
            company_name="TestCorp",
            ticker="TST",
            company_overview="Test Overview",
            industry="Technology",
            business_model="SaaS",
            latest_news="Test News",
            strengths=["Strong Cash Flow"],
            weaknesses=["High Competition"],
            financial_highlights="Revenue up 20%",
            growth_opportunities="AI expansion",
            potential_risks="Regulatory",
            investment_summary="Buy Recommendation"
        )
        self.assertEqual(report.company_name, "TestCorp")
        self.assertEqual(report.strengths, ["Strong Cash Flow"])

    def test_financial_calculator_tools(self):
        cagr_res = calculate_cagr.invoke({"initial_value": 100.0, "final_value": 200.0, "num_years": 5.0})
        self.assertIn("CAGR: 14.87%", cagr_res)

        roi_res = calculate_roi.invoke({"initial_investment": 1000.0, "final_value": 1500.0})
        self.assertIn("ROI: 50.00%", roi_res)

        growth_res = calculate_growth_rate.invoke({"old_value": 50.0, "new_value": 75.0})
        self.assertIn("Growth Rate: 50.00%", growth_res)

    def test_sqlite_memory(self):
        save_msg = save_investor_profile("Test Investor", "Aggressive", "AI & Robotics", "5-10 Years")
        self.assertIn("Saved profile", save_msg)
        
        profile = get_investor_profile("Test Investor")
        self.assertIsNotNone(profile)
        self.assertEqual(profile["risk_profile"], "Aggressive")

        log_conversation_turn("test_session", "user", "What is NVDA CAGR?")
        logs = get_recent_conversation_logs("test_session", limit=1)
        self.assertTrue(len(logs) > 0)
        self.assertEqual(logs[0]["content"], "What is NVDA CAGR?")

    def test_formatters(self):
        txt_path = export_report_as_txt("Sample Report Text", "test_report.txt")
        self.assertTrue(os.path.exists(txt_path))
        os.remove(txt_path)

        pdf_path = export_report_as_pdf("# Sample Report Title\n\n- Bullet 1\n- Bullet 2", "test_report.pdf")
        self.assertTrue(os.path.exists(pdf_path))
        os.remove(pdf_path)

    def test_coordinator_routing(self):
        calc_route = route_and_execute("Calculate CAGR from 100 to 200 over 5 years")
        self.assertEqual(calc_route["agent_name"], "Financial Calculator Tool")
        self.assertIn("CAGR: 14.87%", calc_route["output"])

if __name__ == "__main__":
    unittest.main()
