import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
import base64
from fpdf.enums import XPos, YPos

st.set_page_config(page_title="SSS Commission Store", layout="wide")


EXCEL_FILE = "sss_data.xlsx"

# --------- ADMIN LOGIN CONFIG --------- #
ADMIN_USERNAME = "SSS"
ADMIN_PASSWORD = "Surya@29"

def admin_login():
    st.title("Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state["admin_logged_in"] = True
            st.rerun()
        else:
            st.error("Invalid username or password")

if "admin_logged_in" not in st.session_state:
    admin_login()
    st.stop()  # stop further execution till login success

# --------- UTILITY FUNCTIONS --------- #

def initialize_excel():
    if not os.path.exists(EXCEL_FILE):
        writer = pd.ExcelWriter(EXCEL_FILE, engine='openpyxl')
        pd.DataFrame(columns=["Shop Name", "Amount", "DateTime"]).to_excel(writer, sheet_name="Dealer Entry", index=False)
        pd.DataFrame(columns=["Storage Name", "Bags", "KGs", "In Whose Name", "Bond Number", "DateTime"]).to_excel(writer, sheet_name="Storage Entry", index=False)
        pd.DataFrame(columns=["Storage Name", "Dealer Name", "Bags Moved", "KGs", "In Whose Name", "Amount", "Bond Number", "DateTime"]).to_excel(writer, sheet_name="Storage to Dealer", index=False)
        pd.DataFrame(columns=["Shop Name", "Dealer Name", "Bags", "KGs", "DateTime"]).to_excel(writer, sheet_name="Shop to Dealer", index=False)  # ✅ Added this line
        writer.close()

def read_excel_sheet(sheet):
    try:
        return pd.read_excel(EXCEL_FILE, sheet_name=sheet)
    except:
        return pd.DataFrame()

# 🔥 Cached version for faster repeat reads
@st.cache_data(ttl=300)
def cached_read_excel(sheet):
    return read_excel_sheet(sheet)

def write_to_excel(sheet, new_data):
    df = read_excel_sheet(sheet)
    if df.empty:
        df = new_data
    else:
        df = pd.concat([df, new_data], ignore_index=True)
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=sheet, index=False)




from datetime import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from io import BytesIO
import streamlit as st

from fpdf import FPDF
from io import BytesIO
from datetime import datetime

def generate_pdf(dataframe, title):
    class PDF(FPDF):
        def header(self):
            # Logo
            try:
                self.image("F:/SSS Commision Store/Logo.png", x=10, y=8, w=30)
            except:
                pass

            self.set_xy(45, 10)
            self.set_font("Helvetica", size=16)
            self.set_text_color(0, 0, 128)
            self.set_fill_color(230, 240, 255)
            self.cell(w=200, h=12, text="SSS Commission Store", border=1, new_x="LMARGIN", new_y="NEXT", align="C", fill=True)

            self.set_xy(45, 22)
            self.set_font("Helvetica", size=13)
            self.set_text_color(0, 0, 0)
            self.cell(w=200, h=10, text=title, border=1, new_x="LMARGIN", new_y="NEXT", align="C")

            self.ln(15)

            # Watermark behind content
            try:
                self.image("F:/SSS Commision Store/SEMI_Logo.png", x=80, y=60, w=120)
            except:
                pass

            # Table headers
            self.set_font("Helvetica", style="B", size=9)
            self.set_x(start_x)
            for i, col in enumerate(dataframe.columns):
                self.cell(widths[i], row_height, str(col), border=1)
            self.ln()

        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", size=8)
            self.set_x(start_x)
            self.cell(total_table_width, 10, f"Generated on {datetime.now().strftime('%B %d, %Y %I:%M %p')}", align="C")

    # Setup layout
    pdf = PDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=25)

    page_width = pdf.w - 20
    custom_widths = {
        "Storage Name": 40,
        "Dealer Name": 40,
        "Shop Name": 40,
        "In Whose Name": 40,
        "Bond Number": 25,
        "Type": 20,
        "Bags": 15,
        "KGs": 15,
        "Bags Moved": 25,
        "Amount": 20,
        "Amount Collected": 25,
        "Mode": 20,
        "DateTime": 55
    }

    default_width = page_width / len(dataframe.columns)
    global widths, start_x, row_height, total_table_width
    widths = [custom_widths.get(col, default_width) for col in dataframe.columns]
    total_table_width = sum(widths)
    start_x = (pdf.w - total_table_width) / 2
    row_height = 8

    # Add first page
    pdf.add_page()

    # Font for rows
    try:
        pdf.add_font("FreeSerif", fname="fonts/FreeSerif.ttf")
        pdf.set_font("FreeSerif", size=8)
    except:
        pdf.set_font("Helvetica", size=8)

    # Print rows across pages
    for _, row in dataframe.iterrows():
        if pdf.get_y() > pdf.h - 30:
            pdf.add_page()
        pdf.set_x(start_x)
        for i, col in enumerate(dataframe.columns):
            pdf.cell(widths[i], row_height, str(row[col]), border=1)
        pdf.ln()

    # Save to buffer
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer


    
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
        "shop_to_dealer_entry": "Shop to Dealer Entry",
        "shop_to_dealer_statement": "Shop to Dealer Statement",
        "shop_name": "Shop Name",
        "dealer_name": "Dealer Name",
        "bags": "Number of Bags",
        "kgs": "KGs",
        "manual_date": "Manual Date",
        "save_entry": "Save Entry",
        "amount_collection_entry": "💰 Amount Collection Entry",
        "amount_collection_statement": "📄 Amount Collection Statement",
        "dealer_name": "Dealer Name",
        "amount_collected": "Amount Collected",
        "mode_of_payment": "Mode of Payment",
        "manual_date": "Manual Date",
        "manual_time": "Time"

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
        "shop_to_dealer_entry": "கடை முதல் டீலர் பதிவு",
        "shop_to_dealer_statement": "கடை முதல் டீலர் அறிக்கை",
        "shop_name": "🛍️ கடை பெயர்",
        "dealer_name": "🤝 டீலர் பெயர்",
        "bags": "📦 பைகள் எண்ணிக்கை",
        "kgs": "⚖️ கிலோ எடை",
        "manual_date": "📅 கையேட்டு தேதி",
        "save_entry": "✅ பதிவு சேமிக்கவும்",
        "amount_collection_entry": "💰 தொகை வசூல் பதிவு",
        "amount_collection_statement": "📄 தொகை வசூல் அறிக்கை",
        "dealer_name": "டீலர் பெயர்",
        "amount_collected": "வசூலித்த தொகை",
        "mode_of_payment": "கட்டண வகை",
        "manual_date": "கைமுறையாக உள்ளிடும் தேதி",
        "manual_time": "நேரம்"
        


    }
}

