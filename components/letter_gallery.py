# components/letter_gallery.py
import streamlit as st
from render import SymbolGlyph, GlyphComponents
import matplotlib.pyplot as plt
from pathlib import Path
import json
from typing import Dict, Optional
import time

import numpy as np

import io
import base64
from PIL import Image
from st_clickable_images import clickable_images

from components.analytics import get_freq_distibution
import streamlit as st
from render import SymbolGlyph, GlyphComponents
from typing import Dict


import streamlit as st
from render import SymbolGlyph, GlyphComponents
from typing import Dict

def letter_creator_interface(subheader: str="Letter Components", show_preview: bool=False):
    """A compact letter creator interface using single-level columns"""
    
    st.subheader(subheader)
    
    # Create four columns for the main layout
    col1, col2, col3, col4 = st.columns(4)
    
    # Column 1: Upper Verticals
    with col1:
        st.markdown("##### Upper Verticals")
        upper_verticals = st.checkbox(
            "Left Vertical",
            key="upper_left_vert",
            help="Toggle upper left vertical line"
        )
        upper_center = st.checkbox(
            "Center Vertical",
            key="upper_center",
            help="Toggle upper center vertical line"
        )
    
    # Column 2: Upper Diamond
    with col2:
        st.markdown("##### Upper Diamond")
        upper_diamond = {
            "upper_left": st.checkbox("Upper Left", key="upper_diamond_ul"),
            "upper_right": st.checkbox("Upper Right", key="upper_diamond_ur"),
            "lower_left": st.checkbox("Lower Left", key="upper_diamond_ll"),
            "lower_right": st.checkbox("Lower Right", key="upper_diamond_lr")
        }
    
    # Column 3: Lower Verticals
    with col3:
        st.markdown("##### Lower Verticals")
        lower_verticals = st.checkbox(
            "Left Vertical",
            key="lower_left_vert",
            help="Toggle lower left vertical line"
        )
        lower_center = st.checkbox(
            "Center Vertical",
            key="lower_center",
            help="Toggle lower center vertical line"
        )
        lower_circle = st.checkbox(
            "Circle",
            key="lower_circle",
            help="Toggle lower circle"
        )
    
    # Column 4: Lower Diamond
    with col4:
        st.markdown("##### Lower Diamond")
        lower_diamond = {
            "upper_left": st.checkbox("Upper Left", key="lower_diamond_ul"),
            "upper_right": st.checkbox("Upper Right", key="lower_diamond_ur"),
            "lower_left": st.checkbox("Lower Left", key="lower_diamond_ll"),
            "lower_right": st.checkbox("Lower Right", key="lower_diamond_lr")
        }
    
    # Create glyph based on selections
    glyph = SymbolGlyph()
    
    # Upper components
    if upper_verticals:
        glyph.activate_component(GlyphComponents.UPPER_LEFT_VERTICAL)
    if upper_center:
        glyph.activate_component(GlyphComponents.UPPER_CENTER_VERTICAL)
        
    # Lower components
    if lower_verticals:
        glyph.activate_component(GlyphComponents.LOWER_LEFT_VERTICAL)
    if lower_center:
        glyph.activate_component(GlyphComponents.LOWER_CENTER_VERTICAL)
    if lower_circle:
        glyph.activate_component(GlyphComponents.LOWER_CIRCLE)
    
    # Upper diamond
    if upper_diamond["upper_left"]:
        glyph.activate_component(GlyphComponents.UPPER_DIAMOND_UPPER_LEFT)
    if upper_diamond["upper_right"]:
        glyph.activate_component(GlyphComponents.UPPER_DIAMOND_UPPER_RIGHT)
    if upper_diamond["lower_left"]:
        glyph.activate_component(GlyphComponents.UPPER_DIAMOND_LOWER_LEFT)
    if upper_diamond["lower_right"]:
        glyph.activate_component(GlyphComponents.UPPER_DIAMOND_LOWER_RIGHT)
    
    # Lower diamond
    if lower_diamond["upper_left"]:
        glyph.activate_component(GlyphComponents.LOWER_DIAMOND_UPPER_LEFT)
    if lower_diamond["upper_right"]:
        glyph.activate_component(GlyphComponents.LOWER_DIAMOND_UPPER_RIGHT)
    if lower_diamond["lower_left"]:
        glyph.activate_component(GlyphComponents.LOWER_DIAMOND_LOWER_LEFT)
    if lower_diamond["lower_right"]:
        glyph.activate_component(GlyphComponents.LOWER_DIAMOND_LOWER_RIGHT)

    if show_preview:
        fig = render_letter_preview(glyph, scaling_factor=0.15)
        st.pyplot(fig, use_container_width=False)
        if st.button("Save Letter"):
            save_letter_from_glyph(glyph)
    
    st.session_state.current_glyph = glyph

def save_letter_from_glyph(glyph: SymbolGlyph):
    """Save a letter to the database from a glyph"""
    letters_db = load_letters()
    highest_id = max([int(key) for key in letters_db.keys() if key.isnumeric()], default=0)
    new_id = str(highest_id + 1)
    letter_data = {
        "id": new_id,
        "components": [key for key, value in glyph.active_components.items() if value],
        "notes": "Automatically created letter",
        "location": "Automatically created letter"
    }
    save_letter(letter_data)
    st.write(f"Letter {new_id} saved successfully!")

