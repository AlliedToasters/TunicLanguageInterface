# pages/2_word_creator.py
import streamlit as st
from render import SymbolChain, SymbolGlyph, GlyphComponents
import matplotlib.pyplot as plt
import json
from datetime import datetime
from pathlib import Path

from components.word_gallery import render_word_gallery, save_word, load_words, render_word_preview
from components.letter_gallery import load_letters, render_letter_gallery

def word_creator():
    st.title("Word Creator")
    
    # Create tabs for create and galleries
    tab1, tab2, tab3 = st.tabs(["Create Word", "Letter Gallery", "Word Gallery"])
    
    # Load available letters
    letters_db = load_letters()
    words_db = load_words()

    with tab1:
        # Initialize session state for the current word
        if "current_word_letters" not in st.session_state:
            st.session_state.current_word_letters = []  # List of letter IDs
    
        col1, col2 = st.columns([2, 3])

        # tiny letter gallery for reference
        render_letter_gallery(letters_db, columns=16, incl_text=False)
        
        with col1:
            st.subheader("Compose Word")


            
            # Letter selector
            selected_letter = st.selectbox(
                "Add Letter",
                options=list(letters_db.keys()),
                format_func=lambda x: f"Letter {x}"
            )
            
            if st.button("Add Letter"):
                if selected_letter:
                    st.session_state.current_word_letters.append(selected_letter)
                    st.rerun()
            
            if st.button("Remove Last Letter") and st.session_state.current_word_letters:
                st.session_state.current_word_letters.pop()
                st.rerun()
            
            if st.button("Clear Word"):
                st.session_state.current_word_letters = []
                st.rerun()
            
            # Display current word composition
            st.write("Current Word Composition:")
            st.write("Letters: " + " ".join(st.session_state.current_word_letters))
        
        with col2:
            st.subheader("Preview")
            if st.session_state.current_word_letters:
                fig = render_word_preview(st.session_state.current_word_letters)
                if fig:
                    st.pyplot(fig)
            else:
                st.write("Add letters to preview the word")
            
            # Word metadata
            st.subheader("Word Details")
            word_id = st.text_input("Word ID (required)", 
                                  help="Unique identifier for this word")
            translation = st.text_input("Translation", 
                                    help="English translation of this word")
            notes = st.text_area("Notes",
                              help="Any observations or context about this word")
            location = st.text_input("Location Found",
                                 help="Where in the game this word appears")
            
            if st.button("Save Word", disabled=not (word_id and st.session_state.current_word_letters)):
                # Prepare word data with letter references
                word_data = {
                    "id": word_id,
                    "letter_ids": st.session_state.current_word_letters,  # Store letter IDs instead of components
                    "translation": translation,
                    "notes": notes,
                    "location_found": location,
                    "date_added": datetime.now().isoformat()
                }
                
                # Save to database
                save_word(word_data)
                st.success(f"Word '{word_id}' saved successfully!")

    with tab2:
        render_letter_gallery(letters_db)
        
    with tab3:
        render_word_gallery(words_db)

if __name__ == "__main__":
    word_creator()