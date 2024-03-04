import json
import logging
from datetime import datetime
from typing import Optional, cast

from google.protobuf.timestamp_pb2 import Timestamp
from osgeo import ogr

from thesis import geo, gisevents, utils, geodiff, properties as props
from thesis.api import event_store

_logger = logging.getLogger(__name__)

_validate_creation_event_args = geo.validate_osm_feature


def creation_event(feature: ogr.Feature) -> gisevents.CreationEvent:
    """Create a new Creation event from an ogr feature."""

    try:
        _validate_creation_event_args(feature)
    except Exception:
        raise

    # Initialize event
    event = gisevents.CreationEvent()

    # FID
    fid: int = feature.GetFID()
    event.id = fid

    # Timestamp
    osm_timestamp = feature.GetFieldAsISO8601DateTime("osm_timestamp")
    dt = datetime.fromisoformat(osm_timestamp)
    timestamp_msg = Timestamp()
    timestamp_msg.FromDatetime(dt)
    event.timestamp.CopyFrom(timestamp_msg)

    # OSM Version
    osm_version: int = feature.GetFieldAsInteger("osm_version")
    event.version = osm_version

    # Properties (tags)
    all_tags_str: Optional[str] = feature.GetFieldAsString("all_tags")
    if all_tags_str:
        all_tags: dict = json.loads(all_tags_str)
        for key, val in all_tags.items():
            event.properties.key.append(key)
            event.properties.value.append(val)

    geom: ogr.Geometry = feature.GetGeometryRef()
    match geom.GetGeometryType():
        case ogr.wkbPoint:
            point_msg = gisevents.to_point_message(geom)
            event.point.CopyFrom(point_msg)
        case ogr.wkbLineString:
            ls_msg = gisevents.to_linestring_message(geom)
            event.linestring.CopyFrom(ls_msg)
        case ogr.wkbPolygon:
            p_msg = gisevents.to_polygon_message(geom)
            event.polygon.CopyFrom(p_msg)
        case _:
            raise ValueError(f"Unsupported geometry type: {geom.GetGeometryType()}")

    return event


def _validate_modification_args(prev_feature: ogr.Feature, curr_feature: ogr.Feature):
    # Check IDs
    if prev_feature.GetFID() != curr_feature.GetFID():
        raise ValueError("FID mismatch.")

    # Check geom type
    if (
        prev_feature.GetGeometryRef().GetGeometryType()
        != curr_feature.GetGeometryRef().GetGeometryType()
    ):
        gtype1 = prev_feature.GetGeometryRef().GetGeometryName()
        gtype2 = curr_feature.GetGeometryRef().GetGeometryName()
        raise geodiff.GeometryTypeMismatchError(gtype1, gtype2)


def modification_event(
    prev_feature: ogr.Feature, curr_feature: ogr.Feature
) -> gisevents.ModificationEvent:
    """Create a new ModificationEvent from two versions of a feature.

    A modification event is a description of how to transform a feature from
    one version to another.
    The two features must be of the same type and have the same FID.
    The version number of the previous feature must be one less than the
    version number of the current feature.
    """

    try:
        _validate_modification_args(prev_feature, curr_feature)
    except Exception:
        raise

    event = gisevents.ModificationEvent()

    event.id = prev_feature.GetFID()
    event.version = curr_feature.GetFieldAsInteger("osm_version")
    event.timestamp.FromDatetime(
        datetime.fromisoformat(curr_feature.GetFieldAsISO8601DateTime("osm_timestamp"))
    )

    prev_geom = cast(ogr.Geometry, prev_feature.GetGeometryRef())
    curr_geom = cast(ogr.Geometry, curr_feature.GetGeometryRef())

    prev_geom_wkt = cast(str, prev_geom.ExportToWkt())
    curr_geom_wkt = cast(str, curr_geom.ExportToWkt())

    geom_type = cast(int, prev_geom.GetGeometryType())
    match geom_type:
        case ogr.wkbPoint:
            point_diff = geodiff.diff_points(prev_geom_wkt, curr_geom_wkt)
            point_msg = utils.to_point_message(point_diff)
            event.point_patch.CopyFrom(point_msg)
        case ogr.wkbLineString:
            ls_patch = geodiff.diff_linestrings(prev_geom_wkt, curr_geom_wkt)
            ls_patch_msg = utils.to_lspatch_message(ls_patch)
            event.linestring_patch.CopyFrom(ls_patch_msg)
        case _:
            raise TypeError(f"Unsupported geometry type: {geom_type}")

    # Check properties
    prev_props: props.Properties = json.loads(
        prev_feature.GetFieldAsString("all_tags"), object_hook=props.as_string
    )
    curr_props: props.Properties = json.loads(
        curr_feature.GetFieldAsString("all_tags"), object_hook=props.as_string
    )
    if prev_props != curr_props:
        prop_patch = props.diff(prev_props, curr_props)
        event.prop_patch.CopyFrom(utils.to_prop_patch_msg(prop_patch))

    return event


def deletion_event(
    feature: ogr.Feature, timestamp: datetime
) -> gisevents.DeletionEvent:
    """Create a new DeletionEvent from an ogr feature."""
    event = gisevents.DeletionEvent()
    event.id = feature.GetFID()
    event.version = feature.GetFieldAsInteger("osm_version")
    event.timestamp.FromDatetime(timestamp)
    return event


def initialize_eventstore_from_snapshot(gpkg_fpath: str):
    """Initialize event store from gpkg file.

    The gpkg file is considered to be the initial state of the data.
    Thus, all events will be creation events.
    """
    _logger.info("Initializing event store")
    events: list[gisevents.CreationEvent] = []
    with ogr.Open(gpkg_fpath, driver="GPKG") as ds:
        for layer_name in ["points", "lines", "linearrings"]:
            layer = cast(ogr.Layer, ds.GetLayerByName(layer_name))
            feature = cast(ogr.Feature | None, layer.GetNextFeature())
            while feature:
                event = creation_event(feature)
                events.append(event)

    event_store.write_events(*events)
