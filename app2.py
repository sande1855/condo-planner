import streamlit as st
import yfinance as yf
import datetime
import math
import pandas as pd

st.set_page_config(page_title="Down Payment Planner", layout="wide")

# Banner Image
st.image("https://images.unsplash.com/photo-1494522855154-9297ac14b55f?q=80&w=2070&auto=format&fit=crop", use_container_width=True)

st.title("🏡 Condo Down Payment Planner")
st.write("Map out your path to homeownership based on your timeline, assets, and salary.")

# --- 1. GOAL & TIMELINE (Editable Action Plan inputs) ---
st.markdown("---")
st.header("🎯 1. Your Goal & Timeline")
colA, colB = st.columns(2)
target_amount = colA.number_input("Target Down Payment ($)", min_value=0, value=50000, step=1000)
target_date = colB.date_input("Target Purchase Date", datetime.date.today() + datetime.timedelta(days=365))

# Calculate biweekly paychecks remaining
days_remaining = (target_date - datetime.date.today()).days
paychecks_remaining = max(1, math.floor(days_remaining / 14))

# --- 2. CURRENT FINANCES ---
st.markdown("---")
st.header("💰 2. Current Finances & Assets")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Income & Expenses")
    biweekly_net_pay = st.number_input("Biweekly Salary (Post-Tax)", min_value=0, value=3000)
    monthly_expenses = st.number_input("Current Monthly Expenses", min_value=0, value=4000)
    
    st.subheader("Cash Assets")
    current_savings = st.number_input("Current Savings Allocated", min_value=0, value=10000)
    family_gift = st.number_input("Additional Funding (e.g., Family Gift)", min_value=0, value=0)

with col2:
    st.subheader("Current Stock & Equity")
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

# --- 3. FUTURE INFLOWS (Dynamic Tables) ---
st.markdown("---")
st.header("📈 3. Future Inflows")
st.write("Add your expected future bonuses and unvested stock below. You can add as many rows as you need! *(Note: The math will only count funds that vest/payout **before** your Target Purchase Date).*")

col_table1, col_table2 = st.columns(2)

with col_table1:
    st.subheader("Unvested Stock Grants")
    # Set up default table data
    default_stock = pd.DataFrame([
        {"Grant Name": "Grant 1", "Vesting Date": datetime.date.today() + datetime.timedelta(days=180), "Value ($)": 5000.0, "% Devoted to House": 50.0}
    ])
    # Create the interactive table
    stock_df = st.data_editor(default_stock, num_rows="dynamic", use_container_width=True)

with col_table2:
    st.subheader("Future Bonuses")
    # Set up default table data
    default_bonus = pd.DataFrame([
        {"Bonus Name": "Annual Bonus", "Payout Date": datetime.date.today() + datetime.timedelta(days=200), "Value ($)": 10000.0, "% Devoted to House": 75.0}
    ])
    # Create the interactive table
    bonus_df = st.data_editor(default_bonus, num_rows="dynamic", use_container_width=True)

# Calculate eligible future inflows based on the target date
unvested_contribution = 0
for index, row in stock_df.iterrows():
    if pd.to_datetime(row["Vesting Date"]).date() <= target_date:
        unvested_contribution += row["Value ($)"] * (row["% Devoted to House"] / 100)

bonus_contribution = 0
for index, row in bonus_df.iterrows():
    if pd.to_datetime(row["Payout Date"]).date() <= target_date:
        bonus_contribution += row["Value ($)"] * (row["% Devoted to House"] / 100)

# --- 4. ACTION PLAN & RESULTS ---
st.markdown("---")
st.header("📊 4. Your Action Plan")

total_assets = current_savings + family_gift + live_stock_value + unvested_contribution + bonus_contribution
amount_needed = max(0, target_amount - total_assets)

if amount_needed == 0:
    st.balloons()
    st.success("🎉 You already have enough assets to cover your down payment goal!")
else:
    savings_per_paycheck = amount_needed / paychecks_remaining
    biweekly_free_cashflow = biweekly_net_pay - (monthly_expenses / 2)
    
    # Dashboard style metric cards
    col_res1, col_res2, col_res3 = st.columns(3)
    col_res1.metric(label="🎯 Total Goal", value=f"${target_amount:,.0f}")
    col_res2.metric(label="💰 Current & Future Assets", value=f"${total_assets:,.0f}")
    col_res3.metric(label="📉 Amount Left to Save", value=f"${amount_needed:,.0f}")
    
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
