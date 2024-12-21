import streamlit as st
from render import SymbolChain, SymbolGlyph, GlyphComponents
import matplotlib.pyplot as plt
import json
from datetime import datetime
from pathlib import Path

from components.letter_gallery import render_letter_gallery, load_letters
from components.word_gallery import render_word_gallery, load_words
from components.sentence_gallery import render_sentence_gallery, load_sentences, save_sentence, render_sentence_preview

def sentence_creator():
    st.title("Sentence Creator")

    # Create tabs
    tab1, tab3 = st.tabs(["Compose Sentence", "Sentence Gallery"])
    
    # Load available words
    letters_db = load_letters()
    words_db = load_words()
    sentences_db = load_sentences()

    with tab1:
        # Initialize session state for the current sentence
        if "current_sentence" not in st.session_state:
            st.session_state.current_sentence = []
        
        st.subheader("Compose Sentence")
        
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
            st.session_state.cleared = True

        st.write("Filter words by letters (top 16 most frequent):")
        selected_letter = render_letter_gallery(letters_db, show_top_k=16)
        if selected_letter:
            selected_letters = st.session_state.get("filter_by_letters", [])
            selected_letters.append(selected_letter)
            st.session_state.filter_by_letters = selected_letters

        # button to clear filter_by_letters state
        if st.button("Clear Filter"):
            st.session_state.filter_by_letters = []

        render_word_gallery(words_db, callback=lambda word_id: st.session_state.current_sentence.append({
            "type": "word",
            "content": word_id
        }))

        st.subheader("Preview")
        
        # Visual preview (symbols and text)
        if st.session_state.current_sentence:
            st.write("Symbolic Preview:")
            
            # Create container for inline display
            preview_container = st.container()
            with preview_container:
                cols = st.columns(len(st.session_state.current_sentence))
                # if st.session_state.get("cleared"):
                #     st.session_state.cleared = st.session_state.current_sentence = []
                #     cols = st.columns(1)
                
                # Get all preview components
                preview_components = render_sentence_preview(
                    st.session_state.current_sentence, 
                    words_db
                )
                
                # Display components inline
                for idx, (content, type_) in enumerate(preview_components):
                    with cols[idx]:
                        if type_ == "word":
                            st.pyplot(content)
                        else:
                            st.markdown(f"<h2 style='text-align: center;'>{content}</h2>", 
                                        unsafe_allow_html=True)
            
            # Translation preview
            st.write("Translation Preview:")
            translation_preview = " ".join(
                words_db[item["content"]].get("translation", item["content"])
                if item["type"] == "word" else item["content"]
                for item in st.session_state.current_sentence
            )
            st.write(translation_preview)
        
        # Sentence metadata
        st.subheader("Sentence Details")
        sentences = load_sentences()
        highest_sentence_index = max([int(sentence) for sentence in sentences if isinstance(sentence, str) and sentence.isnumeric()])
        st.write(f"There are currently {len(sentences)} sentences with the hightest index being: {highest_sentence_index}.") 
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

    with tab3:
        render_sentence_gallery(sentences_db, words_db)

if __name__ == "__main__":
    sentence_creator()