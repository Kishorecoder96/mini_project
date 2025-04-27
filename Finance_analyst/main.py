from dotenv import load_dotenv
import os
#libraries import
from textwrap import dedent 
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.newspaper4k import Newspaper4k
load_dotenv
import streamlit as st
api_key=os.getenv("GOOGLE_API_KEY")



from dotenv import load_dotenv
import os
#libraries import
from textwrap import dedent 
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.newspaper4k import Newspaper4k
load_dotenv

api_key=os.getenv("GOOGLE_API_KEY")

research_agent = Agent(
    model=Gemini(id="gemini-1.5-flash"),
    tools=[DuckDuckGo(), Newspaper4k()],
    description=dedent("""\
        You are an elite research analyst in the financial services domain.
        Your expertise encompasses:

        - Deep investigative financial research and analysis
        - fact-checking and source verification
        - Data-driven reporting and visualization
        - Expert interview synthesis
        - Trend analysis and future predictions
        - Complex topic simplification
        - Ethical practices
        - Balanced perspective presentation
        - Global context integration\
    """),
    instructions=dedent("""\
        1. Research Phase
           - Search for 5 authoritative sources on the topic
           - Prioritize recent publications and expert opinions
           - Identify key stakeholders and perspectives

        2. Analysis Phase
           - Extract and verify critical information
           - Cross-reference facts across multiple sources
           - Identify emerging patterns and trends
           - Evaluate conflicting viewpoints

        3. Writing Phase
           - Craft an attention-grabbing headline
           - Structure content in Financial Report style
           - Include relevant quotes and statistics
           - Maintain objectivity and balance
           - Explain complex concepts clearly

        4. Quality Control
           - Verify all facts and attributions
           - Ensure narrative flow and readability
           - Add context where necessary
           - Include future implications
    """),
    expected_output=dedent("""\
        # {Compelling Headline}

        ## Executive Summary
        {Concise overview of key findings and significance}

        ## Background & Context
        {Historical context and importance}
        {Current landscape overview}

        ## Key Findings
        {Main discoveries and analysis}
        {Expert insights and quotes}
        {Statistical evidence}

        ## Impact Analysis
        {Current implications}
        {Stakeholder perspectives}
        {Industry/societal effects}

        ## Future Outlook
        {Emerging trends}
        {Expert predictions}
        {Potential challenges and opportunities}

        ## Expert Insights
        {Notable quotes and analysis from industry leaders}
        {Contrasting viewpoints}

        ## Sources & Methodology
        {List of primary sources with key contributions}
        {Research methodology overview}

        ---
        Research conducted by Financial Agent
        Credit Rating Style Report
        Published: {current_date}
        Last Updated: {current_time}\
    """),
    markdown=True,
    show_tool_calls=True,
    add_datetime_to_instructions=True,
)

# User Prompt 1
def run_research_agent(prompt):
   return research_agent.run(prompt)

def run_financial_agent(prompt):
    return stock_agent.run(prompt)




from textwrap import dedent

from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.yfinance import YFinanceTools

stock_agent = Agent(
    model=Gemini(id="gemini-1.5-flash"),
    tools=[
        YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            stock_fundamentals=True,
            historical_prices=True,
            company_info=True,
            company_news=True,
        )
    ],
    instructions=dedent("""\
        You are a seasoned credit rating analyst with deep expertise in market analysis! 📊

        Follow these steps for comprehensive financial analysis:
        1. Market Overview
           - Latest stock price
           - 52-week high and low
        2. Financial Deep Dive
           - Key metrics (P/E, Market Cap, EPS)
        3. Market Context
           - Industry trends and positioning
           - Competitive analysis
           - Market sentiment indicators

        Your reporting style:
        - Begin with an executive summary
        - Use tables for data presentation
        - Include clear section headers
        - Highlight key insights with bullet points
        - Compare metrics to industry averages
        - Include technical term explanations
        - End with a forward-looking analysis

        Risk Disclosure:
        - Always highlight potential risk factors
        - Note market uncertainties
        - Mention relevant regulatory concerns
    """),
)

import pandas as pd
from datetime import datetime

def format_stock_data(data):
    """
    Format stock market data into a pandas DataFrame with proper table structure
    """
    # Convert the data into a list of dictionaries
    formatted_data = []
    for timestamp, values in data.items():
        row = {
            'Date': datetime.fromtimestamp(int(timestamp)/1000).strftime('%Y-%m-%d'),
            'Open': round(values['Open'], 2),
            'High': round(values['High'], 2),
            'Low': round(values['Low'], 2),
            'Close': round(values['Close'], 2),
            'Volume': format(values['Volume'], ','),
            'Dividends': values['Dividends'],
            'Stock Splits': values['Stock Splits']
        }
        formatted_data.append(row)
    
    # Create DataFrame and sort by date
    df = pd.DataFrame(formatted_data)
    df = df.sort_values(by='Date', ascending=False)
    
    return df

def display_stock_data_streamlit(data):
    """
    Display stock market data in a clean Streamlit table/dataframe
    """
    df = format_stock_data(data)
    
    # Add styling to the dataframe
    st.write("### Stock Market Data")
    st.dataframe(
        df,
        hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "Open": st.column_config.NumberColumn("Open", format="$%.2f"),
            "High": st.column_config.NumberColumn("High", format="$%.2f"),
            "Low": st.column_config.NumberColumn("Low", format="$%.2f"),
            "Close": st.column_config.NumberColumn("Close", format="$%.2f"),
            "Volume": st.column_config.NumberColumn("Volume", format="%d"),
            "Dividends": st.column_config.NumberColumn("Dividends", format="%.2f"),
            "Stock Splits": st.column_config.NumberColumn("Stock Splits", format="%.1f")
        },
        use_container_width=True
    )
    
    return df

def display_stock_data_streamlit_compact(data):
    """
    Display stock market data in a compact static table
    """
    df = format_stock_data(data)
    
    # Format the numeric columns before display
    df['Open'] = df['Open'].apply(lambda x: f'${x:,.2f}')
    df['High'] = df['High'].apply(lambda x: f'${x:,.2f}')
    df['Low'] = df['Low'].apply(lambda x: f'${x:,.2f}')
    df['Close'] = df['Close'].apply(lambda x: f'${x:,.2f}')
    df['Volume'] = df['Volume'].apply(lambda x: f'{x:,}')
    
    st.write("### Stock Market Data")
    st.table(df)
    
    return df

def get_stock_table_json(data):
    """
    Return stock data as JSON for frontend display
    """
    df = format_stock_data(data)
    return df.to_dict('records')

