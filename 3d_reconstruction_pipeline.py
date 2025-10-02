
import cv2
import numpy as np
from matplotlib import pyplot as plt
from skimage import measure
import trimesh
import trimesh.repair
import trimesh.smoothing
import os
# If running outside Colab, you might need to handle file uploads differently
# from google.colab import files

def load_images(uploaded_files):
    """
    Loads grayscale images from uploaded files with error handling.

    Args:
        uploaded_files: A dictionary of uploaded files from google.colab.files.upload().

    Returns:
        A list of loaded grayscale images, or None if an error occurs.
    """
    images = []
    print("Loading images...")
    if not uploaded_files:
        print("Warning: No files uploaded.")
        return images
    try:
        for file_name, content in uploaded_files.items():
            np_arr = np.frombuffer(content, np.uint8)
            img_grayscale = cv2.imdecode(np_arr, cv2.IMREAD_GRAYSCALE)
            if img_grayscale is None:
                print(f"Error: Could not decode image file: {file_name}")
                continue
            images.append(img_grayscale)
            print(f"Successfully loaded {file_name}.")
        print(f"Finished loading {len(images)} images.")
        return images
    except Exception as e:
        print(f"An error occurred during image loading: {e}")
        return None


def process_silhouettes(images, show_previews=False):
    """
    Extracts silhouettes from a list of grayscale images with error handling
    and optionally displays previews.

    Args:
        images: A list of grayscale images.
        show_previews: If True, display the original grayscale image and the extracted silhouette.

    Returns:
        A list of silhouette images (binary masks), or None if an error occurs.
    """
    silhouettes = []
    print("Processing silhouettes...")
    if not images:
        print("No images provided for silhouette processing.")
        return silhouettes
    try:
        for i, img_grayscale in enumerate(images):
            # Ensure image is valid before processing
            if img_grayscale is None or img_grayscale.size == 0:
                print(f"Warning: Skipping processing for invalid image at index {i}.")
                continue

            _, silhouette = cv2.threshold(img_grayscale, 240, 255, cv2.THRESH_BINARY_INV)
            silhouettes.append(silhouette)
            if show_previews:
                plt.figure(figsize=(10, 5))

                plt.subplot(1, 2, 1)
                plt.title(f'Original Image {i+1} (Grayscale)')
                plt.imshow(img_grayscale, cmap='gray')
                plt.axis('off')

                plt.subplot(1, 2, 2)
                plt.title(f'Silhouette {i+1} Extracted')
                plt.imshow(silhouette, cmap='gray')
                plt.axis('off')

                plt.show()

        print(f"Finished processing {len(silhouettes)} images and extracted silhouettes.")
        return silhouettes
    except Exception as e:
        print(f"An error occurred during silhouette processing: {e}")
        return None


def project_voxel_to_silhouette(voxel_coords, silhouette_shape, view_type, volume_bounds, grid_size):
    """Projects a 3D voxel coordinate onto the 2D plane of a silhouette view."""
    voxel_world_x = volume_bounds['x_min'] + (voxel_coords[0] + 0.5) * (volume_bounds['x_max'] - volume_bounds['x_min']) / grid_size
    voxel_world_y = volume_bounds['y_min'] + (voxel_coords[1] + 0.5) * (volume_bounds['y_max'] - volume_bounds['y_min']) / grid_size
    voxel_world_z = volume_bounds['z_min'] + (voxel_coords[2] + 0.5) * (volume_bounds['z_max'] - volume_bounds['z_min']) / grid_size

    img_height, img_width = silhouette_shape

    if view_type == 'front':
        proj_x = int((voxel_world_z - volume_bounds['z_min']) / (volume_bounds['z_max'] - volume_bounds['z_min']) * img_width)
        proj_y = int((volume_bounds['y_max'] - voxel_world_y) / (volume_bounds['y_max'] - volume_bounds['y_min']) * img_height)
    elif view_type == 'side':
        proj_x = int((voxel_world_x - volume_bounds['x_min']) / (volume_bounds['x_max'] - volume_bounds['x_min']) * img_width)
        proj_y = int((volume_bounds['y_max'] - voxel_world_y) / (volume_bounds['y_max'] - volume_bounds['y_min']) * img_height)
    elif view_type == 'top':
        proj_x = int((voxel_world_x - volume_bounds['x_min']) / (volume_bounds['x_max'] - volume_bounds['x_min']) * img_width)
        proj_y = int((volume_bounds['z_max'] - voxel_world_z) / (volume_bounds['z_max'] - volume_bounds['z_min']) * img_height)
    else:
        return None, None

    proj_x = max(0, min(proj_x, img_width - 1))
    proj_y = max(0, min(proj_y, img_height - 1))

    return proj_y, proj_x


