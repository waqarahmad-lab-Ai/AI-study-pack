import os
import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="AI Study Pack Generator",
    page_icon="📚",
    layout="wide",
)

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")


def get_api_key():
    """Read the API key from Streamlit secrets or environment variables."""
    try:
        secret_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        secret_key = None

    return secret_key or os.getenv("OPENAI_API_KEY")


def build_prompt(
    topic,
    level,
    language,
    pack_type,
    source_material,
    flashcard_count,
    mcq_count,
    study_hours,
):
    source_section = (
        f"""
SOURCE MATERIAL:
{source_material}

Use the source material as the primary reference. Do not pretend that
information missing from the source was present in it. If you add useful
background knowledge, label it clearly as "Background".
"""
        if source_material.strip()
        else
        """
SOURCE MATERIAL:
None provided. Use reliable general knowledge appropriate to the topic.
"""
    )

    return f"""
You are an expert AI study assistant and instructional designer.

Create a complete study pack for:

Topic: {topic}
Student level: {level}
Language: {language}
Pack type: {pack_type}
Available study time: {study_hours} hours

{source_section}

Requirements:
1. Start with a clear title.
2. Give 4-8 learning objectives.
3. Give a concise "Quick Summary".
4. Explain the core concepts from beginner to the selected level.
5. Define important terms in simple language.
6. Include practical examples or worked examples where useful.
7. Include a "Common Mistakes" section.
8. Create exactly {flashcard_count} flashcards using this format:
   Q: ...
   A: ...
9. Create exactly {mcq_count} multiple-choice questions.
   Each MCQ must have A, B, C, D options.
   Put the answer key at the end with a one-sentence explanation for each answer.
10. Create a study plan matched to {study_hours} hours.
11. End with a "Last-Minute Revision Sheet" containing the most important points.
12. Use Markdown headings and readable spacing.
13. Keep the language educational, direct, and suitable for a student.
14. Do not claim that a fact came from the source material unless it actually did.

Return only the study pack in Markdown.
"""


def generate_study_pack(prompt, model):
    client = OpenAI(api_key=get_api_key())

    response = client.responses.create(
        model=model,
        instructions=(
            "You create accurate, structured educational study materials. "
            "Follow the requested counts exactly and return clean Markdown."
        ),
        input=prompt,
    )

    return response.output_text


# ---------- UI ----------
st.title("📚 AI Study Pack Generator")
st.caption(
    "Generate notes, explanations, flashcards, MCQs, examples, and a study plan "
    "from a topic or your own study material."
)

with st.sidebar:
    st.header("⚙️ Settings")

    model = st.text_input(
        "OpenAI model",
        value=DEFAULT_MODEL,
        help="Use a model available to your OpenAI API account.",
    )

    level = st.selectbox(
        "Student level",
        ["Beginner", "Intermediate", "Advanced", "Exam-focused"],
    )

    language = st.selectbox(
        "Language",
        ["English", "Urdu", "Roman Urdu", "Simple English"],
    )

    pack_type = st.selectbox(
        "Pack type",
        [
            "Full study pack",
            "Exam revision pack",
            "Concept learning pack",
            "Interview preparation pack",
        ],
    )

    flashcard_count = st.slider("Flashcards", 5, 30, 10)
    mcq_count = st.slider("MCQs", 5, 30, 10)
    study_hours = st.slider("Study time (hours)", 1, 20, 3)

    st.divider()
    st.info(
        "Keep your API key in Streamlit secrets for deployment. "
        "Do not hard-code it in app.py."
    )

topic = st.text_input(
    "What do you want to study?",
    placeholder="Example: Python dictionaries, Linear Regression, Computer Networks",
)

source_material = st.text_area(
    "Paste your notes / lecture text (optional)",
    height=220,
    placeholder="Paste class notes, lecture content, textbook text, or your own notes here...",
)

generate = st.button("🚀 Generate Study Pack", type="primary", use_container_width=True)

if generate:
    if not topic.strip():
        st.error("Please enter a topic.")
        st.stop()

    api_key = get_api_key()
    if not api_key:
        st.error(
            "OpenAI API key not found. Add OPENAI_API_KEY to Streamlit secrets "
            "or set it as an environment variable."
        )
        st.stop()

    prompt = build_prompt(
        topic=topic.strip(),
        level=level,
        language=language,
        pack_type=pack_type,
        source_material=source_material,
        flashcard_count=flashcard_count,
        mcq_count=mcq_count,
        study_hours=study_hours,
    )

    with st.spinner("🧠 Building your study pack..."):
        try:
            st.session_state["study_pack"] = generate_study_pack(prompt, model)
            st.session_state["study_topic"] = topic.strip()
        except Exception as exc:
            st.error(f"Generation failed: {exc}")
            st.stop()

if "study_pack" in st.session_state:
    st.divider()
    st.subheader(f"📖 Study Pack — {st.session_state['study_topic']}")

    study_pack = st.session_state["study_pack"]
    st.markdown(study_pack)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "⬇️ Download Markdown",
            data=study_pack,
            file_name="study_pack.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with col2:
        st.download_button(
            "⬇️ Download TXT",
            data=study_pack,
            file_name="study_pack.txt",
            mime="text/plain",
            use_container_width=True,
        )
else:
    st.info(
        "Enter a topic, optionally paste your notes, choose the difficulty and "
        "question counts, then click Generate Study Pack."
    )
