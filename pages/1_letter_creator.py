# pages/1_letter_creator.py
import streamlit as st
from render import SymbolGlyph, GlyphComponents 
import matplotlib.pyplot as plt
import json
from datetime import datetime
from pathlib import Path

from components.letter_gallery import render_letter_gallery
from components.identity import find_duplicate_letter

def initialize_db():
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
    db_path = initialize_db()
    with open(db_path, "r") as f:
        db = json.load(f)
    
    letter_id = letter_data["id"]
    db[letter_id] = letter_data
    
    with open(db_path, "w") as f:
        json.dump(db, f, indent=2)

def render_preview(glyph: SymbolGlyph):
    """Render the glyph and return the figure"""
    fig, ax = plt.subplots(figsize=(4, 6))
    glyph.render(ax)
    return fig

def main():
    st.title("Letter Creator")

    # Create tabs for create and gallery views
    tab1, tab2 = st.tabs(["Create Letter", "Letter Gallery"])
    
    with tab1:
        # (Previous letter creator code remains the same until the end)
        # After success message in save operation, add:
        if "show_gallery" not in st.session_state:
            st.session_state.show_gallery = False
            
        if st.session_state.get("show_gallery", False):
            st.divider()
            letters_db = load_letters()
            render_letter_gallery(letters_db)

    
        # Initialize session state for the glyph
        if "current_glyph" not in st.session_state:
            st.session_state.current_glyph = SymbolGlyph()
        
        # Load existing letters
        letters_db = load_letters()
        
        # Create two columns for layout
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.subheader("Components")
            
            # Upper components
            st.write("Upper Components:")
            upper_verticals = st.checkbox("Upper Left Vertical", key="upper_left_vert")
            upper_center = st.checkbox("Upper Center Vertical", key="upper_center")
            
            st.write("Upper Diamond:")
            upper_diamond = {
                "upper_left": st.checkbox("Upper Left Edge", key="upper_diamond_ul"),
                "upper_right": st.checkbox("Upper Right Edge", key="upper_diamond_ur"),
                "lower_left": st.checkbox("Lower Left Edge", key="upper_diamond_ll"),
                "lower_right": st.checkbox("Lower Right Edge", key="upper_diamond_lr")
            }
            
            # Lower components
            st.write("Lower Components:")
            lower_verticals = st.checkbox("Lower Left Vertical", key="lower_left_vert")
            lower_center = st.checkbox("Lower Center Vertical", key="lower_center")
            lower_circle = st.checkbox("Lower Circle", key="lower_circle")
            
            st.write("Lower Diamond:")
            lower_diamond = {
                "upper_left": st.checkbox("Upper Left Edge", key="lower_diamond_ul"),
                "upper_right": st.checkbox("Upper Right Edge", key="lower_diamond_ur"),
                "lower_left": st.checkbox("Lower Left Edge", key="lower_diamond_ll"),
                "lower_right": st.checkbox("Lower Right Edge", key="lower_diamond_lr")
            }
        
        # Create a new glyph based on selections
        glyph = SymbolGlyph()
        
        # Activate components based on selections
        if upper_verticals:
            glyph.activate_component(GlyphComponents.UPPER_LEFT_VERTICAL)
        if upper_center:
            glyph.activate_component(GlyphComponents.UPPER_CENTER_VERTICAL)
        if lower_verticals:
            glyph.activate_component(GlyphComponents.LOWER_LEFT_VERTICAL)
        if lower_center:
            glyph.activate_component(GlyphComponents.LOWER_CENTER_VERTICAL)
        if lower_circle:
            glyph.activate_component(GlyphComponents.LOWER_CIRCLE)
            
        # Activate diamond components
        if upper_diamond["upper_left"]:
            glyph.activate_component(GlyphComponents.UPPER_DIAMOND_UPPER_LEFT)
        if upper_diamond["upper_right"]:
            glyph.activate_component(GlyphComponents.UPPER_DIAMOND_UPPER_RIGHT)
        if upper_diamond["lower_left"]:
            glyph.activate_component(GlyphComponents.UPPER_DIAMOND_LOWER_LEFT)
        if upper_diamond["lower_right"]:
            glyph.activate_component(GlyphComponents.UPPER_DIAMOND_LOWER_RIGHT)
            
        if lower_diamond["upper_left"]:
            glyph.activate_component(GlyphComponents.LOWER_DIAMOND_UPPER_LEFT)
        if lower_diamond["upper_right"]:
            glyph.activate_component(GlyphComponents.LOWER_DIAMOND_UPPER_RIGHT)
        if lower_diamond["lower_left"]:
            glyph.activate_component(GlyphComponents.LOWER_DIAMOND_LOWER_LEFT)
        if lower_diamond["lower_right"]:
            glyph.activate_component(GlyphComponents.LOWER_DIAMOND_LOWER_RIGHT)
        
        # Show preview in second column
        with col2:
            st.subheader("Preview")
            fig = render_preview(glyph)
            st.pyplot(fig)
            
            # Check for duplicates before showing save controls
            duplicate_id = find_duplicate_letter(glyph, letters_db)
            if duplicate_id:
                st.warning(f"⚠️ This letter configuration already exists with ID: '{duplicate_id}'")
                
            # Metadata and save controls
            st.subheader("Letter Details")
            letter_id = st.text_input("Letter ID (required)", 
                                    help="Unique identifier for this letter")
            notes = st.text_area("Notes", 
                            help="Any observations or context about this letter")
            location = st.text_input("Location Found", 
                                help="Where in the game this letter appears")
            
            # Only show save button if there's no duplicate
            if not duplicate_id:
                if st.button("Save Letter", disabled=not letter_id):
                    # Prepare letter data
                    letter_data = {
                        "id": letter_id,
                        "components": [comp for comp, is_active in glyph.active_components.items() if is_active],
                        "notes": notes,
                        "location_found": location,
                        "date_added": datetime.now().isoformat()
                    }
                    
                    # Save to database
                    save_letter(letter_data)
                    st.success(f"Letter '{letter_id}' saved successfully!")

    with tab2:
        letters_db = load_letters()
        render_letter_gallery(letters_db, columns=3)  # Larger previews in gallery tab


if __name__ == "__main__":
    main()