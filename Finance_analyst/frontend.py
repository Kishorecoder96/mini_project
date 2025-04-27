import streamlit as st
import pandas as pd
from main import run_research_agent, run_financial_agent, format_stock_data
import plotly.graph_objects as go
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="Multi-Agent Interface", layout="wide")

# --- App Title ---
st.title("🧠 FINANALYST")

# --- Input Area ---
prompt = st.text_area("Prompt", placeholder="Type your question or command here...")

# --- Agent Selection ---
st.subheader("Choose one or more agents:")
selected_agents = st.multiselect(
    label="Agents",
    options=["🔍 Research Agent", "💰 Financial Agent"],
    default=[]
)

def create_stock_chart(df):
    """Create an interactive stock price chart"""
    fig = go.Figure(data=[
        go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        ),
        go.Scatter(
            x=df['Date'],
            y=df['Close'],
            line=dict(color='blue', width=1),
            name='Close Price',
            opacity=0.5
        )
    ])
    
    fig.update_layout(
        title='Stock Price History',
        yaxis_title='Price',
        xaxis_title='Date',
        template='plotly_white'
    )
    
    return fig

def format_financial_analysis(response):
    """Format financial analysis text with proper styling"""
    # Extract content from RunResponse object
    if hasattr(response, 'content'):
        text = response.content
    else:
        text = str(response)
        
    # Split the text into sections
    sections = text.split('\n\n')
    
    for section in sections:
        if section.strip():  # Only process non-empty sections
            if section.startswith('#'):
                # Handle headers
                header_level = len(section.split()[0])  # Count the number of #
                cleaned_header = section.lstrip('#').strip()
                if header_level == 1:
                    st.title(cleaned_header)
                elif header_level == 2:
                    st.header(cleaned_header)
                else:
                    st.subheader(cleaned_header)
            elif section.startswith('*'):
                # Handle bullet points
                st.markdown(section)
            elif section.startswith('---'):
                # Handle horizontal rules
                st.markdown('---')
            else:
                # Handle regular paragraphs
                st.write(section)

# --- Backend Logic ---
def handle_prompt(agent_key, prompt):
    if not prompt.strip():
        return "⚠️ Please enter a valid prompt."

    try:
        response = None
        if agent_key == "research":
            response = run_research_agent(prompt)
        
        elif agent_key == "financial":
            response = run_financial_agent(prompt)
        else:
            return "⚠️ Unknown agent."

        # Check if response contains stock data (dictionary with timestamp keys)
        if isinstance(response, dict) and any(str(key).isdigit() for key in response.keys()):
            df = format_stock_data(response)
            
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["📈 Chart", "📊 Data Table", "📥 Download"])
            
            with tab1:
                st.plotly_chart(create_stock_chart(df), use_container_width=True)
            
            with tab2:
                st.write("### Stock Market Data")
                st.dataframe(
                    df,
                    hide_index=True,
                    column_config={
                        "Date": st.column_config.DateColumn("Date", format="MMM DD, YYYY"),
                        "Open": st.column_config.NumberColumn("Open", format="$%.2f"),
                        "High": st.column_config.NumberColumn("High", format="$%.2f"),
                        "Low": st.column_config.NumberColumn("Low", format="$%.2f"),
                        "Close": st.column_config.NumberColumn("Close", format="$%.2f"),
                        "Volume": st.column_config.NumberColumn("Volume", format="%d"),
                        "Dividends": st.column_config.NumberColumn("Dividends", format="%.4f"),
                        "Stock Splits": st.column_config.NumberColumn("Stock Splits", format="%.1f")
                    },
                    use_container_width=True
                )
            
            with tab3:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Data as CSV",
                    data=csv,
                    file_name="stock_data.csv",
                    mime="text/csv"
                )
            
            # Calculate and display key statistics
            st.write("### 📊 Key Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Latest Close", f"${df['Close'].iloc[0]:.2f}", 
                         f"{((df['Close'].iloc[0] - df['Close'].iloc[1])/df['Close'].iloc[1]*100):.2f}%")
            with col2:
                st.metric("Highest Price", f"${df['High'].max():.2f}")
            with col3:
                st.metric("Lowest Price", f"${df['Low'].min():.2f}")
            with col4:
                st.metric("Avg Volume", f"{df['Volume'].astype(float).mean():,.0f}")
            
            return "Data analysis complete ✅"
            
        else:
            # Handle text-based financial analysis
            format_financial_analysis(response)
            return ""

    except Exception as e:
        return f"❌ Error from {agent_key} agent: {str(e)}"

# --- Mapping Labels to Internal Keys ---
label_to_key = {
    "🔍 Research Agent": "research",
    "💰 Financial Agent": "financial"
}

# --- Submit Button ---
if st.button("🚀 Run"):
    if not selected_agents:
        st.warning("Please select at least one agent.")
    else:
        st.markdown("### 💬 Agent Responses:")
        for label in selected_agents:
            agent_key = label_to_key[label]
            with st.expander(f"{label} Response", expanded=True):
                response = handle_prompt(agent_key, prompt)
                if response:  # Only show if there's a text response
                    st.markdown(response)

# Add some spacing at the bottom
st.markdown("<br><br>", unsafe_allow_html=True)
