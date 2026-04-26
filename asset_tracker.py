import streamlit as st
import csv
import os
from datetime import date

# File where assets will be saved
CSV_FILE = "assets.csv"

# Create the CSV file with headers if it doesn't exist yet
def initialize_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Asset Name",
                "Serial Number",
                "Model",
                "Manufacturer",
                "Location",
                "Status",
                "Date Added"
            ])

initialize_csv()

# Initialize session state
if "clear_form" not in st.session_state:
    st.session_state.clear_form = False

if st.session_state.clear_form:
    st.session_state.clear_form = False
    st.session_state.asset_name = ""
    st.session_state.serial_number = ""
    st.session_state.model = ""
    st.session_state.manufacturer = ""
    st.session_state.location = ""

# Sidebar navigation
st.sidebar.title("Asset Tracker")
menu = st.sidebar.radio(
    "Menu",
    ["Add Asset", "View All Assets", "Search", "Update Status", "Delete Asset"]
)

# ── Add Asset ──────────────────────────────────────
if menu == "Add Asset":
    st.title("Add New Asset")

    asset_name = st.text_input("Asset Name", key="asset_name")
    serial_number = st.text_input("Serial Number", key="serial_number")
    model = st.text_input("Model", key="model")
    manufacturer = st.text_input("Manufacturer", key="manufacturer")
    location = st.text_input("Location", key="location")
    status = st.selectbox("Status", ["Active", "In Repair", "End of Life", "Retired"])
    date_added = st.date_input("Date Added", value=date.today())

    if st.button("Add Asset"):
        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                asset_name,
                serial_number,
                model,
                manufacturer,
                location,
                status,
                date_added
            ])
        st.success(f"Asset '{asset_name}' added successfully!")
        st.session_state.clear_form = True
        st.rerun()

# ── View All Assets ────────────────────────────────
elif menu == "View All Assets":
    st.title("All Assets")

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r") as f:
            reader = csv.DictReader(f)
            assets = list(reader)

        if assets:
            st.dataframe(assets)
        else:
            st.info("No assets added yet.")
    else:
        st.info("No assets added yet.")

# ── Search ─────────────────────────────────────────
elif menu == "Search":
    st.title("Search Assets")

    search_term = st.text_input("Search by Serial Number")

    if st.button("Search"):
        if search_term:
            with open(CSV_FILE, "r") as f:
                reader = csv.DictReader(f)
                results = [row for row in reader if search_term.lower() in row["Serial Number"].lower()]

            if results:
                st.dataframe(results)
            else:
                st.warning(f"No assets found with serial number containing '{search_term}'")
        else:
            st.warning("Please enter a serial number to search for.")

# ── Update Status ──────────────────────────────────
elif menu == "Update Status":
    st.title("Update Asset Status")

    update_serial = st.text_input("Enter Serial Number to Update")

    if st.button("Find Asset"):
        if update_serial:
            with open(CSV_FILE, "r") as f:
                reader = csv.DictReader(f)
                assets = list(reader)

            match = [row for row in assets if row["Serial Number"].lower() == update_serial.lower()]

            if match:
                st.session_state.update_asset = match[0]
            else:
                st.warning(f"No asset found with serial number '{update_serial}'")
        else:
            st.warning("Please enter a serial number.")

    if "update_asset" in st.session_state:
        asset = st.session_state.update_asset
        st.write(f"**Found:** {asset['Asset Name']} — {asset['Model']}")

        new_status = st.selectbox(
            "New Status",
            ["Active", "In Repair", "End of Life", "Retired"],
            key="new_status"
        )

        if st.button("Update Status"):
            with open(CSV_FILE, "r") as f:
                reader = csv.DictReader(f)
                all_assets = list(reader)

            for row in all_assets:
                if row["Serial Number"].lower() == asset["Serial Number"].lower():
                    row["Status"] = new_status

            with open(CSV_FILE, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "Asset Name", "Serial Number", "Model",
                    "Manufacturer", "Location", "Status", "Date Added"
                ])
                writer.writeheader()
                writer.writerows(all_assets)

            st.success(f"Status updated to '{new_status}' successfully!")
            del st.session_state.update_asset
            st.rerun()

# ── Delete Asset ───────────────────────────────────
elif menu == "Delete Asset":
    st.title("Delete Asset")

    delete_serial = st.text_input("Enter Serial Number to Delete")

    if st.button("Find Asset"):
        if delete_serial:
            with open(CSV_FILE, "r") as f:
                reader = csv.DictReader(f)
                assets = list(reader)

            match = [row for row in assets if row["Serial Number"].lower() == delete_serial.lower()]

            if match:
                st.session_state.delete_asset = match[0]
            else:
                st.warning(f"No asset found with serial number '{delete_serial}'")
        else:
            st.warning("Please enter a serial number.")

    if "delete_asset" in st.session_state:
        asset = st.session_state.delete_asset
        st.write(f"**Found:** {asset['Asset Name']} — {asset['Model']}")
        st.error("Are you sure you want to delete this asset? This cannot be undone.")

        if st.button("Yes, Delete Asset"):
            with open(CSV_FILE, "r") as f:
                reader = csv.DictReader(f)
                all_assets = list(reader)

            all_assets = [row for row in all_assets if row["Serial Number"].lower() != asset["Serial Number"].lower()]

            with open(CSV_FILE, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "Asset Name", "Serial Number", "Model",
                    "Manufacturer", "Location", "Status", "Date Added"
                ])
                writer.writeheader()
                writer.writerows(all_assets)

            st.success(f"Asset '{asset['Asset Name']}' deleted successfully!")
            del st.session_state.delete_asset
            st.rerun()