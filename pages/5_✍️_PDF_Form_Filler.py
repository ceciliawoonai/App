import streamlit as st
import streamlit.components.v1 as components
import base64
import os

st.set_page_config(page_title="Interactive PDF Writer", page_icon="✍️", layout="wide")

st.title("✍️ Interactive Adobe-Style PDF Writer")
st.write("Upload a PDF, click anywhere directly on the document canvas to write text, and save your modifications.")

uploaded_file = st.file_uploader("Upload your document to begin editing", type=["pdf"])

if uploaded_file is not None:
    # Read the base64 code of the uploaded PDF
    pdf_bytes = uploaded_file.read()
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    
    # Read local JavaScript code files into memory strings
    with open("static/pdf-lib.min.js", "r", encoding="utf-8") as f:
        pdflib_code = f.read()
    with open("static/pdf.min.js", "r", encoding="utf-8") as f:
        pdfjs_code = f.read()
    with open("static/pdf.worker.min.js", "r", encoding="utf-8") as f:
        worker_code = f.read()

    editor_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <!-- Inject code layers natively to bypass CDN iframe sandboxing completely -->
        <script>{pdflib_code}</script>
        <script>{pdfjs_code}</script>
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
            // Setup worker process via inline data blob allocation mapping tricks
            const workerBlob = new Blob([`{worker_code}`], {{ type: 'application/javascript' }});
            const workerUrl = URL.createObjectURL(workerBlob);
            pdfjsLib.GlobalWorkerOptions.workerSrc = workerUrl;

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

            async function savePDF() {{
                const {{ PDFDocument, rgb, StandardFonts }} = PDFLib;
                const existingPdfDoc = await PDFDocument.load(uint8Data);
                const pages = existingPdfDoc.getPages();
                const firstPage = pages[0];
                const {{ width, height }} = firstPage.getSize();
                const helveticaFont = await existingPdfDoc.embedFont(StandardFonts.Helvetica);

                for (let annot of annotations) {{
                    let pdfX = (annot.x / annot.canvasWidth) * width;
                    let pdfY = height - ((annot.y / annot.canvasHeight) * height) - 10; 

                    firstPage.drawText(annot.text, {{
                        x: pdfX,
                        y: pdfY,
                        size: 14,
                        font: helveticaFont,
                        color: rgb(0, 0, 0),
                    }});
                }}

                const pdfBytes = await existingPdfDoc.save();
                
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
    
    components.html(editor_html, height=1000, scrolling=True)
