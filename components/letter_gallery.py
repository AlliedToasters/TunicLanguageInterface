# components/letter_gallery.py
import streamlit as st
from render import SymbolGlyph, GlyphComponents
import matplotlib.pyplot as plt
from pathlib import Path
import json
from typing import Dict, Optional

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

# def render_letter_gallery(letters_db: Dict, columns: int = 5, incl_text: bool = True):
#     """Render a grid of letter previews with their IDs"""
#     st.subheader("Letter Gallery")
    
#     if not letters_db:
#         st.write("No letters saved yet!")
#         return
    
#     # Create columns for the grid layout
#     cols = st.columns(columns)
    
#     # Distribute letters across columns
#     for idx, (letter_id, letter_data) in enumerate(letters_db.items()):
#         with cols[idx % columns]:
#             if not incl_text:
#                 st.write(letter_id)
#             else:
#                 st.write(f"ID: {letter_id}")
#             fig = create_letter_preview(letter_data["components"])
#             st.pyplot(fig)
#             if letter_data.get("location_found") and incl_text:
#                 st.write(f"Location: {letter_data['location_found']}")

# import io
# from PIL import Image

# def render_letter_gallery(letters_db: Dict, columns: int = 5, incl_text: bool = True, click_callback=None):
#     """Render a grid of clickable letter previews with their IDs"""
#     st.subheader("Letter Gallery")
    
#     if not letters_db:
#         st.write("No letters saved yet!")
#         return
    
#     # Create columns for the grid layout
#     cols = st.columns(columns)
    
#     # Distribute letters across columns
#     for idx, (letter_id, letter_data) in enumerate(letters_db.items()):
#         with cols[idx % columns]:
#             fig = create_letter_preview(letter_data["components"])
            
#             # Convert Matplotlib figure to PIL image
#             buf = io.BytesIO()
#             fig.savefig(buf, format='png')
#             buf.seek(0)
#             img = Image.open(buf)
            
#             # Create a button with the image as its content
#             if st.button("", key=f"letter_{letter_id}"):
#                 # Invoke the click callback if provided
#                 if click_callback:
#                     click_callback(letter_id)
            
#             # Display the PIL image inside the button
#             st.image(img, use_column_width=True)
            
#             if incl_text:
#                 st.write(f"ID: {letter_id}")
#                 if letter_data.get("location_found"):
#                     st.write(f"Location: {letter_data['location_found']}")

import io
import base64
from PIL import Image
from st_clickable_images import clickable_images

def render_letter_gallery(letters_db: Dict, columns: int = 5, incl_text: bool = True, callback=None):
    """Render a grid of clickable letter previews with their IDs"""
    st.subheader("Letter Gallery")
    
    if not letters_db:
        st.write("No letters saved yet!")
        return
    
    # Create a list to store the encoded images and titles
    images = []
    titles = []
    
    # Iterate over the letters and create encoded images
    for letter_id, letter_data in letters_db.items():
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
        titles.append(f"Letter {letter_id}")
    
    # Display the clickable images
    clicked_index = clickable_images(
        images,
        titles=titles,
        div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
        img_style={"margin": "5px", "height": "100px", "width": "100px"},
    )

    if clicked_index > -1:
        clicked_letter_id = list(letters_db.keys())[clicked_index]
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
            # not gr    eat!
        st.session_state.clicked_letter = clicked_letter_id
        return clicked_letter_id#!

def render_letter_preview(glyph: SymbolGlyph):
    """Render the glyph and return the figure"""
    fig, ax = plt.subplots(figsize=(4, 6))
    glyph.render(ax)
    return fig