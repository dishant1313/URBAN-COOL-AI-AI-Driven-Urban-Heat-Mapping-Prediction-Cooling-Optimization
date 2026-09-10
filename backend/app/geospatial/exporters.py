"""
Geospatial Data Exporter for URBAN-COOL AI.

Exports the processed master dataset into multiple production formats:
1. GeoParquet (.parquet): High-efficiency columnar spatial format.
2. GeoJSON (.geojson): Standard web GIS format.
3. CSV (.csv): Tabular ML dataset with latitude/longitude and geometry WKT.
4. Validation Report (.json): Validation summary report.
"""

import os
import json
import logging
import geopandas as gpd
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("urban_cool_exporters")


def export_master_dataset(
    gdf_master: gpd.GeoDataFrame,
    metadata: Dict[str, Any],
    validation_report: Dict[str, Any],
    output_dir: Optional[str] = None,
    file_prefix: str = "pune_master_100m"
) -> Dict[str, str]:
    """
    Exports master dataset and returns absolute paths of generated files.
    """
    if output_dir:
        out_path = Path(output_dir)
    else:
        # Resolve to data/processed
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        out_path = base_dir / "data" / "processed"

    out_path.mkdir(parents=True, exist_ok=True)

    generated_files = {}

    # 1. GeoJSON Export
    geojson_file = out_path / f"{file_prefix}.geojson"
    gdf_master.to_file(geojson_file, driver="GeoJSON")
    generated_files["geojson"] = str(geojson_file)
    logger.info(f"Exported GeoJSON to: {geojson_file}")

    # 2. GeoParquet Export
    try:
        parquet_file = out_path / f"{file_prefix}.parquet"
        gdf_master.to_parquet(parquet_file)
        generated_files["geoparquet"] = str(parquet_file)
        logger.info(f"Exported GeoParquet to: {parquet_file}")
    except Exception as e:
        logger.warning(f"GeoParquet export warning: {e}")

    # 3. CSV Export
    csv_file = out_path / f"{file_prefix}.csv"
    df_csv = gdf_master.copy()
    df_csv["geometry_wkt"] = df_csv.geometry.to_wkt()
    df_csv_export = df_csv.drop(columns=["geometry"])
    df_csv_export.to_csv(csv_file, index=False)
    generated_files["csv"] = str(csv_file)
    logger.info(f"Exported CSV to: {csv_file}")

    # 4. Metadata & Validation Report Export
    report_file = out_path / "validation_report.json"
    full_report = {
        "dataset_metadata": metadata,
        "validation_summary": validation_report,
        "exported_files": generated_files
    }
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)
    generated_files["validation_report"] = str(report_file)
    logger.info(f"Exported Validation Report to: {report_file}")

    return generated_files
