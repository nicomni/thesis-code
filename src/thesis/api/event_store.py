from io import BufferedWriter
import logging
import warnings
from pathlib import Path
from typing import Optional, Sequence

from thesis.gisevents import CreationEvent, DeletionEvent, ModificationEvent

logging.basicConfig(level=logging.INFO)

DEFAULT_CONFIG = {
    "event_store_path": Path("events.pbf"),
}

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
