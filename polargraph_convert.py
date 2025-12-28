#!/usr/bin/env python3
"""
Polargraph PNG to SVG Converter

Converts an image to a Polargraph-optimized SVG format with horizontal paths
that modulate based on pixel darkness. Designed for pen plotter G-code conversion.
"""

import argparse
import math
import sys
from pathlib import Path
from typing import List, Tuple

try:
    from PIL import Image, ImageEnhance, ImageOps
except ImportError:
    print("Error: Pillow library is required. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)


class PolargraphConverter:
    """Convert images to Polargraph SVG format with modulated horizontal paths."""
    
    # Wave modulation constants
    MIN_DARKNESS_THRESHOLD = 0.02  # Pixels below this darkness are considered white
    FREQUENCY_BASE = 0.5  # Base frequency multiplier
    FREQUENCY_SCALE = 1.5  # Additional frequency range based on darkness
    
    # Organic mode constants
    ORGANIC_X_FREQUENCY = 0.05  # X-axis variation frequency
    ORGANIC_Y_FREQUENCY = 0.1   # Y-axis (row) variation frequency
    ORGANIC_NOISE_SCALE = 0.2   # Scale of organic noise
    ORGANIC_AMPLITUDE_VAR = 0.3  # How much organic noise affects amplitude
    ORGANIC_FREQUENCY_VAR = 0.2  # How much organic noise affects frequency
    
    # Wave calculation constant
    WAVE_FREQUENCY_SCALE = 0.1  # Controls overall wave frequency
    
    def __init__(
        self,
        line_spacing: float = 2.0,
        max_amplitude: float = 3.0,
        organic_mode: bool = False,
        contrast_factor: float = 2.0,
        white_threshold: int = 250
    ):
        """
        Initialize the converter.
        
        Args:
            line_spacing: Vertical spacing between horizontal lines (in pixels)
            max_amplitude: Maximum wave amplitude for dark pixels
            organic_mode: If True, adds subtle organic variation to paths
            contrast_factor: Factor for contrast enhancement (higher = more contrast)
            white_threshold: Pixels brighter than this (0-255) are considered white and ignored
        """
        self.line_spacing = line_spacing
        self.max_amplitude = max_amplitude
        self.organic_mode = organic_mode
        self.contrast_factor = contrast_factor
        self.white_threshold = white_threshold
    
    def load_and_preprocess_image(self, image_path: str) -> Image.Image:
        """
        Load image and convert to high-contrast grayscale.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Preprocessed grayscale PIL Image
        """
        # Load image
        img = Image.open(image_path)
        
        # Convert to grayscale
        img = ImageOps.grayscale(img)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(self.contrast_factor)
        
        return img
    
    def calculate_wave_params(self, darkness: float, x: int, row: int) -> Tuple[float, float]:
        """
        Calculate amplitude and frequency based on pixel darkness.
        
        Args:
            darkness: Pixel darkness value (0.0 = white, 1.0 = black)
            x: X coordinate (for organic variation)
            row: Row number (for organic variation)
            
        Returns:
            Tuple of (amplitude, frequency_factor)
        """
        if darkness < self.MIN_DARKNESS_THRESHOLD:  # Nearly white, skip
            return 0.0, 0.0
        
        # Amplitude scales with darkness
        amplitude = self.max_amplitude * darkness
        
        # Frequency increases with darkness (darker = more wavy)
        # Base frequency: more cycles per unit length for darker areas
        frequency_factor = self.FREQUENCY_BASE + (darkness * self.FREQUENCY_SCALE)
        
        # Add organic variation if enabled
        if self.organic_mode:
            # Subtle organic noise based on position
            organic_noise = math.sin(x * self.ORGANIC_X_FREQUENCY + row * self.ORGANIC_Y_FREQUENCY) * self.ORGANIC_NOISE_SCALE
            amplitude *= (1.0 + organic_noise * self.ORGANIC_AMPLITUDE_VAR)
            frequency_factor *= (1.0 + organic_noise * self.ORGANIC_FREQUENCY_VAR)
        
        return amplitude, frequency_factor
    
    def generate_row_path(self, img: Image.Image, row: int, width: int) -> List[str]:
        """
        Generate SVG path points for a single horizontal row.
        
        Args:
            img: Preprocessed grayscale image
            row: Row number (y-coordinate)
            width: Image width
            
        Returns:
            List of SVG path commands (empty if row should be skipped)
        """
        pixels = img.load()
        y_base = row * self.line_spacing
        
        # Collect points for this row
        points = []
        
        for x in range(width):
            # Get pixel brightness (0-255)
            brightness = pixels[x, row]
            
            # Skip if too bright (white)
            if brightness >= self.white_threshold:
                # Add straight line point (no wave)
                if len(points) == 0 or points[-1][1] != y_base:
                    points.append((x, y_base))
                continue
            
            # Calculate darkness (0.0 = white, 1.0 = black)
            darkness = 1.0 - (brightness / 255.0)
            
            # Get wave parameters
            amplitude, frequency_factor = self.calculate_wave_params(darkness, x, row)
            
            # Calculate y-offset using sine wave
            # Frequency based on darkness and position
            wave_offset = amplitude * math.sin(x * frequency_factor * self.WAVE_FREQUENCY_SCALE)
            
            y = y_base + wave_offset
            points.append((x, y))
        
        return points
    
    def points_to_path_commands(self, points: List[Tuple[float, float]]) -> str:
        """
        Convert points to SVG path commands.
        
        Args:
            points: List of (x, y) coordinate tuples
            
        Returns:
            SVG path 'd' attribute string
        """
        if not points:
            return ""
        
        # Start with Move command
        commands = [f"M {points[0][0]:.2f},{points[0][1]:.2f}"]
        
        # Add Line commands for remaining points
        for x, y in points[1:]:
            commands.append(f"L {x:.2f},{y:.2f}")
        
        return " ".join(commands)
    
    def generate_svg(self, img: Image.Image, output_path: str):
        """
        Generate complete SVG file from preprocessed image.
        
        Args:
            img: Preprocessed grayscale image
            output_path: Path where SVG file should be saved
        """
        width, height = img.size
        
        # Calculate SVG dimensions
        svg_height = height * self.line_spacing
        
        # Start SVG document
        svg_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width}" height="{svg_height:.2f}" '
            f'viewBox="0 0 {width} {svg_height:.2f}">',
            '  <g id="polargraph-paths" '
            'stroke="black" stroke-width="0.5" fill="none" '
            'stroke-linecap="round" stroke-linejoin="round">',
        ]
        
        # Generate paths for each row
        for row in range(height):
            points = self.generate_row_path(img, row, width)
            
            if points:
                path_d = self.points_to_path_commands(points)
                if path_d:
                    svg_lines.append(f'    <path d="{path_d}"/>')
        
        # Close SVG
        svg_lines.extend([
            '  </g>',
            '</svg>'
        ])
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg_lines))
    
    def convert(self, input_path: str, output_path: str):
        """
        Main conversion method.
        
        Args:
            input_path: Path to input image
            output_path: Path for output SVG file
        """
        print(f"Loading image: {input_path}")
        img = self.load_and_preprocess_image(input_path)
        
        print(f"Image size: {img.size[0]}x{img.size[1]} pixels")
        print(f"Parameters:")
        print(f"  - Line spacing: {self.line_spacing}")
        print(f"  - Max amplitude: {self.max_amplitude}")
        print(f"  - Organic mode: {self.organic_mode}")
        print(f"  - Contrast factor: {self.contrast_factor}")
        
        print("Generating SVG paths...")
        self.generate_svg(img, output_path)
        
        print(f"SVG saved to: {output_path}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert images to Polargraph-optimized SVG format for pen plotters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.png output.svg
  %(prog)s input.jpg output.svg --line-spacing 3 --amplitude 5
  %(prog)s photo.png drawing.svg --organic --contrast 2.5
        """
    )
    
    parser.add_argument(
        'input',
        type=str,
        help='Input image file path (PNG, JPG, etc.)'
    )
    
    parser.add_argument(
        'output',
        type=str,
        help='Output SVG file path'
    )
    
    parser.add_argument(
        '--line-spacing',
        type=float,
        default=2.0,
        metavar='FLOAT',
        help='Vertical spacing between horizontal lines in pixels (default: 2.0)'
    )
    
    parser.add_argument(
        '--amplitude',
        type=float,
        default=3.0,
        metavar='FLOAT',
        help='Maximum wave amplitude for darkest pixels (default: 3.0)'
    )
    
    parser.add_argument(
        '--organic',
        action='store_true',
        help='Enable organic mode for natural variation in paths'
    )
    
    parser.add_argument(
        '--contrast',
        type=float,
        default=2.0,
        metavar='FLOAT',
        help='Contrast enhancement factor (default: 2.0, higher = more contrast)'
    )
    
    parser.add_argument(
        '--white-threshold',
        type=int,
        default=250,
        metavar='INT',
        help='Brightness threshold for white pixels 0-255 (default: 250)'
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    # Create converter and run
    converter = PolargraphConverter(
        line_spacing=args.line_spacing,
        max_amplitude=args.amplitude,
        organic_mode=args.organic,
        contrast_factor=args.contrast,
        white_threshold=args.white_threshold
    )
    
    try:
        converter.convert(args.input, args.output)
    except Exception as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
