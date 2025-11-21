import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone, date # Added date import
import calendar
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

# ============================================================================
# BS CALENDAR DATA (VERIFIED)
# ============================================================================

# Verified Data source for BS Calendar (2070-2099)
# Format: [Baisakh, Jestha, Asar, Shrawan, Bhadra, Asoj, Kartik, Mangsir, Poush, Magh, Falgun, Chaitra]
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
    2081: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31], # Current Year
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
    2099: [31, 31, 32, 31, 31, 31, 30, 29, 29, 30, 30, 30]
}

# CORRECTED Reference date: 2070/01/01 BS = 2013/04/14 AD
BS_REFERENCE_YEAR = 2070
BS_REFERENCE_MONTH = 1
BS_REFERENCE_DAY = 1
AD_REFERENCE_DATE = datetime(2013, 4, 14) 

# ============================================================================
# HELPERS: AD/BS conversion
# ============================================================================

def get_nepal_time():
    """Get current time in Nepal (UTC+5:45)"""
    utc_now = datetime.now(timezone.utc)
    nepal_time = utc_now + timedelta(hours=5, minutes=45)
    return nepal_time.date()

def ad_to_bs(ad_date):
    """Convert AD date to BS date using calendar data"""
    if isinstance(ad_date, pd.Timestamp):
        ad_date = ad_date.to_pydatetime()
    
    # Handle 'date' objects by converting to 'datetime' at midnight
    if isinstance(ad_date, date) and not isinstance(ad_date, datetime):
        ad_date = datetime.combine(ad_date, datetime.min.time())

    # Ensure ad_date is just date, no time (normalize existing datetime)
    if isinstance(ad_date, datetime):
        ad_date = datetime(ad_date.year, ad_date.month, ad_date.day)

    # Calculate days difference from reference date
    delta = (ad_date - AD_REFERENCE_DATE).days
    
    bs_year = BS_REFERENCE_YEAR
    bs_month = BS_REFERENCE_MONTH
    bs_day = BS_REFERENCE_DAY
    
    # Forward calculation (date is after reference)
    if delta >= 0:
        # Add days
        bs_day += delta
        
        while True:
            if bs_year not in BS_MONTHS:
                return None, None, None
                
            month_days = BS_MONTHS[bs_year]
            
            # Check if we can stay in current year
            days_in_current_year = sum(month_days)
            
            # Optimization: Skip full years if we have enough days
            # But we must be careful about changing month lengths
            # Doing strictly sequential is safer for accuracy
            
            # Check current month
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
        # Backward calculation (date is before reference)
        # Logic: move back day by day/month by month
        delta = abs(delta)
        
        while delta > 0:
            if bs_year not in BS_MONTHS:
                return None, None, None
                
            # Move back one day
            # Use previous month/year logic
            prev_day = bs_day - 1
            if prev_day == 0:
                # Go to previous month
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
    """Convert BS date to AD date using calendar data"""
    if bs_year not in BS_MONTHS:
        return datetime.now() # Fallback
    
    # Calculate total days from reference BS date to target BS date
    days_diff = 0
    
    # 1. Calculate direction
    ref_tuple = (BS_REFERENCE_YEAR, BS_REFERENCE_MONTH, BS_REFERENCE_DAY)
    target_tuple = (bs_year, bs_month, bs_day)
    
    if target_tuple == ref_tuple:
        return AD_REFERENCE_DATE
        
    if target_tuple > ref_tuple:
        # Target is in future relative to reference
        # Add days for full years
        for y in range(BS_REFERENCE_YEAR, bs_year):
            days_diff += sum(BS_MONTHS[y])
            
        # Add days for full months in target year
        for m in range(1, bs_month):
            days_diff += BS_MONTHS[bs_year][m-1]
            
        # Add days in current month
        days_diff += (bs_day - 1)
        
        return AD_REFERENCE_DATE + timedelta(days=days_diff)
    else:
        # Target is in past relative to reference
        # We need to subtract days
        
        # Count days backwards from Reference to Target
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
    """Format BS date, return '-' if out of range"""
    if bs_y is None or bs_m is None or bs_d is None:
        return "-"
    return f"{bs_y:04d}/{bs_m:02d}/{bs_d:02d}"