def compute_visual_hull(silhouettes, grid_size, volume_bounds, view_types, show_previews=False):
    """
    Computes the visual hull from a list of silhouettes with error handling
    and optionally displays voxel grid slices.

    Args:
        silhouettes: A list of silhouette images.
        grid_size: The size of the voxel grid (cubic).
        volume_bounds: A dictionary defining the world coordinates bounds of the volume.
        view_types: A list of strings indicating the view type for each silhouette.
        show_previews: If True, display slices of the resulting voxel grid.

    Returns:
        A numpy array representing the voxel grid, or None if an error occurs.
    """
    print("Computing visual hull...")
    if not silhouettes:
        print("No silhouettes provided for visual hull computation.")
        return np.zeros((grid_size, grid_size, grid_size), dtype=np.uint8) # Return empty grid

    if len(silhouettes) != len(view_types):
        print(f"Error: Number of silhouettes ({len(silhouettes)}) does not match number of view types ({len(view_types)}).")
        return None # Indicate failure

    voxel_grid = np.full((grid_size, grid_size, grid_size), 255, dtype=np.uint8)

    try:
        for x in range(grid_size):
            for y in range(grid_size):
                for z in range(grid_size):
                    if voxel_grid[x, y, z] == 0:
                        continue

                    for i, silhouette in enumerate(silhouettes):
                        view_type = view_types[i]
                        # Check for valid silhouette before projection
                        if silhouette is None or silhouette.size == 0:
                            print(f"Warning: Skipping visual hull computation for invalid silhouette at index {i}.")
                            continue

                        proj_y, proj_x = project_voxel_to_silhouette((x, y, z), silhouette.shape, view_type, volume_bounds, grid_size)

                        if proj_y is not None and proj_x is not None:
                            # Assuming silhouette has object as 255 and background as 0
                            # If projected point is in the black background (0), the voxel is outside the object
                            if silhouette[proj_y, proj_x] == 0:
                                voxel_grid[x, y, z] = 0 # Mark voxel as empty
                                break # No need to check other silhouettes for this voxel

        print("Visual hull computation complete.")

        if show_previews and np.sum(voxel_grid > 0) > 0:
            print("
Displaying slices of the voxel grid:")
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))

            # Display a slice along the XZ plane (fixing Y)
            y_slice = grid_size // 2
            axes[0].imshow(voxel_grid[:, y_slice, :], cmap='gray', origin='lower')
            axes[0].set_title(f'XZ slice (Y={y_slice})')
            axes[0].set_xlabel('Z')
            axes[0].set_ylabel('X')

            # Display a slice along the YZ plane (fixing X)
            x_slice = grid_size // 2
            axes[1].imshow(voxel_grid[x_slice, :, :], cmap='gray', origin='lower')
            axes[1].set_title(f'YZ slice (X={x_slice})')
            axes[1].set_xlabel('Z')
            axes[1].set_ylabel('Y')

            # Display a slice along the XY plane (fixing Z)
            z_slice = grid_size // 2
            axes[2].imshow(voxel_grid[:, :, z_slice], cmap='gray', origin='lower')
            axes[2].set_title(f'XY slice (Z={z_slice})')
            axes[2].set_xlabel('Y')
            axes[2].set_ylabel('X')

            plt.tight_layout()
            plt.show()
        elif show_previews and np.sum(voxel_grid > 0) == 0:
            print("
Voxel grid is empty, cannot display slices.")

        return voxel_grid
    except Exception as e:
        print(f"An error occurred during visual hull computation: {e}")
        return None


def generate_mesh(voxel_grid, volume_bounds, grid_size, level=127):
    """
    Generates a mesh from a voxel grid using Marching Cubes with error handling
    and checks for uniform volume.

    Args:
        voxel_grid: A numpy array representing the voxel grid (uint8, 0 or 255).
        volume_bounds: A dictionary defining the world coordinates bounds of the volume.
        grid_size: The size of the voxel grid (cubic).
        level: The iso-surface value for Marching Cubes.

    Returns:
        A trimesh object or None if mesh generation fails.
    """
    print("Generating mesh using Marching Cubes...")
    if voxel_grid is None or voxel_grid.size == 0:
        print("No valid voxel grid provided for mesh generation.")
        return None

    # Step 1: Verificar o Volume - Check if there is a surface to extract
    # Check if the grid is all 0s or all 255s
    if np.all(voxel_grid == 0) or np.all(voxel_grid == 255):
        print("ERROR: The voxel volume is uniform (all empty or all occupied). There is no surface to extract.")
        return None

    # Check if there are any occupied voxels before generating mesh
    if np.sum(voxel_grid > 0) == 0:
        print("Visual hull computation resulted in an empty grid. No mesh can be generated.")
        return None

    try:
        # Step 2: Converter para Float
        # Convert the voxel grid to float to ensure level works as expected
        voxel_grid_float = voxel_grid.astype(np.float64)

        # Step 3: Definir o Level (using 127 for float data as a standard midpoint)
        # Calculate spacing based on the volume_bounds and grid_size.
        spacing = ((volume_bounds['x_max'] - volume_bounds['x_min']) / grid_size,
                   (volume_bounds['y_max'] - volume_bounds['y_min']) / grid_size,
                   (volume_bounds['z_max'] - volume_bounds['z_min']) / grid_size)
        print(f"Using spacing for Marching Cubes: {spacing}")


        vertices, faces, normals, values = measure.marching_cubes(
            volume=voxel_grid_float,
            level=level, # Using level=127 with float data
            spacing=spacing
        )

        # Vertices are scaled by spacing, so they are in world units relative to the volume's local origin (0,0,0 voxel index).
        # To get them into world coordinates relative to the overall world origin (0,0,0),
        # we need to add the minimum bounds of the volume.
        vertices_world = vertices + np.array([volume_bounds['x_min'], volume_bounds['y_min'], volume_bounds['z_min']])


        mesh = trimesh.Trimesh(vertices=vertices_world, faces=faces, vertex_normals=normals) # Use vertices_world
        print(f"Marching Cubes concluded. Generated mesh with {len(vertices_world)} vertices and {len(faces)} faces.")
        return mesh
    except ValueError as ve:
         print(f"Error during mesh generation (ValueError) with level={level} on float data: {ve}. This might be due to the 'level' parameter not being within the data range or other input issues.")
         return None
    except Exception as e:
        print(f"An unexpected error occurred during mesh generation with level={level} on float data: {e}")
        return None


def export_mesh(mesh, output_filename):
    """
    Exports a trimesh object to a GLB file with error handling.

    Args:
        mesh: A trimesh object.
        output_filename: The name of the output GLB file.
    """
    print(f"Exporting mesh to {output_filename}...")
    if mesh is not None:
        try:
            # Ensure the mesh has valid geometry before exporting
            if len(mesh.vertices) > 0 and len(mesh.faces) > 0:
                mesh.export(output_filename)
                print(f"Successfully exported mesh to {output_filename}")
            else:
                print("Warning: Mesh has no vertices or faces, skipping export.")
        except Exception as e:
            print(f"An error occurred during mesh export: {e}")
    else:
        print("No mesh object available for export.")


def run_reconstruction_pipeline(uploaded_files, view_types, grid_size=100, volume_bounds=None, marching_cubes_level=127, show_previews=True):
    """
    Orchestrates the 3D reconstruction pipeline with configurable options and error handling.

    Args:
        uploaded_files: A dictionary of uploaded files from google.colab.files.upload().
        view_types: A list of strings indicating the view type for each silhouette.
        grid_size: The size of the voxel grid (cubic).
        volume_bounds: A dictionary defining the world coordinates bounds of the volume.
                       If None, default bounds are used.
        marching_cubes_level: The iso-surface value for Marching Cubes.
        show_previews: If True, display previews of silhouettes and voxel grid slices.
    """
    print("--- Starting 3D Reconstruction Pipeline ---")

    # Define default volume bounds if not provided
    if volume_bounds is None:
        volume_bounds = {
            'x_min': -1.0, 'x_max': 1.0,
            'y_min': -1.0, 'y_max': 1.0,
            'z_min': -1.0, 'z_max': 1.0
        }
    print(f"Using voxel grid size: {grid_size}x{grid_size}x{grid_size}")
    print(f"Using volume bounds: {volume_bounds}")
    print(f"Using Marching Cubes level: {marching_cubes_level}")
    print(f"Show previews: {show_previews}")


    # Step 1: Load images
    print("
Step 1: Loading images...")
    images = load_images(uploaded_files)
    if images is None or not images:
        print("Image loading failed or no images loaded. Aborting pipeline.")
        return

    # Step 2: Process silhouettes
    print("
Step 2: Processing silhouettes...")
    silhouettes = process_silhouettes(images, show_previews=show_previews)
    if silhouettes is None or not silhouettes:
        print("Silhouette processing failed or no silhouettes processed. Aborting pipeline.")
        return

    # Check if the number of silhouettes matches the number of view types
    if len(silhouettes) != len(view_types):
        print(f"Error: Number of silhouettes ({len(silhouettes)}) does not match number of view types ({len(view_types)}). Aborting pipeline.")
        return

    # Step 3: Compute visual hull
    print("
Step 3: Computing visual hull...")
    voxel_grid = compute_visual_hull(silhouettes, grid_size, volume_bounds, view_types, show_previews=show_previews)
    # Check if the visual hull computation returned a valid grid
    if voxel_grid is None or voxel_grid.shape != (grid_size, grid_size, grid_size):
         print("Visual hull computation failed or returned an invalid grid. Aborting pipeline.")
         return

    # Check if there are any occupied voxels before generating mesh
    if np.sum(voxel_grid > 0) == 0:
        print("Visual hull computation resulted in an empty grid. No mesh can be generated. Aborting pipeline.")
        return

    # Step 4: Generate mesh using Marching Cubes
    print("
Step 4: Generating mesh...")
    # Pass volume_bounds and grid_size to generate_mesh
    reconstructed_mesh = generate_mesh(voxel_grid, volume_bounds, grid_size, level=marching_cubes_level)
    if reconstructed_mesh is None:
        print("Mesh generation failed. Aborting pipeline.")
        return

    # Step 5: Export the GLB file
    print("
Step 5: Exporting GLB file...")
    output_filename = 'reconstructed_model.glb'
    export_mesh(reconstructed_mesh, output_filename)

    print("
--- 3D Reconstruction Pipeline Complete ---")

# Example usage (will be placed in a separate cell):
# if 'uploaded_files' in locals() and uploaded_files:
#     example_view_types = [f'view{i+1}' for i in range(len(uploaded_files))]
#     run_reconstruction_pipeline(uploaded_files, example_view_types)
# else:
#     print("'uploaded_files' is not defined or is empty. Please upload images first.")

