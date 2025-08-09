
import asyncio
import yfinance as yf
import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
from autogen_agentchat.agents import AssistantAgent, SocietyOfMindAgent,UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.ui import Console
from autogen_core.tools import FunctionTool
import asyncio



#Creating Open AI Model Client 
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("Please set OPENAI_API_KEY in your .env file.")

model_client = OpenAIChatCompletionClient(model="gpt-4o", api_key=api_key)

# =========== INNER TEAM FUNCTIONS ================


async def fetch_data(stock_symbol:str)->dict:
    ticker=yf.Ticker(stock_symbol)
    hist=ticker.history(period="6mo")
    print(f"📈 Fetched data for")
    return hist.to_dict()
stock_analysis_tool = FunctionTool(fetch_data, description="Analyze stock data and generate a plot")




## ============ AUTOGEN AGENTS =============

#  ======= Inner Team Agents =======
#Agent that fetches historical stock data

data_fetcher=AssistantAgent(
    name="DataFetcherAgent",
    model_client=model_client,
    system_message="You are a Data fetcher agent  who fetches latest stock data. Fetch stock data using the function :fetch_data",
    tools=[stock_analysis_tool]
)

#Agent that analyzes trends of the stock data
trend_analyzer=AssistantAgent(
    name="TrendAnalyzerAgent",
    model_client=model_client,
    system_message=" You are  an Analyzer agent who helps to Analyze Data Trends.Analyzes stock data and generate trend graphs",
    #tools=[generate_stock_chart_tool],
)
#Agent that generates summary of the stock trends
summary_generator=AssistantAgent(
    name="SummaryGeneratorAgent",
    model_client=model_client,
    system_message=" You are a summary generator of the  stock trends . Generate human-readable summary of stock analysis in English text  along with trend analysis graphs ",
)
inner_termination = TextMentionTermination("APPROVE")
inner_team= RoundRobinGroupChat([data_fetcher, trend_analyzer, summary_generator], max_turns=3)
# ========  Outer Team Agents ===========

#Outer Team Coordination Agent


#User Proxy Agent fro Human-in-the-loop

user_proxy=UserProxyAgent(
    name='UserProxy',
    #human_input_mode="ALWAYS", # Will always ask for User confirmation
    #code_execution_config=False

    description="You represent the human user and will be consulted for confirmation or extra input when needed.",
    input_func=input

)


# ======== Society Of Mind Agent ===========
society_of_mind=SocietyOfMindAgent(
    name="StockSoMTeam",
    model_client=model_client,
    team=inner_team,
    instruction="You are a Society of Mind Agent responsible  for co ordinating with internal or inner team agents",
    #max_turns=5
 
)

# ========= MAIN FUNCTION =========
termination_condition = TextMentionTermination(text='APPROVE')
team = RoundRobinGroupChat([society_of_mind, user_proxy], max_turns=4)

async def main():
    # Run the team chat stream
    print("Starting Stock Analysis...")

    stock_symbol = input("Enter stock symbol (e.g., AAPL, TSLA): ").upper()
    taskMessage = f"Analyze the stock symbol {stock_symbol}"
    print(f"🔍 Task: {taskMessage}")
    stream = team.run_stream(task=taskMessage)

    print("Please wait while the agents analyze the stock data...")
    print("This may take a few seconds depending on the stock symbol and data availability.")
    await Console(stream)
    
    

asyncio.run(main())