def _automatically_create_letter(active_components: list):
    """
    Creates a letter while skipping the entire form.
    The id is an integer greater than the highest id in the db.
    The rest of the information is not important.
    """
    letters_db = load_letters()
    highest_id = max([int(key) for key in letters_db.keys() if key.isnumeric()])
    new_id = str(highest_id + 1)
    new_letter = {
        "id": new_id,
        "components": active_components,
        "notes": "Automatically created letter",
        "location": "Automatically created letter"
    }
    save_letter(new_letter)
    st.write(f"Letter {new_id} automatically created!")
    time.sleep(1)
    st.session_state.show_gallery = True

def initialize_letter_db():
    """Initialize the letters database if it doesn't exist"""
    db_path = Path("data/letters.json")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not db_path.exists():
        with open(db_path, "w") as f:
            json.dump({}, f)
    
    return db_path

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

def save_letter(letter_data: dict):
    """Save a letter to the database"""
    db_path = initialize_letter_db()
    with open(db_path, "r") as f:
        db = json.load(f)
    
    letter_id = letter_data["id"]
    db[letter_id] = letter_data
    
    with open(db_path, "w") as f:
        json.dump(db, f, indent=2)

def create_letter_preview(components: list) -> Optional[plt.Figure]:
    """Create a preview figure for a letter from its components"""
    glyph = SymbolGlyph()
    for comp in components:
        component_value = getattr(GlyphComponents, comp)
        glyph.activate_component(component_value)
    
    fig, ax = plt.subplots(figsize=(2, 3))  # Smaller figure size for gallery
    glyph.render(ax)
    plt.close()
    return fig

def render_letter_gallery(letters_db: Dict, show_top_k:int|None=None, callback=None):
    """Render a grid of clickable letter previews with their IDs"""
    
    if not letters_db:
        st.write("No letters saved yet!")
        return
    
    # Create a list to store the encoded images and titles
    images = []
    titles = []
    # Create a list to store the letter IDs in order of display
    ordered_letter_ids = []  # New list to maintain order

    words_db = load_words()
    sentence_db = load_sentences()
    _, _, letter_frequency, letter_counts = get_freq_distibution(letters_db, words_db, sentence_db)
    
    # Create a frequency lookup dictionary from the NumPy arrays
    frequency_dict = dict(zip(letter_frequency, letter_counts))

    glyph = st.session_state.get("current_glyph", SymbolGlyph())
    active_components = glyph.active_components
    active_components = [key for key, value in active_components.items() if value]
    
    # Sort letters_db items based on frequency counts
    sorted_items = sorted(
        letters_db.items(),
        key=lambda x: frequency_dict.get(x[0], 0),  # Default to 0 if letter not found
        reverse=True
    )

    # filter letters based on active components
    if len(active_components) > 0:
        new_sorted_items = []
        for letter_id, item in sorted_items:
            item_components = item["components"]

            if all([reference_component in item_components for reference_component in active_components]):
                new_sorted_items.append((letter_id, item))
        sorted_items = new_sorted_items

    if show_top_k:
        sorted_items = sorted_items[:show_top_k]

    if len(sorted_items) == 0:
        st.write("No letters found with the selected components.")
        # st.write("would you like to create this letter?")
        if st.button("Create this letter?"):
            _automatically_create_letter(active_components)
        
    
    for letter_id, letter_data in sorted_items:
        ordered_letter_ids.append(letter_id)  # Store letter IDs in display order
        
        fig = create_letter_preview(letter_data["components"])
        
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
        
        # Add the title
        this_letter_freq = frequency_dict.get(letter_id, 0)
        titles.append(f"{letter_id}f:{this_letter_freq}")
    
    # Display the clickable images
    clicked_index = clickable_images(
        images,
        titles=titles,
        div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
        img_style={"margin": "5px", "height": "100px", "width": "100px"},
    )

    if clicked_index > -1:
        # Use ordered_letter_ids instead of letters_db.keys()
        clicked_letter_id = ordered_letter_ids[clicked_index]
        st.write(f"Clicked on letter: {clicked_letter_id}")
        old_clicked_letter = st.session_state.get("clicked_letter")
        new_clicked_letter = clicked_letter_id
        # check if these have changed!
        if old_clicked_letter != new_clicked_letter:
            st.session_state.clicked_letter = new_clicked_letter
            if callback:
                callback(new_clicked_letter)
            # if so, and only if so, update the session state!
            # otherwise, we end up appending the same letter multiple times!!
            # not great!
        st.session_state.clicked_letter = clicked_letter_id
        return clicked_letter_id

def render_letter_preview(glyph: SymbolGlyph, scaling_factor: int=0.5):
    """Render the glyph and return the figure"""
    fig, ax = plt.subplots(figsize=(4 * scaling_factor, 6 * scaling_factor))
    glyph.render(ax)
    return fig