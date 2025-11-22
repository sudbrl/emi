import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone, date
import calendar
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

# ============================================================================
# PREMIUM VISUAL STYLING & CONFIG
# ============================================================================
def load_custom_css():
    st.markdown("""
        <style>
        /* Import Premium Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@400;500;600;700;800&display=swap');
        
        /* Global Settings */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #1e293b;
            font-size: 15px;
            line-height: 1.6;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Poppins', sans-serif;
            font-weight: 700;
            letter-spacing: -0.02em;
        }

        /* App Background */
        .stApp {
            background: linear-gradient(135deg, #f0f9ff 0%, #cffafe 100%);
            background-attachment: fixed;
        }
        
        /* Main Content Container */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            max-width: 1400px !important;
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(12px);
            border-radius: 24px;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.5);
            margin-top: 1rem;
            margin-bottom: 2rem;
        }
        
        /* Sidebar Container */
        section[data-testid="stSidebar"] {
            background: #0f172a; /* Slate 900 */
            border-right: none;
            box-shadow: 4px 0 24px rgba(0, 0, 0, 0.2);
        }
        
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] .stMarkdown {
            color: #f8fafc !important;
        }
        
        /* ============================================= */
        /* INPUT FIELDS STYLING */
        /* ============================================= */
        
        /* 1. Main Area Inputs (Light Mode) */
        .stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] {
            background-color: #ffffff !important; 
            border: 1px solid #94a3b8 !important;
            color: #0f172a !important; 
            border-radius: 8px !important;
        }

        /* 2. Sidebar Inputs (Dark Mode) */
        section[data-testid="stSidebar"] .stTextInput input,
        section[data-testid="stSidebar"] .stNumberInput input,
        section[data-testid="stSidebar"] .stDateInput input,
        section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
            background-color: #334155 !important; 
            border: 1px solid #475569 !important;
            color: #ffffff !important; 
        }
        
        /* Sidebar Stepper Buttons & Icons Fix */
        section[data-testid="stSidebar"] [data-testid="stNumberInput"] button {
            background-color: transparent !important;
            color: white !important;
            border: none !important;
        }
        section[data-testid="stSidebar"] [data-testid="stNumberInput"] svg,
        section[data-testid="stSidebar"] [data-testid="stDateInput"] svg,
        section[data-testid="stSidebar"] [data-testid="stSelectbox"] svg {
            fill: white !important;
        }

        /* ============================================= */
        /* BUTTON STYLING */
        /* ============================================= */
        
        /* Global Buttons (Base Style) */
        .stButton > button, .stDownloadButton > button {
            border-radius: 10px;
            font-weight: 600;
            border: none;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* 1. MAIN AREA BUTTONS (Light Theme) */
        .block-container .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%);
            color: white;
        }
        
        .block-container .stButton > button:not([kind="primary"]) {
            background: white;
            border: 1px solid #ef4444;
            color: #ef4444;
        }
        
        .block-container .stDownloadButton > button {
            background: #f1f5f9;
            color: #334155;
            border: 1px solid #cbd5e1;
        }
        .block-container .stDownloadButton > button:hover {
            background: #e2e8f0;
            color: #0f172a;
            border-color: #94a3b8;
        }

        /* 2. SIDEBAR BUTTONS (Dark Theme Fixes) */
        section[data-testid="stSidebar"] .stDownloadButton > button {
            background-color: #334155 !important;
            color: #ffffff !important;
            border: 1px solid #475569 !important;
        }
        section[data-testid="stSidebar"] .stDownloadButton > button:hover {
            background-color: #0d9488 !important;
            border-color: #0d9488 !important;
            color: white !important;
        }
        
        section[data-testid="stSidebar"] .stButton > button {
            background-color: #334155 !important;
            color: #ffffff !important;
            border: 1px solid #475569 !important;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            background-color: #0d9488 !important;
            border-color: #0d9488 !important;
            color: white !important;
        }

        /* ============================================= */
        
        div[data-testid="stMetric"] {
            background: white;
            border-left: 5px solid #0d9488;
            padding: 1rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        .stTabs [data-baseweb="tab-list"] {
            border-bottom: 2px solid #e2e8f0;
        }
        
        .stTabs [aria-selected="true"] {
            color: #0d9488;
            border-bottom: 3px solid #0d9488;
        }
        
        .info-box {
            background: #f0fdfa;
            padding: 1.25rem;
            border-radius: 12px;
            border-left: 5px solid #0d9488;
            color: #134e4a;
            margin-bottom: 1.5rem;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

# ============================================================================
# BS CALENDAR DATA (VERIFIED)
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
    2091: [31, 31, 32, 31, 31, 31, 30, 30, 29, 30, 30, 30],
    2092: [30, 31, 32, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2093: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2094: [31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30],
    2095: [31, 31, 32, 31, 31, 31, 30, 29, 30, 30, 30, 30],
    2096: [30, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2097: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2098: [31, 31, 32, 31, 31, 31, 29, 30, 29, 30, 29, 31],
    2099: [31, 31, 32, 31, 31, 31, 30, 29, 29, 30, 30, 30],
    2100: [31, 32, 31, 32, 30, 31, 30, 29, 30, 29, 30, 30],
    2101: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
    2102: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2103: [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2104: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2105: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2106: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2107: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    2108: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2109: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2110: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2111: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    2112: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2113: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2114: [31, 31, 32, 31, 32, 30, 30, 29, 30, 29, 30, 30],
    2115: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2116: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2117: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2118: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2119: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2120: [30, 32, 31, 32, 31, 31, 29, 30, 30, 29, 29, 31],
    2121: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2122: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2123: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2124: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
    2125: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2126: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2127: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2128: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
    2129: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2130: [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30]
}

BS_REFERENCE_YEAR = 2070
BS_REFERENCE_MONTH = 1
BS_REFERENCE_DAY = 1
AD_REFERENCE_DATE = datetime(2013, 4, 14)

# ============================================================================
# HELPERS
# ============================================================================
def get_nepal_time():
    utc_now = datetime.now(timezone.utc)
    nepal_time = utc_now + timedelta(hours=5, minutes=45)
    return nepal_time.date()

def ad_to_bs(ad_date):
    if isinstance(ad_date, pd.Timestamp):
        ad_date = ad_date.to_pydatetime()
    if isinstance(ad_date, date) and not isinstance(ad_date, datetime):
        ad_date = datetime.combine(ad_date, datetime.min.time())
    if isinstance(ad_date, datetime):
        ad_date = datetime(ad_date.year, ad_date.month, ad_date.day)
    
    delta = (ad_date - AD_REFERENCE_DATE).days
    bs_year = BS_REFERENCE_YEAR
    bs_month = BS_REFERENCE_MONTH
    bs_day = BS_REFERENCE_DAY
    
    if delta >= 0:
        bs_day += delta
        while True:
            if bs_year not in BS_MONTHS:
                return None, None, None
            month_days = BS_MONTHS[bs_year]
            days_in_month = month_days[bs_month - 1]
            if bs_day <= days_in_month:
                break
            else:
                bs_day -= days_in_month
                bs_month += 1
                if bs_month > 12:
                    bs_month = 1
                    bs_year += 1
    else:
        delta = abs(delta)
        while delta > 0:
            if bs_year not in BS_MONTHS:
                return None, None, None
            prev_day = bs_day - 1
            if prev_day == 0:
                bs_month -= 1
                if bs_month == 0:
                    bs_month = 12
                    bs_year -= 1
                    if bs_year not in BS_MONTHS:
                        return None, None, None
                bs_day = BS_MONTHS[bs_year][bs_month - 1]
            else:
                bs_day = prev_day
            delta -= 1
    return bs_year, bs_month, bs_day

def bs_to_ad(bs_year, bs_month, bs_day):
    if bs_year not in BS_MONTHS:
        return datetime.now()
    
    days_diff = 0
    ref_tuple = (BS_REFERENCE_YEAR, BS_REFERENCE_MONTH, BS_REFERENCE_DAY)
    target_tuple = (bs_year, bs_month, bs_day)
    
    if target_tuple == ref_tuple:
        return AD_REFERENCE_DATE
    
    if target_tuple > ref_tuple:
        for y in range(BS_REFERENCE_YEAR, bs_year):
            days_diff += sum(BS_MONTHS[y])
        for m in range(1, bs_month):
            days_diff += BS_MONTHS[bs_year][m-1]
        days_diff += (bs_day - 1)
        return AD_REFERENCE_DATE + timedelta(days=days_diff)
    else:
        curr_y, curr_m, curr_d = BS_REFERENCE_YEAR, BS_REFERENCE_MONTH, BS_REFERENCE_DAY
        while (curr_y, curr_m, curr_d) > target_tuple:
            days_diff += 1
            curr_d -= 1
            if curr_d == 0:
                curr_m -= 1
                if curr_m == 0:
                    curr_m = 12
                    curr_y -= 1
                curr_d = BS_MONTHS[curr_y][curr_m-1]
        return AD_REFERENCE_DATE - timedelta(days=days_diff)

def format_bs_date(bs_y, bs_m, bs_d):
    if bs_y is None or bs_m is None or bs_d is None:
        return "-"
    return f"{bs_y:04d}/{bs_m:02d}/{bs_d:02d}"

def add_months(date_obj, n_months):
    year = date_obj.year + (date_obj.month - 1 + n_months) // 12
    month = (date_obj.month - 1 + n_months) % 12 + 1
    day = date_obj.day
    last_day = calendar.monthrange(year, month)[1]
    return datetime(year, month, min(day, last_day))

def payment_date_10th(start_date, offset_months, is_quarterly=False):
    months_to_add = offset_months * 3 if is_quarterly else offset_months
    if start_date.day < 10:
        first_payment_base = start_date.replace(day=10)
    else:
        first_payment_base = add_months(start_date.replace(day=1), 1).replace(day=10)
    
    pd_date = add_months(first_payment_base, months_to_add)
    last_day = calendar.monthrange(pd_date.year, pd_date.month)[1]
    d = min(10, last_day)
    return datetime(pd_date.year, pd_date.month, d)

def get_next_bs_quarter_end(from_date_ad):
    bs_y, bs_m, bs_d = ad_to_bs(from_date_ad)
    if bs_y is None: return from_date_ad + timedelta(days=90)
    
    if bs_m < 3:
        target_m = 3
        target_y = bs_y
    elif bs_m < 6:
        target_m = 6
        target_y = bs_y
    elif bs_m < 9:
        target_m = 9
        target_y = bs_y
    elif bs_m < 12:
        target_m = 12
        target_y = bs_y
    else:
        target_m = 3
        target_y = bs_y + 1
        
    if target_y not in BS_MONTHS:
        return from_date_ad + timedelta(days=90)
        
    target_d = BS_MONTHS[target_y][target_m - 1]
    target_ad = bs_to_ad(target_y, target_m, target_d)
    
    if target_ad <= from_date_ad:
        return get_next_bs_quarter_end(from_date_ad + timedelta(days=1))
        
    return target_ad

def count_payments_between(segment_start_date, segment_end_date, is_quarterly=False, max_check=5000):
    count = 0
    current_marker_date = segment_start_date
    for off in range(max_check):
        if is_quarterly:
            pd_date = get_next_bs_quarter_end(current_marker_date)
            current_marker_date = pd_date
        else:
            pd_date = payment_date_10th(segment_start_date, off, is_quarterly=False)
            
        if pd_date <= segment_end_date:
            count += 1
        else:
            break
    return count

def calculate_emi(principal, annual_rate, tenure_months, is_quarterly=False):
    if is_quarterly:
        quarterly_rate = annual_rate / (4 * 100)
        tenure_quarters = int(np.ceil(tenure_months / 3))
        if quarterly_rate == 0:
            return principal / tenure_quarters
        eqi = (principal * quarterly_rate * (1 + quarterly_rate)**tenure_quarters) / \
              ((1 + quarterly_rate)**tenure_quarters - 1)
        return eqi
    else:
        monthly_rate = annual_rate / (12 * 100)
        if monthly_rate == 0:
            return principal / tenure_months
        emi = (principal * monthly_rate * (1 + monthly_rate)**tenure_months) / \
              ((1 + monthly_rate)**tenure_months - 1)
        return emi

def calculate_emi_schedule(principal, annual_rate, tenure_months, start_date, fixed_emi=None, start_month=1, max_payments=None, is_quarterly=False):
    # Standard EMI for equal monthly installments
    if is_quarterly:
        rate_per_period = annual_rate / (4 * 100)
        tenure_periods = int(np.ceil(tenure_months / 3))
    else:
        rate_per_period = annual_rate / (12 * 100)
        tenure_periods = tenure_months

    if fixed_emi is not None:
        if rate_per_period == 0:
            actual_tenure = int(np.ceil(principal / fixed_emi))
        else:
            if fixed_emi <= principal * rate_per_period:
                return None, None, None
            actual_tenure = int(np.ceil(
                np.log(fixed_emi / (fixed_emi - principal * rate_per_period)) /
                np.log(1 + rate_per_period)
            ))
        emi = fixed_emi
        payments_to_make = actual_tenure if max_payments is None else min(actual_tenure, int(max_payments))
    else:
        actual_tenure = tenure_periods
        emi = calculate_emi(principal, annual_rate, tenure_months, is_quarterly)
        payments_to_make = actual_tenure if max_payments is None else min(actual_tenure, int(max_payments))
        
    schedule = []
    balance = principal
    payment_label = "Quarterly" if is_quarterly else "EMI"
    
    previous_payment_date = start_date
    
    for m in range(payments_to_make):
        if is_quarterly:
            payment_date = get_next_bs_quarter_end(previous_payment_date)
        else:
            payment_date = payment_date_10th(start_date, m, is_quarterly=False)
            
        try:
            bs_y, bs_m, bs_d = ad_to_bs(payment_date)
        except Exception:
            bs_y, bs_m, bs_d = None, None, None
            
        opening_balance = balance
        
        # ---------------------------------------------------------
        # CHANGED LOGIC: Daily Reducing Balance (Exact Days)
        # ---------------------------------------------------------
        days_in_period = (payment_date - previous_payment_date).days
        
        # Avoid division by zero or negative days if dates are messy
        days_in_period = max(1, days_in_period) 
        
        # Daily Rate = Annual Rate / 365
        interest = balance * (annual_rate / 100) * (days_in_period / 365)
        # ---------------------------------------------------------
        
        principal_paid = emi - interest
        
        is_theoretical_last_payment = (m == actual_tenure - 1)
        
        if principal_paid >= balance or is_theoretical_last_payment:
            principal_paid = balance
            emi_paid = balance + interest
        else:
            emi_paid = emi
            
        closing_balance = balance - principal_paid
        period_label = f"Q{start_month + m}" if is_quarterly else str(start_month + m)
        
        schedule.append({
            'Period': period_label,
            'Payment Date (AD)': payment_date.strftime('%Y-%m-%d'),
            'Payment Date (BS)': format_bs_date(bs_y, bs_m, bs_d),
            'Opening Balance': round(opening_balance, 2),
            payment_label: round(emi_paid, 2),
            'Interest': round(interest, 2),
            'Principal': round(principal_paid, 2),
            'Closing Balance': round(max(0, closing_balance), 2),
            'Interest Rate (%)': round(annual_rate, 2)
        })
        
        balance = closing_balance
        previous_payment_date = payment_date # Update for next loop
        
        if balance <= 0.0001:
            break
            
    return pd.DataFrame(schedule), emi, actual_tenure

def apply_multiple_rate_changes(principal, initial_rate, tenure_months, start_date, rate_change_schedule, is_quarterly=False):
    rate_changes_sorted = sorted(rate_change_schedule, key=lambda x: x['date'])
    initial_emi = calculate_emi(principal, initial_rate, tenure_months, is_quarterly)
    
    current_date = start_date
    all_schedules = []
    current_principal = principal
    current_month_index = 1
    
    full_changes = []
    full_changes.append({'date': start_date, 'rate': initial_rate})
    
    for ch in rate_changes_sorted:
        if ch['date'] <= start_date:
            full_changes[0] = {'date': start_date, 'rate': ch['rate']}
        else:
            full_changes.append(ch)
            
    for i in range(len(full_changes)):
        seg_start = full_changes[i]['date']
        seg_rate = full_changes[i]['rate']
        
        if i < len(full_changes) - 1:
            seg_end = full_changes[i + 1]['date']
            months_in_segment = count_payments_between(seg_start, seg_end, is_quarterly)
        else:
            months_in_segment = None
            
        if months_in_segment == 0:
            current_date = full_changes[i]['date']
            continue
            
        schedule, emi_used, theoretical_tenure = calculate_emi_schedule(
            current_principal,
            seg_rate,
            tenure_months,
            seg_start,
            fixed_emi=initial_emi,
            start_month=current_month_index,
            max_payments=months_in_segment,
            is_quarterly=is_quarterly
        )
        
        if schedule is None:
            # Fallback if EMI is too low
            periods_passed = current_month_index - 1
            months_passed = periods_passed * (3 if is_quarterly else 1)
            remaining_months = max(6, tenure_months - months_passed)
            
            new_emi = calculate_emi(current_principal, seg_rate, remaining_months, is_quarterly)
            initial_emi = new_emi
            
            schedule, emi_used, theoretical_tenure = calculate_emi_schedule(
                current_principal,
                seg_rate,
                tenure_months,
                seg_start,
                fixed_emi=initial_emi,
                start_month=current_month_index,
                max_payments=months_in_segment,
                is_quarterly=is_quarterly
            )
            
        if len(schedule) > 0:
            all_schedules.append(schedule)
            
            current_principal = schedule.iloc[-1]['Closing Balance']
            # Update logic for next segment start date
            seg_last_payment_date_str = schedule.iloc[-1]['Payment Date (AD)']
            seg_last_payment_date = datetime.strptime(seg_last_payment_date_str, '%Y-%m-%d')
            
            # The next segment effectively starts from the last payment date
            # Note: calculate_emi_schedule treats 'start_date' as the 'previous payment date'
            # So for the next segment, we should use the last payment date of this segment as the start.
            # However, the loop above uses 'seg_start' from the rate change list.
            # We need to ensure continuity of dates. 
            
            if is_quarterly:
                current_month_index = int(schedule.iloc[-1]['Period'][1:]) + 1
            else:
                current_month_index = int(schedule.iloc[-1]['Period']) + 1
                
        if months_in_segment is None:
            if current_principal <= 0.01:
                break
                
    if all_schedules:
        combined = pd.concat(all_schedules, ignore_index=True)
        return combined, initial_emi
    else:
        return calculate_emi_schedule(principal, initial_rate, tenure_months, start_date, is_quarterly=is_quarterly)[:2]

# [Keep all your export and chart functions exactly as they are]
def create_excel_template():
    template_data = {
        'Date': ['2025-12-10', '2026-06-10', '2027-01-15'],
        'Rate': [13.5, 14.0, 13.0]
    }
    df = pd.DataFrame(template_data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Rate Changes', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Rate Changes']
        
        instructions = pd.DataFrame({
            'Instructions': [
                '1. Enter dates in the "Date" column in YYYY-MM-DD format (e.g., 2025-12-10)',
                '2. Enter the new interest rate in the "Rate" column as a number (e.g., 13.5 for 13.5%)',
                '3. You can add or remove rows as needed',
                '4. Save the file and upload it back to the application',
                '5. Dates must be in AD (Anno Domini) format',
            ]
        })
        instructions.to_excel(writer, sheet_name='Instructions', index=False)
        
        worksheet.column_dimensions['A'].width = 20
        worksheet.column_dimensions['B'].width = 15
        
        from openpyxl.styles import Font, PatternFill, Alignment
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
            
    output.seek(0)
    return output

def parse_excel_rate_changes(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file, sheet_name='Rate Changes')
        df.columns = df.columns.str.strip()
        
        date_col = None
        rate_col = None
        
        if 'Date' in df.columns: date_col = 'Date'
        elif 'date' in df.columns: date_col = 'date'
        else:
            for col in df.columns:
                if 'date' in col.lower(): date_col = col; break
                
        if 'Rate' in df.columns: rate_col = 'Rate'
        elif 'rate' in df.columns: rate_col = 'rate'
        else:
            for col in df.columns:
                if 'rate' in col.lower(): rate_col = col; break
                
        if not date_col or not rate_col:
            return None, "Excel file must have 'Date' and 'Rate' columns"
            
        rate_changes = []
        errors = []
        
        for idx, row in df.iterrows():
            if pd.isna(row[date_col]) and pd.isna(row[rate_col]): continue
            
            if pd.isna(row[date_col]) or pd.isna(row[rate_col]):
                errors.append(f"Row {idx + 2}: Missing date or rate"); continue
                
            try:
                if isinstance(row[date_col], str):
                    for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y']:
                        try:
                            change_dt = datetime.strptime(row[date_col], fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        change_dt = pd.to_datetime(row[date_col]).to_pydatetime()
                else:
                    change_dt = pd.to_datetime(row[date_col]).to_pydatetime()
                    
                rate_val = float(row[rate_col])
                if rate_val < 0 or rate_val > 100:
                    errors.append(f"Row {idx + 2}: Rate {rate_val} is out of valid range (0-100)"); continue
                    
                rate_changes.append({'date': change_dt, 'rate': rate_val})
                
            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")
                
        if not rate_changes and errors:
            return None, "No valid rate changes found. Errors: " + "; ".join(errors)
            
        return rate_changes, errors if errors else None
        
    except Exception as e:
        return None, f"Error reading Excel file: {str(e)}"

def generate_pdf(schedule, principal, emi, total_payment, total_interest, tenure_months, is_quarterly=False):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    styles = getSampleStyleSheet()
    payment_label = "Quarterly" if is_quarterly else "EMI"
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#14b8a6'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(f"{payment_label} Calculator Report", title_style))
    elements.append(Spacer(1, 12))
    
    summary_data = [
        ['Loan Summary', ''],
        ['Loan Amount:', f'Rs. {principal:,.2f}'],
        [f'{payment_label}:', f'Rs. {emi:,.2f}'],
        ['Total Payment:', f'Rs. {total_payment:,.2f}'],
        ['Total Interest:', f'Rs. {total_interest:,.2f}'],
        ['Loan Tenure:', f'{len(schedule)} {"quarters" if is_quarterly else "months"}'],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#14b8a6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    elements.append(PageBreak())
    
    elements.append(Paragraph("Payment Schedule", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    payment_col = payment_label
    # Added 'Days' column to PDF for verification
    schedule_data = [['Period', 'Date (AD)', 'Date (BS)', 'Opening', payment_label, 'Interest', 'Principal', 'Closing', 'Rate %']]
    
    for _, row in schedule.iterrows():
        schedule_data.append([
            str(row['Period']),
            row['Payment Date (AD)'],
            row['Payment Date (BS)'],
            f"{row['Opening Balance']:,.0f}",
            f"{row[payment_col]:,.0f}",
            f"{row['Interest']:,.0f}",
            f"{row['Principal']:,.0f}",
            f"{row['Closing Balance']:,.0f}",
            f"{row['Interest Rate (%)']:.2f}"
        ])
        
    col_widths = [0.4*inch, 0.8*inch, 0.8*inch, 0.4*inch, 0.8*inch, 0.8*inch, 0.7*inch, 0.8*inch, 0.9*inch, 0.5*inch]
    
    schedule_table = Table(schedule_data, colWidths=col_widths)
    schedule_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#14b8a6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    elements.append(schedule_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def create_balance_chart(schedule):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=schedule.index+1,
        y=schedule['Closing Balance'],
        mode='lines',
        fill='tozeroy',
        name='Outstanding Balance',
        line=dict(width=3, color='#14b8a6'),
        text=schedule['Period'],
        hovertemplate='Period: %{text}<br>Balance: Rs. %{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Loan Balance Over Time',
        xaxis_title='Payment Period',
        yaxis_title='Outstanding Balance (Rs.)',
        height=350,
        hovermode='x unified',
        template='plotly_white',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", color="#374151"),
        title_font=dict(family="Poppins, sans-serif", size=16, color="#0f766e"),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_principal_interest_chart(schedule, is_quarterly=False):
    payment_label = "Quarterly" if is_quarterly else "EMI"
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=schedule.index+1,
        y=schedule['Principal'],
        name='Principal',
        marker_color='#14b8a6',
        text=schedule['Period'],
        hovertemplate='Period: %{text}<br>Principal: Rs. %{y:,.0f}<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=schedule.index+1,
        y=schedule['Interest'],
        name='Interest',
        marker_color='#f59e0b',
        text=schedule['Period'],
        hovertemplate='Period: %{text}<br>Interest: Rs. %{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'{payment_label} Breakdown: Principal vs Interest',
        xaxis_title='Payment Period',
        yaxis_title='Amount (Rs.)',
        barmode='stack',
        height=350,
        hovermode='x unified',
        template='plotly_white',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", color="#374151"),
        title_font=dict(family="Poppins, sans-serif", size=16, color="#0f766e"),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_pie_chart(schedule):
    total_principal = schedule['Principal'].sum()
    total_interest = schedule['Interest'].sum()
    
    fig = go.Figure(data=[go.Pie(
        labels=['Principal', 'Interest'],
        values=[total_principal, total_interest],
        hole=0.6,
        textinfo='label+percent',
        marker=dict(colors=['#14b8a6', '#f59e0b']),
        texttemplate='<b>%{label}</b><br>%{percent}<br>Rs. %{value:,.0f}'
    )])
    
    fig.update_layout(
        title='Total Payment Composition',
        height=350,
        template='plotly_white',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", color="#374151"),
        title_font=dict(family="Poppins, sans-serif", size=16, color="#0f766e"),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_interest_rate_timeline(schedule):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=schedule.index+1,
        y=schedule['Interest Rate (%)'],
        mode='lines+markers',
        name='Interest Rate',
        line=dict(width=3, shape='hv', color='#8b5cf6'),
        marker=dict(size=8, color='#7c3aed'),
        text=schedule['Period'],
        hovertemplate='Period: %{text}<br>Rate: %{y:.2f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title='Interest Rate Changes Over Time',
        xaxis_title='Payment Period',
        yaxis_title='Interest Rate (%)',
        height=350,
        hovermode='x unified',
        template='plotly_white',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", color="#374151"),
        title_font=dict(family="Poppins, sans-serif", size=16, color="#0f766e"),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# ============================================================================
# STREAMLIT APP
# ============================================================================
def init_session_state():
    if 'rate_changes' not in st.session_state:
        st.session_state.rate_changes = []
    if 'upload_key' not in st.session_state:
        st.session_state.upload_key = 0
    if 'calculated' not in st.session_state:
        st.session_state.calculated = False

init_session_state()

def main():
    st.set_page_config(
        page_title="Loan Calculator",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    load_custom_css()
    
    st.title("💰 Loan Repayment Planner")
    
    st.markdown("""
    <div class='info-box'>
        <p style='margin:0;'>
        🎯 <strong>Professional EMI/Quarterly Calculator</strong> with <strong>Dynamic Rate Changes</strong>, 
        BS Calendar Support, and Multiple Export Options
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_freq, col_info = st.columns([1, 2])
    
    with col_freq:
        payment_freq = st.radio("💳 Payment Frequency", ["EMI (Monthly)", "Quarterly"], horizontal=True)
        
    is_quarterly = (payment_freq == "Quarterly")
    
    with col_info:
        if is_quarterly:
            st.info("📅 Payments aligned to **BS Quarter Ends** (Ashad, Ashwin, Poush, Chaitra)")
        else:
            st.info("📅 Payments scheduled on the **10th** of each AD month")
            
    st.divider()
    
    with st.sidebar:
        st.header("⚙️ Loan Parameters")
        st.markdown("---")
        
        principal = st.number_input("💵 Loan Amount (Rs.)", min_value=10000, max_value=100000000, value=1000000, step=10000)
        annual_rate = st.number_input("📊 Initial Annual Interest Rate (%)", min_value=0.0, max_value=30.0, value=12.0, step=0.1, format="%.2f")
        tenure_months = st.number_input("⏱️ Loan Tenure (Months)", min_value=1, max_value=360, value=60, step=1)
        
        st.markdown("### 📆 Start Date")
        date_format = st.radio("Date Format", ["AD", "BS"], horizontal=True)
        
        nepal_today = get_nepal_time()
        
        if date_format == "AD":
            start_date = st.date_input("Loan Start Date (AD)", value=nepal_today)
            start_datetime = datetime.combine(start_date, datetime.min.time())
        else:
            today_bs_y, today_bs_m, today_bs_d = ad_to_bs(nepal_today)
            col1, col2, col3 = st.columns(3)
            with col1: bs_year = st.number_input("Year", min_value=2000, max_value=2090, value=today_bs_y if today_bs_y else 2081, step=1)
            with col2: bs_month = st.number_input("Month", min_value=1, max_value=12, value=today_bs_m if today_bs_m else 1, step=1)
            with col3: bs_day = st.number_input("Day", min_value=1, max_value=32, value=today_bs_d if today_bs_d else 1, step=1)
            
            try:
                start_datetime = bs_to_ad(bs_year, bs_month, bs_day)
                st.caption(f"🔄 AD Equivalent: {start_datetime.strftime('%Y-%m-%d')}")
            except Exception as e:
                st.error(f"❌ Could not convert BS → AD: {e}")
                start_datetime = datetime.now()
                
        st.markdown("---")
        st.subheader("📈 Interest Rate Changes")
        st.caption("Configure floating interest rates during loan tenure")
        
        template_excel = create_excel_template()
        st.download_button(
            label="📥 Download Excel Template",
            data=template_excel,
            file_name="rate_changes_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        with st.expander("📂 Upload Excel File", expanded=False):
            st.info("💡 Upload file with 'Date' and 'Rate' columns")
            uploaded_file = st.file_uploader(
                "Choose File",
                type=['xlsx', 'xls'],
                key=f"file_uploader_{st.session_state.upload_key}"
            )
            
            if uploaded_file is not None:
                with st.spinner("⚙️ Processing..."):
                    rate_changes, errors = parse_excel_rate_changes(uploaded_file)
                    
                    if rate_changes:
                        st.success(f"✅ Found {len(rate_changes)} rate change(s)")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✓ Apply", use_container_width=True):
                                st.session_state.rate_changes = rate_changes
                                st.session_state.upload_key += 1
                                st.success("✨ Applied!")
                                st.rerun()
                        with col2:
                            if st.button("✗ Cancel", use_container_width=True):
                                st.session_state.upload_key += 1
                                st.rerun()
                    else:
                        st.error(f"❌ {errors}")
                        
        with st.expander("➕ Add Rate Change Manually"):
            change_date = st.date_input("Change Date (AD)", value=(nepal_today + timedelta(days=365)))
            change_datetime = datetime.combine(change_date, datetime.min.time())
            new_rate = st.number_input("New Interest Rate (%)", min_value=0.0, max_value=30.0, value=13.0, step=0.1, format="%.2f")
            
            if st.button("➕ Add Rate Change", use_container_width=True):
                st.session_state.rate_changes.append({'date': change_datetime, 'rate': new_rate})
                st.success("✅ Rate change added!")
                st.rerun()
                
        if st.session_state.rate_changes:
            st.markdown("#### 📋 Scheduled Rate Changes")
            sorted_changes = sorted(st.session_state.rate_changes, key=lambda x: x['date'])
            
            for idx, change in enumerate(sorted_changes):
                orig_idx = st.session_state.rate_changes.index(change)
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"📅 {change['date'].strftime('%Y-%m-%d')}: **{change['rate']:.2f}%**")
                with col2:
                    if st.button("🗑️", key=f"del_{orig_idx}_{idx}"):
                        st.session_state.rate_changes.pop(orig_idx)
                        st.rerun()
                        
    action_col1, action_col2, _ = st.columns([1, 1, 3])
    with action_col1:
        calculate_btn = st.button("🚀 Calculate Schedule", type="primary", use_container_width=True)
    with action_col2:
        if st.session_state.rate_changes:
            if st.button("🔄 Reset Rate Changes", use_container_width=True):
                st.session_state.rate_changes = []
                st.rerun()
                
    if calculate_btn:
        st.session_state.calculated = True
        
    if st.session_state.calculated:
        period_label = "Quarterly" if is_quarterly else "EMI"
        
        try:
            with st.spinner("⚙️ Calculating your loan schedule..."):
                if st.session_state.rate_changes:
                    schedule, emi = apply_multiple_rate_changes(
                        principal, annual_rate, tenure_months,
                        start_datetime, st.session_state.rate_changes, is_quarterly
                    )
                else:
                    schedule, emi = calculate_emi_schedule(
                        principal, annual_rate, tenure_months,
                        start_datetime, is_quarterly=is_quarterly
                    )[:2]
                    
            period_count = f"{len(schedule)} {'quarters' if is_quarterly else 'months'}"
            
            st.success("✅ Calculation completed successfully!")
            st.markdown("### 📊 Loan Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(f"💰 {period_label}", f"Rs. {emi:,.0f}")
            with col2:
                payment_col = period_label
                total_payment = schedule[payment_col].sum()
                st.metric("💸 Total Payment", f"Rs. {total_payment:,.0f}")
            with col3:
                total_interest = schedule['Interest'].sum()
                st.metric("🔥 Total Interest", f"Rs. {total_interest:,.0f}")
            with col4:
                st.metric("⏱️ Actual Tenure", period_count)
                
            st.markdown("---")
            
            tab1, tab2, tab3 = st.tabs(["📈 Visualizations", "📋 Payment Schedule", "💾 Export Options"])
            
            with tab1:
                left, right = st.columns(2)
                with left:
                    st.plotly_chart(create_balance_chart(schedule), use_container_width=True)
                with right:
                    st.plotly_chart(create_pie_chart(schedule), use_container_width=True)
                    
                if st.session_state.rate_changes:
                    c3, c4 = st.columns(2)
                    with c3:
                        st.plotly_chart(create_interest_rate_timeline(schedule), use_container_width=True)
                    with c4:
                        st.plotly_chart(create_principal_interest_chart(schedule, is_quarterly), use_container_width=True)
                else:
                    st.plotly_chart(create_principal_interest_chart(schedule, is_quarterly), use_container_width=True)
                    
            with tab2:
                st.dataframe(schedule, use_container_width=True, height=500)
                
            with tab3:
                st.subheader("📥 Download Your Loan Schedule")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    csv = schedule.to_csv(index=False)
                    st.download_button(
                        label="📄 Download CSV",
                        data=csv,
                        file_name=f"loan_schedule_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    
                with col2:
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        schedule.to_excel(writer, sheet_name=f'{period_label} Schedule', index=False)
                        summary_df = pd.DataFrame({
                            'Parameter': ['Loan Amount', period_label, 'Total Payment', 'Total Interest', 'Loan Tenure', 'Initial Rate'],
                            'Value': [f"Rs. {principal:,.2f}", f"Rs. {emi:,.2f}", f"Rs. {total_payment:,.2f}", f"Rs. {total_interest:,.2f}", period_count, f"{annual_rate:.2f}%"]
                        })
                        summary_df.to_excel(writer, sheet_name='Summary', index=False)
                    excel_buffer.seek(0)
                    st.download_button(
                        label="📊 Download Excel",
                        data=excel_buffer,
                        file_name=f"loan_schedule_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    
                with col3:
                    pdf_buffer = generate_pdf(schedule, principal, emi, total_payment, total_interest, tenure_months, is_quarterly)
                    st.download_button(
                        label="📑 Download PDF Report",
                        data=pdf_buffer,
                        file_name=f"loan_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
        except Exception as e:
            st.error(f"❌ Error calculating {period_label}: {e}")
            import traceback
            with st.expander("🔍 Error Details"):
                st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
