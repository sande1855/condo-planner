import streamlit as st
import yfinance as yf
import datetime
import math

st.set_page_config(page_title="Down Payment Planner", layout="wide")

st.title("🏡 Condo Down Payment Planner")
st.write("Map out your path to homeownership based on your timeline, assets, and salary.")

# --- SIDEBAR: GOALS & TIMELINE ---
st.sidebar.header("Your Goal")
target_amount = st.sidebar.number_input("Target Down Payment ($)", min_value=0, value=50000, step=1000)
target_date = st.sidebar.date_input("Target Purchase Date", datetime.date.today() + datetime.timedelta(days=365))

# Calculate biweekly paychecks remaining
days_remaining = (target_date - datetime.date.today()).days
paychecks_remaining = max(1, math.floor(days_remaining / 14))

# --- MAIN PAGE: INPUTS ---
col1, col2 = st.columns(2)

with col1:
    st.header("1. Income & Expenses")
    biweekly_net_pay = st.number_input("Biweekly Salary (Post-Tax)", min_value=0, value=3000)
    monthly_expenses = st.number_input("Current Monthly Expenses", min_value=0, value=4000)
    
    st.header("2. Current Assets")
    current_savings = st.number_input("Current Savings Allocated", min_value=0, value=10000)
    family_gift = st.number_input("Additional Funding (e.g., Family Gift)", min_value=0, value=0)

with col2:
    st.header("3. Stocks & Equity")
    stock_ticker = st.text_input("Current Stock Ticker (e.g., AAPL, GOOG)", "AAPL")
    stock_shares = st.number_input("Number of Shares You Own", min_value=0.0, value=10.0)
    
    # Pull live stock price
    live_stock_value = 0
    if stock_ticker:
        try:
            ticker_data = yf.Ticker(stock_ticker)
            current_price = ticker_data.history(period="1d")['Close'].iloc[0]
            live_stock_value = current_price * stock_shares
            st.success(f"Live {stock_ticker.upper()} Price: **${current_price:.2f}** | Total Value: **${live_stock_value:,.2f}**")
        except:
            st.error("Could not fetch stock price. Check the ticker symbol.")

    st.header("4. Future Inflows")
    st.subheader("Unvested Stock")
    unvested_value = st.number_input("Estimated Unvested Stock Value ($)", min_value=0, value=5000)
    unvested_devote_pct = st.slider("% of Unvested Stock Devoted to House", 0, 100, 50)
    unvested_contribution = unvested_value * (unvested_devote_pct / 100)
    
    st.subheader("Future Bonuses")
    future_bonus = st.number_input("Estimated Future Bonus (Post-Tax $)", min_value=0, value=10000)
    bonus_devote_pct = st.slider("% of Bonus Devoted to House", 0, 100, 75)
    bonus_contribution = future_bonus * (bonus_devote_pct / 100)

# --- CALCULATIONS & RESULTS ---
st.markdown("---")
st.header("📊 Your Action Plan")

total_assets = current_savings + family_gift + live_stock_value + unvested_contribution + bonus_contribution
amount_needed = max(0, target_amount - total_assets)

if amount_needed == 0:
    st.balloons()
    st.success("🎉 You already have enough assets to cover your down payment goal!")
else:
    savings_per_paycheck = amount_needed / paychecks_remaining
    biweekly_free_cashflow = biweekly_net_pay - (monthly_expenses / 2) # Rough translation of monthly expenses to biweekly
    
    st.write(f"**Total Goal:** ${target_amount:,.2f}")
    st.write(f"**Current & Future Allocated Assets:** ${total_assets:,.2f}")
    st.write(f"**Amount Remaining to Save:** ${amount_needed:,.2f}")
    st.write(f"**Paychecks Until Target Date:** {paychecks_remaining}")
    
    st.info(f"### 👉 You need to save **${savings_per_paycheck:,.2f}** from each biweekly paycheck.")
    
    if savings_per_paycheck > biweekly_free_cashflow:
        st.warning(f"⚠️ **Warning:** Your needed savings (${savings_per_paycheck:,.2f}) exceed your estimated free cash flow per paycheck (${biweekly_free_cashflow:,.2f}). Consider extending your timeline or adjusting your goal.")
    else:
        st.success(f"✅ This looks doable! You will have about **${(biweekly_free_cashflow - savings_per_paycheck):,.2f}** left over for discretionary spending per paycheck.")
