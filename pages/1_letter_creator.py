# pages/1_letter_creator.py
import streamlit as st
from render import SymbolGlyph, GlyphComponents 
import matplotlib.pyplot as plt
import json
from datetime import datetime
from pathlib import Path

from components.letter_gallery import render_letter_gallery, load_letters, save_letter, render_letter_preview, letter_creator_interface
from components.identity import find_duplicate_letter

def main():
    st.title("Letter Creator")

    letters_db = load_letters()
    letter_creator_interface()
    # Create tabs for create and gallery views
    tab1, tab2 = st.tabs(["Create Letter", "Letter Gallery"])
    
    with tab1:
        # (Previous letter creator code remains the same until the end)
        # After success message in save operation, add:
        glyph = st.session_state.get("current_glyph", SymbolGlyph)
        if "show_gallery" not in st.session_state:
            st.session_state.show_gallery = False
            
        if st.session_state.get("show_gallery", False):
            st.divider()
            letters_db = load_letters()

    
        # Initialize session state for the glyph
        if "current_glyph" not in st.session_state:
            st.session_state.current_glyph = SymbolGlyph()
        
        # Load existing letters
        letters_db = load_letters()
        
        with tab1:
            st.subheader("Preview")
            glyph = st.session_state.get("current_glyph", SymbolGlyph())
            fig = render_letter_preview(glyph)
            st.pyplot(fig, use_container_width=False)
            
            # Check for duplicates before showing save controls
            duplicate_id = find_duplicate_letter(glyph, letters_db)
            if duplicate_id:
                st.warning(f"⚠️ This letter configuration already exists with ID: '{duplicate_id}'")
                
            # Metadata and save controls
            st.subheader("Letter Details")
            letters = load_letters()
            highest_letter_id = max([int(key) for key in letters.keys() if isinstance(key, str) and key.isnumeric()])
            st.write(f"There are currently {len(letters)} letters in the db with the highest ID being: {highest_letter_id}")
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
        render_letter_gallery(letters_db)


if __name__ == "__main__":
    main()