import streamlit as st
from render import SymbolChain, SymbolGlyph, GlyphComponents
import matplotlib.pyplot as plt
import json
from datetime import datetime
from pathlib import Path


def load_words():
    """Load all saved words from the database"""
    db_path = Path("data/words.json")
    if db_path.exists():
        with open(db_path, "r") as f:
            return json.load(f)
    return {}

def initialize_sentences_db():
    """Initialize the sentences database if it doesn't exist"""
    db_path = Path("data/sentences.json")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not db_path.exists():
        with open(db_path, "w") as f:
            json.dump({}, f)
    
    return db_path

def save_sentence(sentence_data: dict):
    """Save a sentence to the database"""
    db_path = initialize_sentences_db()
    with open(db_path, "r") as f:
        db = json.load(f)
    
    sentence_id = sentence_data["id"]
    db[sentence_id] = sentence_data
    
    with open(db_path, "w") as f:
        json.dump(db, f, indent=2)

def sentence_creator():
    st.title("Sentence Creator")
    
    # Load available words
    words_db = load_words()
    
    # Initialize session state for the current sentence
    if "current_sentence" not in st.session_state:
        st.session_state.current_sentence = []  # List of {type: "word"|"text"|"punct", content: str}
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("Compose Sentence")
        
        # Add symbolic word
        selected_word = st.selectbox(
            "Add Symbol Word",
            options=list(words_db.keys()),
            format_func=lambda x: f"{x} ({words_db[x].get('translation', 'No translation')})"
        )
        
        if st.button("Add Symbol Word"):
            if selected_word:
                st.session_state.current_sentence.append({
                    "type": "word",
                    "content": selected_word
                })
        
        # Add plain text
        plain_text = st.text_input("Add Plain Text")
        if st.button("Add Text") and plain_text:
            st.session_state.current_sentence.append({
                "type": "text",
                "content": plain_text
            })
        
        # Add punctuation
        punct = st.selectbox("Add Punctuation", 
                           options=[",", ".", ":", ";", "!", "?"])
        if st.button("Add Punctuation"):
            st.session_state.current_sentence.append({
                "type": "punct",
                "content": punct
            })
        
        if st.button("Remove Last Item") and st.session_state.current_sentence:
            st.session_state.current_sentence.pop()
        
        if st.button("Clear Sentence"):
            st.session_state.current_sentence = []
    
    with col2:
        st.subheader("Preview")
        # Display current sentence (placeholder for actual rendering)
        preview = " ".join(
            words_db[item["content"]].get("translation", item["content"])
            if item["type"] == "word" else item["content"]
            for item in st.session_state.current_sentence
        )
        st.write(preview)
        
        # Sentence metadata
        st.subheader("Sentence Details")
        sentence_id = st.text_input("Sentence ID (required)",
                                  help="Unique identifier for this sentence")
        translation = st.text_input("Full Translation",
                                  help="Complete English translation")
        notes = st.text_area("Notes",
                           help="Any observations or context about this sentence")
        location = st.text_input("Location Found",
                               help="Where in the game this sentence appears")
        
        if st.button("Save Sentence", disabled=not sentence_id):
            # Prepare sentence data
            sentence_data = {
                "id": sentence_id,
                "components": st.session_state.current_sentence,
                "translation": translation,
                "notes": notes,
                "location_found": location,
                "date_added": datetime.now().isoformat()
            }
            
            # Save to database
            save_sentence(sentence_data)
            st.success(f"Sentence '{sentence_id}' saved successfully!")

if __name__ == "__main__":
    sentence_creator()  # or word_creator() depending on the file