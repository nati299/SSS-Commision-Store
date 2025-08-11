import streamlit as st
import importlib.metadata
import pandas as pd
import os
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
import base64

EXCEL_FILE = "sss_data.xlsx"

# --------- UTILITY FUNCTIONS --------- #

def initialize_excel():
    if not os.path.exists(EXCEL_FILE):
        writer = pd.ExcelWriter(EXCEL_FILE, engine='openpyxl')
        pd.DataFrame(columns=["Shop Name", "Amount", "DateTime"]).to_excel(writer, sheet_name="Dealer Entry", index=False)
        pd.DataFrame(columns=["Storage Name", "Bags", "KGs", "In Whose Name", "Bond Number", "DateTime"]).to_excel(writer, sheet_name="Storage Entry", index=False)
        pd.DataFrame(columns=["Storage Name", "Dealer Name", "Bags Moved", "KGs", "In Whose Name", "Amount", "Bond Number", "DateTime"]).to_excel(writer, sheet_name="Storage to Dealer", index=False)
        writer.close()

def read_excel_sheet(sheet):
    try:
        return pd.read_excel(EXCEL_FILE, sheet_name=sheet)
    except:
        return pd.DataFrame()

def write_to_excel(sheet, new_data):
    df = read_excel_sheet(sheet)
    if df.empty:
        df = new_data
    else:
        df = pd.concat([df, new_data], ignore_index=True)
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=sheet, index=False)

def generate_pdf(data, title):
    pdf = FPDF(orientation="L", unit="mm", format="A4")  # Landscape
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, txt=title, ln=True, align="C")

    page_width = pdf.w - 20  # Adjust for margins

    # Calculate column widths
    col_widths = []
    for col in data.columns:
        max_content_length = max(data[col].astype(str).map(len).max(), len(col))
        col_width = max(30, min(max_content_length * 3, 50))
        col_widths.append(col_width)

    # Table header
    for i, col in enumerate(data.columns):
        pdf.cell(col_widths[i], 10, txt=col, border=1)
    pdf.ln()

    # Table rows
    for index, row in data.iterrows():
        for i, col in enumerate(data.columns):
            pdf.cell(col_widths[i], 10, txt=str(row[col]), border=1)
        pdf.ln()

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output
    
def get_pdf_download_link(buffer, filename):
    b64 = base64.b64encode(buffer.read()).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📥 Download PDF</a>'

# --------- LANGUAGE DICTIONARY --------- #

