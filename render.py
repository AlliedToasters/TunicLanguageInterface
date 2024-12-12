import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Optional, Sequence

class SymbolConfig:
    """Configuration constants for symbol rendering"""
    FRACTION_Y = 0.0  # y-position of fraction line
    VERTICAL_EXTENSION_UP = 1.0  # full height above fraction
    VERTICAL_EXTENSION_DOWN = -1.0  # full height below fraction
    HALF_EXTENSION_UP = 0.5  # half height above fraction
    HALF_EXTENSION_DOWN = -0.5  # half height below fraction
    CENTER_X = 0.5  # x-position of center within a single glyph
    LEFT_X = 0.0  # x-position of left vertical
    RIGHT_X = 1.0  # x-position of right vertical (for reference)
    LOWER_GAP = 0.1  # gap between fraction line and lower elements
    UPPER_GAP = 0.1  # gap between fraction line and upper elements
    DIAMOND_ANGLE = 45  # angle of diamond edges in degrees
    CIRCLE_RADIUS = 0.05  # radius of the small circle
    CIRCLE_OFFSET = -0.05  # offset of the circle from the center
    GLYPH_WIDTH = 1.0  # width of a single glyph
    GLYPH_SPACING = 0.0  # spacing between glyphs (0 for shared verticals)
    BRIDGE_LENGTH = 0.1  # length of the tiny bridge lines
    LINEWIDTH = 3.0  # line width for all components

class GlyphComponents:
    """Enumeration of possible glyph components"""
    # Upper components
    UPPER_LEFT_VERTICAL = "UPPER_LEFT_VERTICAL"
    UPPER_CENTER_VERTICAL = "UPPER_CENTER_VERTICAL"
    UPPER_DIAMOND_LOWER_LEFT = "UPPER_DIAMOND_LOWER_LEFT"
    UPPER_DIAMOND_UPPER_LEFT = "UPPER_DIAMOND_UPPER_LEFT"
    UPPER_DIAMOND_UPPER_RIGHT = "UPPER_DIAMOND_UPPER_RIGHT"
    UPPER_DIAMOND_LOWER_RIGHT = "UPPER_DIAMOND_LOWER_RIGHT"
    
    # Lower components
    LOWER_LEFT_VERTICAL = "LOWER_LEFT_VERTICAL"
    LOWER_CENTER_VERTICAL = "LOWER_CENTER_VERTICAL"
    LOWER_DIAMOND_LOWER_LEFT = "LOWER_DIAMOND_LOWER_LEFT"
    LOWER_DIAMOND_UPPER_LEFT = "LOWER_DIAMOND_UPPER_LEFT"
    LOWER_DIAMOND_UPPER_RIGHT = "LOWER_DIAMOND_UPPER_RIGHT"
    LOWER_DIAMOND_LOWER_RIGHT = "LOWER_DIAMOND_LOWER_RIGHT"
    LOWER_CIRCLE = "LOWER_CIRCLE"
    
    @classmethod
    def all_components(cls) -> List[str]:
        """Return all possible component names"""
        return [getattr(cls, attr) for attr in dir(cls) 
                if not attr.startswith('_') and isinstance(getattr(cls, attr), str)]

