import html
import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------
# Project path
# ---------------------------------------------------------
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

import streamlit as st
import streamlit.components.v1 as components


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Grammar & Writing Improver",
    page_icon="✍️",
    layout="wide"
)


# ---------------------------------------------------------
# Load Groq API Key
# ---------------------------------------------------------
def load_groq_api_key():

    # 1. Streamlit Cloud Secrets
    try:
        if "GROQ_API_KEY" in st.secrets:

            api_key = st.secrets["GROQ_API_KEY"]

            if api_key:
                return str(api_key).strip()

    except Exception:
        pass

    # 2. Local .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

    # 3. Environment variable
    api_key = os.getenv("GROQ_API_KEY")

    if api_key:
        return str(api_key).strip()

    return None


GROQ_API_KEY = load_groq_api_key()


# ---------------------------------------------------------
# Improve Writing
# ---------------------------------------------------------
def improve_writing(text, tone, level):

    api_key = load_groq_api_key()

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. "
            "Please add GROQ_API_KEY in Streamlit Cloud Secrets."
        )

    from groq import Groq

    client = Groq(api_key=api_key)

    prompt = f"""
You are an expert English writing assistant.

The user wants:

Tone: {tone}
Language Level: {level}

Analyze the following text and return your response in exactly this format:

## Corrected Text

Write the grammatically corrected version of the user's text.

## Grammar Mistakes

- Mistake → Correction : Simple explanation

## Improved Version

Write a clearer and better version of the text.

## Writing Tips

- Tip 1
- Tip 2
- Tip 3

User Text:
{text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4
    )

    return response.choices[0].message.content


# ---------------------------------------------------------
# Parse response sections
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# Application UI
# ---------------------------------------------------------
st.title("✍️ AI Grammar & Writing Improver")

st.write(
    "Improve grammar, clarity, writing style, and tone using AI."
)


# ---------------------------------------------------------
# API Key status
# ---------------------------------------------------------
if not GROQ_API_KEY:

    st.error(
        "Missing GROQ_API_KEY. "
        "Please add it in Streamlit Cloud → "
        "Manage app → Settings → Secrets."
    )


# ---------------------------------------------------------
# User input
# ---------------------------------------------------------
text = st.text_area(
    "Enter your paragraph or essay",
    height=220,
    placeholder="Enter your paragraph or essay here..."
)


# ---------------------------------------------------------
# Tone
# ---------------------------------------------------------
tone = st.selectbox(
    "Choose Tone",
    [
        "Professional",
        "Friendly",
        "Formal",
        "Casual"
    ]
)


# ---------------------------------------------------------
# Language level
# ---------------------------------------------------------
level = st.selectbox(
    "Choose Language Level",
    [
        "Simple",
        "Intermediate",
        "Advanced"
    ]
)


# ---------------------------------------------------------
# Improve button
# ---------------------------------------------------------
if st.button("✨ Improve Writing"):

    if not text.strip():

        st.warning(
            "Please enter some text."
        )

    elif not GROQ_API_KEY:

        st.error(
            "GROQ_API_KEY is missing. "
            "Please add it in Streamlit Cloud Secrets "
            "and reboot the app."
        )

    else:

        with st.spinner(
            "Improving your writing..."
        ):

            try:

                result = improve_writing(
                    text,
                    tone,
                    level
                )

                sections = parse_response_sections(
                    result
                )

                # -------------------------------------------------
                # Corrected Text
                # -------------------------------------------------
                corrected_text = sections.get(
                    "Corrected Text"
                )

                if corrected_text:

                    st.markdown(
                        "### Corrected Text"
                    )

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
                    }}

                    .copy-button:hover {{
                        background: #f3f4f6;
                    }}

                    .copy-content {{
                        margin: 0;
                        white-space: pre-wrap;
                        word-break: break-word;
                        font-family:
                            ui-monospace,
                            SFMono-Regular,
                            Menlo,
                            Monaco,
                            Consolas,
                            "Liberation Mono",
                            "Courier New",
                            monospace;
                        font-size: 14px;
                        line-height: 1.6;
                        padding-right: 48px;
                    }}

                    </style>

                    <div class="copy-block">

                        <button
                            class="copy-button"
                            id="copy-btn"
                            title="Copy corrected text"
                        >
                            📋
                        </button>

                        <pre class="copy-content">{html.escape(corrected_text)}</pre>

                    </div>

                    <script>

                    const correctedText =
                        {json.dumps(corrected_text)};

                    const btn =
                        document.getElementById("copy-btn");

                    if (btn) {{

                        btn.addEventListener(
                            "click",
                            () => {{

                                navigator.clipboard
                                    .writeText(correctedText)
                                    .then(() => {{

                                        btn.textContent = "✅";

                                        setTimeout(
                                            () => {{
                                                btn.textContent = "📋";
                                            }},
                                            1500
                                        );

                                    }})
                                    .catch(() => {{

                                        btn.textContent = "❌";

                                        setTimeout(
                                            () => {{
                                                btn.textContent = "📋";
                                            }},
                                            1500
                                        );

                                    }});

                            }}
                        );

                    }}

                    </script>
                    """

                    components.html(
                        copy_html,
                        height=260
                    )


                # -------------------------------------------------
                # Grammar Mistakes
                # -------------------------------------------------
                grammar_mistakes = sections.get(
                    "Grammar Mistakes"
                )

                if grammar_mistakes:

                    st.markdown(
                        "### Grammar Mistakes"
                    )

                    st.markdown(
                        grammar_mistakes
                    )


                # -------------------------------------------------
                # Improved Version
                # -------------------------------------------------
                improved_version = sections.get(
                    "Improved Version"
                )

                if improved_version:

                    st.markdown(
                        "### Improved Version"
                    )

                    st.markdown(
                        improved_version
                    )


                # -------------------------------------------------
                # Writing Tips
                # -------------------------------------------------
                writing_tips = sections.get(
                    "Writing Tips"
                )

                if writing_tips:

                    st.markdown(
                        "### Writing Tips"
                    )

                    st.markdown(
                        writing_tips
                    )


                # -------------------------------------------------
                # Fallback
                # -------------------------------------------------
                if not sections:

                    st.markdown(result)


            except Exception as exc:

                st.error(
                    f"Something went wrong: {exc}"
                )