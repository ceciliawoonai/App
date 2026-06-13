import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os

st.set_page_config(page_title="Smart PDF Filler", page_icon="✍️")

st.title("✍️ Smart PDF Filler & Signer")
st.write("Upload any PDF to fill native form fields, or manually stamp custom text onto a flat document.")

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    # Read file data
    reader = PdfReader(uploaded_file)
    num_pages = len(reader.pages)
    
    # Check for interactive fields
    fields = reader.get_fields()
    
    if fields:
        st.success(f"📊 Interactive PDF Form Detected ({len(fields)} fields)")
        field_values = {}
        with st.form("interactive_form"):
            st.subheader("📝 Fill out form fields:")
            for field_name in fields:
                field_values[field_name] = st.text_input(label=f"Field: {field_name}", value="")
            
            submit_interactive = st.form_submit_button("Generate Interactive PDF")
            
        if submit_interactive:
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            writer.update_page_form_field_values(writer.pages, field_values)
            
            output = io.BytesIO()
            writer.write(output)
            st.balloons()
            st.download_button(
                label="📥 Download Filled Form",
                data=output.getvalue(),
                file_name=f"filled_{uploaded_file.name}",
                mime="application/pdf"
            )
            
    else:
        st.info("📄 Flat PDF Layout Detected (No interactive fields found). Switching to manual text-stamping mode.")
        
        # Initialize session state to track multiple custom text stamps
        if "stamps" not in st.session_state:
            st.session_state.stamps = []
            
        # UI controls for creating a text stamp
        st.subheader("🛠️ Create Text Overlay Stamp")
        col1, col2 = st.columns(2)
        with col1:
            stamp_text = st.text_input("Text to add", placeholder="Type your text, name, or date here...")
            target_page = st.number_input("Target Page Number", min_value=1, max_value=num_pages, value=1)
            font_size = st.slider("Font Size", min_value=6, max_value=36, value=12)
        with col2:
            # Standard PDF coordinate points (Approx A4/Letter bounds)
            x_pos = st.slider("Horizontal Position (Left to Right)", min_value=10, max_value=600, value=100, step=5)
            y_pos = st.slider("Vertical Position (Bottom to Top)", min_value=10, max_value=800, value=700, step=5)
            
        if st.button("➕ Add Text Stamp to Document"):
            if stamp_text:
                st.session_state.stamps.append({
                    "text": stamp_text,
                    "page": target_page - 1, # 0-indexed for code
                    "x": x_pos,
                    "y": y_pos,
                    "size": font_size
                })
                st.toast("Stamp added successfully!")
            else:
                st.warning("Please type some text before adding.")
                
        # Display current stamps list
        if st.session_state.stamps:
            st.subheader("📋 Active Stamps Layer Summary")
            for i, s in enumerate(st.session_state.stamps):
                st.text(f"[{i+1}] Page {s['page']+1}: '{s['text']}' at position ({s['x']}, {s['y']})")
                
            if st.button("🗑️ Clear All Stamps"):
                st.session_state.stamps = []
                st.rerun()
                
            # Process & Merge the layout overlays
            if st.button("🚀 Burn Stamps onto PDF Document"):
                writer = PdfWriter()
                
                # Loop through each page of original document
                for idx in range(num_pages):
                    orig_page = reader.pages[idx]
                    
                    # Filter stamps belonging to this specific page index loop
                    page_stamps = [s for s in st.session_state.stamps if s["page"] == idx]
                    
                    if page_stamps:
                        # Draw a transparent reportlab overlay layer
                        packet = io.BytesIO()
                        can = canvas.Canvas(packet, pagesize=letter)
                        
                        for stamp in page_stamps:
                            can.setFont("Helvetica", stamp["size"])
                            can.drawString(stamp["x"], stamp["y"], stamp["text"])
                        can.save()
                        
                        packet.seek(0)
                        overlay_reader = PdfReader(packet)
                        overlay_page = overlay_reader.pages[0]
                        
                        # Merge text overlay vector graphics directly over original page
                        orig_page.merge_page(overlay_page)
                        
                    writer.add_page(orig_page)
                    
                output = io.BytesIO()
                writer.write(output)
                
                st.success("Successfully burned text elements directly into document layer architecture!")
                st.download_button(
                    label="📥 Download Final Stamped PDF",
                    data=output.getvalue(),
                    file_name=f"stamped_{uploaded_file.name}",
                    mime="application/pdf"
                )