class SymbolGlyph:
    def __init__(self):
        self.config = SymbolConfig()
        self.active_components = {
            component: False for component in GlyphComponents.all_components()
        }
    
    def activate_component(self, component: str):
        """Activate a specific component"""
        if component in self.active_components:
            self.active_components[component] = True
        else:
            raise ValueError(f"Unknown component: {component}")
        
    def activate_full_upper_diamond(self):
        """Convenience method to activate all upper diamond components"""
        for component in GlyphComponents.all_components():
            if component.startswith("UPPER_DIAMOND"):
                self.active_components[component] = True

    def activate_full_lower_diamond(self):
        """Convenience method to activate all lower diamond components"""
        for component in GlyphComponents.all_components():
            if component.startswith("LOWER_DIAMOND"):
                self.active_components[component] = True
    
    def to_vector(self) -> np.ndarray:
        """Convert symbol to one-hot encoded vector"""
        return np.array([int(v) for v in self.active_components.values()])
    
    @classmethod
    def from_vector(cls, vector: np.ndarray) -> 'SymbolGlyph':
        """Create a symbol from a vector representation"""
        symbol = cls()
        for i, component in enumerate(GlyphComponents.all_components()):
            if vector[i]:
                symbol.activate_component(component)
        return symbol
    
    def draw_center_bridge_line(self, ax: plt.Axes) -> plt.Axes:
        ax.plot([self.config.CENTER_X, self.config.CENTER_X],
                [self.config.FRACTION_Y, 
                self.config.FRACTION_Y + self.config.BRIDGE_LENGTH],
                'k-', linewidth=self.config.LINEWIDTH)
        return ax
    
    def draw_left_bridge_line(self, ax: plt.Axes) -> plt.Axes:
        ax.plot([self.config.LEFT_X, self.config.LEFT_X],
                [self.config.FRACTION_Y, 
                self.config.FRACTION_Y + self.config.BRIDGE_LENGTH],
                'k-', linewidth=self.config.LINEWIDTH)
        return ax
    
    def render(self, ax: Optional[plt.Axes] = None) -> plt.Axes:
        """Render the symbol"""
        if ax is None:
            _, ax = plt.subplots(figsize=(4, 6))
        
        # Set up the plot
        ax.set_xlim(0, 1)
        ax.set_ylim(self.config.VERTICAL_EXTENSION_DOWN - 0.2, 
                    self.config.VERTICAL_EXTENSION_UP + 0.2)
        ax.axis('off')
        
        # Draw fraction line
        ax.axhline(y=self.config.FRACTION_Y, color='black', linewidth=self.config.LINEWIDTH)
        
        # Draw upper components with gap
        if self.active_components[GlyphComponents.UPPER_LEFT_VERTICAL]:
            # Draw the main vertical line starting from above the gap
            ax.plot([self.config.LEFT_X, self.config.LEFT_X],
                   [self.config.FRACTION_Y + self.config.UPPER_GAP, 
                    self.config.HALF_EXTENSION_UP],
                   'k-', linewidth=self.config.LINEWIDTH)
            # Draw left bridge line
            ax = self.draw_left_bridge_line(ax)
            
        if self.active_components[GlyphComponents.UPPER_CENTER_VERTICAL]:
            # Draw the main vertical line starting from above the gap
            ax.plot([self.config.CENTER_X, self.config.CENTER_X],
                   [self.config.FRACTION_Y + self.config.UPPER_GAP, 
                    self.config.VERTICAL_EXTENSION_UP],
                   'k-', linewidth=self.config.LINEWIDTH)
            # Draw the center bridge line
            ax = self.draw_center_bridge_line(ax)
        
        # Draw lower components with gap
        if self.active_components[GlyphComponents.LOWER_LEFT_VERTICAL]:
            ax.plot([self.config.LEFT_X, self.config.LEFT_X],
                   [self.config.FRACTION_Y - self.config.LOWER_GAP, 
                    self.config.HALF_EXTENSION_DOWN],
                   'k-', linewidth=self.config.LINEWIDTH)
            
        if self.active_components[GlyphComponents.LOWER_CENTER_VERTICAL]:
            ax.plot([self.config.CENTER_X, self.config.CENTER_X],
                   [self.config.FRACTION_Y - self.config.LOWER_GAP, 
                    self.config.VERTICAL_EXTENSION_DOWN],
                   'k-', linewidth=self.config.LINEWIDTH)
            
        # Draw circle if present
        if self.active_components[GlyphComponents.LOWER_CIRCLE]:
            circle = plt.Circle((self.config.CENTER_X, 
                               self.config.VERTICAL_EXTENSION_DOWN + self.config.CIRCLE_OFFSET),
                              self.config.CIRCLE_RADIUS,
                              fill=False, color='black',
                                lw=self.config.LINEWIDTH)
            ax.add_artist(circle)
        
        # Draw diamond edges with gaps and bridges
        self._render_diamond_edges(ax, "upper")
        self._render_diamond_edges(ax, "lower")
        
        return ax
    
    def _render_diamond_edges(self, ax: plt.Axes, position: str):
        """Helper method to render diamond edges for upper or lower section"""
        config = self.config
        y_offset = config.LOWER_GAP if position == "lower" else config.UPPER_GAP
        base_y = config.FRACTION_Y - y_offset if position == "lower" else config.FRACTION_Y + y_offset
        
        # Calculate diamond points
        left_top = (config.LEFT_X, 
                   config.HALF_EXTENSION_UP if position == "upper" 
                   else config.HALF_EXTENSION_DOWN)
        center_top = (config.CENTER_X,
                     config.VERTICAL_EXTENSION_UP if position == "upper"
                     else config.VERTICAL_EXTENSION_DOWN)
        right_ref = (config.RIGHT_X,
                    config.HALF_EXTENSION_UP if position == "upper"
                    else config.HALF_EXTENSION_DOWN)
        
        prefix = "UPPER_" if position == "upper" else "LOWER_"
        components = GlyphComponents
        
        if position == "upper":
            # Handle upper diamond edges
            if self.active_components[getattr(components, f"{prefix}DIAMOND_LOWER_LEFT")]:
                ax.plot([left_top[0], center_top[0]], [left_top[1], base_y], 'k-', linewidth=self.config.LINEWIDTH)
                # Add center bridge line
                # ax = self.draw_center_bridge_line(ax)
                
            if self.active_components[getattr(components, f"{prefix}DIAMOND_UPPER_LEFT")]:
                ax.plot([left_top[0], center_top[0]], [left_top[1], center_top[1]], 'k-', linewidth=self.config.LINEWIDTH)
                
            if self.active_components[getattr(components, f"{prefix}DIAMOND_UPPER_RIGHT")]:
                ax.plot([center_top[0], right_ref[0]], [center_top[1], right_ref[1]], 'k-', linewidth=self.config.LINEWIDTH)
                
            if self.active_components[getattr(components, f"{prefix}DIAMOND_LOWER_RIGHT")]:
                ax.plot([center_top[0], right_ref[0]], [base_y, right_ref[1]], 'k-', linewidth=self.config.LINEWIDTH)
                if self.active_components[getattr(components, "LOWER_CENTER_VERTICAL")]:
                    ax = self.draw_center_bridge_line(ax)
        else:
            # Handle lower diamond edges (unchanged)
            if self.active_components[getattr(components, f"{prefix}DIAMOND_LOWER_LEFT")]:
                ax.plot([left_top[0], center_top[0]], [left_top[1], center_top[1]], 'k-', linewidth=self.config.LINEWIDTH)
                
            if self.active_components[getattr(components, f"{prefix}DIAMOND_UPPER_LEFT")]:
                ax.plot([left_top[0], center_top[0]], [left_top[1], base_y], 'k-', linewidth=self.config.LINEWIDTH)
                
            if self.active_components[getattr(components, f"{prefix}DIAMOND_UPPER_RIGHT")]:
                ax.plot([center_top[0], right_ref[0]], [base_y, right_ref[1]], 'k-', linewidth=self.config.LINEWIDTH)
                
            if self.active_components[getattr(components, f"{prefix}DIAMOND_LOWER_RIGHT")]:
                ax.plot([center_top[0], right_ref[0]], [center_top[1], right_ref[1]], 'k-', linewidth=self.config.LINEWIDTH)

    def draw_center_bridge_line_at_position(self, ax: plt.Axes, x_offset: float) -> plt.Axes:
        ax.plot([x_offset + self.config.CENTER_X, x_offset + self.config.CENTER_X],
                [self.config.FRACTION_Y, 
                self.config.FRACTION_Y + self.config.BRIDGE_LENGTH],
                'k-', linewidth=self.config.LINEWIDTH)
        return ax
    
    def draw_left_bridge_line_at_position(self, ax: plt.Axes, x_offset: float) -> plt.Axes:
        ax.plot([x_offset + self.config.LEFT_X, x_offset + self.config.LEFT_X],
                [self.config.FRACTION_Y, 
                self.config.FRACTION_Y + self.config.BRIDGE_LENGTH],
                'k-', linewidth=self.config.LINEWIDTH)
        return ax


    def render_at_position(self, ax: plt.Axes, position: int) -> None:
        """Render this glyph at a specific position in a chain"""
        config = self.config
        x_offset = position * (config.GLYPH_WIDTH + config.GLYPH_SPACING)
        
        # Draw upper components with gap
        if self.active_components[GlyphComponents.UPPER_LEFT_VERTICAL]:
            # Draw the main vertical line starting from above the gap
            ax.plot([x_offset + config.LEFT_X, x_offset + config.LEFT_X],
                   [config.FRACTION_Y + config.UPPER_GAP, 
                    config.HALF_EXTENSION_UP],
                   'k-', linewidth=self.config.LINEWIDTH)
            # Draw left bridge line
            ax = self.draw_left_bridge_line_at_position(ax, x_offset)
            
        if self.active_components[GlyphComponents.UPPER_CENTER_VERTICAL]:
            # Draw the main vertical line starting from above the gap
            ax.plot([x_offset + config.CENTER_X, x_offset + config.CENTER_X],
                   [config.FRACTION_Y + config.UPPER_GAP, 
                    config.VERTICAL_EXTENSION_UP],
                   'k-', linewidth=self.config.LINEWIDTH)
            # Draw center bridge line
            ax = self.draw_center_bridge_line_at_position(ax, x_offset)
        
        # Draw lower components with gap
        if self.active_components[GlyphComponents.LOWER_LEFT_VERTICAL]:
            ax.plot([x_offset + config.LEFT_X, x_offset + config.LEFT_X],
                   [config.FRACTION_Y - config.LOWER_GAP, 
                    config.HALF_EXTENSION_DOWN],
                   'k-', linewidth=self.config.LINEWIDTH)
            
        if self.active_components[GlyphComponents.LOWER_CENTER_VERTICAL]:
            ax.plot([x_offset + config.CENTER_X, x_offset + config.CENTER_X],
                   [config.FRACTION_Y - config.LOWER_GAP, 
                    config.VERTICAL_EXTENSION_DOWN],
                   'k-', linewidth=self.config.LINEWIDTH)
            
        # Draw circle if present
        if self.active_components[GlyphComponents.LOWER_CIRCLE]:
            circle = plt.Circle((x_offset + config.CENTER_X, 
                               config.VERTICAL_EXTENSION_DOWN + config.CIRCLE_OFFSET),
                              config.CIRCLE_RADIUS,
                              fill=False, color='black',
                                lw=self.config.LINEWIDTH)
            ax.add_artist(circle)
        
        # Draw diamond edges with offset
        self._render_diamond_edges_at_position(ax, "upper", x_offset)
        self._render_diamond_edges_at_position(ax, "lower", x_offset)

    def _render_diamond_edges_at_position(self, ax: plt.Axes, position: str, x_offset: float):
        """Helper method to render diamond edges for upper or lower section at a specific position"""
        config = self.config
        y_offset = config.LOWER_GAP if position == "lower" else config.UPPER_GAP
        base_y = config.FRACTION_Y - y_offset if position == "lower" else config.FRACTION_Y + y_offset
        
        # Calculate diamond points with x_offset
        if position == "upper":
            left_top = (x_offset + config.LEFT_X, config.HALF_EXTENSION_UP)
            center_top = (x_offset + config.CENTER_X, config.VERTICAL_EXTENSION_UP)
            right_ref = (x_offset + config.RIGHT_X, config.HALF_EXTENSION_UP)
        else:
            left_top = (x_offset + config.LEFT_X, config.HALF_EXTENSION_DOWN)
            center_top = (x_offset + config.CENTER_X, config.VERTICAL_EXTENSION_DOWN)
            right_ref = (x_offset + config.RIGHT_X, config.HALF_EXTENSION_DOWN)
        
        prefix = "UPPER_" if position == "upper" else "LOWER_"
        components = GlyphComponents
        
        if position == "upper":
            # Handle upper diamond edges
            if self.active_components[getattr(components, f"{prefix}DIAMOND_LOWER_LEFT")]:
                ax.plot([left_top[0], center_top[0]], [left_top[1], base_y], 'k-', linewidth=self.config.LINEWIDTH)
                # Add center bridge line
                # ax = self.draw_center_bridge_line_at_position(ax, x_offset)
                
            if self.active_components[getattr(components, f"{prefix}DIAMOND_UPPER_LEFT")]:
                ax.plot([left_top[0], center_top[0]], [left_top[1], center_top[1]], 'k-', linewidth=self.config.LINEWIDTH)
                
            if self.active_components[getattr(components, f"{prefix}DIAMOND_UPPER_RIGHT")]:
                ax.plot([center_top[0], right_ref[0]], [center_top[1], right_ref[1]], 'k-', linewidth=self.config.LINEWIDTH)
                
            if self.active_components[getattr(components, f"{prefix}DIAMOND_LOWER_RIGHT")]:
                ax.plot([center_top[0], right_ref[0]], [base_y, right_ref[1]], 'k-', linewidth=self.config.LINEWIDTH)
                # Add center bridge line
                # ax = self.draw_center_bridge_line_at_position(ax, x_offset)
                # this rule is weird: we only draw this when there is also a lower center vertical
                if self.active_components[getattr(components, "LOWER_CENTER_VERTICAL")]:
                    ax = self.draw_center_bridge_line_at_position(ax, x_offset)
        else:
            # Handle lower diamond edges (unchanged)
            if self.active_components[getattr(components, f"{prefix}DIAMOND_LOWER_LEFT")]:
                ax.plot([left_top[0], center_top[0]], [left_top[1], center_top[1]], 'k-', linewidth=self.config.LINEWIDTH)
                
            if self.active_components[getattr(components, f"{prefix}DIAMOND_UPPER_LEFT")]:
                ax.plot([left_top[0], center_top[0]], [left_top[1], base_y], 'k-', linewidth=self.config.LINEWIDTH)
                
            if self.active_components[getattr(components, f"{prefix}DIAMOND_UPPER_RIGHT")]:
                ax.plot([center_top[0], right_ref[0]], [base_y, right_ref[1]], 'k-', linewidth=self.config.LINEWIDTH)
                
            if self.active_components[getattr(components, f"{prefix}DIAMOND_LOWER_RIGHT")]:
                ax.plot([center_top[0], right_ref[0]], [center_top[1], right_ref[1]], 'k-', linewidth=self.config.LINEWIDTH)