translations = {
    "en": {
        "home_title": "Welcome to SSS Commission Store System",
        "select_option": "Select an option from the left sidebar.",
        "download_backup": "💾 Download Excel Backup",
        "dealer_entry": "Dealer Entry",
        "new_entry": "🆕 New Entry",
        "existing_entry": "✏️ Existing Entry",
        "shop_name": "🛍️ Shop Name",
        "amount": "💰 Amount",
        "add_dealer_entry": "➕ Add Dealer Entry",
        "reduce_amount": "➖ Reduce Amount",
        "reduce_from_dealer": "💸 Reduce from Dealer",
        "insufficient_balance": "⚠️ Insufficient balance for reduction.",
        "shop_not_found": "❌ Shop not found.",
        "entry_added": "✅ Entry added!",
        "reduced_success": "✅ Reduced ₹{amount} from {shop}",
        "storage_entry": "Storage Entry",
        "storage_name": "🏬 Storage Name",
        "bags": "📦 Number of Bags",
        "kgs": "⚖️ Number of KGs",
        "in_whose_name": "👤 In Whose Name",
        "bond_number": "🔖 Bond Number",
        "manual_date": "📅 Manual Date",
        "save_storage_entry": "📥 Save Storage Entry",
        "bond_exists": "⚠️ Bond Number already exists.",
        "storage_saved": "✅ Storage entry saved.",
        "storage_to_dealer_entry": "Storage to Dealer Entry",
        "dealer_name": "🛍️ Dealer Name",
        "bags_moved": "📦 Bags Moved",
        "kgs_moved": "⚖️ KGs Moved",
        "amount_to_dealer": "💰 Amount to Dealer",
        "transfer": "🔄 Transfer",
        "bond_used": "⚠️ Bond Number already used.",
        "only_available": "❌ Only {available} bags available in {storage}",
        "moved_success": "✅ Moved {bags} bags to {dealer} and credited ₹{amount}",
        "dealer_statement": "Dealer Statement",
        "search_by_dealer": "🔍 Search by Dealer",
        "credit": "💰 Credit",
        "debit": "🔻 Debit",
        "balance": "🧾 Balance",
        "storage_statement": "Storage Statement",
        "search_by_storage": "🔍 Search by Storage Name",
        "storage_to_dealer_statement": "Storage to Dealer Statement",
        "search_by_dealer_storage": "🔍 Search by Dealer or Storage",
        "language": "Language",
        "english": "English",
        "tamil": "தமிழ்",
    },
    "ta": {
        "home_title": "SSS கமிஷன் கடை அமைப்புக்கு வரவேற்கிறோம்",
        "select_option": "இடதுபுறத்தில் உள்ள பட்டியலில் ஒரு விருப்பத்தை தேர்ந்தெடுக்கவும்.",
        "download_backup": "💾 எக்செல் காப்புப்பதிவை பதிவிறக்கு",
        "dealer_entry": "டீலர் பதிவுகள்",
        "new_entry": "🆕 புதிய பதிவு",
        "existing_entry": "✏️ ஏற்கனவே உள்ள பதிவு",
        "shop_name": "🛍️ கடை பெயர்",
        "amount": "💰 தொகை",
        "add_dealer_entry": "➕ டீலர் பதிவு சேர்க்கவும்",
        "reduce_amount": "➖ தொகை குறைக்கவும்",
        "reduce_from_dealer": "💸 டீலர் கணக்கில் இருந்து குறைக்கவும்",
        "insufficient_balance": "⚠️ குறைக்க போதுமான தொகை இல்லை.",
        "shop_not_found": "❌ கடை கிடைக்கவில்லை.",
        "entry_added": "✅ பதிவு சேர்க்கப்பட்டது!",
        "reduced_success": "✅ ₹{amount} குறைக்கப்பட்டது {shop} இல் இருந்து",
        "storage_entry": "சேமிப்பு பதிவு",
        "storage_name": "🏬 சேமிப்பு பெயர்",
        "bags": "📦 பைகள் எண்ணிக்கை",
        "kgs": "⚖️ கிலோ எடை",
        "in_whose_name": "👤 யாருடைய பெயரில்",
        "bond_number": "🔖 பத்திர எண்",
        "manual_date": "📅 கையேட்டு தேதி",
        "save_storage_entry": "📥 சேமிப்பு பதிவை சேமிக்கவும்",
        "bond_exists": "⚠️ பத்திர எண் ஏற்கனவே உள்ளது.",
        "storage_saved": "✅ சேமிப்பு பதிவு சேமிக்கப்பட்டது.",
        "storage_to_dealer_entry": "சேமிப்பிலிருந்து டீலர் பதிவுக்கு",
        "dealer_name": "🛍️ டீலர் பெயர்",
        "bags_moved": "📦 நகர்த்தப்பட்ட பைகள்",
        "kgs_moved": "⚖️ நகர்த்தப்பட்ட கிலோகிராம்கள்",
        "amount_to_dealer": "💰 டீலருக்கு தொகை",
        "transfer": "🔄 மாற்று",
        "bond_used": "⚠️ பத்திர எண் ஏற்கனவே பயன்படுத்தப்பட்டுள்ளது.",
        "only_available": "❌ {storage} இல் மட்டுமே {available} பைகள் உள்ளன",
        "moved_success": "✅ {bags} பைகள் {dealer}க்கு நகர்த்தப்பட்டு ₹{amount} நகலெடுக்கப்பட்டது",
        "dealer_statement": "டீலர் அறிக்கை",
        "search_by_dealer": "🔍 டீலர் பெயரில் தேடுக",
        "credit": "💰 நகல்",
        "debit": "🔻 கழிவு",
        "balance": "🧾 இருப்பு",
        "storage_statement": "சேமிப்பு அறிக்கை",
        "search_by_storage": "🔍 சேமிப்பு பெயரில் தேடுக",
        "storage_to_dealer_statement": "சேமிப்பிலிருந்து டீலர் அறிக்கை",
        "search_by_dealer_storage": "🔍 டீலர் அல்லது சேமிப்பில் தேடுக",
        "language": "மொழி",
        "english": "English",
        "tamil": "தமிழ்",
    }
}

# --------- MAIN APP --------- #

def tr(key):
    return translations[language].get(key, key)

st.set_page_config(page_title="SSS Commission Store", layout="wide")

# Language selector in sidebar
language = st.sidebar.selectbox(
    label="🌐 " + "Language",
    options=["en", "ta"],
    format_func=lambda x: translations[x]["english"] if x=="en" else translations[x]["tamil"]
)

st.title("🏪 SSS Commission Store")

initialize_excel()

menu = [
    "🏠 Home",
    "🧾 Dealer Entry",
    "📦 Storage Entry",
    "🔁 Storage to Dealer Entry",
    "📄 Dealer Statement",
    "📄 Storage Statement",
    "📄 Storage to Dealer Statement",
]
choice = st.sidebar.radio(tr("select_option"), menu)

