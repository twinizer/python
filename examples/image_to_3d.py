#!/usr/bin/env python3
"""
Example script demonstrating image to 3D model conversion.

This example shows how to use the ImageTo3DConverter class to convert
an image to various 3D representations like height maps, normal maps,
3D meshes, and point clouds.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import twinizer
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from twinizer.converters.image.image_to_3d import ImageTo3DConverter


def main():
    """Run the example."""
    parser = argparse.ArgumentParser(description="Convert an image to 3D representations")
    parser.add_argument("image_path", help="Path to the input image")
    parser.add_argument("--output-dir", help="Output directory")
    parser.add_argument("--scale-z", type=float, default=0.1, help="Scale factor for height values")
    parser.add_argument("--invert", action="store_true", help="Invert height values")
    parser.add_argument("--blur", type=float, default=1.0, help="Blur sigma (0 for no blur)")
    parser.add_argument("--format", choices=["obj", "stl", "ply"], default="obj", 
                       help="Output format for 3D models")
    
    args = parser.parse_args()
    
    # Check if the image exists
    if not os.path.exists(args.image_path):
        print(f"Error: Image not found: {args.image_path}")
        return 1
    
    try:
        # Create converter
        converter = ImageTo3DConverter(output_dir=args.output_dir)
        
        # Get the base name of the image
        base_name = os.path.basename(args.image_path)
        name_without_ext = os.path.splitext(base_name)[0]
        
        # Create height map
        print(f"\nGenerating height map from {args.image_path}...")
        heightmap_path = converter.image_to_heightmap(
            image_path=args.image_path,
            invert=args.invert,
            blur_sigma=args.blur,
            scale_factor=1.0
        )
        print(f"Height map saved to: {heightmap_path}")
        
        # Create normal map
        print(f"\nGenerating normal map from {args.image_path}...")
        normalmap_path = converter.image_to_normalmap(
            image_path=args.image_path,
            strength=1.0
        )
        print(f"Normal map saved to: {normalmap_path}")
        
        # Create 3D mesh
        print(f"\nGenerating 3D mesh from {args.image_path}...")
        mesh_path = converter.image_to_mesh(
            image_path=args.image_path,
            scale_z=args.scale_z,
            invert=args.invert,
            blur_sigma=args.blur,
            smooth=True,
            simplify=False,
            output_format=args.format
        )
        print(f"3D mesh saved to: {mesh_path}")
        
        # Create point cloud
        print(f"\nGenerating point cloud from {args.image_path}...")
        pointcloud_path = converter.image_to_point_cloud(
            image_path=args.image_path,
            scale_z=args.scale_z,
            sample_ratio=0.1,
            output_format="ply"
        )
        print(f"Point cloud saved to: {pointcloud_path}")
        
        print("\nAll conversions completed successfully!")
        return 0
    
    except ImportError as e:
        print(f"Error: Missing dependencies: {e}")
        print("Please install the required dependencies:")
        print("  pip install trimesh scikit-image matplotlib")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
