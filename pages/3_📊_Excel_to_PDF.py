import streamlit as st
import os
import subprocess

st.set_page_config(page_title="Excel to PDF Converter", page_icon="📊")

st.title("📊 Excel to PDF Converter")
st.write("Upload any Microsoft Excel file (.xlsx or .xls) to convert it cleanly into a PDF document.")

uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Save the uploaded file locally in the container workspace
    input_filename = "temp_input_sheet.xlsx"
    with open(input_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.info("Converting document layout... Please wait.")
    
    try:
        # Run the serverless background layout renderer command
        # This converts the sheet into a PDF named "temp_input_sheet.pdf"
        command = [
            "libreoffice",
            "--headless",
            "--convert-to", "pdf",
            input_filename
        ]
        
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        output_filename = "temp_input_sheet.pdf"
        
        # Verify the file was generated safely
        if os.path.exists(output_filename):
            final_size_mb = os.path.getsize(output_filename) / (1024 * 1024)
            st.success(f"Success! Generated PDF Document ({final_size_mb:.2f} MB)")
            
            # Read file bytes for download mechanism
            with open(output_filename, "rb") as file:
                st.download_button(
                    label="Download Converted PDF",
                    data=file,
                    file_name=uploaded_file.name.rsplit('.', 1)[0] + ".pdf",
                    mime="application/pdf"
                )
                
            # Clean up the output file
            os.remove(output_filename)
        else:
            st.error("Conversion completed but output PDF file was not generated.")
            
    except Exception as e:
        st.error(f"An error occurred during layout conversion: {e}")
        
    finally:
        # Clean up the input file
        if os.path.exists(input_filename):
            os.remove(input_filename)
