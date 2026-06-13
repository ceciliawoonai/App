import streamlit as st
import pandas as pd
import pdfplumber
import io

st.set_page_config(page_title="PDF to Excel Converter", page_icon="📈")

st.title("📈 PDF to Excel Converter")
st.write("Upload a PDF document containing tables, and this app will extract them into an Excel spreadsheet.")

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    st.info("Reading PDF and extracting data tables... Please wait.")
    
    try:
        # Open the PDF directly from memory
        with pdfplumber.open(uploaded_file) as pdf:
            all_tables = []
            
            # Extract tables from each page
            for page_num, page in enumerate(pdf.pages, start=1):
                extracted_tables = page.extract_tables()
                
                for table_num, table in enumerate(extracted_tables, start=1):
                    if table: # If a table structure was found
                        # Convert raw table rows into a pandas Dataframe
                        df = pd.DataFrame(table)
                        
                        # Clean up: Use first row as header if it looks valid
                        if not df.empty:
                            df.columns = df.iloc[0]
                            df = df[1:].reset_index(drop=True)
                        
                        all_tables.append((f"Page{page_num}_Table{table_num}", df))
        
        if all_tables:
            st.success(f"Success! Found {len(all_tables)} table(s) inside your PDF.")
            
            # Create an in-memory Excel workbook
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                for sheet_name, df in all_tables:
                    # Excel sheet names can only be 31 characters long max
                    clean_sheet_name = sheet_name[:30]
                    df.to_excel(writer, sheet_name=clean_sheet_name, index=False)
            
            processed_data = output.getvalue()
            
            # Provide download button
            st.download_button(
                label="📥 Download Extracted Excel File",
                data=processed_data,
                file_name=uploaded_file.name.rsplit('.', 1)[0] + "_extracted.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("No structured data tables could be identified in this PDF. Ensure it contains actual text grids and is not a raw scanned image.")
            
    except Exception as e:
        st.error(f"An error occurred during extraction: {e}")
