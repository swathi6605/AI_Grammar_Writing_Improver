import html
import json
import os
import streamlit as st
import streamlit.components.v1 as components
from groq_helper import improve_writing


def parse_response_sections(response_text):
    sections = {}
    current_section = None
    lines = []

    for line in response_text.splitlines():
        if line.startswith("## "):
            if current_section is not None:
                sections[current_section] = "\n".join(lines).strip()
            current_section = line[3:].strip()
            lines = []
        elif current_section is not None:
            lines.append(line)

    if current_section is not None:
        sections[current_section] = "\n".join(lines).strip()

    return sections


st.set_page_config(
    page_title="AI Grammar & Writing Improver",
    page_icon="✍️",
    layout="wide"
)

st.title("✍️ AI Grammar & Writing Improver")

st.write(
    "Improve grammar, clarity, writing style, and tone using AI."
)

if os.getenv("GROQ_API_KEY") is None:
    st.error(
        "Missing GROQ_API_KEY environment variable. Create a `.env` file or set GROQ_API_KEY before clicking Improve Writing."
    )

text = st.text_area(
    "Enter your paragraph or essay",
    height=220
)

tone = st.selectbox(
    "Choose Tone",
    ["Professional", "Friendly", "Formal", "Casual"]
)

level = st.selectbox(
    "Choose Language Level",
    ["Simple", "Intermediate", "Advanced"]
)

if st.button("✨ Improve Writing"):

    if text.strip() == "":
        st.warning("Please enter some text.")
    else:

        with st.spinner("Improving your writing..."):
            try:
                result = improve_writing(
                    text,
                    tone,
                    level
                )
                sections = parse_response_sections(result)
                corrected_text = sections.get("Corrected Text")

                if corrected_text:
                    st.markdown("### Corrected Text")

                    copy_html = f"""
                    <style>
                    .copy-block {{
                        position: relative;
                        background: #f8fafc;
                        border: 1px solid #e2e8f0;
                        border-radius: 16px;
                        padding: 18px;
                        color: #111827;
                    }}
                    .copy-button {{
                        position: absolute;
                        top: 16px;
                        right: 16px;
                        width: 36px;
                        height: 36px;
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        border: 1px solid #d1d5db;
                        border-radius: 12px;
                        background: #ffffff;
                        color: #111827;
                        cursor: pointer;
                        font-size: 16px;
                        transition: background 0.2s ease, transform 0.2s ease;
                    }}
                    .copy-button:hover {{
                        background: #f3f4f6;
                        transform: translateY(-1px);
                    }}
                    .copy-content {{
                        margin: 0;
                        white-space: pre-wrap;
                        word-break: break-word;
                        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
                        font-size: 14px;
                        line-height: 1.6;
                        padding-right: 48px;
                    }}
                    </style>
                    <div class="copy-block">
                        <button class="copy-button" id="copy-btn" title="Copy corrected text">📋</button>
                        <pre class="copy-content">{html.escape(corrected_text)}</pre>
                    </div>
                    <script>
                    const correctedText = {json.dumps(corrected_text)};
                    const btn = document.getElementById('copy-btn');
                    if (btn) {{
                        btn.addEventListener('click', () => {{
                            navigator.clipboard.writeText(correctedText)
                                .then(() => {{
                                    btn.textContent = '✅';
                                    setTimeout(() => {{ btn.textContent = '📋'; }}, 1500);
                                }})
                                .catch(() => {{
                                    btn.textContent = '❌';
                                    setTimeout(() => {{ btn.textContent = '📋'; }}, 1500);
                                }});
                        }});
                    }}
                    </script>
                    """

                    components.html(copy_html, height=260)

                for section_name in ["Grammar Mistakes", "Improved Version", "Writing Tips"]:
                    section_value = sections.get(section_name)
                    if section_value:
                        st.markdown(f"### {section_name}")
                        st.markdown(section_value)

                if not sections:
                    st.markdown(result)
            except Exception as exc:
                st.error(str(exc))
