import logging
import warnings
from pathlib import Path
from typing import Optional, Sequence

from thesis.protobuf import (CreationEvent, DeletionEvent,
                                  ModificationEvent)

logging.basicConfig(level=logging.INFO)

DEFAULT_CONFIG = {
    "event_store_path": Path("events.pbf"),
}

_config = DEFAULT_CONFIG.copy()

_configured = False


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


def write_events(events: Sequence[CreationEvent | ModificationEvent | DeletionEvent]):
    global _config
    outpath = _config["event_store_path"]
    with open(outpath, "wb") as event_store:
        for event in events:
            event_store.write(event.SerializeToString())
