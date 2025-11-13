"""
glTF Transform Helper Module

This module provides functions to apply various glTF transformation operations
to asset files using the @gltf-transform npm package.
"""

import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

from django.conf import settings
from django.core.files import File
from icosa.models import Asset, Format, Resource

logger = logging.getLogger(__name__)


# Path to the gltf_transform.js script - it's in the Django project root (django/)
# which is the parent directory of the Django project settings
GLTF_TRANSFORM_SCRIPT = os.path.join(
    settings.BASE_DIR,
    "gltf_transform.js"
)

# Available transformation operations
AVAILABLE_OPERATIONS = [
    # Phase 1: Core optimizations (already implemented)
    "dedup",
    "prune",
    "resample",
    "quantize",
    "weld",
    "flatten",
    "join",
    "instance",
    "metalrough",
    # Phase 1: Additional operations (now exposed in UI)
    "partition",
    "unweld",
    "simplify",
    "unlit",
    # Phase 2: Compression (high priority)
    "draco",
    "textureCompress",
    "meshopt",
]


def transform_gltf_file(
    input_path: str,
    output_path: str,
    operations: List[str],
    options: Optional[Dict] = None,
) -> Dict[str, any]:
    """
    Apply glTF transformation operations to a file.

    Args:
        input_path: Path to the input glTF/GLB file
        output_path: Path where the output file should be saved
        operations: List of operations to apply (e.g., ['dedup', 'prune'])
        options: Optional dictionary of operation-specific options

    Returns:
        Dictionary containing:
            - success: Boolean indicating success/failure
            - message: Status message
            - input_size: Input file size in bytes
            - output_size: Output file size in bytes
            - reduction_percent: Percentage reduction in file size

    Raises:
        FileNotFoundError: If input file doesn't exist
        subprocess.CalledProcessError: If the transformation fails
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Validate operations
    invalid_ops = [op for op in operations if op not in AVAILABLE_OPERATIONS]
    if invalid_ops:
        raise ValueError(f"Invalid operations: {invalid_ops}")

    # Prepare command
    operations_str = ",".join(operations)
    cmd = [
        "node",
        GLTF_TRANSFORM_SCRIPT,
        input_path,
        output_path,
        operations_str,
    ]

    # Add options if provided
    if options:
        cmd.append(json.dumps(options))

    # Run the transformation
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

        # Get file sizes
        input_size = os.path.getsize(input_path)
        output_size = os.path.getsize(output_path)
        reduction_percent = (
            ((input_size - output_size) / input_size * 100) if input_size > 0 else 0
        )

        return {
            "success": True,
            "message": result.stdout,
            "input_size": input_size,
            "output_size": output_size,
            "reduction_percent": reduction_percent,
        }

    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "message": f"Transformation failed: {e.stderr}",
            "error": str(e),
        }


def transform_asset_formats(
    asset: Asset,
    operations: List[str],
    options: Optional[Dict] = None,
    format_types: Optional[List[str]] = None,
) -> Dict[str, any]:
    """
    Transform glTF/GLB formats associated with an asset.

    Args:
        asset: The Asset model instance
        operations: List of operations to apply
        options: Optional operation-specific options
        format_types: List of format types to transform (e.g., ['GLTF2', 'GLB'])
                     If None, transforms all GLTF formats

    Returns:
        Dictionary containing transformation results for each format
    """
    results = {}

    # Default to all GLTF format types if not specified
    if format_types is None:
        format_types = ["GLTF1", "GLTF2", "GLB"]

    # Get all formats for this asset that match the specified types
    formats = asset.format_set.filter(format_type__in=format_types)

    for fmt in formats:
        if not fmt.root_resource:
            results[fmt.format_type] = {
                "success": False,
                "message": "No root resource found",
            }
            continue

        # Get the resource file path
        resource = fmt.root_resource
        if not resource.file:
            results[fmt.format_type] = {
                "success": False,
                "message": "Resource file not found",
            }
            continue

        try:
            logger.info(f"Starting transformation for {fmt.format_type} (resource_id={resource.id})")

            # Create temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Copy input file to temp location
                input_path = os.path.join(temp_dir, "input.glb")
                logger.debug(f"Copying file from storage to {input_path}")

                # Open and read the file from storage (works with S3, local, etc.)
                with resource.file.open('rb') as source_file:
                    with open(input_path, "wb") as dest_file:
                        dest_file.write(source_file.read())

                input_size = os.path.getsize(input_path)
                logger.info(f"Input file size: {input_size} bytes")

                # Set output path
                output_path = os.path.join(temp_dir, "output.glb")

                # Transform the file
                logger.info(f"Running transformations: {operations}")
                result = transform_gltf_file(
                    input_path, output_path, operations, options
                )

                if result["success"]:
                    # Get the original filename (just the basename, not full path)
                    original_name = os.path.basename(resource.file.name)
                    logger.info(f"Transformation successful, saving back as {original_name}")

                    # Delete the old file from storage
                    old_path = resource.file.name
                    resource.file.delete(save=False)
                    logger.debug(f"Deleted old file: {old_path}")

                    # Save the transformed file back to the resource
                    with open(output_path, "rb") as f:
                        resource.file.save(
                            original_name,
                            File(f),
                            save=True,
                        )

                    logger.info(f"Saved transformed file to: {resource.file.name}")

                    # Add file size info to result
                    result["original_name"] = original_name
                    result["new_file_path"] = resource.file.name
                else:
                    logger.error(f"Transformation failed: {result.get('message')}")

                results[fmt.format_type] = result

        except Exception as e:
            logger.exception(f"Exception during transformation for {fmt.format_type}")
            results[fmt.format_type] = {
                "success": False,
                "message": str(e),
                "error_type": type(e).__name__,
            }

    return results


def get_gltf_formats_for_asset(asset: Asset) -> List[Format]:
    """
    Get all GLTF-compatible formats for an asset.

    Args:
        asset: The Asset model instance

    Returns:
        List of Format instances that are GLTF-compatible
    """
    return list(
        asset.format_set.filter(format_type__in=["GLTF1", "GLTF2", "GLB"]).order_by(
            "format_type"
        )
    )


def validate_operations(operations: List[str]) -> tuple[bool, Optional[str]]:
    """
    Validate a list of operations.

    Args:
        operations: List of operation names to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not operations:
        return False, "No operations specified"

    invalid_ops = [op for op in operations if op not in AVAILABLE_OPERATIONS]
    if invalid_ops:
        return False, f"Invalid operations: {', '.join(invalid_ops)}"

    return True, None
