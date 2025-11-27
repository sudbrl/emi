import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone, date
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

# ============================================================================
# VISUAL STYLING & CONFIG
# ============================================================================
def load_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #374151;
            font-size: 14px;
        }
        h1, h2, h3 {
            font-family: 'Poppins', sans-serif;
            color: #1e293b;
            font-weight: 600;
        }
        .stApp { background: linear-gradient(135deg, #f8fafc, #e2e8f0); }
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 1rem !important;
            max-width: 95% !important;
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(to bottom, #f0f9ff, #e0f2fe);
            border-right: 1px solid #94a3b8;
        }
        div[data-testid="stMetric"] {
            background: linear-gradient(to bottom, #e0f2fe, #f0f9ff);
            border: 1px solid #60a5fa;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .info-box {
            background-color: #f0fdfa;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #0d9488;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            color: #1e293b;
            margin-bottom: 20px;
        }
        div[data-testid="column"] button {
            border: 1px solid #ef4444;
            color: #ef4444;
        }
        div[data-testid="column"] button:hover {
            background-color: #fee2e2;
            border-color: #dc2626;
        }
        
        /* CATCHY PRIMARY BUTTON STYLING */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(90deg, #0d9488, #2dd4bf) !important;
            border: none !important;
            border-radius: 50px !important; /* Pill shape */
            color: white !important;
            padding: 0.6rem 1.5rem !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            box-shadow: 0 10px 20px -10px rgba(13, 148, 136, 0.5) !important;
            transition: all 0.3s ease !important;
            white-space: nowrap;
        }
        div.stButton > button[kind="primary"]:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 14px 24px -10px rgba(13, 148, 136, 0.6) !important;
            background: linear-gradient(90deg, #0f766e, #14b8a6) !important;
        }
        div.stButton > button[kind="primary"]:active {
            transform: translateY(-1px) !important;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

# ============================================================================
# BS CALENDAR DATA
# ============================================================================
BS_MONTHS = {
    2070: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
    2071: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2072: [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2073: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2074: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2075: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2076: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    2077: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2078: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2079: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2080: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    2081: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2082: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2083: [31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30],
    2084: [31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30],
    2085: [31, 32, 31, 32, 30, 31, 30, 30, 29, 30, 30, 30],
    2086: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2087: [31, 31, 32, 31, 31, 31, 30, 30, 30, 30, 30, 30],
    2088: [30, 31, 32, 32, 30, 31, 30, 30, 29, 30, 30, 30],
    2089: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2090: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
}

BS_REFERENCE_YEAR = 2070
BS_REFERENCE_MONTH = 1
BS_REFERENCE_DAY = 1
AD_REFERENCE_DATE = datetime(2013, 4, 14)

# ============================================================================
# DATE HELPERS
# ============================================================================
def get_nepal_time():
    utc_now = datetime.now(timezone.utc)
    nepal_time = utc_now + timedelta(hours=5, minutes=45)
    return nepal_time.date()

def ad_to_bs(ad_date):
    if isinstance(ad_date, pd.Timestamp): ad_date = ad_date.to_pydatetime()
    if isinstance(ad_date, date) and not isinstance(ad_date, datetime):
        ad_date = datetime.combine(ad_date, datetime.min.time())
    
    delta = (ad_date - AD_REFERENCE_DATE).days
    bs_year, bs_month, bs_day = BS_REFERENCE_YEAR, BS_REFERENCE_MONTH, BS_REFERENCE_DAY
    
    if delta >= 0:
        bs_day += delta
        while True:
            if bs_year not in BS_MONTHS: return None, None, None
            month_days = BS_MONTHS[bs_year]
            days_in_month = month_days[bs_month - 1]
            if bs_day <= days_in_month: break
            bs_day -= days_in_month
            bs_month += 1
            if bs_month > 12:
                bs_month = 1
                bs_year += 1
    return bs_year, bs_month, bs_day

def bs_to_ad(bs_year, bs_month, bs_day):
    days_diff = 0
    ref_tuple = (BS_REFERENCE_YEAR, BS_REFERENCE_MONTH, BS_REFERENCE_DAY)
    target_tuple = (bs_year, bs_month, bs_day)
    
    if target_tuple == ref_tuple: return AD_REFERENCE_DATE
    
    if target_tuple > ref_tuple:
        for y in range(BS_REFERENCE_YEAR, bs_year):
            days_diff += sum(BS_MONTHS[y])
        for m in range(1, bs_month):
            days_diff += BS_MONTHS[bs_year][m-1]
        days_diff += (bs_day - 1)
        return AD_REFERENCE_DATE + timedelta(days=days_diff)
    return AD_REFERENCE_DATE

def format_bs_date(bs_y, bs_m, bs_d):
    return f"{bs_y:04d}/{bs_m:02d}/{bs_d:02d}" if bs_y else "-"

def get_next_payment_date(current_date, is_quarterly=False):
    if is_quarterly:
        return get_next_bs_quarter_end(current_date)
    else:
        if current_date.day < 10:
            return datetime(current_date.year, current_date.month, 10)
        else:
            year = current_date.year + (current_date.month // 12)
            month = (current_date.month % 12) + 1
            return datetime(year, month, 10)

def get_next_bs_quarter_end(from_date_ad):
    bs_y, bs_m, bs_d = ad_to_bs(from_date_ad)
    if bs_y is None: return from_date_ad + timedelta(days=90)
    
    if bs_m < 3: target_m, target_y = 3, bs_y
    elif bs_m < 6: target_m, target_y = 6, bs_y
    elif bs_m < 9: target_m, target_y = 9, bs_y
    elif bs_m < 12: target_m, target_y = 12, bs_y
    else: target_m, target_y = 3, bs_y + 1
    
    if target_y not in BS_MONTHS: return from_date_ad + timedelta(days=90)
    
    target_d = BS_MONTHS[target_y][target_m - 1]
    target_ad = bs_to_ad(target_y, target_m, target_d)
    
    if target_ad <= from_date_ad:
        return get_next_bs_quarter_end(from_date_ad + timedelta(days=1))
    return target_ad

# ============================================================================
# CALCULATION ENGINE
# ============================================================================

def get_active_rate_at_date(check_date, rate_schedule):
    active_rate = 0
    for item in rate_schedule:
        if item['date'] <= check_date:
            active_rate = item['rate']
        else:
            break
    return active_rate

def calculate_composite_interest(principal, start_date, end_date, rate_schedule):
    if start_date >= end_date: return 0.0
    
    relevant_changes = [r['date'] for r in rate_schedule if start_date < r['date'] < end_date]
    timeline = [start_date] + relevant_changes + [end_date]
    
    total_interest = 0.0
    
    for i in range(len(timeline) - 1):
        seg_start = timeline[i]
        seg_end = timeline[i+1]
        days = (seg_end - seg_start).days
        rate = get_active_rate_at_date(seg_start, rate_schedule)
        interest = (principal * rate * days) / (100 * 365)
        total_interest += interest
        
    return total_interest

def calculate_emi_amount(principal, annual_rate, tenure_remaining, is_quarterly):
    if tenure_remaining <= 0: return principal
    
    rate_per_period = (annual_rate / (4 * 100)) if is_quarterly else (annual_rate / (12 * 100))
        
    if rate_per_period == 0: return principal / tenure_remaining
        
    emi = (principal * rate_per_period * (1 + rate_per_period)**tenure_remaining) / \
          ((1 + rate_per_period)**tenure_remaining - 1)
    return emi

def calculate_dynamic_schedule(principal, initial_rate, total_tenure_periods, start_date, rate_changes_input, is_quarterly=False):
    rate_schedule = [{'date': start_date, 'rate': initial_rate}]
    
    if rate_changes_input:
        for r in rate_changes_input:
            if r['date'] <= start_date:
                rate_schedule = [{'date': start_date, 'rate': r['rate']}]
            else:
                rate_schedule.append(r)
    
    rate_schedule.sort(key=lambda x: x['date'])
    
    # --- UPDATED LOGIC: FIXED EMI, VARIABLE TENURE ---
    
    # 1. Calculate Base EMI (Fixed Payment) based on initial conditions
    fixed_payment = calculate_emi_amount(principal, initial_rate, total_tenure_periods, is_quarterly)
    
    schedule = []
    balance = principal
    prev_payment_date = start_date
    
    current_payment_date = get_next_payment_date(start_date, is_quarterly)
    iteration = 0
    # Safety limit for extended tenure (e.g., 50 years worth of payments to prevent infinite loops)
    max_iterations = 600 if not is_quarterly else 200 
    
    while balance > 1.0 and iteration < max_iterations:
        iteration += 1
        interest_amount = calculate_composite_interest(balance, prev_payment_date, current_payment_date, rate_schedule)
        current_rate_display = get_active_rate_at_date(prev_payment_date, rate_schedule)
        
        is_first_payment = (iteration == 1)
        is_start_1_to_10 = (1 <= start_date.day <= 10)
        
        if is_first_payment and is_start_1_to_10:
            # Interest Only Rule for specific first payment condition
            principal_component = 0
            payment_amount = interest_amount
        else:
            # Standard Payment is FIXED based on initial calculation
            payment_amount = fixed_payment
            
            # Check for Last Payment
            total_due = balance + interest_amount
            if total_due <= payment_amount:
                # Last payment is usually smaller
                payment_amount = total_due
                principal_component = balance
            else:
                # Standard calculation
                principal_component = payment_amount - interest_amount
                # Note: principal_component can be negative here (Negative Amortization)
                # This is allowed and increases the balance/tenure.

        closing_balance = balance - principal_component
        
        bs_y, bs_m, bs_d = ad_to_bs(current_payment_date)
        
        schedule.append({
            'Period': iteration,
            'Payment Date (AD)': current_payment_date.strftime('%Y-%m-%d'),
            'Payment Date (BS)': format_bs_date(bs_y, bs_m, bs_d),
            'Opening Balance': round(balance, 2),
            'Payment': round(payment_amount, 2),
            'Interest': round(interest_amount, 2),
            'Principal': round(principal_component, 2),
            'Closing Balance': round(closing_balance, 2),
            'Interest Rate (%)': current_rate_display
        })
        
        balance = closing_balance
        prev_payment_date = current_payment_date
        current_payment_date = get_next_payment_date(current_payment_date, is_quarterly)

    return pd.DataFrame(schedule)

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================
def create_excel_template():
    df = pd.DataFrame({
        'Date': ['2025-12-20', '2026-06-15'],
        'Rate': [13.5, 12.5]
    })
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Rate Changes', index=False)
    output.seek(0)
    return output

def parse_excel_rate_changes(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = [c.strip().lower() for c in df.columns]
        date_col = next((c for c in df.columns if 'date' in c), None)
        rate_col = next((c for c in df.columns if 'rate' in c), None)
        
        if not date_col or not rate_col:
            return None, "Columns 'Date' and 'Rate' required."
            
        changes = []
        for _, row in df.iterrows():
            d_val = row[date_col]
            r_val = row[rate_col]
            if pd.isna(d_val) or pd.isna(r_val): continue
            
            if isinstance(d_val, str):
                d_obj = pd.to_datetime(d_val).to_pydatetime()
            else:
                d_obj = pd.to_datetime(d_val).to_pydatetime()
            changes.append({'date': d_obj, 'rate': float(r_val)})
        return changes, None
    except Exception as e:
        return None, str(e)

def generate_pdf(schedule, principal, total_payment, total_interest, is_quarterly):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    styles = getSampleStyleSheet()
    
    label = "Quarterly" if is_quarterly else "Monthly"
    
    elements.append(Paragraph(f"{label} Repayment Schedule", styles['Heading1']))
    elements.append(Spacer(1, 12))
    
    summary_data = [
        ['Loan Amount:', f'Rs. {principal:,.2f}'],
        ['Total Payment:', f'Rs. {total_payment:,.2f}'],
        ['Total Interest:', f'Rs. {total_interest:,.2f}'],
    ]
    t = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    data = [['#', 'Date (AD)', 'Date (BS)', 'Opening', 'Payment', 'Int.', 'Prin.', 'Closing']]
    for _, row in schedule.iterrows():
        data.append([
            str(row['Period']),
            row['Payment Date (AD)'],
            row['Payment Date (BS)'],
            f"{row['Opening Balance']:,.0f}",
            f"{row['Payment']:,.0f}",
            f"{row['Interest']:,.0f}",
            f"{row['Principal']:,.0f}",
            f"{row['Closing Balance']:,.0f}"
        ])
        
    t_sch = Table(data, colWidths=[0.4*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.7*inch, 0.8*inch, 0.9*inch])
    t_sch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    elements.append(t_sch)
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_excel(schedule, principal, total_payment, total_interest, tenure, rate_label):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        schedule.to_excel(writer, sheet_name='Repayment Schedule', index=False)
        summary_df = pd.DataFrame({
            'Item': ['Principal Amount', 'Initial Interest Rate', 'Tenure', 'Total Payment', 'Total Interest Paid'],
            'Value': [principal, rate_label, tenure, total_payment, total_interest]
        })
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        worksheet = writer.sheets['Repayment Schedule']
        for column_cells in worksheet.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2
    buffer.seek(0)
    return buffer

# ============================================================================
# STREAMLIT UI
# ============================================================================
def init_session_state():
    if 'rate_changes' not in st.session_state: st.session_state.rate_changes = []
    if 'calculated' not in st.session_state: st.session_state.calculated = True

init_session_state()

def main():
    st.set_page_config(page_title="Loan Repayment Planner", page_icon=":bank:", layout="wide")
    load_custom_css()
    
    st.title(":bank: Loan Repayment Planner")
    
    st.markdown("""
    <div class='info-box'>
        <strong>Calculation Rules Applied:</strong><br>
        1. <strong>Fixed EMI/EQI:</strong> Monthly/Quarterly payment is determined by initial loan terms and remains fixed.<br>
        2. <strong>Variable Tenure:</strong> If interest rates change, the loan duration extends or shortens to accommodate the fixed payment.<br>
        3. <strong>Daily Interest:</strong> Interest calculated on exact days between payments.<br>
        4. <strong>1st-10th Rule:</strong> If Loan starts between 1st-10th, first payment is Interest Only.
    </div>
    """, unsafe_allow_html=True)
    
    col_freq, _ = st.columns([1, 2])
    with col_freq:
        freq = st.radio("Frequency", ["Monthly (EMI)", "Quarterly (EQI)"], horizontal=True)
        is_quarterly = (freq == "Quarterly (EQI)")

    with st.sidebar:
        st.header("Loan Details")
        principal = st.number_input("Principal (Rs.)", value=1000000, step=10000)
        rate = st.number_input("Initial Interest Rate (%)", value=12.0, step=0.1)
        tenure = st.number_input("Tenure (Months/Quarters)", value=60 if not is_quarterly else 20)
        
        st.markdown("### Start Date")
        is_bs = st.toggle("Use BS Date", value=False)
        nepal_today = get_nepal_time()
        
        if not is_bs:
            start_date_input = st.date_input("Start Date (AD)", value=nepal_today)
            start_datetime = datetime.combine(start_date_input, datetime.min.time())
        else:
            cur_bs_y, cur_bs_m, cur_bs_d = ad_to_bs(nepal_today)
            c1, c2, c3 = st.columns(3)
            y = c1.number_input("Year", 2070, 2090, cur_bs_y)
            m = c2.number_input("Month", 1, 12, cur_bs_m)
            d = c3.number_input("Day", 1, 32, cur_bs_d)
            start_datetime = bs_to_ad(y, m, d)
            st.caption(f"AD: {start_datetime.date()}")

        st.markdown("---")
        st.markdown("### Rate Changes")
        
        template_data = create_excel_template()
        st.download_button(
            label="Download Template (Excel)",
            data=template_data,
            file_name="rate_changes_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        uploaded = st.file_uploader("Upload Excel (Date, Rate)", type=['xlsx'])
        if uploaded:
            changes, err = parse_excel_rate_changes(uploaded)
            if changes: 
                st.session_state.rate_changes = changes
                st.success(f"Loaded {len(changes)} changes")
        
        with st.expander("Add Manual Change"):
            md = st.date_input("Date", value=nepal_today + timedelta(days=365))
            mr = st.number_input("New Rate %", value=13.0)
            if st.button("Add Rate Change"):
                st.session_state.rate_changes.append({
                    'date': datetime.combine(md, datetime.min.time()), 
                    'rate': mr
                })
        
        if st.session_state.rate_changes:
            st.markdown("**Scheduled Changes:**")
            sorted_changes = sorted(st.session_state.rate_changes, key=lambda x: x['date'])
            for i, change in enumerate(sorted_changes):
                cols = st.columns([0.7, 0.3])
                with cols[0]:
                    st.write(f"{change['date'].strftime('%Y-%m-%d')}: **{change['rate']}%**")
                with cols[1]:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state.rate_changes.remove(change)
                        st.rerun()
            if st.button("Reset All Changes", use_container_width=True):
                st.session_state.rate_changes = []
                st.rerun()

    st.markdown("---")
    # Change: Swap columns to put the button on the left
    col_btn, col_space = st.columns([1.5, 3]) 
    with col_btn:
        if st.button("GENERATE SCHEDULE 🚀", type="primary", use_container_width=True):
            st.session_state.calculated = True

    # Main Display
    if st.session_state.calculated:
        periods = int(tenure)
        
        df = calculate_dynamic_schedule(
            principal, rate, periods, start_datetime, 
            st.session_state.rate_changes, is_quarterly
        )
        
        tot_pay = df['Payment'].sum()
        tot_int = df['Interest'].sum()
        last_emi = df.iloc[-2]['Payment'] if len(df) > 1 else df.iloc[0]['Payment']
        
        # Display Final Tenure Metric
        final_tenure = df.iloc[-1]['Period']
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Repayment", f"Rs. {tot_pay:,.0f}")
        m2.metric("Total Interest", f"Rs. {tot_int:,.0f}")
        m3.metric("Regular Payment", f"Rs. {df.iloc[1]['Payment'] if len(df)>1 else df.iloc[0]['Payment']:,.0f}")
        m4.metric("Actual Tenure", f"{final_tenure} {'Qtrs' if is_quarterly else 'Mths'}")
        
        t1, t2, t3 = st.tabs(["Schedule", "Charts", "Export"])
        
        with t1:
            st.dataframe(df, use_container_width=True, height=500)
            
        with t2:
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=df['Period'], y=df['Closing Balance'], 
                mode='lines', fill='tozeroy', name='Balance',
                line=dict(color='#6366f1', width=3)
            ))
            fig_line.update_layout(title="Outstanding Balance Over Time", height=350, template='plotly_white')
            st.plotly_chart(fig_line, use_container_width=True)

            c_chart_1, c_chart_2 = st.columns(2)
            
            with c_chart_1:
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(x=df['Period'], y=df['Principal'], name='Principal', marker_color='#0d9488'))
                fig_bar.add_trace(go.Bar(x=df['Period'], y=df['Interest'], name='Interest', marker_color='#f59e0b'))
                fig_bar.update_layout(barmode='stack', title='Monthly Breakdown', height=350, template='plotly_white')
                st.plotly_chart(fig_bar, use_container_width=True)

            with c_chart_2:
                fig_pie = go.Figure(data=[go.Pie(
                    labels=['Principal', 'Interest'],
                    values=[df['Principal'].sum(), df['Interest'].sum()],
                    hole=.4,
                    marker_colors=['#0d9488', '#f59e0b']
                )])
                fig_pie.update_layout(title="Total Cost Distribution", height=350, template='plotly_white')
                st.plotly_chart(fig_pie, use_container_width=True)
            
        with t3:
            st.subheader("Download Options")
            c1, c2, c3 = st.columns(3)
            
            csv = df.to_csv(index=False).encode('utf-8')
            c1.download_button("Download CSV", csv, "schedule.csv", "text/csv", use_container_width=True)
            
            excel_data = generate_excel(df, principal, tot_pay, tot_int, tenure, f"{rate}%")
            c2.download_button(
                label="Download Excel",
                data=excel_data,
                file_name="repayment_schedule.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            pdf = generate_pdf(df, principal, tot_pay, tot_int, is_quarterly)
            c3.download_button(
                label="Download PDF", 
                data=pdf, 
                file_name="schedule.pdf", 
                mime="application/pdf",
                use_container_width=True
            )

if __name__ == "__main__":
    main()
