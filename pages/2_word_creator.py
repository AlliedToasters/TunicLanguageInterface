# pages/2_word_creator.py
import streamlit as st
from render import SymbolChain, SymbolGlyph, GlyphComponents
import matplotlib.pyplot as plt
import json
from datetime import datetime
from pathlib import Path

from components.word_gallery import render_word_gallery, save_word, load_words, render_word_preview
from components.letter_gallery import load_letters, render_letter_gallery, letter_creator_interface
from components.sentence_gallery import load_sentences
from components.identity import find_duplicate_word
from components.analytics import translate_words_from_english_freq

def word_creator():
    st.title("Word Creator")
    letter_creator_interface(subheader="Create Letters", show_preview=True)

    # Create tabs for create and galleries
    tab1, tab3 = st.tabs(["Create Word", "Word Gallery"])
    
    # Load available letters
    letters_db = load_letters()
    words_db = load_words()


    with tab1:
        # Initialize session state for the current word
        if "current_word_letters" not in st.session_state:
            st.session_state.current_word_letters = []  # List of letter IDs
    
        col1, col2 = st.columns([2, 3])

        # tiny letter gallery for reference
        # render_letter_gallery(letters_db, columns=16, incl_text=False)
        
        with col1:
            st.subheader("Compose Word")
            
            if st.button("Remove Last Letter") and st.session_state.current_word_letters:
                st.session_state.current_word_letters.pop()
                st.rerun()
            
            if st.button("Clear Word"):
                st.session_state.current_word_letters = []
                st.rerun()

            st.write("letters containing the selected components:")
            render_letter_gallery(letters_db, callback=lambda letter_id: st.session_state.current_word_letters.append(letter_id))
            

            
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
            words = load_words()
            highest_word_index = max([int(word) for word in words if isinstance(word, str) and word.isnumeric()])
            st.write(f"There are currently {len(words)} words in the database with the highest index being {highest_word_index}.")
            word_id = st.text_input("Word ID (required)", 
                                  help="Unique identifier for this word")
            translation = st.text_input("Translation", 
                                    help="English translation of this word")
            notes = st.text_area("Notes",
                              help="Any observations or context about this word")
            location = st.text_input("Location Found",
                                 help="Where in the game this word appears")
            
            # Check for duplicates before showing save controls
            duplicate_id = find_duplicate_word(st.session_state.current_word_letters, words_db) 
            if duplicate_id:
                st.warning(f"⚠️ This word configuration already exists with ID: '{duplicate_id}'")
            
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

    with tab3:
        if st.button("Translate from English word frequency distribution"):
            try:
                letters, words, sentences = load_letters(), load_words(), load_sentences()
                translate_words_from_english_freq(
                    letters,
                    words,
                    sentences
                )
                st.warning("Word translations have been updated in the database!")
            except FileNotFoundError:
                msg = "Error: No English language data found on this device."
                msg += "\nPlease acquire some English text and place it in a file called"
                msg += "\nenglish_sample.txt next to this program entrypoint (app.py)"
                st.error(msg)


        render_word_gallery(words_db)

if __name__ == "__main__":
    word_creator()