# --------- MAIN APP --------- #

def tr(key):
    return translations[language].get(key, key)



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
    "📤 Shop to Dealer Entry",
    "💰 Amount Collection Entry",    
    "📄 Dealer Statement",
    "📄 Storage Statement",
    "📄 Storage to Dealer Statement",
    "📄 Shop to Dealer Statement",
    "📄 Amount Collection Statement"   
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
    tab1, tab2, tab3 = st.tabs([tr("new_entry"), tr("existing_entry"), "📝 Edit/Delete Entry"])

    # --- Tab 1: New Entry ---
    with tab1:
        shop = st.text_input(tr("shop_name"), key="new_dealer_shop")
        amount = st.number_input(tr("amount"), min_value=0, key="new_dealer_amount")
        if st.button(tr("add_dealer_entry")):
            if shop:
                new_data = pd.DataFrame([{
                    "Shop Name": shop,
                    "Amount": amount,
                    "DateTime": datetime.now()
                }])
                write_to_excel("Dealer Entry", new_data)
                st.success(tr("entry_added"))

    # --- Tab 2: Existing Entry (Reduce Amount) ---
    with tab2:
        shop = st.text_input(tr("shop_name") + " (Existing)", key="existing_dealer_shop")
        amount = st.number_input(tr("reduce_amount"), min_value=0, key="reduce_dealer_amount")
        if st.button(tr("reduce_from_dealer")):
            df = read_excel_sheet("Dealer Entry")
            if shop in df["Shop Name"].values:
                existing = df[df["Shop Name"] == shop]
                balance = existing["Amount"].sum()
                if balance >= amount:
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

    # --- Tab 3: Edit/Delete Entry ---
    with tab3:
        st.subheader("📝 Edit or Delete Dealer Entries")
        df = read_excel_sheet("Dealer Entry")
        if df.empty:
            st.info("No Dealer Entries available.")
        else:
            df_display = df.reset_index()
            selected_index = st.selectbox("Select Entry by Index", df_display["index"], key="dealer_edit_index")
            selected_row = df_display[df_display["index"] == selected_index].iloc[0]

            shop_edit = st.text_input("Shop Name", value=selected_row["Shop Name"], key="edit_shop")
            amount_edit = st.number_input("Amount", value=float(selected_row["Amount"]), format="%.2f", key="edit_amount")
            datetime_edit = st.date_input("Date", value=selected_row["DateTime"].date(), key="edit_date")
            time_edit = st.time_input("Time", value=selected_row["DateTime"].time(), key="edit_time")

            if st.button("Save Changes", key="save_dealer_edit"):
                df.loc[selected_index, "Shop Name"] = shop_edit
                df.loc[selected_index, "Amount"] = amount_edit
                df.loc[selected_index, "DateTime"] = datetime.combine(datetime_edit, time_edit)
                with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name="Dealer Entry", index=False)
                st.success("Entry updated successfully!")

            if st.button("Delete Entry", key="delete_dealer_entry"):
                df = df.drop(selected_index).reset_index(drop=True)
                with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name="Dealer Entry", index=False)
                st.success("Entry deleted successfully!")


               

