import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Excel to PDF Converter", page_icon="📊")

st.title("📊 Excel to PDF HTML Viewer")
st.write("Upload an Excel file (.xlsx) to cleanly render its grid layout.")

uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Read Excel sheets smoothly without heavy background engines
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_names = excel_file.sheet_names
        
        selected_sheet = st.selectbox("Select sheet to view", sheet_names)
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
        
        st.subheader(f"📋 Data View: {selected_sheet}")
        st.dataframe(df, use_container_width=True)
        
        # Convert grid structure to a clean downloadable format safely
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Clean Data Layer",
            data=csv,
            file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Error rendering data view: {e}")
