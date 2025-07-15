#!/usr/bin/env python3
"""
Quick debug test for change detection
"""

from pathlib import Path
from aquaspot.config import config
from aquaspot.ndwi import calculate_ndwi_from_file, detect_change

def debug_change_detection():
    data_dir = Path(config.data_dir)
    tiff_files = list(data_dir.rglob("*.tif"))
    
    print(f"Found {len(tiff_files)} files:")
    for i, f in enumerate(tiff_files):
        print(f"  {i}: {f.name}")
    
    if len(tiff_files) >= 2:
        print(f"\nTesting change detection between:")
        print(f"  File 1: {tiff_files[0].name}")
        print(f"  File 2: {tiff_files[1].name}")
        
        try:
            # Calculate NDWI
            print("Calculating NDWI for file 1...")
            ndwi1 = calculate_ndwi_from_file(str(tiff_files[0]))
            print(f"NDWI1 shape: {ndwi1.shape}, range: {ndwi1.min():.3f} to {ndwi1.max():.3f}")
            
            print("Calculating NDWI for file 2...")
            ndwi2 = calculate_ndwi_from_file(str(tiff_files[1]))
            print(f"NDWI2 shape: {ndwi2.shape}, range: {ndwi2.min():.3f} to {ndwi2.max():.3f}")
            
            # Test change detection
            print("Running change detection...")
            results = detect_change(ndwi1, ndwi2, config.ndwi_threshold)
            print(f"Results: {results}")
            
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print("Need at least 2 files for testing")
        return False

if __name__ == "__main__":
    debug_change_detection()