# --------- STORAGE ENTRY --------- #
elif choice == "📦 Storage Entry":
    st.header(tr("storage_entry"))
    st.divider()
    tab1, tab2 = st.tabs([tr("new_entry"), "📝 Edit/Delete Entry"])

    # ----------- TAB 1: New Entry -----------
    with tab1:
        name = st.text_input(tr("storage_name"), key="storage_name_new")
        bags = st.number_input(tr("bags"), min_value=0, key="bags_new")
        kgs = st.number_input(tr("kgs"), min_value=0, key="kgs_new")
        in_whose_name = st.text_input(tr("in_whose_name"), key="in_whose_name_new")
        bond = st.text_input(tr("bond_number"), key="bond_new")
        type_option = st.selectbox("Type", ["SSS BOLD", "CTC BOLD", "SSS SPL", "S BOLD"], key="your_key")
        manual_date = st.date_input(tr("manual_date"), value=datetime.now().date(), key="manual_date_new")
        time_input = st.time_input("Time", value=datetime.now().time(), key="time_new")


        if st.button(tr("add_storage_entry")):
            if name:
                new_data = pd.DataFrame([{
                    "Storage Name": name,
                    "Bags": bags,
                    "KGs": kgs,
                    "In Whose Name": in_whose_name,
                    "Bond Number": bond,
                    "Type": type_option,
                    "DateTime": datetime.combine(manual_date, time_input)
                }])
                write_to_excel("Storage Entry", new_data)
                st.success(tr("entry_added"))
            else:
                st.warning("Please enter Storage Name.")

    # ----------- TAB 2: Edit/Delete -----------
    with tab2:
        st.subheader("📝 Edit or Delete Storage Entries")
        df = read_excel_sheet("Storage Entry")
        if "Type" not in df.columns:
            df["Type"] = None  # or pd.NA


        if df.empty:
            st.info("No Storage Entries available.")
        else:
            df_display = df.reset_index()
            selected_index = st.selectbox("Select Entry by Index", df_display["index"], key="storage_edit_index")
            selected_row = df_display[df_display["index"] == selected_index].iloc[0]

            # Validate and correct negative values before displaying in number_input
            bags_value = max(0, int(selected_row["Bags"]))
            kgs_value = max(0.0, float(selected_row["KGs"]))

            # Pre-fill form fields with existing data
            name_edit = st.text_input(tr("storage_name"), value=selected_row["Storage Name"], key="storage_name_edit")
            bags_edit = st.number_input(tr("bags"), min_value=0, value=bags_value, key="bags_edit")
            kgs_edit = st.number_input(tr("kgs"), min_value=0.0, value=kgs_value, key="kgs_edit")
            in_whose_name_edit = st.text_input(tr("in_whose_name"), value=selected_row["In Whose Name"], key="in_whose_name_edit")
            bond_edit = st.text_input(tr("bond_number"), value=selected_row["Bond Number"], key="bond_edit")
            existing_type = selected_row["Type"] if "Type" in selected_row else "SPL"
            type_list = ["SSS BOLD", "CTC BOLD", "SSS SPL", "S BOLD"]
            existing_type = selected_row["Type"] if "Type" in selected_row else "SSS BOLD"
            type_index = type_list.index(existing_type) if existing_type in type_list else 0
            type_edit = st.selectbox("Type", type_list, index=type_index)



            manual_date_edit = st.date_input(tr("manual_date"), value=selected_row["DateTime"].date(), key="manual_date_edit")
            time_edit = st.time_input("Time", value=selected_row["DateTime"].time(), key="time_edit")

            if st.button("Save Changes", key="save_storage_entry"):
                df.loc[selected_index, "Storage Name"] = name_edit
                df.loc[selected_index, "Bags"] = bags_edit
                df.loc[selected_index, "KGs"] = kgs_edit
                df.loc[selected_index, "In Whose Name"] = in_whose_name_edit
                df.loc[selected_index, "Bond Number"] = bond_edit
                df.loc[selected_index, "Type"] = type_edit
                df.loc[selected_index, "DateTime"] = datetime.combine(manual_date_edit, time_edit)

                with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name="Storage Entry", index=False)
                st.success("Entry updated successfully!")

            if st.button("Delete Entry", key="delete_storage_entry"):
                df = df.drop(selected_index).reset_index(drop=True)
                with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name="Storage Entry", index=False)
                st.success("Entry deleted successfully!")

