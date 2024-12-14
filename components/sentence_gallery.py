# components/sentence_gallery.py
import streamlit as st
from render import SymbolChain, SymbolGlyph, GlyphComponents
import matplotlib.pyplot as plt
from pathlib import Path
import json
from typing import Dict, List, Tuple

from components.word_gallery import create_glyph_from_letter_id

def load_letters():
    """Load all saved letters from the database"""
    db_path = Path("data/letters.json")
    if db_path.exists():
        with open(db_path, "r") as f:
            return json.load(f)
    return {}

def load_words():
    """Load all saved words from the database"""
    db_path = Path("data/words.json")
    if db_path.exists():
        with open(db_path, "r") as f:
            return json.load(f)
    return {}

def load_sentences():
    """Load all saved sentences from the database"""
    db_path = Path("data/sentences.json")
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

def render_sentence_component(component: dict, words_db: Dict, letters_db: Dict) -> Tuple[plt.Figure, str]:
    """Render a single sentence component (word, text, or punctuation)"""
    if component["type"] == "word":
        word_data = words_db[component["content"]]
        # Create glyphs from letter IDs
        glyphs = []
        for letter_id in word_data["letter_ids"]:
            glyph = create_glyph_from_letter_id(letter_id, letters_db)
            if glyph:
                glyphs.append(glyph)
        
        if glyphs:
            # Create figure for this word
            fig, ax = plt.subplots(figsize=(len(glyphs) * 1.5, 3))
            word_chain = SymbolChain(glyphs)
            word_chain.render(ax)
            plt.close()
            return fig, word_data.get("translation", component["content"])
        else:
            return None, word_data.get("translation", component["content"])
    else:
        return component["content"], component["content"]

def render_sentence_gallery(sentences_db: Dict, words_db: Dict):
    """Render a list of sentences with their translations"""
    st.subheader("Sentence Gallery")
    
    if not sentences_db:
        st.write("No sentences saved yet!")
        return
    
    # Load letters database for rendering
    letters_db = load_letters()
    
    # Add search/filter options
    search_term = st.text_input("Search sentences (ID, translation, or location)", "")
    
    # Filter sentences based on search
    filtered_sentences = {
        id_: data for id_, data in sentences_db.items()
        if (search_term.lower() in id_.lower() or
            search_term.lower() in data.get("translation", "").lower() or
            search_term.lower() in data.get("location_found", "").lower())
    }
    
    if not filtered_sentences:
        st.write("No matching sentences found.")
        return
    
    # Display each sentence
    for sentence_id, sentence_data in filtered_sentences.items():
        with st.expander(f"Sentence: {sentence_id}"):
            # Location and date info
            if sentence_data.get("location_found"):
                st.caption(f"Found: {sentence_data['location_found']}")
            
            # Display original sentence with symbols
            st.write("Original:")
            original_container = st.container()
            with original_container:
                # Use columns for inline display
                cols = st.columns(len(sentence_data["components"]))
                
                # Render each component
                for idx, component in enumerate(sentence_data["components"]):
                    with cols[idx]:
                        rendered, translation = render_sentence_component(component, words_db, letters_db)
                        if isinstance(rendered, plt.Figure):
                            st.pyplot(rendered)
                        elif rendered is not None:
                            st.markdown(f"<h2 style='text-align: center;'>{rendered}</h2>", 
                                      unsafe_allow_html=True)
                        else:
                            st.warning("Failed to render component")
            
            # Display translation
            st.write("Translation:")
            if sentence_data.get("translation"):
                st.write(sentence_data["translation"])
            else:
                # Build translation from components
                translation = " ".join(
                    render_sentence_component(comp, words_db, letters_db)[1]
                    for comp in sentence_data["components"]
                )
                st.write(translation)
            
            # Display notes if any
            if sentence_data.get("notes"):
                st.write("Notes:")
                st.write(sentence_data["notes"])
            
            # Show date added
            if sentence_data.get("date_added"):
                st.caption(f"Added: {sentence_data['date_added']}")

def render_sentence_preview(sentence_components: List[dict], words_db: Dict) -> List[Tuple[plt.Figure, str]]:
    """Render the visual preview of the sentence"""
    letters_db = load_letters()
    word_figures = []
    
    for item in sentence_components:
        rendered, _ = render_sentence_component(item, words_db, letters_db)
        word_figures.append((rendered, item["type"]))
    
    return word_figures