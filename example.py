#!/usr/bin/env python3
"""
Example script demonstrating the Polargraph converter with a generated test image.
This creates a simple gradient and geometric shapes to show how the converter works.
"""

from PIL import Image, ImageDraw
import subprocess
import sys

def create_example_image(filename='example_input.png', size=(300, 200)):
    """Create an example image with gradients and shapes."""
    img = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(img)
    
    # Create a circular gradient in the center
    center_x, center_y = size[0] // 3, size[1] // 2
    for i in range(60, 0, -1):
        gray = int(255 - (i * 4))
        draw.ellipse(
            [center_x - i, center_y - i, center_x + i, center_y + i],
            fill=(gray, gray, gray)
        )
    
    # Add some geometric shapes
    # Rectangle with gradient
    for i in range(50):
        gray = int(50 + i * 2)
        draw.rectangle(
            [size[0] * 2 // 3, 50 + i, size[0] * 2 // 3 + 80, 51 + i],
            fill=(gray, gray, gray)
        )
    
    # Add some diagonal lines
    for i in range(0, size[1], 10):
        gray = int(100 + (i / size[1]) * 100)
        draw.line([0, i, size[0] // 4, size[1]], fill=(gray, gray, gray), width=2)
    
    img.save(filename)
    print(f"Created example image: {filename}")
    return filename

def run_converter(input_file, output_file, extra_args=None):
    """Run the polargraph converter."""
    cmd = [sys.executable, 'polargraph_convert.py', input_file, output_file]
    if extra_args:
        cmd.extend(extra_args)
    
    print(f"\nRunning: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return False
    return True

def main():
    """Run examples with different settings."""
    print("=" * 60)
    print("Polargraph Converter - Example Script")
    print("=" * 60)
    
    # Create example image
    input_file = create_example_image()
    
    # Example 1: Default settings
    print("\n" + "=" * 60)
    print("Example 1: Default settings")
    print("=" * 60)
    run_converter(input_file, 'example_default.svg')
    
    # Example 2: Tight spacing for detail
    print("\n" + "=" * 60)
    print("Example 2: Tight line spacing for more detail")
    print("=" * 60)
    run_converter(input_file, 'example_detailed.svg', ['--line-spacing', '1.5'])
    
    # Example 3: Organic mode with high amplitude
    print("\n" + "=" * 60)
    print("Example 3: Organic mode with high amplitude")
    print("=" * 60)
    run_converter(input_file, 'example_organic.svg', [
        '--organic',
        '--amplitude', '6.0',
        '--line-spacing', '2.5'
    ])
    
    # Example 4: High contrast
    print("\n" + "=" * 60)
    print("Example 4: Very high contrast")
    print("=" * 60)
    run_converter(input_file, 'example_highcontrast.svg', [
        '--contrast', '3.5',
        '--amplitude', '4.0'
    ])
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  - example_input.png (test image)")
    print("  - example_default.svg")
    print("  - example_detailed.svg")
    print("  - example_organic.svg")
    print("  - example_highcontrast.svg")
    print("\nOpen the SVG files in a viewer or editor to see the results!")

if __name__ == '__main__':
    main()