# --------- STORAGE TO DEALER ENTRY --------- #
elif choice == "🔁 Storage to Dealer Entry":
    st.header(tr("storage_to_dealer_entry"))
    st.divider()

    tab1, tab2 = st.tabs([tr("new_entry"), "📝 Edit/Delete Entry"])

    # ---------- TAB 1: New Entry ----------
    with tab1:
        storage = st.text_input(tr("storage_name"), key="new_storage_name_std")
        dealer = st.text_input(tr("dealer_name"), key="new_dealer_name_std")
        bags_moved = st.number_input(tr("bags_moved"), min_value=0, key="new_bags_moved_std")
        kgs_moved = st.number_input(tr("kgs_moved"), min_value=0, key="new_kgs_moved_std")
        amount_to_dealer = st.number_input(tr("amount_to_dealer"), min_value=0, key="new_amount_std")
        in_whose_name = st.text_input(tr("in_whose_name"), key="new_in_whose_std")
        bond = st.text_input(tr("bond_number"), key="new_bond_std")
        type_option = st.selectbox("Type", ["SSS BOLD", "CTC BOLD", "SSS SPL", "S BOLD"], key="your_key")
        manual_date = st.date_input(tr("manual_date"), value=datetime.now().date(), key="new_manual_date_std")
        time_edit = st.time_input("Time", value=datetime.now().time(), key="new_time_std")

        if st.button(tr("transfer"), key="transfer_new"):
            storage_df = read_excel_sheet("Storage Entry")
            dealer_df = read_excel_sheet("Dealer Entry")
            storage_to_dealer_df = read_excel_sheet("Storage to Dealer")

            if bond in storage_to_dealer_df["Bond Number"].astype(str).values:
                st.info("ℹ️ Bond Number already exists, but duplicate use is allowed.")

            if bond not in storage_df["Bond Number"].astype(str).values:
                st.error(tr("bond_exists"))
            else:
                available_bags = storage_df[storage_df["Bond Number"].astype(str) == bond]["Bags"].sum()
                if bags_moved > available_bags:
                    st.error(tr("only_available").format(available=available_bags, storage=storage))
                else:
                    date_time_obj = datetime.combine(manual_date, time_edit)

                    new_storage_data = pd.DataFrame([{
                        "Storage Name": storage,
                        "Bags": -bags_moved,
                        "KGs": -kgs_moved,
                        "In Whose Name": in_whose_name,
                        "Bond Number": bond,
                        "Type": type_option,
                        "DateTime": date_time_obj
                    }])
                    write_to_excel("Storage Entry", new_storage_data)

                    new_dealer_data = pd.DataFrame([{
                        "Shop Name": dealer,
                        "Amount": amount_to_dealer,
                        "DateTime": date_time_obj
                    }])
                    write_to_excel("Dealer Entry", new_dealer_data)

                    new_storage_to_dealer_data = pd.DataFrame([{
                        "Storage Name": storage,
                        "Dealer Name": dealer,
                        "Bags Moved": bags_moved,
                        "KGs": kgs_moved,
                        "In Whose Name": in_whose_name,
                        "Amount": amount_to_dealer,
                        "Bond Number": bond,
                        "Type": type_option,
                        "DateTime": date_time_obj
                    }])
                    write_to_excel("Storage to Dealer", new_storage_to_dealer_data)

                    st.success(tr("moved_success").format(bags=bags_moved, dealer=dealer, amount=amount_to_dealer))

    # ---------- TAB 2: Edit/Delete Entry ----------
    with tab2:
        st.subheader("📝 Edit or Delete Storage to Dealer Entries")
        df = cached_read_excel("Storage to Dealer")
        if "Type" not in df.columns:
            df["Type"] = None  # or pd.NA

        

        if df.empty:
            st.info("No Storage to Dealer entries found.")
        else:
            df_display = df.reset_index()
            selected_index = st.selectbox("Select Entry by Index", df_display["index"], key="edit_select_index_std")
            selected_row = df_display[df_display["index"] == selected_index].iloc[0]

            storage_edit = st.text_input(tr("storage_name"), value=selected_row["Storage Name"], key="edit_storage_name_std")
            dealer_edit = st.text_input(tr("dealer_name"), value=selected_row["Dealer Name"], key="edit_dealer_name_std")
            bags_edit = st.number_input(tr("bags_moved"), min_value=0.0, value=float(selected_row["Bags Moved"]), key="edit_bags_std")
            kgs_edit = st.number_input(tr("kgs_moved"), min_value=0.0, value=float(selected_row["KGs"]), key="edit_kgs_std")
            amount_edit = st.number_input(tr("amount_to_dealer"), min_value=0.0, value=float(selected_row["Amount"]), key="edit_amount_std")
            in_whose_name_edit = st.text_input(tr("in_whose_name"), value=selected_row["In Whose Name"], key="edit_in_whose_std")
            bond_edit = st.text_input(tr("bond_number"), value=selected_row["Bond Number"], key="edit_bond_std")
            existing_type = selected_row["Type"] if "Type" in selected_row else "SPL"
            type_list = ["SSS BOLD", "CTC BOLD", "SSS SPL", "S BOLD"]
            existing_type = selected_row["Type"] if "Type" in selected_row else "SSS BOLD"
            type_index = type_list.index(existing_type) if existing_type in type_list else 0
            type_edit = st.selectbox("Type", type_list, index=type_index)

            manual_date_edit = st.date_input(tr("manual_date"), value=selected_row["DateTime"].date(), key="edit_date_std")
            time_edit = st.time_input("Time", value=selected_row["DateTime"].time(), key="edit_time_std")

            if st.button("Save Changes", key="save_storage_to_dealer"):
                df.loc[selected_index, "Storage Name"] = storage_edit
                df.loc[selected_index, "Dealer Name"] = dealer_edit
                df.loc[selected_index, "Bags Moved"] = bags_edit
                df.loc[selected_index, "KGs"] = kgs_edit
                df.loc[selected_index, "Amount"] = amount_edit
                df.loc[selected_index, "In Whose Name"] = in_whose_name_edit
                df.loc[selected_index, "Bond Number"] = bond_edit
                df.loc[selected_index, "Type"] = type_edit
                df.loc[selected_index, "DateTime"] = datetime.combine(manual_date_edit, time_edit)

                with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name="Storage to Dealer", index=False)
                st.success("Entry updated successfully!")

            confirm = st.checkbox("Are you sure you want to delete this entry?", key="confirm_delete_std")
            if st.button("Delete Entry", key="delete_entry_std"):
                if confirm:
                    df = df.drop(selected_index).reset_index(drop=True)
                    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                        df.to_excel(writer, sheet_name="Storage to Dealer", index=False)
                    st.success("Entry deleted successfully!")
                else:
                    st.info("Please confirm delete by checking the box.")

        
