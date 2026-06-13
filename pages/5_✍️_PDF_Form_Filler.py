import streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(page_title="Interactive PDF Writer", page_icon="✍️", layout="wide")

st.title("✍️ Interactive Adobe-Style PDF Writer")
st.write("Upload a PDF, click anywhere directly on the document canvas to write text, and save your modifications.")

# Initialize file upload interface
uploaded_file = st.file_uploader("Upload your document to begin editing", type=["pdf"])

if uploaded_file is not None:
    # Encode the PDF data to Base64 so the browser engine can inject it safely
    pdf_bytes = uploaded_file.read()
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    
    # Complete Embedded Frontend Editor Workspace (HTML5 + PDF-Lib + Canvas Engine)
    editor_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com"></script>
        <script src="https://cloudflare.com"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 10px; background: #f0f2f6; }}
            #toolbar {{ background: #ffffff; padding: 10px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; gap: 15px; align-items: center; }}
            .btn {{ background: #ff4b4b; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer; font-weight: bold; }}
            .btn:hover {{ background: #e03e3e; }}
            #canvas-container {{ position: relative; display: inline-block; background: #ffffff; border: 1px solid #ccc; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
            #pdf-canvas {{ display: block; z-index: 1; }}
            .text-annotation {{ position: absolute; border: 1px dashed #ff4b4b; background: transparent; font-family: Helvetica; font-size: 14px; padding: 2px; outline: none; z-index: 10; min-width: 50px; color: black; }}
            .hint {{ color: #555; font-size: 14px; }}
        </style>
    </head>
    <body>

        <div id="toolbar">
            <button class="btn" onclick="savePDF()">💾 Export & Download PDF</button>
            <span class="hint">💡 <b>How to Edit:</b> Click anywhere directly on the page layout below to start typing text!</span>
        </div>

        <div id="canvas-container">
            <canvas id="pdf-canvas"></canvas>
        </div>

        <script>
            const pdfData = atob("{base64_pdf}");
            const uint8Data = new Uint8Array(pdfData.length);
            for (let i = 0; i < pdfData.length; i++) {{
                uint8Data[i] = pdfData.charCodeAt(i);
            }}

            let pdfDoc = null;
            let pageNum = 1;
            let canvas = document.getElementById('pdf-canvas');
            let ctx = canvas.getContext('2d');
            let viewportScale = 1.3; 
            let annotations = [];

            // Initialize rendering viewport via PDF.js core library links
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cloudflare.com';
            
            pdfjsLib.getDocument({{data: uint8Data}}).promise.then(pdf => {{
                pdfDoc = pdf;
                renderPage(pageNum);
            }});

            function renderPage(num) {{
                pdfDoc.getPage(num).then(page => {{
                    let viewport = page.getViewport({{scale: viewportScale}});
                    canvas.height = viewport.height;
                    canvas.width = viewport.width;

                    let renderContext = {{
                        canvasContext: ctx,
                        viewport: viewport
                    }};
                    page.render(renderContext);
                }});
            }}

            // Event handler to capture click coordinates on document canvas layout
            document.getElementById('canvas-container').addEventListener('click', function(e) {{
                if (e.target.id !== 'pdf-canvas') return;

                let rect = canvas.getBoundingClientRect();
                let x = e.clientX - rect.left;
                let y = e.clientY - rect.top;

                createTextField(x, y);
            }});

            function createTextField(x, y) {{
                let container = document.getElementById('canvas-container');
                let input = document.createElement('div');
                input.className = 'text-annotation';
                input.contentEditable = true;
                input.style.left = x + 'px';
                input.style.top = y + 'px';
                
                container.appendChild(input);
                input.focus();

                // Save coordinate configurations on loss of focus
                input.addEventListener('blur', function() {{
                    if (input.innerText.trim() !== '') {{
                        annotations.push({{
                            text: input.innerText,
                            x: x,
                            y: y,
                            canvasHeight: canvas.height,
                            canvasWidth: canvas.width
                        }});
                    }} else {{
                        input.remove();
                    }}
                }});
            }}

            // Merge dynamic coordinate text collections onto structural PDF bytes via PDF-Lib
            async function savePDF() {{
                const {{ PDFDocument, rgb, StandardFonts }} = PDFLib;
                const existingPdfDoc = await PDFDocument.load(uint8Data);
                const pages = existingPdfDoc.getPages();
                const firstPage = pages[0];
                const {{ width, height }} = firstPage.getSize();
                const helveticaFont = await existingPdfDoc.embedFont(StandardFonts.Helvetica);

                for (let annot of annotations) {{
                    // Scale local canvas click vectors into core PDF layout points
                    let pdfX = (annot.x / annot.canvasWidth) * width;
                    let pdfY = height - ((annot.y / annot.canvasHeight) * height) - 10; 

                    firstPage.drawText(annot.text, {{
                        x: pdfX,
                        y: pdfY,
                        size: 14,
                        font: helveticaFont,
                        color: rgb(0, 0, 0),
                    }});
                }

                const pdfBytes = await existingPdfDoc.save();
                
                // Trigger download mechanism directly inside the sandboxed iframe interface
                let blob = new Blob([pdfBytes], {{ type: "application/pdf" }});
                let link = document.createElement('a');
                link.href = window.URL.createObjectURL(blob);
                link.download = "edited_document.pdf";
                link.click();
            }}
        </script>
    </body>
    </html>
    """
    
    # Render the dynamic interactive editor component using explicit pixel frames
    components.html(editor_html, height=900, scrolling=True)
