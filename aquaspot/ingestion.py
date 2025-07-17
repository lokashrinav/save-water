"""
Sentinel-2 data ingestion module.

Handles downloading and processing of Sentinel-2 satellite imagery
for pipeline monitoring and leak detection using STAC APIs.
"""

import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import geopandas as gpd
import planetary_computer as pc
import requests
import shapely.geometry
from pystac_client import Client

from .config import config

logger = logging.getLogger(__name__)


def download_sentinel_tiles(
    aoi: shapely.geometry.Polygon,
    date: datetime,
    out_dir: Path,
    days_tolerance: int = 7,
    max_cloud_cover: float = 20.0,
    max_retries: int = 3,
) -> list[Path]:
    """
    Download Sentinel-2 tiles for given area of interest and date.

    Args:
        aoi: Area of interest as shapely polygon
        date: Target date for imagery
        out_dir: Output directory for downloaded tiles
        days_tolerance: Days before/after target date to search
        max_cloud_cover: Maximum cloud cover percentage (0-100)
        max_retries: Maximum number of retry attempts

    Returns:
        List of paths to downloaded tile files

    Raises:
        ValueError: If AOI or date parameters are invalid
        ConnectionError: If STAC API is unavailable
        RuntimeError: If no suitable imagery found
    """
    logger.debug(f"Starting tile download for AOI bounds: {aoi.bounds}, date: {date}")
    
    # Validate inputs
    if not aoi.is_valid:
        raise ValueError("Invalid area of interest polygon")
    
    if date > datetime.now():
        raise ValueError("Cannot download imagery for future dates")
    
    # Create output directory
    out_dir.mkdir(parents=True, exist_ok=True)
    date_dir = out_dir / date.strftime("%Y-%m-%d")
    date_dir.mkdir(exist_ok=True)
    
    downloaded_files = []
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries}: Searching for Sentinel-2 imagery")
            
            # Search using Microsoft Planetary Computer (fallback to CDSE if needed)
            items = _search_sentinel2_imagery(
                aoi, date, days_tolerance, max_cloud_cover
            )
            
            if not items:
                logger.warning(f"No suitable imagery found for {date} ± {days_tolerance} days")
                if attempt == max_retries - 1:
                    raise RuntimeError("No suitable Sentinel-2 imagery found")
                continue
            
            logger.info(f"Found {len(items)} suitable Sentinel-2 scenes")
            
            # Download the items
            for i, item in enumerate(items[:3]):  # Limit to 3 items max
                try:
                    downloaded_file = _download_sentinel2_item(item, date_dir, i)
                    if downloaded_file:
                        downloaded_files.append(downloaded_file)
                        logger.info(f"Downloaded: {downloaded_file.name}")
                except Exception as e:
                    logger.warning(f"Failed to download item {item.id}: {e}")
                    continue
            
            if downloaded_files:
                logger.info(f"Successfully downloaded {len(downloaded_files)} files")
                return downloaded_files
            
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise ConnectionError(f"Failed to download after {max_retries} attempts: {e}")
    
    raise RuntimeError("Download failed after all retry attempts")