# --------- SHOP TO DEALER ENTRY --------- #
elif choice == "📤 Shop to Dealer Entry":
    st.header(tr("shop_to_dealer_entry"))
    st.divider()

    tab1, tab2 = st.tabs(["🆕 New Entry", "📝 Edit/Delete Entry"])

    # ----------- TAB 1: New Entry -----------
    with tab1:
        shop_name = st.text_input("🛍️ Shop Name", key="shop_to_dealer_new_shop")
        dealer_name = st.text_input("🤝 Dealer Name", key="shop_to_dealer_new_dealer")
        bags = st.number_input("📦 Number of Bags", min_value=0, key="shop_to_dealer_new_bags")
        kgs = st.number_input("⚖️ KGs", min_value=0.0, key="shop_to_dealer_new_kgs")
        type_option = st.selectbox("Type", ["SSS BOLD", "CTC BOLD", "SSS SPL", "S BOLD"], key="your_key")
        manual_date = st.date_input(tr("manual_date"), value=datetime.now().date(), key="shop_to_dealer_new_date")
        time_input = st.time_input("Time", value=datetime.now().time(), key="shop_to_dealer_new_time")

        if st.button("✅ Save Entry", key="shop_to_dealer_save_new"):
            new_data = pd.DataFrame([{
                "Shop Name": shop_name,
                "Dealer Name": dealer_name,
                "Bags": bags,
                "KGs": kgs,
                "Type": type_option,
                "DateTime": datetime.combine(manual_date, time_input)
            }])
            write_to_excel("Shop to Dealer", new_data)
            st.success("✅ Entry saved successfully!")

    # ----------- TAB 2: Edit/Delete Entry -----------
    with tab2:
        st.subheader("📝 Edit or Delete Shop to Dealer Entries")
        df = read_excel_sheet("Shop to Dealer")
        if "Type" not in df.columns:
            df["Type"] = None  # or pd.NA


        if df.empty:
            st.info("No entries found.")
        else:
            df_display = df.reset_index()
            selected_index = st.selectbox("Select Entry by Index", df_display["index"], key="shop_to_dealer_select_index")
            selected_row = df_display[df_display["index"] == selected_index].iloc[0]

            shop_edit = st.text_input("Shop Name", value=selected_row["Shop Name"], key="shop_to_dealer_edit_shop")
            dealer_edit = st.text_input("Dealer Name", value=selected_row["Dealer Name"], key="shop_to_dealer_edit_dealer")
            bags_edit = st.number_input("Number of Bags", min_value=0, value=int(selected_row["Bags"]), key="shop_to_dealer_edit_bags")
            kgs_edit = st.number_input("KGs", min_value=0.0, value=float(selected_row["KGs"]), key="shop_to_dealer_edit_kgs")
            manual_date_edit = st.date_input("Manual Date", value=selected_row["DateTime"].date(), key="shop_to_dealer_edit_date")
            existing_type = selected_row["Type"] if "Type" in selected_row else "SPL"
            type_list = ["SSS BOLD", "CTC BOLD", "SSS SPL", "S BOLD"]
            existing_type = selected_row["Type"] if "Type" in selected_row else "SSS BOLD"
            type_index = type_list.index(existing_type) if existing_type in type_list else 0
            type_edit = st.selectbox("Type", type_list, index=type_index)


            time_edit = st.time_input("Time", value=selected_row["DateTime"].time(), key="shop_to_dealer_edit_time")

            if st.button("💾 Save Changes", key="shop_to_dealer_edit_save"):
                df.loc[selected_index, "Shop Name"] = shop_edit
                df.loc[selected_index, "Dealer Name"] = dealer_edit
                df.loc[selected_index, "Bags"] = bags_edit
                df.loc[selected_index, "KGs"] = kgs_edit
                df.loc[selected_index, "Type"] = type_edit
                df.loc[selected_index, "DateTime"] = datetime.combine(manual_date_edit, time_edit)
                with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name="Shop to Dealer", index=False)
                st.success("✅ Entry updated successfully!")

            if st.button("🗑️ Delete Entry", key="shop_to_dealer_delete"):
                df = df.drop(selected_index).reset_index(drop=True)
                with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name="Shop to Dealer", index=False)
                st.success("🗑️ Entry deleted successfully!")

# --------- AMOUNT COLLECTION ENTRY --------- #
elif choice == "💰 Amount Collection Entry":
    st.header("💰 Amount Collection Entry")
    st.divider()

    tab1, tab2 = st.tabs(["🆕 New Entry", "📝 Edit/Delete Entry"])

    with tab1:
        dealer_name = st.text_input("🤝 Dealer Name", key="ac_dealer_name")
        amount = st.number_input("💸 Amount Collected", min_value=0.0, key="ac_amount")
        mode = st.selectbox("💳 Mode of Payment", ["Cash", "UPI", "Bank","Check"], key="ac_mode")
        manual_date = st.date_input("📅 Manual Date", value=datetime.now().date(), key="ac_date")
        manual_time = st.time_input("⏰ Manual Time", value=datetime.now().time(), key="ac_time")

        if st.button("✅ Save Entry", key="ac_save_btn"):
            new_data = pd.DataFrame([{
                "Dealer Name": dealer_name,
                "Amount": amount,
                "Mode": mode,
                "DateTime": datetime.combine(manual_date, manual_time)
            }])
            write_to_excel("Amount Collection", new_data)
            st.success("✅ Amount collection entry saved successfully!")

    with tab2:
        st.subheader("📝 Edit or Delete Amount Collection Entries")
        df = read_excel_sheet("Amount Collection")

        if df.empty:
            st.info("No amount collection entries found.")
        else:
            df_display = df.reset_index()
            selected_index = st.selectbox("Select Entry by Index", df_display["index"], key="ac_edit_index")
            selected_row = df_display[df_display["index"] == selected_index].iloc[0]

            dealer_edit = st.text_input("Dealer Name", value=selected_row["Dealer Name"], key="ac_edit_dealer")
            amount_edit = st.number_input("Amount", min_value=0.0, value=float(selected_row["Amount"]), key="ac_edit_amount")
            mode_edit = st.selectbox("Mode", ["Cash", "UPI", "Bank","Check"], index=["Cash", "UPI", "Bank","Check"].index(selected_row["Mode"]), key="ac_edit_mode")
            manual_date_edit = st.date_input("Manual Date", value=selected_row["DateTime"].date(), key="ac_edit_date")
            manual_time_edit = st.time_input("Time", value=selected_row["DateTime"].time(), key="ac_edit_time")

            if st.button("💾 Save Changes", key="ac_save_changes"):
                df.loc[selected_index, "Dealer Name"] = dealer_edit
                df.loc[selected_index, "Amount"] = amount_edit
                df.loc[selected_index, "Mode"] = mode_edit
                df.loc[selected_index, "DateTime"] = datetime.combine(manual_date_edit, manual_time_edit)

                with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name="Amount Collection", index=False)
                st.success("✅ Entry updated successfully!")

            if st.button("🗑️ Delete Entry", key="ac_delete"):
                df = df.drop(selected_index).reset_index(drop=True)
                with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name="Amount Collection", index=False)
                st.success("🗑️ Entry deleted successfully!")



    
                
