from typing import List
from render import SymbolGlyph, SymbolChain
import string

import numpy as np

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

def find_duplicate_word(current_letters: List[str], words_db: dict):
    """
    order matters
    """
    for word_id, word_data in words_db.items():
        if current_letters == word_data["letter_ids"]:
            return word_id
    return None
