import streamlit as st
from pypdf import PdfReader, PdfWriter
import io

st.set_page_config(page_title="PDF Form Filler", page_icon="✍️")

st.title("✍️ PDF Form Filler")
st.write("Upload a PDF document to type text directly into its native form fields.")

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    st.info("Reading PDF structural fields... Please wait.")
    
    try:
        # Load the PDF file into a reader object
        reader = PdfReader(uploaded_file)
        writer = PdfWriter()
        
        # Look for interactive fillable fields inside the PDF layout metadata
        fields = reader.get_fields()
        
        if fields:
            st.success(f"Success! Detected {len(fields)} interactive form fields.")
            
            # Dynamically generate text boxes for each form field found
            field_values = {}
            with st.form("form_filler_panel"):
                st.subheader("📝 Fill out the fields:")
                for field_name in fields:
                    # Provide an input block for every individual text anchor field
                    field_values[field_name] = st.text_input(label=f"Field: {field_name}", value="")
                
                submit_button = st.form_submit_button("Generate Completed PDF")
            
            if submit_button:
                # Add all pages to the writer instance
                for page in reader.pages:
                    writer.add_page(page)
                
                # Apply the dictionary containing custom typed user data to the fields
                writer.update_page_form_field_values(writer.pages[0], field_values)
                
                # Output compiled data stream directly to memory buffer blocks
                output_stream = io.BytesIO()
                writer.write(output_stream)
                filled_pdf_data = output_stream.getvalue()
                
                st.balloons()
                st.download_button(
                    label="📥 Download Filled PDF Document",
                    data=filled_pdf_data,
                    file_name=uploaded_file.name.rsplit('.', 1)[0] + "_filled.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("This PDF does not contain interactive, pre-formatted fillable text boxes. It appears to be a flat document layout.")
            
    except Exception as e:
        st.error(f"An error occurred while attempting to parse form inputs: {e}")