# --------- DEALER STATEMENT --------- #
elif choice == "📄 Dealer Statement":
    st.header(tr("dealer_statement"))
    st.divider()

    df = read_excel_sheet("Dealer Entry")


    # Convert DateTime column to datetime safely
    df["DateTime"] = pd.to_datetime(df["DateTime"], errors='coerce')

    # --- Filters ---

    # Multiselect for Dealer Names (sorted for better UX)
    dealer_options = sorted(df["Shop Name"].dropna().unique())
    selected_dealers = st.multiselect(tr("select_dealer"), options=dealer_options, key="dealer_multiselect")

    # Text input for dealer search (optional)
    dealer_search = st.text_input(tr("search_by_dealer"), key="dealer_search")

    # Amount slider filter with safe min/max check
    min_amount = int(df["Amount"].min()) if not df["Amount"].empty else 0
    max_amount = int(df["Amount"].max()) if not df["Amount"].empty else 10000
    if min_amount == max_amount:
        max_amount = min_amount + 1
    amount_range = st.slider(
        tr("filter_amount_range"), 
        min_value=min_amount, max_value=max_amount, 
        value=(min_amount, max_amount),
        key="amount_slider"
    )

    # Enable date filter checkbox
    enable_date_filter = st.checkbox(tr("enable_date_filter"), key="enable_date_filter")
    if enable_date_filter:
        min_date = df["DateTime"].min().date() if not df["DateTime"].isnull().all() else datetime.today().date()
        max_date = df["DateTime"].max().date() if not df["DateTime"].isnull().all() else datetime.today().date()
        start_date = st.date_input(tr("start_date"), value=min_date, key="start_date")
        end_date = st.date_input(tr("end_date"), value=max_date, key="end_date")
    else:
        start_date = None
        end_date = None

    # --- Apply filters stepwise ---
    filtered_df = df.copy()

    # 1. Filter by multiselect dealers
    if selected_dealers:
        filtered_df = filtered_df[filtered_df["Shop Name"].isin(selected_dealers)]

    # 2. Filter by dealer search input
    if dealer_search:
        filtered_df = filtered_df[filtered_df["Shop Name"].str.contains(dealer_search, case=False, na=False)]

    # 3. Filter by amount range
    filtered_df = filtered_df[
        (filtered_df["Amount"] >= amount_range[0]) & (filtered_df["Amount"] <= amount_range[1])
    ]

    # 4. Filter by date range if enabled
    if enable_date_filter and start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df["DateTime"].dt.date >= start_date) & (filtered_df["DateTime"].dt.date <= end_date)
        ]

    # --- Display results ---
    if not filtered_df.empty:
        st.dataframe(filtered_df.sort_values(by="DateTime", ascending=False))

        # Show sum balance by dealer
        balance = filtered_df.groupby("Shop Name")["Amount"].sum().reset_index()
        st.subheader(tr("balance"))
        st.dataframe(balance)

        # PDF export
        pdf_df = filtered_df.drop(columns=["In Whose Name"], errors="ignore")
        pdf_buffer = generate_pdf(pdf_df, tr("dealer_statement"))

        st.markdown(get_pdf_download_link(pdf_buffer, "dealer_statement.pdf"), unsafe_allow_html=True)
    else:
        st.info(tr("no_data_found"))

