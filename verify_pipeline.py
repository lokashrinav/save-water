#!/usr/bin/env python3
"""
🔍 AquaSpot Pipeline Verification Script
This script performs comprehensive testing to verify the pipeline is working correctly.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import logging

# Import AquaSpot modules
from aquaspot.config import config
from aquaspot.ndwi import calculate_ndwi_from_file, detect_change
import rasterio

def setup_logging():
    """Setup logging for verification"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def verify_data_exists():
    """Verify that satellite data was actually downloaded"""
    print("🔍 Step 1: Verifying Data Download")
    print("=" * 50)
    
    data_dir = Path(config.data_dir)
    
    if not data_dir.exists():
        print("❌ Data directory doesn't exist!")
        return False
    
    # Find all TIFF files
    tiff_files = list(data_dir.rglob("*.tif"))
    print(f"📁 Found {len(tiff_files)} TIFF files:")
    
    total_size = 0
    for tiff_file in tiff_files:
        size_mb = tiff_file.stat().st_size / (1024 * 1024)
        total_size += size_mb
        print(f"  📄 {tiff_file.name}: {size_mb:.1f} MB")
    
    print(f"💾 Total data size: {total_size:.1f} MB")
    
    if total_size < 100:  # Less than 100MB seems suspicious
        print("⚠️  Warning: Data size seems small for satellite imagery")
    else:
        print("✅ Data download verified - good file sizes")
    
    return len(tiff_files) > 0

def verify_image_properties():
    """Verify the satellite images have correct properties"""
    print("\n🖼️  Step 2: Verifying Image Properties")
    print("=" * 50)
    
    data_dir = Path(config.data_dir)
    tiff_files = list(data_dir.rglob("*.tif"))
    
    if not tiff_files:
        print("❌ No TIFF files found!")
        return False
    
    for i, tiff_file in enumerate(tiff_files[:3]):  # Check first 3 files
        print(f"\n📊 Analyzing {tiff_file.name}:")
        
        try:
            with rasterio.open(tiff_file) as src:
                print(f"  📏 Dimensions: {src.width} x {src.height}")
                print(f"  🎨 Bands: {src.count}")
                print(f"  🗺️  CRS: {src.crs}")
                print(f"  📍 Bounds: {src.bounds}")
                
                # Read a small sample to check data
                sample = src.read(1, window=rasterio.windows.Window(0, 0, 100, 100))
                print(f"  📈 Sample data range: {sample.min()} to {sample.max()}")
                print(f"  🔢 Sample data type: {sample.dtype}")
                
                # Check for actual data (not all zeros)
                non_zero_pixels = np.count_nonzero(sample)
                print(f"  ✨ Non-zero pixels in sample: {non_zero_pixels}/10000")
                
                if non_zero_pixels == 0:
                    print("  ⚠️  Warning: Sample area appears to be all zeros")
                else:
                    print("  ✅ Image contains real data")
                    
        except Exception as e:
            print(f"  ❌ Error reading image: {e}")
            return False
    
    return True

def verify_ndwi_calculation():
    """Verify NDWI calculation produces reasonable results"""
    print("\n🌊 Step 3: Verifying NDWI Calculation")
    print("=" * 50)
    
    data_dir = Path(config.data_dir)
    tiff_files = list(data_dir.rglob("*.tif"))
    
    if len(tiff_files) < 1:
        print("❌ Need at least 1 image for NDWI calculation")
        return False
    
    test_file = tiff_files[0]
    print(f"🧮 Calculating NDWI for: {test_file.name}")
    
    try:
        ndwi = calculate_ndwi_from_file(str(test_file))
        
        print(f"📊 NDWI Statistics:")
        print(f"  📏 Shape: {ndwi.shape}")
        print(f"  📈 Range: {ndwi.min():.3f} to {ndwi.max():.3f}")
        print(f"  📊 Mean: {ndwi.mean():.3f}")
        print(f"  📊 Std: {ndwi.std():.3f}")
        
        # NDWI should be between -1 and 1
        if ndwi.min() < -1.1 or ndwi.max() > 1.1:
            print("  ⚠️  Warning: NDWI values outside expected range [-1, 1]")
        else:
            print("  ✅ NDWI values in expected range")
        
        # Check for water pixels (NDWI > threshold)
        water_pixels = np.sum(ndwi > config.ndwi_threshold)
        total_pixels = ndwi.size
        water_percentage = (water_pixels / total_pixels) * 100
        
        print(f"  💧 Water pixels: {water_pixels:,} ({water_percentage:.2f}%)")
        
        if water_percentage == 0:
            print("  ⚠️  Warning: No water detected - might be desert/urban area")
        elif water_percentage > 50:
            print("  ⚠️  Warning: Very high water percentage - check image quality")
        else:
            print("  ✅ Reasonable water percentage detected")
            
        return True
        
    except Exception as e:
        print(f"❌ Error calculating NDWI: {e}")
        return False

