"""
Command-line interface for AquaSpot.

Provides CLI commands for pipeline leak detection operations.
"""

import logging
from datetime import datetime
from pathlib import Path

import click

from aquaspot.config import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def main(verbose: bool) -> None:
    """AquaSpot pipeline leak detection CLI."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")


@main.command()
@click.option(
    "--geojson",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to pipeline GeoJSON file",
)
@click.option(
    "--date",
    required=True,
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Target date for imagery (YYYY-MM-DD)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output directory (default: DATA_DIR)",
)
@click.option(
    "--days-tolerance",
    type=int,
    default=7,
    help="Days before/after target date to search (default: 7)",
)
@click.option(
    "--max-cloud-cover",
    type=float,
    default=20.0,
    help="Maximum cloud cover percentage (default: 20)",
)
def ingest(
    geojson: Path,
    date: datetime,
    output: Path | None,
    days_tolerance: int,
    max_cloud_cover: float,
) -> None:
    """Download Sentinel-2 imagery for pipeline monitoring."""
    from .ingestion import download_sentinel_tiles, load_pipeline_geojson

    logger.info(f"Starting ingestion for {geojson.name} on {date.strftime('%Y-%m-%d')}")
    click.echo(f"Ingestion started for {geojson.name} on {date.strftime('%Y-%m-%d')}")
    
    # Set output directory
    out_dir = output or config.data_dir
    click.echo(f"Output directory: {out_dir}")
    
    try:
        # Load pipeline geometry and create AOI
        logger.info("Loading pipeline geometry...")
        aoi = load_pipeline_geojson(geojson)
        
        # Download imagery
        logger.info("Searching for Sentinel-2 imagery...")
        downloaded_files = download_sentinel_tiles(
            aoi=aoi,
            date=date,
            out_dir=out_dir,
            days_tolerance=days_tolerance,
            max_cloud_cover=max_cloud_cover,
        )
        
        click.echo(f"\n✅ Successfully downloaded {len(downloaded_files)} files:")
        for file_path in downloaded_files:
            click.echo(f"  📄 {file_path}")
            
        click.echo(f"\n📁 Files saved to: {out_dir / date.strftime('%Y-%m-%d')}")
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        click.echo(f"\n❌ Ingestion failed: {e}")
        raise click.ClickException(str(e))


@main.command()
@click.option(
    "--baseline",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to baseline imagery",
)
@click.option(
    "--current",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to current imagery",
)
@click.option(
    "--pipeline",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to pipeline GeoJSON",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output directory",
)
def detect(baseline: Path, current: Path, pipeline: Path, output: Path | None) -> None:
    """Run leak detection analysis."""
    logger.info(f"Starting detection: baseline={baseline}, current={current}")

    if output is None:
        output = config.data_dir / "results"

    # TODO: Implement detection workflow
    # TODO: Calculate NDWI for both images
    # TODO: Apply masking and change detection
    # TODO: Generate candidates and reports

    click.echo(f"Detection started for {baseline} vs {current}")
    click.echo(f"Pipeline: {pipeline}")
    click.echo(f"Output: {output}")

    msg = "Detection command not yet implemented"
    raise NotImplementedError(msg)


if __name__ == "__main__":
    main()