# --------- STORAGE STATEMENT --------- #
elif choice == "📄 Storage Statement":
    st.header(tr("storage_statement"))
    st.divider()

    # Read both sheets
    storage_df = read_excel_sheet("Storage Entry")
    std_df = read_excel_sheet("Storage to Dealer")

    # Ensure columns exist
    if "Type" not in storage_df.columns:
        storage_df["Type"] = None
    if "Dealer Name" not in std_df.columns:
        std_df["Dealer Name"] = None

    # Clean and convert datetimes
    storage_df = storage_df.dropna(subset=["Storage Name"])
    storage_df = storage_df[storage_df["Storage Name"].str.strip() != ""]
    storage_df["DateTime"] = pd.to_datetime(storage_df["DateTime"], errors='coerce')
    std_df["DateTime"] = pd.to_datetime(std_df["DateTime"], errors='coerce')

    # Sort for later use
    std_df_sorted = std_df.sort_values(by=["Bond Number", "DateTime"])

    # Merge on Bond Number and DateTime
    storage_df = storage_df.merge(
        std_df[["Bond Number", "DateTime", "Dealer Name"]],
        on=["Bond Number", "DateTime"],
        how="left"
    )

    # ✅ Fix: Only assign Dealer Name if Bags < 0
    def get_latest_dealer(bond, dt):
        sub = std_df[std_df["Bond Number"] == bond]
        sub = sub[sub["DateTime"] <= dt]
        if not sub.empty:
            return sub.sort_values("DateTime", ascending=False)["Dealer Name"].iloc[0]
        return None

    def assign_dealer(row):
        if pd.notna(row["Dealer Name"]):
            return row["Dealer Name"]
        if row["Bags"] < 0:
            return get_latest_dealer(row["Bond Number"], row["DateTime"])
        return None

    storage_df["Dealer Name"] = storage_df.apply(assign_dealer, axis=1)

    # Sort for correct balance logic
    storage_df = storage_df.sort_values(by=["Bond Number", "DateTime"])

    # ✅ Corrected Bond Balance Logic
    def calculate_running_balance(group):
        group = group.sort_values("DateTime")
        balance = 0
        balance_list = []
        for _, row in group.iterrows():
            balance += row["Bags"]
            balance_list.append(balance)
        group["Balance Bags"] = balance_list
        return group

    # Apply calculation per Bond Number
    storage_statement_df = (
        storage_df.groupby("Bond Number", group_keys=False)
        .apply(calculate_running_balance)
        .reset_index(drop=True)
    )

    storage_statement_df = storage_statement_df.sort_values(by=["Bond Number", "DateTime"])

    # -------------------- Filters --------------------
    storage_options = sorted(storage_statement_df["Storage Name"].dropna().unique())
    selected_storages = st.multiselect("Select Storage Name", options=storage_options, key="storage_name_multiselect")

    bond_search = st.text_input(tr("search_by_bond_number"), key="bond_search")

    # ✅ Dealer Name Filter
    dealer_options = sorted(storage_statement_df["Dealer Name"].dropna().unique())
    selected_dealers = st.multiselect("Select Dealer Name", options=dealer_options, key="dealer_name_multiselect")

    type_filter = st.selectbox("Filter by Type", ["All", "SSS BOLD", "CTC BOLD", "SSS SPL", "S BOLD"])

    min_bags = int(storage_statement_df["Balance Bags"].min()) if not storage_statement_df["Balance Bags"].empty else 0
    max_bags = int(storage_statement_df["Balance Bags"].max()) if not storage_statement_df["Balance Bags"].empty else 10000
    if min_bags == max_bags:
        max_bags += 1
    bags_range = st.slider(
        tr("filter_bags_range"),
        min_value=min_bags,
        max_value=max_bags,
        value=(min_bags, max_bags),
        key="bags_slider"
    )

    enable_date_filter = st.checkbox(tr("enable_date_filter"), key="storage_enable_date_filter")
    if enable_date_filter:
        min_date = storage_statement_df["DateTime"].min().date() if not storage_statement_df["DateTime"].isnull().all() else datetime.today().date()
        max_date = storage_statement_df["DateTime"].max().date() if not storage_statement_df["DateTime"].isnull().all() else datetime.today().date()
        start_date = st.date_input(tr("start_date"), value=min_date, key="storage_start_date")
        end_date = st.date_input(tr("end_date"), value=max_date, key="storage_end_date")
    else:
        start_date = None
        end_date = None

    # -------------------- Apply Filters --------------------
    filtered_df = storage_statement_df.copy()

    if selected_storages:
        filtered_df = filtered_df[filtered_df["Storage Name"].isin(selected_storages)]

    if bond_search:
        filtered_df = filtered_df[filtered_df["Bond Number"].astype(str).str.contains(bond_search, case=False, na=False)]

    if selected_dealers:
        filtered_df = filtered_df[filtered_df["Dealer Name"].isin(selected_dealers)]

    if type_filter != "All":
        filtered_df = filtered_df[filtered_df["Type"] == type_filter]

    filtered_df = filtered_df[
        (filtered_df["Balance Bags"] >= bags_range[0]) & (filtered_df["Balance Bags"] <= bags_range[1])
    ]

    if enable_date_filter and start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df["DateTime"].dt.date >= start_date) & (filtered_df["DateTime"].dt.date <= end_date)
        ]

    # -------------------- Output --------------------
    if not filtered_df.empty:
        st.dataframe(filtered_df)
        pdf_df = filtered_df.drop(columns=["In Whose Name"], errors="ignore")
        pdf_buffer = generate_pdf(pdf_df, tr("storage_statement"))
        st.markdown(get_pdf_download_link(pdf_buffer, "storage_statement.pdf"), unsafe_allow_html=True)
    else:
        st.info(tr("no_data_found"))


# --------- STORAGE TO DEALER STATEMENT --------- #
elif choice == "📄 Storage to Dealer Statement":
    st.header(tr("storage_to_dealer_statement"))
    st.divider()

    df = read_excel_sheet("Storage to Dealer")
    if "Type" not in df.columns:
        df["Type"] = None



    # 👉 Optional Type Filter
    type_filter = st.selectbox("Filter by Type", ["All", "SSS BOLD", "CTC BOLD", "SSS SPL", "S BOLD"])
    if type_filter != "All":
         df = df[df["Type"] == type_filter]


    # --- Filters ---

    # Multiselect for Dealer Names
    dealer_options = sorted(df["Dealer Name"].dropna().unique())
    selected_dealers = st.multiselect(tr("select_dealer"), options=dealer_options, key="storage_to_dealer_select")

    # Multiselect for Storage Names
    storage_options = sorted(df["Storage Name"].dropna().unique())
    selected_storages = st.multiselect(tr("select_storage"), options=storage_options, key="storage_to_dealer_storage_select")

    # Text input search across Dealer and Storage names
    search_text = st.text_input(tr("search_by_dealer_storage"), key="storage_to_dealer_search")

    # Text input for Bond Number search
    bond_search_text = st.text_input("🔍 Search by Bond Number", key="storage_to_dealer_bond_search")

    # Enable date filter checkbox
    enable_date_filter = st.checkbox(tr("enable_date_filter"), key="storage_to_dealer_date_filter")
    if enable_date_filter:
        min_date = df["DateTime"].min().date() if not df["DateTime"].isnull().all() else datetime.today().date()
        max_date = df["DateTime"].max().date() if not df["DateTime"].isnull().all() else datetime.today().date()
        start_date = st.date_input(tr("start_date"), value=min_date, key="storage_to_dealer_start_date")
        end_date = st.date_input(tr("end_date"), value=max_date, key="storage_to_dealer_end_date")
    else:
        start_date = None
        end_date = None

    # --- Apply filters ---
    filtered_df = df.copy()

    # Filter by selected dealers
    if selected_dealers:
        filtered_df = filtered_df[filtered_df["Dealer Name"].isin(selected_dealers)]

    # Filter by selected storages
    if selected_storages:
        filtered_df = filtered_df[filtered_df["Storage Name"].isin(selected_storages)]

    # Filter by search text (Dealer Name / Storage Name)
    if search_text:
        filtered_df = filtered_df[
            filtered_df["Dealer Name"].str.contains(search_text, case=False, na=False) |
            filtered_df["Storage Name"].str.contains(search_text, case=False, na=False)
        ]

    # Filter by Bond Number search
    if bond_search_text:
        filtered_df = filtered_df[
            filtered_df["Bond Number"].astype(str).str.contains(bond_search_text, case=False, na=False)
        ]

    # Filter by date range if enabled
    if enable_date_filter and start_date and end_date:
        filtered_df["DateOnly"] = pd.to_datetime(filtered_df["DateTime"]).dt.date
        filtered_df = filtered_df[(filtered_df["DateOnly"] >= start_date) & (filtered_df["DateOnly"] <= end_date)]
        filtered_df = filtered_df.drop(columns=["DateOnly"])

    # --- Display ---
    if not filtered_df.empty:
        st.dataframe(filtered_df.sort_values(by="DateTime", ascending=False))

        # PDF export
        pdf_df = filtered_df.drop(columns=["In Whose Name"], errors="ignore")
        pdf_buffer = generate_pdf(pdf_df, tr("storage_to_dealer_statement"))
        st.markdown(get_pdf_download_link(pdf_buffer, "storage_to_dealer_statement.pdf"), unsafe_allow_html=True)
    else:
        st.info(tr("no_data_found"))



