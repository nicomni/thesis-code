import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Literal, Optional, cast

from osgeo import ogr

from thesis import osm

_logger = logging.getLogger(__name__)

FileName = str

DEFAULT_OSM_CONFIG = "osmconf.ini"


# Singleton
class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        osm_conf_path: Optional[Path] = Path(DEFAULT_OSM_CONFIG),
        osm_max_tmpfile_size: int = 4000,
    ):
        if not hasattr(self, "_initialized"):
            self._osm_conf_path = osm_conf_path
            self._osm_max_tmpfile_size = osm_max_tmpfile_size
            tmp_fd = None
            try:
                tmp_fd, osm_out_tmp = tempfile.mkstemp(suffix=".osm.pbf")
            finally:
                if tmp_fd:
                    os.close(tmp_fd)
            self._osm_out_tmp = Path(osm_out_tmp)
            self._initialized = True
        else:
            _logger.debug("Config already initialized. Skipping reinitialization.")

    @property
    def osm_conf_path(self) -> Optional[Path]:
        return self._osm_conf_path

    @property
    def osm_max_tmpfile_size(self) -> int:
        return self._osm_max_tmpfile_size

    @property
    def osm_out_tmp(self) -> Path:
        return self._osm_out_tmp


def convert_osm_to_gpkg(osm_file_path: Path, gpkg_out_path: Path):
    """Convert osm file to gpkg file using `ogr2ogr`.

    Requires `ogr2ogr` to be in $PATH.
    """
    if gpkg_out_path.exists():
        _logger.error(f"The GPKG output file already exists: {gpkg_out_path}")
        raise RuntimeError
    config = Config()
    OGR_CONFIG = {
        "OSM_MAX_TMPFILE_SIZE": str(config.osm_max_tmpfile_size),
    }

    if config.osm_conf_path:
        OGR_CONFIG["OSM_CONFIG_FILE"] = str(config.osm_conf_path)

    ogr2ogr_path = shutil.which("ogr2ogr")
    if ogr2ogr_path is None:
        raise RuntimeError("ogr2ogr not found in the PATH")
    command: list[str] = [
        ogr2ogr_path,
        "-f",
        "GPKG",
        "-if",
        "OSM",
        "-preserve_fid",
        "-overwrite",
        str(gpkg_out_path),
        str(osm_file_path),
    ]
    _logger.debug(
        f"Executing command: `{' '.join(command)}`. Using variables: {OGR_CONFIG}"
    )
    with subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=2,
        env=OGR_CONFIG,
    ) as proc:
        while proc.poll() is None:
            continue
        outb, errb = proc.communicate()
        outs, errs = outb.decode("utf-8"), errb.decode("utf-8")

        if len(outs) > 0:
            _logger.debug(f"Output from ogr2ogr: \n\t{outs}")

        if len(errs) > 0:
            _logger.error(f"Error from ogr2ogr: \n\t{errs}")
        else:
            _logger.info("ogr2ogr ran without errors.")


def get_all_features(gpkg_fpath: FileName, layer_name: str):
    """Get all features from a layer in a gpkg file."""
    with ogr.Open(gpkg_fpath) as ds:
        layer = cast(ogr.Layer, ds.GetLayerByName(layer_name))
        return [cast(ogr.Feature, feat) for feat in layer]


Delete = tuple[Literal[osm.ChangeType.DELETE], ogr.Feature]
Modify = tuple[Literal[osm.ChangeType.MODIFY], ogr.Feature, ogr.Feature]
Create = tuple[Literal[osm.ChangeType.CREATE], ogr.Feature]


def apply_changes(osm_fpath: Path, osc_fpath: Path) -> None:
    """Apply changes from osc file to osm file.

    Overwrites the input osm file.
    Requires `osmium` to be in $PATH.
    """
    config = Config()
    osm_tmp_out = config.osm_out_tmp

    def get_command() -> list[str]:
        osmium_cmd = shutil.which("osmium")
        if osmium_cmd is None:
            raise RuntimeError("osmium not found in path")
        return [
            osmium_cmd,
            "apply-changes",
            "-f",
            "pbf",
            "--overwrite",
            "-o",
            str(osm_tmp_out),
            str(osm_fpath),
            str(osc_fpath),
        ]

    command = get_command()
    with subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ) as proc:
        _logger.debug(f"Applying change file with: `{' '.join(command)}`")
        while proc.poll() is None:
            continue
        outb, errb = proc.communicate()
        outs, errs = outb.decode("utf-8"), errb.decode("utf-8")

        if len(outs) > 0:
            _logger.debug(f"Output from osmium: \n\t{outs}")

        if len(errs) > 0:
            _logger.error(f"Error from osmium: \n\t{errs}")

        if proc.returncode != 0:
            raise RuntimeError(
                f"Applying changes failed with return code {proc.returncode}."
            )

    _logger.debug("Copying temporary osm file to output file.")
    shutil.copy(osm_tmp_out, osm_fpath)
    _logger.info(f"Applied changes and wrote to file: {osm_fpath}")
