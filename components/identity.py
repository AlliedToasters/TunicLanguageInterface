from typing import List
from render import SymbolGlyph, SymbolChain

def get_active_components_set(glyph: SymbolGlyph):
    """Convert glyph's active components to a frozenset for comparison"""
    return frozenset(comp for comp, is_active in glyph.active_components.items() if is_active)

def find_duplicate_letter(glyph: SymbolGlyph, letters_db: dict):
    """
    Check if a letter with the same component configuration already exists.
    Returns the letter ID if found, None otherwise.
    """
    current_components = get_active_components_set(glyph)
    
    for letter_id, letter_data in letters_db.items():
        # Convert stored components to a set
        stored_components = frozenset(letter_data["components"])
        if current_components == stored_components:
            return letter_id
    return None

def find_duplicate_word(word: SymbolChain, words_db: dict):
    """
    Check if a word with the same component configuration already exists.
    Returns the word ID if found, None otherwise.
    """
    glyphs: List[SymbolGlyph] = word.glyphs
    current_components = [
        get_active_components_set(glyph) for glyph in glyphs
    ] # order matters

    for word_id, word_data in words_db.items():
        # Convert stored components to a set
        stored_components = [
            frozenset(glyph_data) for glyph_data in word_data["components"]
        ]
        if current_components == stored_components:
            return word_id
        
    return None
