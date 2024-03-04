from io import BufferedWriter
import logging
import warnings
from pathlib import Path
from typing import Optional, cast

from osgeo import ogr
from thesis.events import creation_event

from thesis.gisevents import CreationEvent, DeletionEvent, ModificationEvent

DEFAULT_CONFIG = {
    "event_store_path": Path("events.pbf"),
}

_logger = logging.getLogger(__name__)

_config = DEFAULT_CONFIG.copy()
_configured = False
_initialized = False

_writer: BufferedWriter


def configure(config: Optional[dict] = None):
    global _configured
    if _configured:
        warnings.warn(
            "Event store already configured. You should not call configure more than once."
        )
    global _config
    if config:
        _config.update(config)
    _configured = True


def write_events(*events: CreationEvent | ModificationEvent | DeletionEvent):
    if not _initialized:
        raise RuntimeError("Event store not initialized")
    global _writer
    for event in events:
        _writer.write(event.SerializeToString())


def _initialize_from_data(gpkg: str):
    _logger.info(f"Initializing event store from GPKG: {gpkg}")
    with cast(ogr.DataSource, ogr.Open(gpkg)) as ds:
        for i in range(ds.GetLayerCount()):
            layer = ds[i]
            events = map(lambda feature: creation_event(feature), layer)
            write_events(*events)


def init(config: Optional[dict] = None, gpkg: Optional[str] = None):
    global _initialized
    if _initialized:
        _logger.warning("Event store already initialized")
        return -1
    if _configured and config is not None:
        global _config
        _config.update(config)
    else:
        configure(config)

    global _writer
    _writer = open(_config["event_store_path"], "wb").__enter__()
    _initialized = True
    if gpkg:
        _initialize_from_data(gpkg)


def teardown():
    global _initialized
    if _initialized:
        global _writer
        _writer.__exit__(None, None, None)
