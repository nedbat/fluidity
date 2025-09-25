#!/usr/bin/env python3
"""
SVG Frame Animator - Combine multiple SVG files into one animated SVG
"""

import os
import re
import argparse
from pathlib import Path
from xml.etree import ElementTree as ET


def extract_svg_content(svg_file):
    """Extract the inner content of an SVG file, removing the outer <svg> tag."""
    try:
        tree = ET.parse(svg_file)
        root = tree.getroot()

        # Get dimensions from the first SVG for the final output
        width = root.get("width", "100")
        height = root.get("height", "100")
        viewbox = root.get("viewBox", f"0 0 {width} {height}")

        # Convert the root element's children to string
        content = ""
        for child in root:
            content += ET.tostring(child, encoding="unicode")

        return content, width, height, viewbox
    except ET.ParseError as e:
        print(f"Error parsing {svg_file}: {e}")
        return None, None, None, None


def create_animated_svg(svg_files, output_file, duration=0.1, iterations="infinite"):
    """
    Create an animated SVG from multiple frame files.

    Args:
        svg_files: List of SVG file paths in frame order
        output_file: Output animated SVG file path
        duration: Duration per frame in seconds
        iterations: Number of iterations ('infinite' or integer)
    """

    if not svg_files:
        print("No SVG files provided")
        return False

    frames = []
    width, height, viewbox = None, None, None

    # Extract content from each SVG file
    for i, svg_file in enumerate(svg_files):
        content, w, h, vb = extract_svg_content(svg_file)
        if content is None:
            continue

        # Use dimensions from first valid file
        if width is None:
            width, height, viewbox = w, h, vb

        frames.append({"id": f"frame{i}", "content": content})

    if not frames:
        print("No valid SVG files found")
        return False

    # Calculate animation timing
    total_duration = len(frames) * duration
    frame_percentage = 100 / len(frames)

    # Generate CSS animation
    css_keyframes = "@keyframes svgAnimation {\n"

    for i, frame in enumerate(frames):
        start_pct = i * frame_percentage
        end_pct = start_pct + frame_percentage

        if i < len(frames) - 1:
            css_keyframes += f"  {start_pct:.1f}%, {end_pct:.1f}% {{ opacity: {'1' if i == 0 else '0'}; }}\n"
        else:  # Last frame
            css_keyframes += f"  {start_pct:.1f}%, 100% {{ opacity: 0; }}\n"

    css_keyframes += "}\n\n"

    # Create frame-specific animations
    frame_animations = ""
    for i, frame in enumerate(frames):
        visibility_keyframes = f"@keyframes showFrame{i} {{\n"

        for j in range(len(frames)):
            pct = j * frame_percentage
            opacity = "1" if j == i else "0"
            visibility_keyframes += f"  {pct:.1f}% {{ opacity: {opacity}; }}\n"

        visibility_keyframes += "}\n\n"
        frame_animations += visibility_keyframes

    # Generate the final SVG
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" viewBox="{viewbox}" 
     xmlns="http://www.w3.org/2000/svg">
<defs>
  <style type="text/css"><![CDATA[
{frame_animations}
  ]]></style>
</defs>
'''

    # Add each frame as a group
    for i, frame in enumerate(frames):
        animation_style = (
            f"animation: showFrame{i} {total_duration}s {iterations} steps(1, end);"
        )
        svg_content += (
            f'  <g id="{frame["id"]}" style="opacity:0; {animation_style}">\n'
        )
        svg_content += f"    {frame['content']}\n"
        svg_content += "  </g>\n"

    svg_content += "</svg>"

    # Write to output file
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"Animated SVG created: {output_file}")
        return True
    except IOError as e:
        print(f"Error writing output file: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Create animated SVG from frame files")
    parser.add_argument("files", nargs="+", help="Input SVG files (in frame order)")
    parser.add_argument(
        "-o",
        "--output",
        default="animation.svg",
        help="Output file (default: animation.svg)",
    )
    parser.add_argument(
        "-d",
        "--duration",
        type=float,
        default=0.1,
        help="Duration per frame in seconds (default: 0.1)",
    )
    parser.add_argument(
        "-i",
        "--iterations",
        default="infinite",
        help="Animation iterations (default: infinite)",
    )

    args = parser.parse_args()

    # Validate input files
    svg_files = []
    for file_path in args.files:
        if os.path.exists(file_path) and file_path.lower().endswith(".svg"):
            svg_files.append(file_path)
        else:
            print(f"Warning: File not found or not an SVG: {file_path}")

    if not svg_files:
        print("No valid SVG files found")
        return 1

    # Sort files naturally (frame1.svg, frame2.svg, etc.)
    svg_files.sort(
        key=lambda x: [
            int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", x)
        ]
    )

    print(f"Processing {len(svg_files)} frames...")
    for f in svg_files:
        print(f"  {f}")

    success = create_animated_svg(
        svg_files, args.output, args.duration, args.iterations
    )
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
