# components/letter_gallery.py
import streamlit as st
from render import SymbolGlyph, GlyphComponents
import matplotlib.pyplot as plt
from pathlib import Path
import json
from typing import Dict, Optional

def load_letters():
    """Load all saved letters from the database"""
    db_path = Path("data/letters.json")
    if db_path.exists():
        with open(db_path, "r") as f:
            return json.load(f)
    return {}

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

def render_letter_gallery(letters_db: Dict, columns: int = 4):
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
            st.write(f"ID: {letter_id}")
            fig = create_letter_preview(letter_data["components"])
            st.pyplot(fig)
            if letter_data.get("location_found"):
                st.caption(f"Found: {letter_data['location_found']}")