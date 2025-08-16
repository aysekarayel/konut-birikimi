
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Konut Birikimi Simülasyonu", layout="wide")

st.title("🏠 Konut Birikimi ve Rezidans Yatırım Simülasyonu")


with st.sidebar:
    st.header("Parametreler")
    start_age = st.number_input("Başlangıç Yaşı", min_value=18, max_value=60, value=25, step=1)
    end_age = st.number_input("Bitiş Yaşı", min_value=start_age+1, max_value=90, value=65, step=1)
    monthly_saving = st.number_input("Aylık Birikim (₺)", min_value=0, value=3000, step=500)
    unit_price = st.number_input("Daire Fiyatı (₺)", min_value=100000, value=1250000, step=50000)
    monthly_rent = st.number_input("Aylık Kira (₺)", min_value=0, value=8000, step=500)
    down_payment_rate = st.slider("Peşinat Oranı (%)", min_value=5, max_value=50, value=20, step=1) / 100.0
    loan_years = st.number_input("Kredi Süresi (Yıl)", min_value=1, max_value=30, value=15, step=1)

def simulate(start_age, end_age, monthly_saving, unit_price, monthly_rent, down_payment_rate, loan_years):
    months = (end_age - start_age) * 12
    down_payment = unit_price * down_payment_rate
    monthly_loan_payment = (unit_price - down_payment) / (loan_years * 12)

    cash = 0.0
    units = 0
    active_loans = []
    log = []

    for m in range(1, months + 1):
        inflow = monthly_saving + units * monthly_rent
        outflow = monthly_loan_payment * len(active_loans)
        cash += inflow - outflow

        while cash >= down_payment:
            cash -= down_payment
            units += 1
            active_loans.append(loan_years * 12)
            year = start_age + (m - 1) // 12
            month_in_year = ((m - 1) % 12) + 1
            log.append({
                "MonthIndex": m,
                "Age": year,
                "Month": month_in_year,
                "TotalUnitsAfterPurchase": units,
                "CashAfterPurchase": round(cash, 2),
                "ActiveLoans": len(active_loans)
            })

        if active_loans:
            active_loans = [rm - 1 for rm in active_loans if rm - 1 > 0]

    monthly_rent_income = units * monthly_rent
    total_monthly_loan_payment = monthly_loan_payment * len(active_loans)
    net_monthly_cashflow_at_end = monthly_saving + monthly_rent_income - total_monthly_loan_payment

    summary = 
        "Toplam Daire Sayısı": units,
        "Bitiş Yaşı Aylık Kira Geliri (₺)": round(monthly_rent_income, 2),
        "Aktif Kredi Sayısı": len(active_loans),
        "Tek Daire Aylık Kredi Ödemesi (₺)": round(monthly_loan_payment, 2),
        "Toplam Aylık Kredi Ödemesi (₺)": round(total_monthly_loan_payment, 2),
        "Bitiş Yaşı Aylık Net Nakit Akışı (₺)": round(net_monthly_cashflow_at_end, 2),
    
    return summary, pd.DataFrame(log)

summary, df = simulate(start_age, end_age, monthly_saving, unit_price, monthly_rent, down_payment_rate, loan_years)

left, right = st.columns([1,1])
with left:
    st.subheader("Özet")
    st.json(summary)



st.subheader("Zaman İçinde Toplam Daire Sayısı")
if not df.empty:
    
    plot_df = df[["MonthIndex", "TotalUnitsAfterPurchase"]].rename(columns={"TotalUnitsAfterPurchase":"Toplam Daire"})
    st.line_chart(plot_df.set_index("MonthIndex"))
else:
    st.info("Henüz satın alma gerçekleşmedi. Parametreleri artırmayı deneyin.")
