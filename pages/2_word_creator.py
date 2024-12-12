# pages/2_word_creator.py
import streamlit as st
from render import SymbolChain, SymbolGlyph, GlyphComponents
import matplotlib.pyplot as plt
import json
from datetime import datetime
from pathlib import Path

from components.letter_gallery import render_letter_gallery, load_letters
from components.word_gallery import render_word_gallery, load_words
from components.identity import find_duplicate_word

def load_letters():
    """Load all saved letters from the database"""
    db_path = Path("data/letters.json")
    if db_path.exists():
        with open(db_path, "r") as f:
            return json.load(f)
    return {}

def initialize_words_db():
    """Initialize the words database if it doesn't exist"""
    db_path = Path("data/words.json")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not db_path.exists():
        with open(db_path, "w") as f:
            json.dump({}, f)
    
    return db_path

def save_word(word_data: dict):
    """Save a word to the database"""
    db_path = initialize_words_db()
    with open(db_path, "r") as f:
        db = json.load(f)
    
    word_id = word_data["id"]
    db[word_id] = word_data
    
    with open(db_path, "w") as f:
        json.dump(db, f, indent=2)

def create_glyph_from_components(components):
    """Create a SymbolGlyph from a list of component names"""
    glyph = SymbolGlyph()
    for comp in components:
        try:
            # Use getattr to access the component string from GlyphComponents
            component_value = getattr(GlyphComponents, comp)
            glyph.activate_component(component_value)
        except AttributeError:
            st.warning(f"Unknown component: {comp}")
    return glyph

def render_word_preview(glyphs):
    """Render the word and return the figure"""
    if not glyphs:
        return None
        
    fig, ax = plt.subplots(figsize=(12, 6))
    word_chain = SymbolChain(glyphs)
    word_chain.render(ax)
    plt.close()  # Clean up the current figure
    return fig

def word_creator():
    st.title("Word Creator")

def word_creator():
    st.title("Word Creator")
    
    # Create tabs for create and gallery views
    tab1, tab2, tab3 = st.tabs(["Create Word", "Letter Gallery", "Word Gallery"])
    
    with tab1:
        # Load available letters
        letters_db = load_letters()
        words_db = load_words()
        
        # Initialize session state for the current word
        if "current_word_glyphs" not in st.session_state:
            st.session_state.current_word_glyphs = []
        
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.subheader("Compose Word")
            
            # Letter selector
            selected_letter = st.selectbox(
                "Add Letter",
                options=list(letters_db.keys()),
                format_func=lambda x: f"Letter {x}"
            )
            
            if st.button("Add Letter") and selected_letter:
                letter_data = letters_db[selected_letter]
                glyph = create_glyph_from_components(letter_data["components"])
                st.session_state.current_word_glyphs.append(glyph)
                st.rerun()
            
            if st.button("Remove Last Letter") and st.session_state.current_word_glyphs:
                st.session_state.current_word_glyphs.pop()
                st.rerun()
            
            if st.button("Clear Word"):
                st.session_state.current_word_glyphs = []
                st.rerun()
            
            # Display current word composition
            st.write("Current Word Composition:")
            for i, glyph in enumerate(st.session_state.current_word_glyphs):
                st.write(f"Letter {i+1}: {len([comp for comp in glyph.active_components if glyph.active_components[comp]])} active components")
        
        with col2:
            st.subheader("Preview")
            if st.session_state.current_word_glyphs:
                fig = render_word_preview(st.session_state.current_word_glyphs)
                if fig:
                    st.pyplot(fig)
            else:
                st.write("Add letters to preview the word")

            # Check for duplicate word before showing save button
            duplicate_word_id = find_duplicate_word(SymbolChain(st.session_state.current_word_glyphs), words_db)
            if duplicate_word_id:
                st.warning(f"Duplicate word found: {duplicate_word_id}")
            
            # Word metadata and save controls
            st.subheader("Word Details")
            word_id = st.text_input("Word ID (required)", 
                                help="Unique identifier for this word")
            translation = st.text_input("Translation", 
                                    help="English translation of this word")
            notes = st.text_area("Notes",
                            help="Any observations or context about this word")
            location = st.text_input("Location Found",
                                help="Where in the game this word appears")
        
            if st.button("Save Word", disabled=not (word_id and st.session_state.current_word_glyphs)):
                # Prepare word data
                word_data = {
                    "id": word_id,
                    "components": [
                        [comp for comp in glyph.active_components if glyph.active_components[comp]]
                        for glyph in st.session_state.current_word_glyphs
                    ],
                    "translation": translation,
                    "notes": notes,
                    "location_found": location,
                    "date_added": datetime.now().isoformat()
                }
                
                # Save to database
                save_word(word_data)
                st.success(f"Word '{word_id}' saved successfully!")

    with tab2:
        letters_db = load_letters()
        render_letter_gallery(letters_db, columns=3)  # Larger previews in gallery tab

    with tab3:
        words_db = load_words()
        render_word_gallery(words_db)

if __name__ == "__main__":
    word_creator()