# ============================================================================
# UTILS: date arithmetic
# ============================================================================

def add_months(date_obj, n_months):
    """Return a new datetime by adding n_months to date_obj, preserving day if possible."""
    year = date_obj.year + (date_obj.month - 1 + n_months) // 12
    month = (date_obj.month - 1 + n_months) % 12 + 1
    day = date_obj.day
    last_day = calendar.monthrange(year, month)[1]
    return datetime(year, month, min(day, last_day))

def payment_date_10th(start_date, offset_months, is_quarterly=False):
    """Return the payment date for offset_months (0-based). Each payment is on AD day=10."""
    months_to_add = offset_months * 3 if is_quarterly else offset_months
    
    if start_date.day <= 10:
        first_payment_base = start_date.replace(day=10)
    else:
        first_payment_base = add_months(start_date.replace(day=1), 1).replace(day=10)
    
    pd_date = add_months(first_payment_base, months_to_add)
    last_day = calendar.monthrange(pd_date.year, pd_date.month)[1]
    d = min(10, last_day)
    return datetime(pd_date.year, pd_date.month, d)

def count_payments_between(segment_start_date, segment_end_date, is_quarterly=False, max_check=5000):
    """Count how many payment dates (10th) occur between segment_start_date and segment_end_date."""
    count = 0
    for off in range(max_check):
        pd = payment_date_10th(segment_start_date, off, is_quarterly)
        if pd < segment_end_date:
            count += 1
        else:
            break
    return count

# ============================================================================
# EMI CALCULATION
# ============================================================================

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
    """Generate EMI schedule where payments occur on the AD 10th of each month/quarter."""
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

    for m in range(payments_to_make):
        payment_date = payment_date_10th(start_date, m, is_quarterly)
        try:
            bs_y, bs_m, bs_d = ad_to_bs(payment_date)
        except Exception:
            bs_y, bs_m, bs_d = None, None, None

        opening_balance = balance
        interest = balance * rate_per_period
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
        if balance <= 0.0001:
            break

    return pd.DataFrame(schedule), emi, actual_tenure

def apply_multiple_rate_changes(principal, initial_rate, tenure_months, start_date, rate_change_schedule, is_quarterly=False):
    """Apply multiple rate changes based on their AD dates."""
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
            period_type = "Quarterly" if is_quarterly else "EMI"
            raise ValueError(f"Fixed {period_type} {initial_emi:.2f} is too small for the rate {seg_rate}% (interest >= {period_type}).")

        if len(schedule) > 0:
            all_schedules.append(schedule)
            current_principal = schedule.iloc[-1]['Closing Balance']
            if is_quarterly:
                current_month_index = int(schedule.iloc[-1]['Period'][1:]) + 1
            else:
                current_month_index = int(schedule.iloc[-1]['Period']) + 1

        if months_in_segment is None:
            break

        if current_principal <= 0.01:
            break

    if all_schedules:
        combined = pd.concat(all_schedules, ignore_index=True)
        return combined, initial_emi

    return calculate_emi_schedule(principal, initial_rate, tenure_months, start_date, is_quarterly=is_quarterly)[:2]

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def create_excel_template():
    """Create an Excel template for rate changes upload"""
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
                '',
                'Example:',
                'Date: 2025-12-10, Rate: 13.5',
                'Date: 2026-06-10, Rate: 14.0'
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
    """Parse uploaded Excel file and extract rate changes"""
    try:
        df = pd.read_excel(uploaded_file, sheet_name='Rate Changes')
        df.columns = df.columns.str.strip()
        
        date_col = None
        rate_col = None
        
        if 'Date' in df.columns: date_col = 'Date'
        elif 'date' in df.columns: date_col = 'date'
        else:
            for col in df.columns:
                if 'date' in col.lower():
                    date_col = col
                    break
        
        if 'Rate' in df.columns: rate_col = 'Rate'
        elif 'rate' in df.columns: rate_col = 'rate'
        else:
            for col in df.columns:
                if 'rate' in col.lower():
                    rate_col = col
                    break
        
        if not date_col or not rate_col:
            return None, "Excel file must have 'Date' and 'Rate' columns"
        
        rate_changes = []
        errors = []
        
        for idx, row in df.iterrows():
            if pd.isna(row[date_col]) and pd.isna(row[rate_col]):
                continue
            
            if pd.isna(row[date_col]) or pd.isna(row[rate_col]):
                errors.append(f"Row {idx + 2}: Missing date or rate")
                continue
            
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
                    errors.append(f"Row {idx + 2}: Rate {rate_val} is out of valid range (0-100)")
                    continue
                
                rate_changes.append({
                    'date': change_dt,
                    'rate': rate_val
                })
                
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
    report_title = f"{payment_label} Calculator Report"
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(report_title, title_style))
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
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
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
    
    schedule_table = Table(schedule_data, colWidths=[0.4*inch, 0.8*inch, 0.8*inch, 0.9*inch, 0.8*inch, 0.8*inch, 0.9*inch, 0.9*inch, 0.5*inch])
    schedule_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
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