class SymbolChain:
    """Class to handle chains of symbols"""
    def __init__(self, glyphs: Sequence[SymbolGlyph]):
        self.glyphs = glyphs
        self.config = SymbolConfig()  # Use same config for consistency
    
    def render(self, ax: Optional[plt.Axes] = None) -> plt.Axes:
        """Render the entire chain of symbols"""
        if ax is None:
            width = len(self.glyphs) * (self.config.GLYPH_WIDTH + self.config.GLYPH_SPACING)
            _, ax = plt.subplots(figsize=(width * 4, 6))
        
        # Set up the plot
        ax.set_xlim(-0.2, len(self.glyphs) * (self.config.GLYPH_WIDTH + self.config.GLYPH_SPACING) + 0.2)
        ax.set_ylim(self.config.VERTICAL_EXTENSION_DOWN - 0.2, 
                    self.config.VERTICAL_EXTENSION_UP + 0.2)
        ax.axis('off')
        
        # Draw the continuous fraction line
        ax.axhline(y=self.config.FRACTION_Y, color='black', linewidth=self.config.LINEWIDTH,
                  xmin=0, xmax=len(self.glyphs))
        
        # Render each glyph
        for i, glyph in enumerate(self.glyphs):
            glyph.render_at_position(ax, i)
        
        return ax