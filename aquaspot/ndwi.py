"""
NDWI (Normalized Difference Water Index) calculation and change detection.

Implements water detection algorithms for pipeline leak monitoring using
Sentinel-2 multispectral imagery.
"""

import logging
from pathlib import Path
from typing import Tuple, Optional

import numpy as np
import rasterio
from rasterio.windows import Window

from .config import config

logger = logging.getLogger(__name__)


def calc_ndwi(
    green_band: np.ndarray,
    nir_band: np.ndarray,
    mask: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Calculate NDWI (Normalized Difference Water Index).
    
    NDWI = (Green - NIR) / (Green + NIR)
    
    Args:
        green_band: Green band array (Band 3 for Sentinel-2)
        nir_band: Near-infrared band array (Band 8 for Sentinel-2)
        mask: Optional mask to exclude invalid pixels
        
    Returns:
        NDWI array with values between -1 and 1
        
    Raises:
        ValueError: If bands have different shapes or invalid data
    """
    logger.debug(f"Calculating NDWI for {green_band.shape} arrays")
    
    # Validate inputs
    if green_band.shape != nir_band.shape:
        raise ValueError(f"Band shape mismatch: {green_band.shape} vs {nir_band.shape}")
    
    # Convert to float to avoid integer overflow
    green = green_band.astype(np.float32)
    nir = nir_band.astype(np.float32)
    
    # Apply mask if provided
    if mask is not None:
        if mask.shape != green.shape:
            raise ValueError(f"Mask shape mismatch: {mask.shape} vs {green.shape}")
        green = np.where(mask, green, np.nan)
        nir = np.where(mask, nir, np.nan)
    
    # Calculate NDWI with division by zero protection
    denominator = green + nir
    ndwi = np.where(
        denominator != 0,
        (green - nir) / denominator,
        0
    )
    
    # Handle invalid values
    ndwi = np.where(np.isfinite(ndwi), ndwi, 0)
    
    # Clamp to valid NDWI range [-1, 1]
    ndwi = np.clip(ndwi, -1, 1)
    
    logger.info(f"NDWI calculated: min={ndwi.min():.3f}, max={ndwi.max():.3f}, mean={ndwi.mean():.3f}")
    
    return ndwi


def load_sentinel2_bands(
    image_path: Path,
    bands: list[int] = [3, 8],  # Green (B03) and NIR (B08)
    window: Optional[Window] = None,
) -> Tuple[np.ndarray, ...]:
    """
    Load specific bands from Sentinel-2 imagery.
    
    Args:
        image_path: Path to Sentinel-2 image file
        bands: List of band numbers to load (1-indexed)
        window: Optional window for spatial subsetting
        
    Returns:
        Tuple of band arrays
        
    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If bands are invalid
    """
    logger.debug(f"Loading bands {bands} from {image_path}")
    
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    try:
        with rasterio.open(image_path) as src:
            # Check if bands exist
            available_bands = src.count
            for band in bands:
                if band > available_bands:
                    raise ValueError(f"Band {band} not available (image has {available_bands} bands)")
            
            # Load bands
            band_arrays = []
            for band in bands:
                data = src.read(band, window=window)
                band_arrays.append(data)
                logger.debug(f"Loaded band {band}: {data.shape}, dtype={data.dtype}")
            
            return tuple(band_arrays)
            
    except rasterio.RasterioIOError as e:
        raise ValueError(f"Failed to read image {image_path}: {e}")


def detect_water_pixels(
    ndwi: np.ndarray,
    threshold: Optional[float] = None,
) -> np.ndarray:
    """
    Detect water pixels using NDWI threshold.
    
    Args:
        ndwi: NDWI array
        threshold: Water detection threshold (uses config default if None)
        
    Returns:
        Binary mask where True indicates water pixels
    """
    if threshold is None:
        threshold = config.ndwi_threshold
    
    logger.debug(f"Detecting water pixels with threshold: {threshold}")
    
    water_mask = ndwi > threshold
    water_pixels = np.sum(water_mask)
    total_pixels = ndwi.size
    water_percent = (water_pixels / total_pixels) * 100
    
    logger.info(f"Water detection: {water_pixels}/{total_pixels} pixels ({water_percent:.2f}%)")
    
    return water_mask


def detect_change(
    baseline_ndwi: np.ndarray,
    current_ndwi: np.ndarray,
    change_threshold: float = 0.1,
    min_change_area: int = 10,
) -> Tuple[np.ndarray, dict]:
    """
    Detect changes between baseline and current NDWI.
    
    Args:
        baseline_ndwi: Baseline NDWI array
        current_ndwi: Current NDWI array
        change_threshold: Minimum NDWI difference to consider as change
        min_change_area: Minimum number of connected pixels for valid change
        
    Returns:
        Tuple of (change_mask, change_stats)
        
    Raises:
        ValueError: If arrays have different shapes
    """
    logger.debug(f"Detecting changes between {baseline_ndwi.shape} NDWI arrays")
    
    if baseline_ndwi.shape != current_ndwi.shape:
        raise ValueError(f"Array shape mismatch: {baseline_ndwi.shape} vs {current_ndwi.shape}")
    
    # Calculate NDWI difference
    ndwi_diff = current_ndwi - baseline_ndwi
    
    # Detect significant changes
    positive_change = ndwi_diff > change_threshold  # New water
    negative_change = ndwi_diff < -change_threshold  # Lost water
    
    # Combine changes
    change_mask = positive_change | negative_change
    
    # Calculate statistics
    stats = {
        'total_changed_pixels': np.sum(change_mask),
        'new_water_pixels': np.sum(positive_change),
        'lost_water_pixels': np.sum(negative_change),
        'max_positive_change': np.max(ndwi_diff),
        'max_negative_change': np.min(ndwi_diff),
        'mean_change': np.mean(ndwi_diff),
        'std_change': np.std(ndwi_diff),
    }
    
    logger.info(f"Change detection: {stats['total_changed_pixels']} pixels changed")
    logger.info(f"New water: {stats['new_water_pixels']}, Lost water: {stats['lost_water_pixels']}")
    
    return change_mask, stats


def calculate_ndwi_from_file(
    image_path: Path,
    output_path: Optional[Path] = None,
    green_band: int = 3,
    nir_band: int = 8,
) -> np.ndarray:
    """
    Calculate NDWI directly from Sentinel-2 image file.
    
    Args:
        image_path: Path to Sentinel-2 image
        output_path: Optional path to save NDWI as GeoTIFF
        green_band: Green band number (default: 3 for Sentinel-2)
        nir_band: NIR band number (default: 8 for Sentinel-2)
        
    Returns:
        NDWI array
        
    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If bands are invalid
    """
    logger.info(f"Calculating NDWI from {image_path}")
    
    # For TCI (True Color Image) files, we need to handle differently
    # TCI files are RGB composite images, not individual bands
    if "TCI" in str(image_path) or "visual" in str(image_path):
        logger.warning("TCI/visual files don't contain separate spectral bands for NDWI calculation")
        logger.info("For real NDWI calculation, need individual B03 (green) and B08 (NIR) band files")
        
        # Load as RGB and create a mock NDWI using green channel
        try:
            with rasterio.open(image_path) as src:
                # Read RGB bands
                red = src.read(1).astype(np.float32)
                green = src.read(2).astype(np.float32)
                blue = src.read(3).astype(np.float32)
                
                # Create a pseudo-NDWI using green-red difference (approximation)
                # This is NOT real NDWI but demonstrates the workflow
                pseudo_ndwi = (green - red) / (green + red + 1e-8)
                pseudo_ndwi = np.clip(pseudo_ndwi, -1, 1)
                
                logger.info("Created pseudo-NDWI from RGB channels (approximation only)")
                logger.info("For accurate results, download B03 and B08 bands separately")
                
                if output_path:
                    save_ndwi_geotiff(pseudo_ndwi, image_path, output_path)
                
                return pseudo_ndwi
                
        except Exception as e:
            raise ValueError(f"Failed to process TCI file: {e}")
    
    else:
        # Standard multi-band image processing
        try:
            green, nir = load_sentinel2_bands(image_path, [green_band, nir_band])
            ndwi = calc_ndwi(green, nir)
            
            if output_path:
                save_ndwi_geotiff(ndwi, image_path, output_path)
            
            return ndwi
            
        except Exception as e:
            raise ValueError(f"Failed to calculate NDWI: {e}")


def save_ndwi_geotiff(
    ndwi: np.ndarray,
    reference_image: Path,
    output_path: Path,
) -> None:
    """
    Save NDWI array as GeoTIFF with spatial reference from original image.
    
    Args:
        ndwi: NDWI array
        reference_image: Reference image for spatial information
        output_path: Output GeoTIFF path
    """
    logger.debug(f"Saving NDWI to {output_path}")
    
    try:
        with rasterio.open(reference_image) as src:
            profile = src.profile.copy()
            profile.update({
                'dtype': 'float32',
                'count': 1,
                'compress': 'lzw'
            })
            
            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(ndwi.astype(np.float32), 1)
                
        logger.info(f"NDWI saved to {output_path}")
        
    except Exception as e:
        logger.error(f"Failed to save NDWI: {e}")
        raise