# ============================================================================
# CHARTS
# ============================================================================

def create_balance_chart(schedule):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=schedule.index + 1,
        y=schedule['Closing Balance'],
        mode='lines',
        fill='tozeroy',
        name='Outstanding Balance',
        line=dict(width=3),
        text=schedule['Period'],
        hovertemplate='Period: %{text}<br>Balance: Rs. %{y:,.0f}<extra></extra>'
    ))
    fig.update_layout(
        title='Loan Balance Over Time',
        xaxis_title='Payment Period',
        yaxis_title='Outstanding Balance (Rs.)',
        height=350,
        hovermode='x unified'
    )
    return fig

def create_principal_interest_chart(schedule, is_quarterly=False):
    payment_label = "Quarterly" if is_quarterly else "EMI"
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=schedule.index + 1,
        y=schedule['Principal'],
        name='Principal',
        text=schedule['Period'],
        hovertemplate='Period: %{text}<br>Principal: Rs. %{y:,.0f}<extra></extra>'
    ))
    fig.add_trace(go.Bar(
        x=schedule.index + 1,
        y=schedule['Interest'],
        name='Interest',
        text=schedule['Period'],
        hovertemplate='Period: %{text}<br>Interest: Rs. %{y:,.0f}<extra></extra>'
    ))
    fig.update_layout(
        title=f'{payment_label} Breakdown: Principal vs Interest',
        xaxis_title='Payment Period',
        yaxis_title='Amount (Rs.)',
        barmode='stack',
        height=350,
        hovermode='x unified'
    )
    return fig

def create_pie_chart(schedule):
    total_principal = schedule['Principal'].sum()
    total_interest = schedule['Interest'].sum()
    fig = go.Figure(data=[go.Pie(
        labels=['Principal', 'Interest'],
        values=[total_principal, total_interest],
        hole=0.4,
        textinfo='label+percent+value',
        texttemplate='<b>%{label}</b><br>%{percent}<br>Rs. %{value:,.0f}'
    )])
    fig.update_layout(title='Total Payment Composition', height=350)
    return fig