# --------- SHOP TO DEALER STATEMENT --------- #
elif choice == "📄 Shop to Dealer Statement":
    st.header(tr("shop_to_dealer_entry"))
    bags = st.number_input(tr("bags"), min_value=0)

    st.divider()

    df = read_excel_sheet("Shop to Dealer")
    if "Type" not in df.columns:
        df["Type"] = None


    # 👉 Optional Type Filter
    type_filter = st.selectbox("Filter by Type", ["All", "SSS BOLD", "CTC BOLD", "SSS SPL", "S BOLD"])
    if type_filter != "All":
        df = df[df["Type"] == type_filter]

    df["DateTime"] = pd.to_datetime(df["DateTime"], errors="coerce")

    shop_options = sorted(df["Shop Name"].dropna().unique())
    selected_shops = st.multiselect("Select Shop Name", options=shop_options)

    dealer_options = sorted(df["Dealer Name"].dropna().unique())
    selected_dealers = st.multiselect("Select Dealer Name", options=dealer_options)

    enable_date_filter = st.checkbox("📅 Enable Date Filter")
    if enable_date_filter:
        min_date = df["DateTime"].min().date()
        max_date = df["DateTime"].max().date()
        start_date = st.date_input(tr("start_date"), value=min_date, key="shop_to_dealer_start")
        end_date = st.date_input(tr("end_date"), value=max_date, key="shop_to_dealer_end")

    else:
        start_date = None
        end_date = None

    filtered_df = df.copy()

    if selected_shops:
        filtered_df = filtered_df[filtered_df["Shop Name"].isin(selected_shops)]
    if selected_dealers:
        filtered_df = filtered_df[filtered_df["Dealer Name"].isin(selected_dealers)]
    if enable_date_filter and start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df["DateTime"].dt.date >= start_date) & (filtered_df["DateTime"].dt.date <= end_date)
        ]

    if not filtered_df.empty:
        st.dataframe(filtered_df.sort_values(by="DateTime", ascending=False))
        pdf_df = filtered_df.drop(columns=["In Whose Name"], errors="ignore")
        pdf_buffer = generate_pdf(pdf_df, "Shop to Dealer Statement")
        st.markdown(get_pdf_download_link(pdf_buffer, "shop_to_dealer_statement.pdf"), unsafe_allow_html=True)
    else:
        st.info("No data found.")


# --------- AMOUNT COLLECTION STATEMENT --------- #
elif choice == "📄 Amount Collection Statement":
    st.header("📄 Amount Collection Statement")
    st.divider()

    df = read_excel_sheet("Amount Collection")
    if "DateTime" in df.columns:
        df["DateTime"] = pd.to_datetime(df["DateTime"], errors="coerce")

    if df.empty:
        st.info("No amount collection data available.")
    else:
        dealer_options = sorted(df["Dealer Name"].dropna().unique())
        selected_dealers = st.multiselect("Select Dealer Name", options=dealer_options, key="acs_dealer_filter")

        mode_filter = st.selectbox("Filter by Mode", ["All", "Cash", "UPI", "Bank"], key="acs_mode_filter")

        enable_date_filter = st.checkbox("Enable Date Filter", key="acs_enable_date")
        if enable_date_filter:
            min_date = df["DateTime"].min().date()
            max_date = df["DateTime"].max().date()
            start_date = st.date_input("Start Date", value=min_date, key="acs_start_date")
            end_date = st.date_input("End Date", value=max_date, key="acs_end_date")
        else:
            start_date = None
            end_date = None

        # Apply filters
        filtered_df = df.copy()
        if selected_dealers:
            filtered_df = filtered_df[filtered_df["Dealer Name"].isin(selected_dealers)]

        if mode_filter != "All":
            filtered_df = filtered_df[filtered_df["Mode"] == mode_filter]

        if enable_date_filter and start_date and end_date:
            filtered_df = filtered_df[
                (filtered_df["DateTime"].dt.date >= start_date) &
                (filtered_df["DateTime"].dt.date <= end_date)
            ]

        if not filtered_df.empty:
            st.dataframe(filtered_df)
            pdf_df = filtered_df.drop(columns=["In Whose Name"], errors="ignore")
            pdf_buffer = generate_pdf(pdf_df, "Amount Collection Statement")
            st.markdown(get_pdf_download_link(pdf_buffer, "amount_collection_statement.pdf"), unsafe_allow_html=True)
        else:
            st.warning("No data found for the selected filters.")

