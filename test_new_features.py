import unittest
import os
from utils.charts import (
    generate_stock_performance_chart,
    generate_revenue_breakdown_chart,
    generate_comparison_bar_chart
)
from utils.guardrails import (
    sanitize_input,
    append_guardrail_disclaimer,
    calculate_token_cost
)
from agents.coordinator import route_and_execute
from memory.long_term import (
    save_investor_profile,
    get_investor_profile,
    get_all_investor_profiles,
    delete_investor_profile
)

class TestNewResumeFeatures(unittest.TestCase):

    def test_plotly_charts_generation(self):
        """Test Plotly interactive chart generation"""
        fig1 = generate_stock_performance_chart("NVDA", "NVIDIA Corp")
        self.assertIsNotNone(fig1)
        
        fig2 = generate_revenue_breakdown_chart("Microsoft")
        self.assertIsNotNone(fig2)
        
        fig3 = generate_comparison_bar_chart(["Microsoft", "Google", "Amazon", "Meta"])
        self.assertIsNotNone(fig3)

    def test_guardrails_and_sanitization(self):
        """Test AI safety input sanitizer and SEC/FINRA financial compliance disclaimers"""
        clean_q, is_safe = sanitize_input("Research NVIDIA stock performance")
        self.assertTrue(is_safe)
        self.assertEqual(clean_q, "Research NVIDIA stock performance")

        disclaimed_txt = append_guardrail_disclaimer("Investment Report Content")
        self.assertIn("Compliance Disclaimer", disclaimed_txt)

    def test_telemetry_cost_estimation(self):
        """Test LLMOps token usage and API cost calculation"""
        stats = calculate_token_cost(100, 400, provider="groq")
        self.assertIn("total_tokens", stats)
        self.assertIn("estimated_cost_usd", stats)
        self.assertTrue(stats["total_tokens"] > 0)

    def test_investor_profile_crud(self):
        """Test SQLite Investor & Client Profile CRUD operations"""
        save_msg = save_investor_profile("Resume Test Client", "Aggressive", "AI, Semiconductors", "5 Years", "High CAGR target.")
        self.assertIn("Saved profile", save_msg)
        
        all_profs = get_all_investor_profiles()
        self.assertTrue(len(all_profs) > 0)
        
        prof = get_investor_profile("Resume Test Client")
        self.assertIsNotNone(prof)
        self.assertEqual(prof["risk_profile"], "Aggressive")
        
        del_msg = delete_investor_profile("Resume Test Client")
        self.assertIn("Deleted profile", del_msg)

    def test_coordinator_telemetry_trace(self):
        """Test Agent Coordinator execution telemetry and latency tracing"""
        res = route_and_execute("Calculate CAGR from 100 to 250 over 5 years", provider="groq")
        self.assertIn("telemetry", res)
        self.assertIn("execution_latency_sec", res["telemetry"])
        self.assertIn("Compliance Disclaimer", res["output"])

if __name__ == "__main__":
    unittest.main()
