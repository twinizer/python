"""
Image to 3D model converter module.

This module provides functionality to convert images to 3D models,
including height maps, normal maps, and 3D meshes.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Optional imports for 3D processing
try:
    import trimesh

    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False

try:
    from skimage import color, filters, morphology

    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False

console = Console()


class ImageTo3DConverter:
    """
    Converter for transforming images to 3D models.
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the image to 3D converter.

        Args:
            output_dir: Directory to save output files
        """
        self.output_dir = output_dir or os.getcwd()

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        # Check for required libraries
        self._check_dependencies()

    def _check_dependencies(self) -> None:
        """Check if required dependencies are available."""
        missing_deps = []

        if not TRIMESH_AVAILABLE:
            missing_deps.append("trimesh")

        if not SKIMAGE_AVAILABLE:
            missing_deps.append("scikit-image")

        if missing_deps:
            console.print(
                f"[yellow]Warning: Some dependencies are missing: {', '.join(missing_deps)}[/yellow]"
            )
            console.print(
                "[yellow]Install them with: pip install "
                + " ".join(missing_deps)
                + "[/yellow]"
            )

    def image_to_heightmap(
        self,
        image_path: str,
        invert: bool = False,
        blur_sigma: float = 1.0,
        scale_factor: float = 1.0,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Convert an image to a height map.

        Args:
            image_path: Path to the input image
            invert: Whether to invert the height map
            blur_sigma: Sigma value for Gaussian blur
            scale_factor: Scale factor for height values
            output_path: Path to save the height map (optional)

        Returns:
            Path to the saved height map
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Load image
        img = Image.open(image_path)

        # Convert to grayscale if needed
        if img.mode != "L":
            img = img.convert("L")

        # Convert to numpy array
        height_map = np.array(img).astype(np.float32) / 255.0

        # Invert if requested
        if invert:
            height_map = 1.0 - height_map

        # Apply Gaussian blur if requested
        if blur_sigma > 0 and SKIMAGE_AVAILABLE:
            height_map = filters.gaussian(height_map, sigma=blur_sigma)

        # Apply scale factor
        height_map *= scale_factor

        # Create output path if not provided
        if output_path is None:
            base_name = os.path.basename(image_path)
            output_name = f"{os.path.splitext(base_name)[0]}_heightmap.png"
            output_path = os.path.join(self.output_dir, output_name)

        # Save height map as image
        plt.imsave(output_path, height_map, cmap="gray")

        console.print(f"[green]Height map saved to: {output_path}[/green]")
        return output_path

    def image_to_normalmap(
        self, image_path: str, strength: float = 1.0, output_path: Optional[str] = None
    ) -> str:
        """
        Convert an image (or height map) to a normal map.

        Args:
            image_path: Path to the input image
            strength: Strength of the normal map effect
            output_path: Path to save the normal map (optional)

        Returns:
            Path to the saved normal map
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        if not SKIMAGE_AVAILABLE:
            raise ImportError("scikit-image is required for normal map generation")

        # Load image
        img = Image.open(image_path)

        # Convert to grayscale if needed
        if img.mode != "L":
            img = img.convert("L")

        # Convert to numpy array
        height_map = np.array(img).astype(np.float32) / 255.0

        # Calculate gradients
        dy, dx = np.gradient(height_map)

        # Apply strength factor
        dx *= strength
        dy *= strength

        # Create normal map
        normal_map = np.zeros(
            (height_map.shape[0], height_map.shape[1], 3), dtype=np.float32
        )
        normal_map[..., 0] = -dx
        normal_map[..., 1] = -dy
        normal_map[..., 2] = 1.0

        # Normalize
        norm = np.sqrt(np.sum(normal_map**2, axis=2, keepdims=True))
        normal_map = normal_map / (norm + 1e-10)

        # Convert to 0-1 range
        normal_map = (normal_map + 1.0) / 2.0

        # Create output path if not provided
        if output_path is None:
            base_name = os.path.basename(image_path)
            output_name = f"{os.path.splitext(base_name)[0]}_normalmap.png"
            output_path = os.path.join(self.output_dir, output_name)

        # Save normal map as image
        plt.imsave(output_path, normal_map)

        console.print(f"[green]Normal map saved to: {output_path}[/green]")
        return output_path

    def heightmap_to_mesh(
        self,
        heightmap_path: str,
        scale_z: float = 0.1,
        smooth: bool = True,
        simplify: bool = False,
        output_format: str = "obj",
        output_path: Optional[str] = None,
    ) -> str:
        """
        Convert a height map to a 3D mesh.

        Args:
            heightmap_path: Path to the height map image
            scale_z: Scale factor for height values
            smooth: Whether to smooth the mesh
            simplify: Whether to simplify the mesh
            output_format: Output format ('obj', 'stl', or 'ply')
            output_path: Path to save the mesh (optional)

        Returns:
            Path to the saved mesh
        """
        if not os.path.exists(heightmap_path):
            raise FileNotFoundError(f"Height map not found: {heightmap_path}")

        if not TRIMESH_AVAILABLE:
            raise ImportError("trimesh is required for mesh generation")

        # Load height map
        img = Image.open(heightmap_path)

        # Convert to grayscale if needed
        if img.mode != "L":
            img = img.convert("L")

        # Convert to numpy array
        height_map = np.array(img).astype(np.float32) / 255.0

        # Create a grid of vertices
        h, w = height_map.shape
        x, y = np.meshgrid(np.arange(w), np.arange(h))

        vertices = np.zeros((h * w, 3), dtype=np.float32)
        vertices[:, 0] = x.flatten()
        vertices[:, 1] = y.flatten()
        vertices[:, 2] = height_map.flatten() * scale_z

        # Create faces (triangles)
        faces = []
        for i in range(h - 1):
            for j in range(w - 1):
                idx = i * w + j
                faces.append([idx, idx + 1, idx + w])
                faces.append([idx + 1, idx + w + 1, idx + w])

        faces = np.array(faces, dtype=np.int32)

        # Create mesh
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

        # Smooth mesh if requested
        if smooth:
            mesh = mesh.smoothed()

        # Simplify mesh if requested
        if simplify:
            mesh = mesh.simplify_quadratic_decimation(int(len(mesh.faces) * 0.5))

        # Create output path if not provided
        if output_path is None:
            base_name = os.path.basename(heightmap_path)
            output_name = f"{os.path.splitext(base_name)[0]}_mesh.{output_format}"
            output_path = os.path.join(self.output_dir, output_name)

        # Save mesh
        mesh.export(output_path)

        console.print(f"[green]Mesh saved to: {output_path}[/green]")
        return output_path

    def image_to_mesh(
        self,
        image_path: str,
        scale_z: float = 0.1,
        invert: bool = False,
        blur_sigma: float = 1.0,
        smooth: bool = True,
        simplify: bool = False,
        output_format: str = "obj",
        output_path: Optional[str] = None,
    ) -> str:
        """
        Convert an image directly to a 3D mesh.

        Args:
            image_path: Path to the input image
            scale_z: Scale factor for height values
            invert: Whether to invert the height map
            blur_sigma: Sigma value for Gaussian blur
            smooth: Whether to smooth the mesh
            simplify: Whether to simplify the mesh
            output_format: Output format ('obj', 'stl', or 'ply')
            output_path: Path to save the mesh (optional)

        Returns:
            Path to the saved mesh
        """
        # First convert to height map
        heightmap_path = self.image_to_heightmap(
            image_path=image_path,
            invert=invert,
            blur_sigma=blur_sigma,
            scale_factor=1.0,  # We'll apply scale_z in the mesh conversion
            output_path=None,  # Use temporary path
        )

        # Then convert height map to mesh
        mesh_path = self.heightmap_to_mesh(
            heightmap_path=heightmap_path,
            scale_z=scale_z,
            smooth=smooth,
            simplify=simplify,
            output_format=output_format,
            output_path=output_path,
        )

        return mesh_path

    def image_to_point_cloud(
        self,
        image_path: str,
        scale_z: float = 0.1,
        sample_ratio: float = 0.1,
        output_format: str = "ply",
        output_path: Optional[str] = None,
    ) -> str:
        """
        Convert an image to a 3D point cloud.

        Args:
            image_path: Path to the input image
            scale_z: Scale factor for height values
            sample_ratio: Ratio of points to sample (0-1)
            output_format: Output format ('ply' or 'xyz')
            output_path: Path to save the point cloud (optional)

        Returns:
            Path to the saved point cloud
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        if not TRIMESH_AVAILABLE:
            raise ImportError("trimesh is required for point cloud generation")

        # Load image
        img = Image.open(image_path)

        # Get color information
        if img.mode != "RGB":
            img_rgb = img.convert("RGB")
        else:
            img_rgb = img

        # Convert to grayscale for height
        img_gray = img.convert("L")

        # Convert to numpy arrays
        height_map = np.array(img_gray).astype(np.float32) / 255.0
        color_map = np.array(img_rgb)

        # Create a grid of points
        h, w = height_map.shape
        x, y = np.meshgrid(np.arange(w), np.arange(h))

        # Flatten and sample points
        n_points = h * w
        n_samples = int(n_points * sample_ratio)
        indices = np.random.choice(n_points, n_samples, replace=False)

        x_sampled = x.flatten()[indices]
        y_sampled = y.flatten()[indices]
        z_sampled = height_map.flatten()[indices] * scale_z
        colors_sampled = color_map.reshape(-1, 3)[indices]

        # Create point cloud
        points = np.column_stack((x_sampled, y_sampled, z_sampled))
        cloud = trimesh.PointCloud(points, colors=colors_sampled)

        # Create output path if not provided
        if output_path is None:
            base_name = os.path.basename(image_path)
            output_name = f"{os.path.splitext(base_name)[0]}_pointcloud.{output_format}"
            output_path = os.path.join(self.output_dir, output_name)

        # Save point cloud
        cloud.export(output_path)

        console.print(f"[green]Point cloud saved to: {output_path}[/green]")
        return output_path


def image_to_heightmap(
    image_path: str,
    invert: bool = False,
    blur_sigma: float = 1.0,
    scale_factor: float = 1.0,
    output_path: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> str:
    """
    Convert an image to a height map.

    Args:
        image_path: Path to the input image
        invert: Whether to invert the height map
        blur_sigma: Sigma value for Gaussian blur
        scale_factor: Scale factor for height values
        output_path: Path to save the height map (optional)
        output_dir: Directory to save output files (optional)

    Returns:
        Path to the saved height map
    """
    converter = ImageTo3DConverter(output_dir=output_dir)
    return converter.image_to_heightmap(
        image_path=image_path,
        invert=invert,
        blur_sigma=blur_sigma,
        scale_factor=scale_factor,
        output_path=output_path,
    )


def image_to_normalmap(
    image_path: str,
    strength: float = 1.0,
    output_path: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> str:
    """
    Convert an image (or height map) to a normal map.

    Args:
        image_path: Path to the input image
        strength: Strength of the normal map effect
        output_path: Path to save the normal map (optional)
        output_dir: Directory to save output files (optional)

    Returns:
        Path to the saved normal map
    """
    converter = ImageTo3DConverter(output_dir=output_dir)
    return converter.image_to_normalmap(
        image_path=image_path, strength=strength, output_path=output_path
    )


def image_to_mesh(
    image_path: str,
    scale_z: float = 0.1,
    invert: bool = False,
    blur_sigma: float = 1.0,
    smooth: bool = True,
    simplify: bool = False,
    output_format: str = "obj",
    output_path: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> str:
    """
    Convert an image directly to a 3D mesh.

    Args:
        image_path: Path to the input image
        scale_z: Scale factor for height values
        invert: Whether to invert the height map
        blur_sigma: Sigma value for Gaussian blur
        smooth: Whether to smooth the mesh
        simplify: Whether to simplify the mesh
        output_format: Output format ('obj', 'stl', or 'ply')
        output_path: Path to save the mesh (optional)
        output_dir: Directory to save output files (optional)

    Returns:
        Path to the saved mesh
    """
    converter = ImageTo3DConverter(output_dir=output_dir)
    return converter.image_to_mesh(
        image_path=image_path,
        scale_z=scale_z,
        invert=invert,
        blur_sigma=blur_sigma,
        smooth=smooth,
        simplify=simplify,
        output_format=output_format,
        output_path=output_path,
    )


def image_to_point_cloud(
    image_path: str,
    scale_z: float = 0.1,
    sample_ratio: float = 0.1,
    output_format: str = "ply",
    output_path: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> str:
    """
    Convert an image to a 3D point cloud.

    Args:
        image_path: Path to the input image
        scale_z: Scale factor for height values
        sample_ratio: Ratio of points to sample (0-1)
        output_format: Output format ('ply' or 'xyz')
        output_path: Path to save the point cloud (optional)
        output_dir: Directory to save output files (optional)

    Returns:
        Path to the saved point cloud
    """
    converter = ImageTo3DConverter(output_dir=output_dir)
    return converter.image_to_point_cloud(
        image_path=image_path,
        scale_z=scale_z,
        sample_ratio=sample_ratio,
        output_format=output_format,
        output_path=output_path,
    )
