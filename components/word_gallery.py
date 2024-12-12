# components/word_gallery.py
import streamlit as st
from render import SymbolChain, SymbolGlyph, GlyphComponents
import matplotlib.pyplot as plt
from pathlib import Path
import json
from typing import Dict, Optional, List

def load_words():
    """Load all saved words from the database"""
    db_path = Path("data/words.json")
    if db_path.exists():
        with open(db_path, "r") as f:
            return json.load(f)
    return {}

def create_glyph_from_components(components: List[str]) -> SymbolGlyph:
    """Create a single glyph from component names"""
    glyph = SymbolGlyph()
    for comp in components:
        component_value = getattr(GlyphComponents, comp)
        glyph.activate_component(component_value)
    return glyph

def create_word_preview(components_list: List[List[str]]) -> Optional[plt.Figure]:
    """Create a preview figure for a word from its component lists"""
    glyphs = [create_glyph_from_components(components) for components in components_list]
    
    fig, ax = plt.subplots(figsize=(6, 3))  # Wider figure for words
    word_chain = SymbolChain(glyphs)
    word_chain.render(ax)
    plt.close()
    return fig

def render_word_gallery(words_db: Dict, columns: int = 2):
    """Render a grid of word previews with their IDs and translations"""
    st.subheader("Word Gallery")
    
    if not words_db:
        st.write("No words saved yet!")
        return
    
    # Create columns for the grid layout
    cols = st.columns(columns)
    
    # Distribute words across columns
    for idx, (word_id, word_data) in enumerate(words_db.items()):
        with cols[idx % columns]:
            st.write(f"ID: {word_id}")
            if word_data.get("translation"):
                st.caption(f"Translation: {word_data['translation']}")
            fig = create_word_preview(word_data["components"])
            st.pyplot(fig)
            if word_data.get("location_found"):
                st.caption(f"Found: {word_data['location_found']}")
            if word_data.get("notes"):
                with st.expander("Notes"):
                    st.write(word_data["notes"])