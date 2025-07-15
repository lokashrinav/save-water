#!/usr/bin/env python3
"""
🧪 Test NDWI calculation and change detection functionality
"""

from aquaspot.ndwi import calculate_ndwi_from_file, detect_change, detect_water_pixels
from pathlib import Path
import numpy as np

def test_ndwi_pipeline():
    """Test the complete NDWI pipeline with downloaded imagery."""
    
    print("🧪 Testing AquaSpot NDWI Pipeline")
    print("=" * 40)
    
    # Check available images
    data_dir = Path('my_data/2024-06-15')
    images = list(data_dir.glob('*.tif'))
    print(f"📁 Found {len(images)} images:")
    for img in images:
        print(f"  📄 {img.name}")
    
    if len(images) < 2:
        print("❌ Need at least 2 images for change detection")
        return
    
    print(f"\n📊 Calculating NDWI for baseline image...")
    baseline_path = images[0]
    baseline_ndwi = calculate_ndwi_from_file(baseline_path)
    
    print(f"📊 Calculating NDWI for current image...")
    current_path = images[1]
    current_ndwi = calculate_ndwi_from_file(current_path)
    
    print(f"\n🔍 Detecting changes between images...")
    change_mask, stats = detect_change(baseline_ndwi, current_ndwi)
    
    print(f"\n✅ Results:")
    print(f"📏 Image size: {baseline_ndwi.shape}")
    print(f"📈 Total pixels changed: {stats['total_changed_pixels']:,}")
    print(f"💧 New water pixels: {stats['new_water_pixels']:,}")
    print(f"🏜️ Lost water pixels: {stats['lost_water_pixels']:,}")
    print(f"📊 Max positive change: {stats['max_positive_change']:.3f}")
    print(f"📊 Max negative change: {stats['max_negative_change']:.3f}")
    print(f"📊 Mean change: {stats['mean_change']:.3f}")
    
    # Test water detection
    print(f"\n💧 Water Detection Test:")
    water_mask_baseline = detect_water_pixels(baseline_ndwi)
    water_mask_current = detect_water_pixels(current_ndwi)
    
    baseline_water = np.sum(water_mask_baseline)
    current_water = np.sum(water_mask_current)
    water_change = current_water - baseline_water
    
    print(f"🌊 Baseline water pixels: {baseline_water:,}")
    print(f"🌊 Current water pixels: {current_water:,}")
    print(f"📈 Water change: {water_change:+,} pixels")
    
    if water_change > 1000:
        print("🚨 Potential leak detected! Significant water increase")
    elif water_change < -1000:
        print("⚠️ Water decrease detected")
    else:
        print("✅ No significant water changes detected")

if __name__ == "__main__":
    test_ndwi_pipeline()
