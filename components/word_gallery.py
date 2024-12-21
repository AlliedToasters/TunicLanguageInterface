# components/word_gallery.py
import streamlit as st
from render import SymbolChain, SymbolGlyph, GlyphComponents
import matplotlib.pyplot as plt
from pathlib import Path
import json
from typing import Dict, Optional, List
import io
import base64
from PIL import Image
from st_clickable_images import clickable_images

from components.analytics import get_freq_distibution

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

def create_glyph_from_letter_id(letter_id: str, letters_db: Dict) -> Optional[SymbolGlyph]:
    """Create a glyph from a letter ID using the letters database"""
    if letter_id not in letters_db:
        st.warning(f"Letter '{letter_id}' not found in database")
        return None
        
    letter_data = letters_db[letter_id]
    glyph = SymbolGlyph()
    for comp in letter_data["components"]:
        component_value = getattr(GlyphComponents, comp)
        glyph.activate_component(component_value)
    return glyph

def create_word_preview(letter_ids: List[str], letters_db: Dict) -> Optional[plt.Figure]:
    """Create a preview figure for a word from its letter IDs"""
    glyphs = []
    for letter_id in letter_ids:
        glyph = create_glyph_from_letter_id(letter_id, letters_db)
        if glyph:
            glyphs.append(glyph)
    
    if not glyphs:
        return None
    
    fig, ax = plt.subplots(figsize=(6, 3))  # Wider figure for words
    word_chain = SymbolChain(glyphs)
    word_chain.render(ax)
    plt.close()
    return fig

def render_word_gallery(words_db: Dict, columns: int = 4, callback=None):
    """Render a grid of clickable word previews with their IDs and translations, sorted by frequency"""
    
    if not words_db:
        st.write("No words saved yet!")
        return
    
    # Load letters database for rendering and get frequency distribution
    letters_db = load_letters()
    sentences_db = load_sentences()
    word_frequency, word_counts, _, _ = get_freq_distibution(letters_db, words_db, sentences_db)
    
    # Create frequency lookup dictionary
    frequency_dict = dict(zip(word_frequency, word_counts))
    
    # Add search/filter options
    search_term = st.text_input("Search words (ID, translation, or location)", "")
    
    # Filter words based on search
    filtered_words = {
        id_: data for id_, data in words_db.items()
        if (search_term.lower() in id_.lower() or
            search_term.lower() in data.get("translation", "").lower() or
            search_term.lower() in data.get("location_found", "").lower())
    }
    
    selected_letters = st.session_state.get("filter_by_letters", [])
    if len(selected_letters) > 0:
        # filter down only to words
        # containing all selected letters
        new_filtered_words = {}
        for word_id, word_data in filtered_words.items():
            word_letters = word_data["letter_ids"]
            if all([letter_id in word_letters for letter_id in selected_letters]):
                new_filtered_words[word_id] = word_data

        filtered_words = new_filtered_words

    if not filtered_words:
        st.write("No matching words found.")
        return
    
    # Sort filtered words by frequency
    sorted_items = sorted(
        filtered_words.items(),
        key=lambda x: frequency_dict.get(x[0], 0),  # Default to 0 if word not found
        reverse=True
    )
    filtered_words = dict(sorted_items)
    
    # Create lists to store the encoded images, titles, and word data
    images = []
    titles = []
    word_data_list = []
    ordered_word_ids = []  # Keep track of word IDs in display order
    
    # Iterate over the filtered and sorted words
    for word_id, word_data in filtered_words.items():
        fig = create_word_preview(word_data["letter_ids"], letters_db)
        if fig:
            # Convert Matplotlib figure to PIL image
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)
            img = Image.open(buf)
            
            # Encode the image as base64
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            encoded_img = base64.b64encode(buffered.getvalue()).decode()
            images.append(f"data:image/png;base64,{encoded_img}")
            
            # Add the title, word data, and ID
            freq = frequency_dict.get(word_id, 0)
            titles.append(f"Word {word_id} (f:{freq})")
            word_data_list.append(word_data)
            ordered_word_ids.append(word_id)
    
    # Display the clickable images
    clicked_index = clickable_images(
        images,
        titles=titles,
        div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
        img_style={"margin": "5px", "height": "150px", "width": "auto"},
    )
    
    if clicked_index > -1:
        clicked_word_id = ordered_word_ids[clicked_index]  # Use ordered list instead of filtered_words.keys()
        clicked_word_data = word_data_list[clicked_index]
        st.write(f"Clicked on word: {clicked_word_id}")
        
        # Display word details
        if clicked_word_data.get("translation"):
            st.write(f"Translation: {clicked_word_data['translation']}")
        st.write("Letters: " + " ".join(clicked_word_data["letter_ids"]))
        if clicked_word_data.get("location_found"):
            st.write(f"Found: {clicked_word_data['location_found']}")
        if clicked_word_data.get("notes"):
            with st.expander("Notes"):
                st.write(clicked_word_data["notes"])

        # check for change!
        old_clicked_word = st.session_state.get("clicked_word")
        new_clicked_word = clicked_word_id
        if old_clicked_word != new_clicked_word:
            # if, only if, the clicked word has changed
            if callback:
                callback(new_clicked_word)
                
            st.session_state.clicked_word = new_clicked_word
            
    else:
        st.write("No word clicked")

def render_word_preview(letter_ids: List[str]) -> Optional[plt.Figure]:
    """Render a preview of a word being composed"""
    if not letter_ids:
        return None
    
    letters_db = load_letters()
    return create_word_preview(letter_ids, letters_db)