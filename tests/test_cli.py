"""Test CLI module."""

from click.testing import CliRunner

from aquaspot.cli import main


def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "AquaSpot pipeline leak detection CLI" in result.output


def test_ingest_command_not_implemented():
    """Test ingest command raises NotImplementedError."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create dummy geojson file
        with open("pipeline.geojson", "w") as f:
            f.write('{"type": "FeatureCollection", "features": []}')

        result = runner.invoke(
            main, ["ingest", "--geojson", "pipeline.geojson", "--date", "2025-07-10"],
        )

        # Should show the error message about not being implemented
        assert result.exit_code != 0


def test_detect_command_not_implemented():
    """Test detect command raises NotImplementedError."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create dummy files
        for filename in ["baseline.tif", "current.tif", "pipeline.geojson"]:
            with open(filename, "w") as f:
                f.write("dummy")

        result = runner.invoke(
            main,
            [
                "detect",
                "--baseline",
                "baseline.tif",
                "--current",
                "current.tif",
                "--pipeline",
                "pipeline.geojson",
            ],
        )

        # Should show the error message about not being implemented
        assert result.exit_code != 0
