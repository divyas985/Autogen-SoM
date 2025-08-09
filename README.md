

# Society of Mind — Stock Trend Analyzer

This document contains:

1. Clear documentation of agent roles & responsibilities
2. Demonstration of human-in-the-loop functionality
3. Flow diagrams ( with clear indication of the UserProxyAgent


---

## 1) Agent Roles & Responsibilities

### Outer Layer

- **StockSoMTeam (SocietyOfMindAgent)**

  - Role: Orchestrator for the inner team. Receives the user's task and coordinates inner agents in order (DataFetcher -> TrendAnalyzer -> SummaryGenerator).
  - Responsibility: Ensure correctness of data flow, handle retries or failures, and present the final consolidated output to the outer agents/human.

- **UserProxy (UserProxyAgent)**

  - Role: Human-in-the-loop interface.
  - Responsibility: Collect user input (stock symbol), confirm starting the analysis, and request explicit approval (uses the `APPROVE` keyword) before finalizing or publishing the result.

### Inner Layer (Stock Analysis Team)

- **DataFetcherAgent**

  - Role: Retrieve historical stock data (6 months) using `yfinance`.
  - Responsibility: Call a registered function tool that returns a pandas DataFrame. Validate data completeness and return the DataFrame to the next agent.

- **TrendAnalyzerAgent**

  - Role: Compute technical indicators (SMA50, SMA200, RSI) and generate a trend chart (PNG → base64).(Need to Fix code to generate Graphs)
  - Responsibility: Produce numeric analysis + a base64-encoded PNG image of the trend. Return both summary metrics and the encoded image to the team.

- **SummaryGeneratorAgent**

  - Role: Convert numeric results and chart into a human‑readable report.
  - Responsibility: Compose the final message with observations and suggested next steps or caveats.

---

## 2) Human-in-the-loop Demonstration

**Flow**

1. User runs `main()` and is prompted by the `UserProxy` to enter a stock symbol.
2. `UserProxy` asks for confirmation to proceed.
3. If approved, `StockSoMTeam` triggers the inner team in a round-robin fashion.
4. `DataFetcherAgent` fetches historical price data and returns it.
5. `TrendAnalyzerAgent` calculates indicators and creates a PNG trend chart. It encodes the image as base64 and returns a compact payload.
6. `SummaryGeneratorAgent` creates a polished summary that references the chart.
7. The `UserProxy` receives the final consolidated output and asks the user to type `APPROVE` to finalize; on `APPROVE` the system finishes.

**Example CLI interaction:**

```
Enter stock symbol (e.g., AAPL, TSLA): AAPL
Analyze AAPL? (y/n): y
Please wait while the agents analyze the stock data...

--- Analysis Ready ---
UserProxy: Please review the analysis below and type APPROVE to accept.
[Summary text here]
[Chart as base64 or link]
APPROVE
✅ Analysis approved and complete.
```

---

## 3) Flow Diagram

### ASCII Diagram

```
                ┌─────────────────────────┐
                │       Human User         │
                └─────────────────────────┘
                           ▲
                           │ (input & approval)
                           ▼
                ┌─────────────────────────┐
                │     UserProxyAgent      │  <-- clearly shown here
                │ (human-in-the-loop GUI) │
                └─────────────────────────┘
                           ▲
                           │
                           ▼
                ┌─────────────────────────┐
                │   StockSoMTeam (SoM)    │
                │ (outer coordinator)     │
                └─────────────────────────┘
                           │
       ┌───────────────────┼────────────────────┐
       ▼                   ▼                    ▼
┌──────────────┐   ┌──────────────┐   ┌────────────────┐
│DataFetcher   │   │TrendAnalyzer │   │SummaryGenerator│
│(fetches df)  │   │(chart + nums)│   │(text report)   │
└──────────────┘   └──────────────┘   └────────────────┘
```



---

Make sure you have `autogen-agentchat`, `autogen-ext`, `autogen-core`, `yfinance`, `matplotlib`, `pandas`, `python-dotenv` installed and your `OPENAI_API_KEY` in a `.env` file.

