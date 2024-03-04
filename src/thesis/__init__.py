from osgeo import ogr as _ogr
import logging

_ogr.UseExceptions()

logging.basicConfig(
    filename="thesis.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s: %(message)s",
)