# --------- HOME --------- #
if choice == "🏠 Home":
    st.header(tr("home_title"))
    st.markdown("---")
    st.markdown(tr("select_option"))
    with open(EXCEL_FILE, "rb") as f:
        st.download_button(tr("download_backup"), f, file_name="sss_data_backup.xlsx")

# --------- DEALER ENTRY --------- #
elif choice == "🧾 Dealer Entry":
    st.header(tr("dealer_entry"))
    st.divider()
    tab1, tab2 = st.tabs([tr("new_entry"), tr("existing_entry")])
    
    with tab1:
        shop = st.text_input(tr("shop_name"))
        amount = st.number_input(tr("amount"), min_value=0)
        if st.button(tr("add_dealer_entry")):
            if shop:
                new_data = pd.DataFrame([{
                    "Shop Name": shop, "Amount": amount, "DateTime": datetime.now()
                }])
                write_to_excel("Dealer Entry", new_data)
                st.success(tr("entry_added"))

    with tab2:
        shop = st.text_input(tr("shop_name") + " (Existing)")
        amount = st.number_input(tr("reduce_amount"), min_value=0)
        if st.button(tr("reduce_from_dealer")):
            df = read_excel_sheet("Dealer Entry")
            if shop in df["Shop Name"].values:
                existing = df[df["Shop Name"] == shop]
                balance = existing["Amount"].sum()
                if balance >= amount:
                    # Reduce the amount
                    new_data = pd.DataFrame([{
                        "Shop Name": shop,
                        "Amount": -amount,
                        "DateTime": datetime.now()
                    }])
                    write_to_excel("Dealer Entry", new_data)
                    st.success(tr("reduced_success").format(amount=amount, shop=shop))
                else:
                    st.warning(tr("insufficient_balance"))
            else:
                st.error(tr("shop_not_found"))
               

# --------- STORAGE ENTRY --------- #
elif choice == "📦 Storage Entry":
    st.header(tr("storage_entry"))
    st.divider()
    name = st.text_input(tr("storage_name"))
    bags = st.number_input(tr("bags"), min_value=0)
    kgs = st.number_input(tr("kgs"), min_value=0)
    in_whose_name = st.text_input(tr("in_whose_name"))
    bond = st.text_input(tr("bond_number"))
    manual_date = st.date_input(tr("manual_date"), value=datetime.now())
    new_data = pd.DataFrame([{
        "Storage Name": name,
        "Bags": bags,
        "KGs": kgs,
        "In Whose Name": in_whose_name,
        "Bond Number": bond,
        "DateTime": datetime.combine(manual_date, datetime.now().time())
    }])
    write_to_excel("Storage Entry", new_data)


# --------- STORAGE TO DEALER ENTRY --------- #
elif choice == "🔁 Storage to Dealer Entry":
    st.header(tr("storage_to_dealer_entry"))
    st.divider()
    
    storage = st.text_input(tr("storage_name"))
    dealer = st.text_input(tr("dealer_name"))
    bags_moved = st.number_input(tr("bags_moved"), min_value=0)
    kgs_moved = st.number_input(tr("kgs_moved"), min_value=0)
    amount_to_dealer = st.number_input(tr("amount_to_dealer"), min_value=0)
    in_whose_name = st.text_input(tr("in_whose_name"))  # <-- Added this input
    bond = st.text_input(tr("bond_number"))
    manual_date = st.date_input(tr("manual_date"), value=datetime.now())

    if st.button(tr("transfer")):
        storage_df = read_excel_sheet("Storage Entry")
        dealer_df = read_excel_sheet("Dealer Entry")
        storage_to_dealer_df = read_excel_sheet("Storage to Dealer")

        # Inform if bond already used (allow duplicates)
        if bond in storage_to_dealer_df["Bond Number"].astype(str).values:
            st.info("ℹ️ Bond Number already exists, but duplicate use is allowed.")

        # Check if bond exists in storage
        if bond not in storage_df["Bond Number"].astype(str).values:
            st.error(tr("bond_exists"))
        else:
            # Check available bags
            available_bags = storage_df[storage_df["Bond Number"].astype(str) == bond]["Bags"].sum()
            if bags_moved > available_bags:
                st.error(tr("only_available").format(available=available_bags, storage=storage))
            else:
                # Update storage bags
                new_storage_data = pd.DataFrame([{
                    "Storage Name": storage,
                    "Bags": -bags_moved,
                    "KGs": -kgs_moved,
                    "In Whose Name": in_whose_name,
                    "Bond Number": bond,
                    "DateTime": datetime.combine(manual_date, datetime.now().time())
                }])
                write_to_excel("Storage Entry", new_storage_data)

                # Add amount to dealer
                new_dealer_data = pd.DataFrame([{
                    "Shop Name": dealer,
                    "Amount": amount_to_dealer,
                    "DateTime": datetime.combine(manual_date, datetime.now().time())
                }])
                write_to_excel("Dealer Entry", new_dealer_data)

                # Record storage to dealer transfer
                new_storage_to_dealer_data = pd.DataFrame([{
                    "Storage Name": storage,
                    "Dealer Name": dealer,
                    "Bags Moved": bags_moved,
                    "KGs": kgs_moved,
                    "In Whose Name": in_whose_name,
                    "Amount": amount_to_dealer,
                    "Bond Number": bond,
                    "DateTime": datetime.combine(manual_date, datetime.now().time())
                }])
                write_to_excel("Storage to Dealer", new_storage_to_dealer_data)

                st.success(tr("moved_success").format(bags=bags_moved, dealer=dealer, amount=amount_to_dealer))
                
