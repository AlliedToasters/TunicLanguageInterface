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

def render_letter_gallery(letters_db: Dict, columns: int = 5, incl_text: bool = True):
    """Render a grid of letter previews with their IDs"""
    st.subheader("Letter Gallery")
    
    if not letters_db:
        st.write("No letters saved yet!")
        return
    
    # Create columns for the grid layout
    cols = st.columns(columns)
    
    # Distribute letters across columns
    for idx, (letter_id, letter_data) in enumerate(letters_db.items()):
        with cols[idx % columns]:
            if not incl_text:
                st.write(letter_id)
            else:
                st.write(f"ID: {letter_id}")
            fig = create_letter_preview(letter_data["components"])
            st.pyplot(fig)
            if letter_data.get("location_found") and incl_text:
                st.write(f"Location: {letter_data['location_found']}")

def render_letter_preview(glyph: SymbolGlyph):
    """Render the glyph and return the figure"""
    fig, ax = plt.subplots(figsize=(4, 6))
    glyph.render(ax)
    return fig