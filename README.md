# Polargraph PNG to SVG Converter

Convert images to Polargraph-optimized SVG format with horizontal paths that modulate based on pixel darkness. Designed specifically for pen plotter G-code conversion.

## Features

- **High-contrast grayscale conversion**: Automatically enhances contrast for better plotting results
- **Horizontal SVG paths**: Generates clean, connected paths row by row
- **Darkness-based modulation**: Amplitude and frequency vary based on pixel darkness
- **White pixel handling**: Ignores white pixels to avoid unnecessary pen movements
- **Organic mode**: Optional natural variation in paths for artistic effects
- **Plotter-optimized**: Clean polyline/path elements without overlaps, ready for G-code conversion
- **Configurable parameters**: Adjust line spacing, amplitude, and contrast to suit your needs

## Installation

1. Clone this repository:
```bash
git clone https://github.com/morebrackets/polargraph-png2.git
cd polargraph-png2
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python polargraph_convert.py input.png output.svg
```

### Advanced Options

```bash
python polargraph_convert.py input.jpg output.svg \
  --line-spacing 3.0 \
  --amplitude 5.0 \
  --organic \
  --contrast 2.5
```

### Command-Line Arguments

- `input`: Input image file path (required)
- `output`: Output SVG file path (required)
- `--line-spacing FLOAT`: Vertical spacing between horizontal lines in pixels (default: 2.0)
- `--amplitude FLOAT`: Maximum wave amplitude for darkest pixels (default: 3.0)
- `--organic`: Enable organic mode for natural variation in paths
- `--contrast FLOAT`: Contrast enhancement factor (default: 2.0, higher = more contrast)
- `--white-threshold INT`: Brightness threshold for white pixels 0-255 (default: 250)

### Examples

**Simple conversion with defaults:**
```bash
python polargraph_convert.py photo.png drawing.svg
```

**Tighter lines for detailed images:**
```bash
python polargraph_convert.py detailed.png output.svg --line-spacing 1.5
```

**More dramatic wave effects:**
```bash
python polargraph_convert.py portrait.jpg output.svg --amplitude 6.0
```

**Organic, natural-looking output:**
```bash
python polargraph_convert.py landscape.png output.svg --organic --amplitude 4.0
```

**High contrast for bold lines:**
```bash
python polargraph_convert.py sketch.png output.svg --contrast 3.0
```

## Quick Demo

Try the example script to see the converter in action:

```bash
python example.py
```

This will create several example conversions with different settings, demonstrating the various features and parameters.

## How It Works

1. **Image Preprocessing**: The input image is converted to grayscale and contrast-enhanced
2. **Row Processing**: Each horizontal row is processed independently
3. **Darkness Calculation**: For each pixel, darkness is calculated (0.0 = white, 1.0 = black)
4. **Wave Modulation**: 
   - Darker pixels create higher amplitude waves
   - Darker pixels also increase wave frequency for more texture
   - White pixels (above threshold) are ignored
5. **SVG Generation**: Points are connected into clean SVG path elements optimized for plotters

## Output Format

The generated SVG contains:
- Clean, connected `<path>` elements (one per row)
- Stroke properties optimized for pen plotting
- No overlapping paths
- Precise coordinates suitable for G-code conversion

## Tips for Best Results

- **Start with high-resolution images**: More pixels = more detail
- **Experiment with line spacing**: Smaller values = denser output, but longer plotting time
- **Adjust amplitude**: Higher values = more dramatic wave effects
- **Use contrast enhancement**: Higher contrast values emphasize dark/light differences
- **Try organic mode**: Adds natural variation, great for artistic pieces

## License

MIT License - see LICENSE file for details