# --------- DEALER STATEMENT --------- #
elif choice == "📄 Dealer Statement":
    st.header(tr("dealer_statement"))
    st.divider()
    df = read_excel_sheet("Dealer Entry")
    dealer_search = st.text_input(tr("search_by_dealer"))
    if dealer_search:
        df = df[df["Shop Name"].str.contains(dealer_search, case=False, na=False)]
    if not df.empty:
        st.dataframe(df.sort_values(by="DateTime", ascending=False))
        balance = df.groupby("Shop Name")["Amount"].sum().reset_index()
        st.subheader(tr("balance"))
        st.dataframe(balance)
        pdf_buffer = generate_pdf(df, tr("dealer_statement"))
        st.markdown(get_pdf_download_link(pdf_buffer, "dealer_statement.pdf"), unsafe_allow_html=True)
    else:
        st.info("No data found.")


# --------- STORAGE STATEMENT --------- #
elif choice == "📄 Storage Statement":
    st.header(tr("storage_statement"))
    st.divider()

    storage_df = read_excel_sheet("Storage Entry")
    storage_to_dealer_df = read_excel_sheet("Storage to Dealer")

    # ✅ Only count positive bags as added
    total_bags_added = storage_df[storage_df["Bags"] > 0].groupby("Bond Number")["Bags"].sum().reset_index(name="Total Bags Added")

    # ✅ Get total bags moved from 'Storage to Dealer'
    total_bags_moved = storage_to_dealer_df.groupby("Bond Number")["Bags Moved"].sum().reset_index(name="Total Bags Moved")

    # ✅ Merge to calculate correct balance
    balance_df = pd.merge(total_bags_added, total_bags_moved, on="Bond Number", how="left")
    balance_df["Total Bags Moved"] = balance_df["Total Bags Moved"].fillna(0)
    balance_df["Balance Bags"] = balance_df["Total Bags Added"] - balance_df["Total Bags Moved"]

    # 🔄 Merge balance info back into storage entries
    storage_statement_df = pd.merge(storage_df, balance_df[["Bond Number", "Balance Bags"]], on="Bond Number", how="left")

    # ℹ️ If a bond was only used for movement (negative entries), use 'Bags' as Balance
    storage_statement_df["Balance Bags"] = storage_statement_df["Balance Bags"].fillna(
        storage_statement_df.apply(lambda row: row["Bags"] if row["Bags"] > 0 else 0, axis=1)
    )

    # 📊 Display
    st.dataframe(storage_statement_df)

    # 📄 Generate PDF for download
    pdf_buffer = generate_pdf(storage_statement_df, tr("storage_statement"))
    st.markdown(get_pdf_download_link(pdf_buffer, "storage_statement.pdf"), unsafe_allow_html=True)


# --------- STORAGE TO DEALER STATEMENT --------- #
elif choice == "📄 Storage to Dealer Statement":
    st.header(tr("storage_to_dealer_statement"))
    st.divider()
    df = read_excel_sheet("Storage to Dealer")
    search = st.text_input(tr("search_by_dealer_storage"))
    if search:
        df = df[
            df["Dealer Name"].str.contains(search, case=False, na=False) |
            df["Storage Name"].str.contains(search, case=False, na=False)
        ]
    if not df.empty:
        st.dataframe(df.sort_values(by="DateTime", ascending=False))
        pdf_buffer = generate_pdf(df, tr("storage_to_dealer_statement"))
        st.markdown(get_pdf_download_link(pdf_buffer, "storage_to_dealer_statement.pdf"), unsafe_allow_html=True)
    else:
        st.info("No data found.")
