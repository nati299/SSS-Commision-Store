# SSS-Commission-Store  
A Python-based inventory and commission management application for dealers and storage units, featuring **Excel integration**, **transaction tracking**, and **real-time balance updates**.

## Project Description:  
SSS Commission Store is designed to manage dealer accounts, storage stock, and commission transactions efficiently.  
The system allows new and existing dealer entries, storage management, and transferring stock from storage to dealers with automatic updates in balances and stock counts.  
It also generates statements for dealers, storage, and storage-to-dealer transfers, all saved in Excel format for record-keeping.

## Features:
- Dealer Entry (New / Existing) with balance tracking.
- Storage Entry with item count and bond number.
- Transfer stock from storage to dealer with automatic balance update.
- Generate and view Excel statements for:
  - Dealer transactions
  - Storage transactions
  - Storage-to-dealer transactions
- Timestamped records for all entries.
- Simple, interactive user interface.

## Running the app:
Python:  
- Run <code>pip install -r requirements.txt</code> to install all dependencies.  
- Ensure the Excel template files exist or the script will create them automatically.  
- Run <code>python main.py</code> to start the application.

## Tech Stack:
- Python  
- Pandas (Data handling)  
- OpenPyXL (Excel integration)  
- Streamlit / Tkinter (UI - depending on your implementation)  

## Data Structure:
The Excel sheets store the following information:  

**Dealer Entry:**
- Date & Time  
- Shop Name  
- Amount (Added or Reduced)  
- Current Balance  

**Storage Entry:**
- Date & Time  
- Storage Name  
- Bond Number  
- Bags/KG Count  

**Storage to Dealer:**
- Date & Time  
- Storage Name  
- Dealer Name  
- Bags Transferred  
- Amount  

## Current Condition:
The application is fully functional:  
- Handles dealer and storage operations smoothly.  
- Automatically updates and maintains all statements.  
- UI is user-friendly and easy to navigate.  

## Project Components:
- `main.py` – Runs the main application with navigation.  
- `dealer_entry.py` – Handles new and existing dealer transactions.  
- `storage_entry.py` – Handles storage inventory entry.  
- `storage_to_dealer.py` – Manages transfer of stock from storage to dealers.  
- `statements/` – Stores generated Excel statement files.  
- `requirements.txt` – List of dependencies.  

