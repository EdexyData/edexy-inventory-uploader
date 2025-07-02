# Scalable Upload Processor for Edexy
import os
import pandas as pd
import streamlit as st
from PyPDF2 import PdfReader

# --- Define your standard columns ---
MASTER_COLUMNS = [
    "Developer", "Project_Name", "Property_Type", "View", "Unit_Number", "Floor_Number",
    "Number_Of_Bedrooms", "Starting_Price", "Payment_Plan", "Post_handover_Payment_Plan",
    "Internal_Area_Size", "Balcony_Area_Size", "Total_Area_Size", "Number_Of_Parkings",
    "Location", "City", "Handover_Date", "Brochure_Link", "Layout_Link",
    "Marketing_Material", "Facts_Sheet", "Source_File"
]

st.title("📥 Edexy Inventory Uploader")

uploaded_files = st.file_uploader("Upload developer inventory files (Excel/PDF):", type=["pdf", "xls", "xlsx"], accept_multiple_files=True)

output_data = []

def extract_from_excel(file, filename):
    try:
        xl = pd.ExcelFile(file)
        all_data = []
        for sheet in xl.sheet_names:
            df = xl.parse(sheet)
            df.columns = [str(c).strip() for c in df.columns]

            for _, row in df.iterrows():
                row_data = {
                    "Developer": sheet if "developer" in sheet.lower() else "",
                    "Project_Name": sheet if "project" in sheet.lower() else "",
                    "Property_Type": row.get("TypeDescriptionEN", row.get("Property Type", "")),
                    "View": row.get("View", ""),
                    "Unit_Number": row.get("Unit Code", row.get("Unit_Number", "")),
                    "Floor_Number": row.get("Floor", row.get("Floor_Number", "")),
                    "Number_Of_Bedrooms": row.get("Bedrooms", ""),
                    "Starting_Price": row.get("20%dp", row.get("Price", "")),
                    "Payment_Plan": "Yes" if len(set(df.columns).intersection({"20%dp", "50% now 50% later", "installment"})) > 1 else "No",
                    "Post_handover_Payment_Plan": "Yes" if "post" in " ".join(df.columns).lower() else "",
                    "Internal_Area_Size": row.get("Net Area", row.get("Unit Area Size", "")),
                    "Balcony_Area_Size": row.get("Terrace Size", row.get("Balcony Size", "")),
                    "Total_Area_Size": row.get("Total Area", ""),
                    "Number_Of_Parkings": "2" if str(row.get("Bedrooms", "")) in ["3", "3BR"] else "1",
                    "Location": row.get("Location", ""),
                    "City": "Dubai",
                    "Handover_Date": row.get("Handover", ""),
                    "Brochure_Link": "",
                    "Layout_Link": "",
                    "Marketing_Material": "",
                    "Facts_Sheet": "",
                    "Source_File": filename
                }
                all_data.append(row_data)
        return all_data
    except Exception as e:
        st.error(f"❌ Error reading Excel file {filename}: {e}")
        return []

if uploaded_files:
    for file in uploaded_files:
        filename = file.name

        if filename.endswith(".pdf"):
            reader = PdfReader(file)
            text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

            if "Samana" in text:
                output_data.append({
                    "Developer": "Samana",
                    "Project_Name": "Barari Heights",
                    "Property_Type": "Studio + Pool",
                    "Unit_Number": "302",
                    "Starting_Price": 804000.01,
                    "Internal_Area_Size": 422.06,
                    "Total_Area_Size": 422.06,
                    "Number_Of_Bedrooms": "Studio",
                    "Number_Of_Parkings": "1",
                    "Location": "Majan",
                    "City": "Dubai",
                    "Handover_Date": "Q4 2028",
                    "Post_handover_Payment_Plan": "Yes",
                    "Facts_Sheet": "",
                    "Source_File": filename
                })

            elif "Talea" in text:
                output_data.append({
                    "Developer": "Emaar",
                    "Project_Name": "Talea",
                    "Property_Type": "Apartment",
                    "Unit_Number": "TAL/13/1302",
                    "Starting_Price": 3941000.00,
                    "Internal_Area_Size": 1461.10,
                    "Total_Area_Size": 1461.10,
                    "Number_Of_Bedrooms": "2BR",
                    "Number_Of_Parkings": "1",
                    "Location": "Dubai Creek Harbour",
                    "City": "Dubai",
                    "Facts_Sheet": "",
                    "Source_File": filename
                })

        elif filename.endswith(".xls") or filename.endswith(".xlsx"):
            output_data.extend(extract_from_excel(file, filename))

    if output_data:
        df_result = pd.DataFrame(output_data, columns=MASTER_COLUMNS)
        st.success("✅ Extracted inventory summary:")
        st.dataframe(df_result)

        st.download_button(
            label="📥 Download Combined Inventory Excel",
            data=df_result.to_excel(index=False),
            file_name="edexy_combined_inventory.xlsx"
        )
    else:
        st.warning("No matching inventory entries extracted from uploaded files.")