def _search_sentinel2_imagery(
    aoi: shapely.geometry.Polygon,
    date: datetime,
    days_tolerance: int,
    max_cloud_cover: float,
) -> list:
    """Search for Sentinel-2 imagery using STAC API."""
    try:
        # Try Microsoft Planetary Computer first (more reliable)
        logger.debug("Searching Microsoft Planetary Computer...")
        catalog = Client.open(
            "https://planetarycomputer.microsoft.com/api/stac/v1",
            modifier=pc.sign_inplace
        )
        
        # Define search parameters
        bbox = list(aoi.bounds)  # [minx, miny, maxx, maxy]
        date_range = f"{(date - timedelta(days=days_tolerance)).isoformat()}/{(date + timedelta(days=days_tolerance)).isoformat()}"
        
        search = catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox,
            datetime=date_range,
            query={"eo:cloud_cover": {"lt": max_cloud_cover}},
            limit=10
        )
        
        items = list(search.items())
        
        if items:
            logger.debug(f"Found {len(items)} items from Planetary Computer")
            # Sort by date proximity to target date
            def date_diff(item):
                try:
                    item_date = datetime.fromisoformat(item.datetime.replace('Z', '+00:00'))
                    return abs((item_date - date).days)
                except:
                    # Fallback for parsing issues
                    return 999
            
            return sorted(items, key=date_diff)
        
    except Exception as e:
        logger.warning(f"Planetary Computer search failed: {e}")
    
    try:
        # Fallback to Copernicus Data Space Ecosystem
        logger.debug("Searching Copernicus Data Space Ecosystem...")
        catalog = Client.open(config.stac_api_url)
        
        bbox = list(aoi.bounds)
        date_range = f"{(date - timedelta(days=days_tolerance)).isoformat()}/{(date + timedelta(days=days_tolerance)).isoformat()}"
        
        search = catalog.search(
            collections=["SENTINEL-2"],
            bbox=bbox,
            datetime=date_range,
            limit=10
        )
        
        items = list(search.items())
        logger.debug(f"Found {len(items)} items from CDSE")
        
        # Filter by cloud cover manually since CDSE doesn't support query parameter
        filtered_items = []
        for item in items:
            try:
                cloud_cover = item.properties.get('eo:cloud_cover', 0)
                if cloud_cover <= max_cloud_cover:
                    filtered_items.append(item)
            except:
                # Include item if we can't determine cloud cover
                filtered_items.append(item)
        
        logger.debug(f"After cloud cover filtering: {len(filtered_items)} items")
        
        # Sort by date proximity with more robust date parsing
        def get_date_diff(item):
            try:
                if hasattr(item, 'datetime'):
                    item_date_str = item.datetime
                elif hasattr(item, 'properties') and 'datetime' in item.properties:
                    item_date_str = item.properties['datetime']
                else:
                    return float('inf')  # Put items without dates at the end
                
                # Handle different datetime formats
                if item_date_str.endswith('Z'):
                    item_date_str = item_date_str.replace('Z', '+00:00')
                
                item_date = datetime.fromisoformat(item_date_str)
                diff = abs((item_date - date).total_seconds() / 86400)  # Convert to days
                return diff
            except Exception as e:
                logger.debug(f"Error parsing date for item: {e}")
                return float('inf')  # Put problematic items at the end
        
        return sorted(filtered_items, key=get_date_diff)
        
    except Exception as e:
        logger.error(f"CDSE search failed: {e}")
        return []


def _download_sentinel2_item(item, output_dir: Path, index: int) -> Optional[Path]:
    """Download a single Sentinel-2 STAC item."""
    try:
        # Get the visual (TCI) asset for quick visualization
        # For NDWI calculation, we'd want B03 (green) and B08 (NIR) bands
        asset_key = "visual"  # or "rendered_preview" depending on catalog
        
        # Try different asset keys based on the catalog
        possible_assets = ["visual", "rendered_preview", "overview", "B04", "red"]
        asset = None
        asset_key = None
        
        for key in possible_assets:
            if key in item.assets:
                asset = item.assets[key]
                asset_key = key
                break
        
        if not asset:
            logger.warning(f"No suitable asset found in item {item.id}")
            return None
        
        # Generate filename
        try:
            item_date = datetime.fromisoformat(item.datetime.replace('Z', '+00:00')).strftime('%Y%m%d')
        except:
            # Fallback for date parsing issues
            item_date = "unknown_date"
        
        filename = f"sentinel2_{item_date}_{index:02d}_{asset_key}.tif"
        output_path = output_dir / filename
        
        # Skip if already exists
        if output_path.exists():
            logger.debug(f"File already exists: {filename}")
            return output_path
        
        # Download the asset
        logger.debug(f"Downloading {asset.href} to {filename}")
        
        response = requests.get(asset.href, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.debug(f"Successfully downloaded {filename} ({output_path.stat().st_size} bytes)")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to download item {item.id}: {e}")
        return None


def load_pipeline_geojson(geojson_path: Path) -> shapely.geometry.Polygon:
    """
    Load pipeline geometry from GeoJSON and create buffered AOI.
    
    Args:
        geojson_path: Path to pipeline GeoJSON file
        
    Returns:
        Buffered polygon around pipeline for imagery search
        
    Raises:
        ValueError: If GeoJSON is invalid or empty
    """
    try:
        gdf = gpd.read_file(geojson_path)
        
        if gdf.empty:
            raise ValueError("GeoJSON file is empty")
        
        # Combine all geometries and buffer by pipeline_buffer_m
        combined_geom = gdf.geometry.unary_union
        
        # Buffer in meters (assuming CRS is geographic, convert to UTM for accurate buffering)
        if gdf.crs and gdf.crs.to_string() == 'EPSG:4326':
            # For simplicity, use a rough degree conversion (this should be improved for production)
            buffer_degrees = config.pipeline_buffer_m / 111000  # rough conversion
            buffered = combined_geom.buffer(buffer_degrees)
        else:
            buffered = combined_geom.buffer(config.pipeline_buffer_m)
        
        if isinstance(buffered, shapely.geometry.MultiPolygon):
            # Use the largest polygon if multiple
            buffered = max(buffered.geoms, key=lambda x: x.area)
        
        logger.info(f"Created AOI with bounds: {buffered.bounds}")
        return buffered
        
    except Exception as e:
        raise ValueError(f"Failed to load pipeline GeoJSON: {e}")
