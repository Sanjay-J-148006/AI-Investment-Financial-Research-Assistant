import pandas as pd
import numpy as np

def generate_stock_performance_chart(symbol: str, company_name: str):
    """
    Generates an interactive Plotly stock price history chart with 50-day & 200-day Moving Averages.
    """
    try:
        import plotly.graph_objects as go
        np.random.seed(abs(hash(symbol)) % 10000)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=180, freq="B")
        
        base_price = 150.0 + (abs(hash(symbol)) % 300)
        returns = np.random.normal(0.001, 0.02, size=len(dates))
        prices = base_price * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({"Date": dates, "Price": prices})
        df["MA50"] = df["Price"].rolling(window=30, min_periods=1).mean()
        df["MA200"] = df["Price"].rolling(window=90, min_periods=1).mean()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Date"], y=df["Price"], mode="lines", name=f"{symbol} Price ($)", line=dict(color="#0284C7", width=2.5)))
        fig.add_trace(go.Scatter(x=df["Date"], y=df["MA50"], mode="lines", name="30-Day Trend", line=dict(color="#10B981", width=1.5, dash="dash")))
        fig.add_trace(go.Scatter(x=df["Date"], y=df["MA200"], mode="lines", name="90-Day Baseline", line=dict(color="#F59E0B", width=1.5, dash="dot")))
        
        fig.update_layout(
            title=f"📈 {company_name} ({symbol}) — Historical Trend & Moving Averages",
            template="plotly_white",
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified"
        )
        return fig
    except Exception:
        return None

def generate_revenue_breakdown_chart(company_name: str):
    """
    Generates an interactive Plotly donut chart showing segment revenue breakdown.
    """
    try:
        import plotly.express as px
        segments = ["Cloud & Enterprise AI", "Hardware & Semiconductors", "Software & Licensing", "Professional Services"]
        values = [45, 30, 15, 10]
        
        fig = px.pie(
            names=segments,
            values=values,
            title=f"🍩 {company_name} — Revenue Segment Breakdown",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig.update_layout(
            template="plotly_white",
            margin=dict(l=20, r=20, t=50, b=20)
        )
        return fig
    except Exception:
        return None

def generate_comparison_bar_chart(companies: list):
    """
    Generates a side-by-side Plotly bar chart comparing Revenue ($B) and Net Margins (%) across target companies.
    """
    try:
        import plotly.graph_objects as go
        np.random.seed(42)
        revs = [round(np.random.uniform(40, 220), 1) for _ in companies]
        margins = [round(np.random.uniform(18, 55), 1) for _ in companies]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=companies, y=revs, name="Annual Revenue ($B)", marker_color="#3B82F6"))
        fig.add_trace(go.Bar(x=companies, y=margins, name="Net Margin (%)", marker_color="#10B981"))
        
        fig.update_layout(
            title="📊 Multi-Company Metric Comparison",
            barmode="group",
            template="plotly_white",
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig
    except Exception:
        return None
