import streamlit as st
from render import SymbolChain, SymbolGlyph, GlyphComponents
import matplotlib.pyplot as plt
import json
from datetime import datetime
from pathlib import Path

from components.word_gallery import render_word_gallery, load_words
from components.sentence_gallery import render_sentence_gallery, load_sentences, save_sentence, render_sentence_preview

def sentence_creator():
    st.title("Sentence Creator")

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Compose Sentence", "Word Gallery", "Sentence Gallery"])
    
    # Load available words
    words_db = load_words()
    sentences_db = load_sentences()

    with tab1:
        # Initialize session state for the current sentence
        if "current_sentence" not in st.session_state:
            st.session_state.current_sentence = []
        
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
            
            # Visual preview (symbols and text)
            if st.session_state.current_sentence:
                st.write("Symbolic Preview:")
                
                # Create container for inline display
                preview_container = st.container()
                with preview_container:
                    cols = st.columns(len(st.session_state.current_sentence))
                    
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

    with tab2:
        render_word_gallery(words_db)

    with tab3:
        render_sentence_gallery(sentences_db, words_db)

if __name__ == "__main__":
    sentence_creator()