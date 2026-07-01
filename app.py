import streamlit as st
import asyncio
import os
from dotenv import load_dotenv

from run_synthesis import synthesize, sanitize, MAX_CHARS
from ask_memory import ask
from research_memory.memory import add_study, get_collection

# Load environment variables (API Key)
load_dotenv()

st.set_page_config(page_title="Design Research Synthesis", layout="wide")

st.title("🎯 Design Research Hub")
st.markdown("Automate your user research synthesis and query past studies using AI.")

# Check if API key is set
if not os.getenv("GOOGLE_API_KEY"):
    st.error("⚠️ GOOGLE_API_KEY is not set. Please add it to your `.env` file.")
    st.stop()

# Create main tabs
tab_synthesis, tab_memory = st.tabs(["🚀 New Synthesis", "🧠 Research Memory (RAG)"])

# ==========================================
# TAB 1: NEW SYNTHESIS
# ==========================================
with tab_synthesis:
    st.header("Synthesize New Notes")
    st.write("Extract pain points, themes, and personas from a single set of research notes.")
    
    # Input options: File Upload OR Text Area
    upload_file = st.file_uploader("Upload interview notes (.txt)", type=["txt"], key="synthesis_upload")
    notes_input = st.text_area(
        "Or paste your user interview notes/transcripts here:", 
        height=200,
        placeholder="e.g. User 1 mentioned they struggle with finding the export button..."
    )

    if st.button("Synthesize Notes", type="primary", key="btn_synth"):
        # Combine uploaded text and pasted text
        final_text = ""
        if upload_file is not None:
            final_text += upload_file.getvalue().decode("utf-8") + "\n\n"
        if notes_input.strip():
            final_text += notes_input.strip()

        if not final_text.strip():
            st.error("Please paste some notes or upload a file before synthesizing.")
        else:
            try:
                sanitized_notes = sanitize(final_text)
                if len(final_text) > MAX_CHARS:
                    st.warning(f"Note: Your input was very long and has been truncated to the first {MAX_CHARS} characters for security/limits.")
                
                with st.spinner("Our AI agents are analyzing your notes. This may take a minute..."):
                    results = asyncio.run(synthesize(sanitized_notes))
                    
                st.success("Synthesis complete!")
                
                # Display results in columns
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.subheader("🔥 Pain Points")
                    st.markdown(results.get("pain_points", "No pain points found."))
                with col2:
                    st.subheader("🧩 Themes")
                    st.markdown(results.get("themes", "No themes found."))
                with col3:
                    st.subheader("👤 Personas")
                    st.markdown(results.get("personas", "No personas found."))
                    
            except Exception as e:
                st.error(f"An error occurred during synthesis: {e}")

# ==========================================
# TAB 2: RESEARCH MEMORY (RAG)
# ==========================================
with tab_memory:
    st.header("Query Past Research")
    st.write("Search across all your historical user studies using semantic meaning.")
    
    col_ask, col_ingest = st.columns([2, 1], gap="large")
    
    with col_ask:
        st.subheader("Ask a Question")
        question = st.text_input("e.g. 'What have users said about confusing instructions?'")
        
        if st.button("Search Memory", type="primary", key="btn_ask"):
            if not question.strip():
                st.error("Please enter a question.")
            else:
                try:
                    # Check if DB has anything
                    collection = get_collection()
                    if collection.count() == 0:
                        st.warning("Research memory is empty. Please upload some past studies first!")
                    else:
                        with st.spinner("Searching past research and synthesizing answer..."):
                            answer = asyncio.run(ask(question))
                        
                        st.info(f"**Question:** {question}")
                        st.markdown(answer)
                except Exception as e:
                    st.error(f"Error querying memory: {e}")
                    
    with col_ingest:
        st.subheader("Add to Memory")
        st.write("Upload past studies to make them searchable.")
        
        memory_files = st.file_uploader("Upload past studies (.txt)", type=["txt"], accept_multiple_files=True, key="memory_upload")
        
        if st.button("Add to Database", key="btn_ingest"):
            if not memory_files:
                st.error("Please select files to upload.")
            else:
                try:
                    total_chunks = 0
                    with st.spinner("Chunking and vectorizing documents..."):
                        for file in memory_files:
                            text = file.getvalue().decode("utf-8")
                            study_name = file.name.replace(".txt", "")
                            chunks_added = add_study(study_name=study_name, text=text)
                            total_chunks += chunks_added
                    
                    st.success(f"Added {len(memory_files)} studies ({total_chunks} text chunks) to Research Memory!")
                    
                    try:
                        count = get_collection().count()
                        st.metric("Total Documents in Memory", count)
                    except Exception:
                        pass
                except Exception as e:
                    st.error(f"Error adding to memory: {e}")
