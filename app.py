import streamlit as st
import asyncio
import os
from dotenv import load_dotenv

from run_synthesis import synthesize, sanitize, MAX_CHARS

# Load environment variables (API Key)
load_dotenv()

st.set_page_config(page_title="Design Research Synthesis", layout="wide")

st.title("🎯 Design Research Synthesis Agent")
st.markdown("Turn messy user-research notes into structured design insight — pain points, themes, and personas — in one run.")

# Check if API key is set
if not os.getenv("GOOGLE_API_KEY"):
    st.error("⚠️ GOOGLE_API_KEY is not set. Please add it to your `.env` file.")
    st.stop()

notes_input = st.text_area(
    "Paste your user interview notes or transcripts here:", 
    height=300,
    placeholder="e.g. User 1 mentioned they struggle with finding the export button..."
)

if st.button("Synthesize Notes", type="primary"):
    if not notes_input.strip():
        st.error("Please paste some notes before synthesizing.")
    else:
        try:
            sanitized_notes = sanitize(notes_input)
            if len(notes_input) > MAX_CHARS:
                st.warning(f"Note: Your input was very long and has been truncated to the first {MAX_CHARS} characters for security/limits.")
            
            with st.spinner("Our AI agents are analyzing your notes. This may take a minute..."):
                # Run the async agent pipeline
                results = asyncio.run(synthesize(sanitized_notes))
                
            st.success("Synthesis complete!")
            
            # Display results in tabs
            tab1, tab2, tab3 = st.tabs(["🔥 Pain Points", "🧩 Themes", "👤 Personas"])
            
            with tab1:
                st.markdown(results.get("pain_points", "No pain points found."))
                
            with tab2:
                st.markdown(results.get("themes", "No themes found."))
                
            with tab3:
                st.markdown(results.get("personas", "No personas found."))
                
        except Exception as e:
            st.error(f"An error occurred during synthesis: {e}")
