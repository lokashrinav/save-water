#!/usr/bin/env python3
"""
🎯 AquaSpot Usage Examples

This shows you how to use the AquaSpot pipeline leak detection system
that you've just built!
"""

from datetime import datetime
from pathlib import Path

# Example 1: Check what we built
print("🚀 AquaSpot Pipeline Leak Detection System")
print("=" * 50)

# Show the configuration
from aquaspot.config import config
print(f"📁 Data directory: {config.data_dir}")
print(f"🌊 NDWI threshold: {config.ndwi_threshold}")
print(f"📏 Min leak area: {config.min_leak_area_m2} m²")
print(f"📍 Pipeline buffer: {config.pipeline_buffer_m} meters")

# Show what was downloaded
data_dir = Path("my_data/2024-06-15")
if data_dir.exists():
    files = list(data_dir.glob("*.tif"))
    print(f"\n📥 Downloaded {len(files)} Sentinel-2 files:")
    for file in files:
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"  📄 {file.name} ({size_mb:.1f} MB)")

# Example 2: Show CLI commands you can run
print(f"\n🔧 CLI Commands you can run:")
print("=" * 30)
print("# Show help:")
print('python -c "from aquaspot.cli import main; main()" --help')

print("\n# Download imagery for a pipeline:")
print('python -c "from aquaspot.cli import main; main()" ingest \\')
print("  --geojson example_pipeline.geojson \\")
print("  --date 2024-06-15 \\")
print("  --days-tolerance 30 \\")
print("  --max-cloud-cover 50")

print("\n# Run leak detection (when implemented):")
print('python -c "from aquaspot.cli import main; main()" detect \\')
print("  --baseline my_data/2024-06-15/sentinel2_unknown_date_00_visual.tif \\")
print("  --current my_data/2024-06-15/sentinel2_unknown_date_01_visual.tif \\")
print("  --pipeline example_pipeline.geojson")

# Example 3: Show the LeakCandidate model
print(f"\n🔍 Leak Detection Model:")
print("=" * 25)
from aquaspot.detection import LeakCandidate, rank_candidates

# Create example leak candidates
candidates = [
    LeakCandidate(
        geometry={'type': 'Point', 'coordinates': [-122.4194, 37.7749]},
        score=0.85,
        area_m2=45.0,
        centroid=(-122.4194, 37.7749),
        bounding_box=(-122.42, 37.77, -122.41, 37.78)
    ),
    LeakCandidate(
        geometry={'type': 'Point', 'coordinates': [-122.4094, 37.7849]},
        score=0.72,
        area_m2=32.0,
        centroid=(-122.4094, 37.7849),
        bounding_box=(-122.41, 37.78, -122.40, 37.79)
    )
]

print("Example leak candidates:")
for i, candidate in enumerate(candidates, 1):
    print(f"  🚨 Candidate {i}: Score={candidate.score}, Area={candidate.area_m2}m²")

# Test ranking function
top_candidates = rank_candidates(candidates, min_area=25, top_k=5)
print(f"Top candidates (area >= 25m²): {len(top_candidates)} found")

print(f"\n✅ AquaSpot is ready for the next implementation phase!")
print("🔄 Next: Implement NDWI calculation and change detection algorithms")