def verify_change_detection():
    """Verify change detection between images"""
    print("\n🔄 Step 4: Verifying Change Detection")
    print("=" * 50)
    
    data_dir = Path(config.data_dir)
    tiff_files = list(data_dir.rglob("*.tif"))
    
    if len(tiff_files) < 2:
        print("❌ Need at least 2 images for change detection")
        return False
    
    print(f"🔍 Comparing {tiff_files[0].name} vs {tiff_files[1].name}")
    
    try:
        # Calculate NDWI for both images
        ndwi1 = calculate_ndwi_from_file(str(tiff_files[0]))
        ndwi2 = calculate_ndwi_from_file(str(tiff_files[1]))
        
        # Detect changes
        change_mask, results = detect_change(ndwi1, ndwi2, config.ndwi_threshold)
        
        print(f"📊 Change Detection Results:")
        print(f"  🔄 Total changed pixels: {results['total_changed_pixels']:,}")
        print(f"  💧 New water pixels: {results['new_water_pixels']:,}")
        print(f"  🏜️ Lost water pixels: {results['lost_water_pixels']:,}")
        print(f"  📈 Net water change: {results['new_water_pixels'] - results['lost_water_pixels']:,}")
        
        # Calculate percentages
        total_pixels = ndwi1.size
        change_percentage = (results['total_changed_pixels'] / total_pixels) * 100
        print(f"  📊 Change percentage: {change_percentage:.2f}%")
        
        # Sanity checks
        if results['total_changed_pixels'] == 0:
            print("  ⚠️  Warning: No changes detected - images might be identical")
        elif change_percentage > 80:
            print("  ⚠️  Warning: Very high change percentage - images might be very different")
        else:
            print("  ✅ Reasonable change detection results")
        
        # Check if changes are realistic
        net_change = results['new_water_pixels'] - results['lost_water_pixels']
        if abs(net_change) > total_pixels * 0.1:  # More than 10% net change
            print("  🚨 ALERT: Large net water change detected - potential leak!")
        else:
            print("  ✅ Net water change within normal range")
            
        return True
        
    except Exception as e:
        print(f"❌ Error in change detection: {e}")
        return False

def create_visual_verification():
    """Create visual plots to verify results"""
    print("\n📊 Step 5: Creating Visual Verification")
    print("=" * 50)
    
    data_dir = Path(config.data_dir)
    tiff_files = list(data_dir.rglob("*.tif"))
    
    if len(tiff_files) < 2:
        print("❌ Need at least 2 images for visual verification")
        return False
    
    try:
        # Calculate NDWI for first two images
        print("🧮 Calculating NDWI for visual comparison...")
        ndwi1 = calculate_ndwi_from_file(str(tiff_files[0]))
        ndwi2 = calculate_ndwi_from_file(str(tiff_files[1]))
        
        # Create a quick visualization
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # NDWI images
        im1 = axes[0, 0].imshow(ndwi1[::10, ::10], cmap='RdYlBu', vmin=-1, vmax=1)
        axes[0, 0].set_title(f'NDWI: {tiff_files[0].name}')
        axes[0, 0].axis('off')
        plt.colorbar(im1, ax=axes[0, 0], fraction=0.046)
        
        im2 = axes[0, 1].imshow(ndwi2[::10, ::10], cmap='RdYlBu', vmin=-1, vmax=1)
        axes[0, 1].set_title(f'NDWI: {tiff_files[1].name}')
        axes[0, 1].axis('off')
        plt.colorbar(im2, ax=axes[0, 1], fraction=0.046)
        
        # Water detection
        water1 = ndwi1 > config.ndwi_threshold
        water2 = ndwi2 > config.ndwi_threshold
        
        axes[1, 0].imshow(water1[::10, ::10], cmap='Blues')
        axes[1, 0].set_title('Water Detection (Image 1)')
        axes[1, 0].axis('off')
        
        axes[1, 1].imshow(water2[::10, ::10], cmap='Blues')
        axes[1, 1].set_title('Water Detection (Image 2)')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        
        # Save the plot
        output_path = data_dir / "verification_plot.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"📊 Visual verification saved to: {output_path}")
        
        # Show basic statistics
        water1_count = np.sum(water1)
        water2_count = np.sum(water2)
        total_pixels = water1.size
        
        print(f"📈 Visual Statistics:")
        print(f"  💧 Image 1 water pixels: {water1_count:,} ({water1_count/total_pixels*100:.2f}%)")
        print(f"  💧 Image 2 water pixels: {water2_count:,} ({water2_count/total_pixels*100:.2f}%)")
        print(f"  🔄 Water change: {water2_count - water1_count:,} pixels")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating visual verification: {e}")
        return False

def run_comprehensive_verification():
    """Run all verification steps"""
    print("🔍 AquaSpot Pipeline Verification")
    print("=" * 60)
    print("This script will verify that your pipeline is working correctly.\n")
    
    setup_logging()
    
    # Run all verification steps
    tests = [
        ("Data Download", verify_data_exists),
        ("Image Properties", verify_image_properties),
        ("NDWI Calculation", verify_ndwi_calculation),
        ("Change Detection", verify_change_detection),
        ("Visual Verification", create_visual_verification)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("🏁 VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\n📊 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 SUCCESS: Your AquaSpot pipeline is working correctly!")
        print("\n💡 Next steps:")
        print("  1. Check the visual verification plot")
        print("  2. Try with different threshold values")
        print("  3. Test with your own pipeline GeoJSON")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        print("\n💡 Troubleshooting tips:")
        print("  1. Check your data directory path")
        print("  2. Verify internet connection for downloads")
        print("  3. Check the log messages for details")

if __name__ == "__main__":
    run_comprehensive_verification()
