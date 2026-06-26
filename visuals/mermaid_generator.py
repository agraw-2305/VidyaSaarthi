"""
mermaid_generator.py
Generates process flows and classification trees using Mermaid.js.
"""

import re
import json
import logging

logger = logging.getLogger(__name__)

def generate_mermaid_visual(visual_data: dict) -> str | None:
    """
    Takes structured visual data containing mermaid syntax and returns
    an HTML string that renders it via Mermaid.js CDN.
    """
    mermaid_code = visual_data.get("mermaid_code")
    if not mermaid_code:
        return None
        
    # Clean up code and sanitize
    mermaid_code = mermaid_code.strip()
    
    # Remove code fences
    mermaid_code = re.sub(r'^```[a-zA-Z]*\n?', '', mermaid_code)
    mermaid_code = re.sub(r'\n?```$', '', mermaid_code)
    mermaid_code = mermaid_code.replace('```mermaid', '').replace('```', '')
    
    # Remove HTML tags
    mermaid_code = re.sub(r'<[^>]+>', '', mermaid_code)
    
    # Fix arrow syntax errors and remove hallucinated > after labels
    mermaid_code = re.sub(r'-->\s*\|\s*(.*?)\s*\|\s*>?\s*', r'-->|\1|', mermaid_code)
    
    mermaid_code = mermaid_code.strip()
    
    logger.info("GENERATED MERMAID CODE:\n%s", mermaid_code)
    print("---MERMAID CODE START---")
    print(mermaid_code)
    print("---MERMAID CODE END---")

    js_code_json = json.dumps(mermaid_code)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: #ffffff;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100%;
                margin: 0;
                padding: 20px;
            }}
            .mermaid {{
                max-width: 100%;
            }}
        </style>
    </head>
    <body>
        <div id="mermaid-chart" class="mermaid"></div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            
            mermaid.initialize({{ 
                startOnLoad: false, 
                theme: 'default',
                securityLevel: 'loose'
            }});
            
            const code = {js_code_json};
            const container = document.getElementById("mermaid-chart");
            
            try {{
                const {{ svg }} = await mermaid.render('mermaid-svg', code);
                container.innerHTML = svg;
            }} catch (error) {{
                container.innerHTML = `<div style="color: red; background: #fee; padding: 10px; border: 1px solid #fcc; border-radius: 5px; width: 100%;">
                    <strong>Mermaid Syntax Error:</strong><br>
                    <pre style="white-space: pre-wrap; font-size: 12px;">${{error.message || error}}</pre>
                    <hr>
                    <strong>Raw Code:</strong><br>
                    <pre style="white-space: pre-wrap; font-size: 12px;">${{code}}</pre>
                </div>`;
            }}
        </script>
    </body>
    </html>
    """
    return html_content
