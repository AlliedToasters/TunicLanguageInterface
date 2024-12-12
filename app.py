# app.py
import streamlit as st

st.set_page_config(
    page_title="Symbol Decoder",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main():
    st.title("Symbol Decoder")
    st.write("""
    Welcome to the Symbol Decoder application. Use this tool to:
    
    - Create and catalog individual symbol glyphs
    - Compose words from saved symbols
    - Build complete sentences mixing symbols and text
    
    Navigate using the sidebar to access different tools.
    """)
    
    # Display some basic stats if databases exist
    try:
        from pathlib import Path
        import json
        
        stats = []
        
        # Check letters
        letters_path = Path("data/letters.json")
        if letters_path.exists():
            with open(letters_path) as f:
                letters = json.load(f)
                stats.append(f"📝 Letters cataloged: {len(letters)}")
        
        # Check words
        words_path = Path("data/words.json")
        if words_path.exists():
            with open(words_path) as f:
                words = json.load(f)
                stats.append(f"📚 Words composed: {len(words)}")
        
        # Check sentences
        sentences_path = Path("data/sentences.json")
        if sentences_path.exists():
            with open(sentences_path) as f:
                sentences = json.load(f)
                stats.append(f"📜 Sentences recorded: {len(sentences)}")
        
        if stats:
            st.subheader("Current Progress")
            for stat in stats:
                st.write(stat)
                
    except Exception as e:
        st.error("Error loading statistics")

if __name__ == "__main__":
    main()