def create_interest_rate_timeline(schedule):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=schedule.index + 1,
        y=schedule['Interest Rate (%)'],
        mode='lines+markers',
        name='Interest Rate',
        line=dict(width=3, shape='hv'),
        text=schedule['Period'],
        hovertemplate='Period: %{text}<br>Rate: %{y:.2f}%<extra></extra>'
    ))
    fig.update_layout(
        title='Interest Rate Changes Over Time',
        xaxis_title='Payment Period',
        yaxis_title='Interest Rate (%)',
        height=350,
        hovermode='x unified'
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

init_session_state()

def main():
    st.set_page_config(page_title="Dynamic EMI/Quarterly Calculator", page_icon="💰", layout="wide")
    
    # --- HIDE UI ELEMENTS ---
    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    # ------------------------

    st.title("Dynamic EMI/Quarterly Calculator")
    
    # Payment frequency selector at the top
    payment_freq = st.radio("Payment Frequency", ["EMI (Monthly)", "Quarterly"], horizontal=True)
    is_quarterly = (payment_freq == "Quarterly")
    
    freq_text = "quarter" if is_quarterly else "month"
    st.markdown(f"Payments are scheduled on the **10th** of each AD {freq_text} and remain equal over period")
    
    st.divider()

    with st.sidebar:
        st.header("🏦 Loan Parameters")
        principal = st.number_input("Loan Amount (Rs.)", min_value=10000, max_value=100000000, value=1000000, step=10000)
        annual_rate = st.number_input("Initial Annual Interest Rate (%)", min_value=0.0, max_value=30.0, value=12.0, step=0.1, format="%.2f")
        tenure_months = st.number_input("Loan Tenure (Months)", min_value=1, max_value=360, value=60, step=1)

        date_format = st.radio("Start Date Format", ["AD", "BS"], horizontal=True)

        # Use Nepal Time for default value
        nepal_today = get_nepal_time()

        if date_format == "AD":
            start_date = st.date_input("Loan Start Date (AD)", value=nepal_today)
            start_datetime = datetime.combine(start_date, datetime.min.time())
        else:
            # Convert Nepal Today to BS for default values
            today_bs_y, today_bs_m, today_bs_d = ad_to_bs(nepal_today)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                bs_year = st.number_input("Year (BS)", min_value=2000, max_value=2090, value=today_bs_y if today_bs_y else 2081, step=1)
            with col2:
                bs_month = st.number_input("Month", min_value=1, max_value=12, value=today_bs_m if today_bs_m else 1, step=1)
            with col3:
                bs_day = st.number_input("Day", min_value=1, max_value=32, value=today_bs_d if today_bs_d else 1, step=1)
            try:
                start_datetime = bs_to_ad(bs_year, bs_month, bs_day)
                st.caption(f"AD: {start_datetime.strftime('%Y-%m-%d')}")
            except Exception as e:
                st.error(f"Could not convert BS → AD: {e}")
                start_datetime = datetime.now()

        st.divider()
        st.subheader("🔄 Interest Rate Changes")
        st.caption("Add future rate changes in AD format")

        # Download template button
        template_excel = create_excel_template()
        st.download_button(
            label="📥 Download Excel Template",
            data=template_excel,
            file_name="rate_changes_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        with st.expander("📤 Upload Rate Changes (Excel)", expanded=False):
            st.info("📋 Upload the Excel template with 'Date' and 'Rate' columns")
            
            uploaded_file = st.file_uploader(
                "Choose Excel file",
                type=['xlsx', 'xls'],
                key=f"file_uploader_{st.session_state.upload_key}"
            )
            
            if uploaded_file is not None:
                with st.spinner("Processing Excel file..."):
                    rate_changes, errors = parse_excel_rate_changes(uploaded_file)
                    
                    if rate_changes:
                        # Show preview
                        st.success(f"✅ Found {len(rate_changes)} rate change(s)")
                        
                        preview_df = pd.DataFrame(rate_changes)
                        preview_df['date'] = preview_df['date'].dt.strftime('%Y-%m-%d')
                        st.dataframe(preview_df, use_container_width=True)
                        
                        if errors:
                            with st.expander("⚠️ Warnings", expanded=False):
                                for error in errors:
                                    st.warning(error)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Apply Changes", use_container_width=True):
                                st.session_state.rate_changes = rate_changes
                                st.session_state.upload_key += 1  # Reset file uploader
                                st.success("Rate changes applied!")
                                st.rerun()
                        
                        with col2:
                            if st.button("❌ Cancel", use_container_width=True):
                                st.session_state.upload_key += 1  # Reset file uploader
                                st.rerun()
                    else:
                        st.error(f"❌ {errors}")

        with st.expander("➕ Add Rate Change Manually"):
            change_date = st.date_input("Change Date (AD)", value=(nepal_today + timedelta(days=365)))
            change_datetime = datetime.combine(change_date, datetime.min.time())
            
            new_rate = st.number_input("New Rate (%)", min_value=0.0, max_value=30.0, value=13.0, step=0.1, format="%.2f")
            
            if st.button("Add Rate Change", use_container_width=True):
                st.session_state.rate_changes.append({'date': change_datetime, 'rate': new_rate})
                st.success("Rate change added!")
                st.rerun()

        if st.session_state.rate_changes:
            st.write("**Scheduled Rate Changes:**")
            # Sort by date for display
            sorted_changes = sorted(st.session_state.rate_changes, key=lambda x: x['date'])
            
            for idx, change in enumerate(sorted_changes):
                # Find original index
                orig_idx = st.session_state.rate_changes.index(change)
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"📅 {change['date'].strftime('%Y-%m-%d')}: **{change['rate']:.2f}%**")
                with col2:
                    if st.button("🗑️", key=f"del_{orig_idx}_{idx}"):
                        st.session_state.rate_changes.pop(orig_idx)
                        st.rerun()

        st.divider()
        calculate_btn = st.button("📊 Calculate Schedule", type="primary", use_container_width=True)
        if st.session_state.rate_changes:
            if st.button("🔄 Reset Rate Changes", use_container_width=True):
                st.session_state.rate_changes = []
                st.rerun()

    # Main content area - Perform calculation
    if calculate_btn:
        # Define period_label BEFORE the try block so it is available if an error occurs
        period_label = "Quarterly" if is_quarterly else "EMI"
        try:
            if st.session_state.rate_changes:
                schedule, emi = apply_multiple_rate_changes(
                    principal,
                    annual_rate,
                    tenure_months,
                    start_datetime,
                    st.session_state.rate_changes,
                    is_quarterly
                )
            else:
                schedule, emi = calculate_emi_schedule(principal, annual_rate, tenure_months, start_datetime, is_quarterly=is_quarterly)[:2]

            # Summary metrics
            period_count = f"{len(schedule)} {'quarters' if is_quarterly else 'months'}"
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(period_label, f"Rs. {emi:,.2f}")
            with col2:
                # Get the correct column name for total payment
                payment_col = period_label
                total_payment = schedule[payment_col].sum()
                st.metric("Total Payment", f"Rs. {total_payment:,.2f}")
            with col3:
                total_interest = schedule['Interest'].sum()
                st.metric("Total Interest", f"Rs. {total_interest:,.2f}")
            with col4:
                st.metric("Actual Tenure", period_count)

            st.divider()
            
            # Tabs for different views
            tab1, tab2, tab3 = st.tabs(["📊 Charts", "📋 Schedule", "💾 Export"])
            
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
                st.subheader("📥 Download Options")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # CSV Download
                    csv = schedule.to_csv(index=False)
                    st.download_button(
                        label="📄 Download CSV",
                        data=csv,
                        file_name=f"{period_label.lower()}_schedule_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    # Excel Download
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        schedule.to_excel(writer, sheet_name=f'{period_label} Schedule', index=False)
                        
                        # Add summary sheet
                        summary_df = pd.DataFrame({
                            'Parameter': ['Loan Amount', period_label, 'Total Payment', 'Total Interest', 'Loan Tenure', 'Initial Rate'],
                            'Value': [
                                f"Rs. {principal:,.2f}",
                                f"Rs. {emi:,.2f}",
                                f"Rs. {total_payment:,.2f}",
                                f"Rs. {total_interest:,.2f}",
                                period_count,
                                f"{annual_rate:.2f}%"
                            ]
                        })
                        summary_df.to_excel(writer, sheet_name='Summary', index=False)
                    
                    excel_buffer.seek(0)
                    st.download_button(
                        label="📊 Download Excel",
                        data=excel_buffer,
                        file_name=f"{period_label.lower()}_schedule_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
                with col3:
                    # PDF Download
                    pdf_buffer = generate_pdf(schedule, principal, emi, total_payment, total_interest, tenure_months, is_quarterly)
                    st.download_button(
                        label="📑 Download PDF",
                        data=pdf_buffer,
                        file_name=f"{period_label.lower()}_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                
                st.divider()
                
                
        except Exception as e:
            st.error(f"Error calculating {period_label}: {e}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
