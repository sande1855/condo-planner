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
# --- CHICAGO CONSIDERATIONS ---
st.markdown("---")
st.header("🏙️ Chicago Condo Considerations")

with st.expander("Click here to view important factors for buying in Chicago"):
    st.markdown("""
    * **HOA Fees / Assessments:** In Chicago, high-rise HOAs are notoriously high (often $500 to $1,500+ a month). However, they usually include water, trash, snow removal, exterior maintenance, and often heat, AC, basic cable, and internet. Vintage walk-ups will have lower HOAs, but you'll pay your own utilities.
    * **Special Assessments:** Older brick/limestone walk-ups (very common in Lakeview, Lincoln Park, Logan Square) often face facade repairs. If the condo association hasn't saved enough in their "reserves," they will issue a special assessment. You could be hit with a sudden $5,000–$20,000 bill. Always ask to see the reserve study before buying.
    * **Property Taxes (Cook County):** Chicago property taxes are high and paid *in arrears* (meaning you pay last year's taxes this year). They are billed in two installments, and the second installment is routinely delayed or significantly higher due to reassessments. Make sure your mortgage escrow over-prepares for this.
    * **Deeded vs. Leased Parking:** Parking is rarely automatically included. A "deeded" parking spot means you own it, adding $15,000 to $40,000 to your purchase price, and it has its own property tax bill and HOA fee. Alternatively, you can lease a spot in the building (usually $150–$300/month).
    * **Owner Occupancy Ratios:** If you ever plan to rent the condo out later, check the building's rental cap. Many Chicago condo boards strictly cap the number of units that can be rented out, which can put you on a years-long waitlist.
    """)
