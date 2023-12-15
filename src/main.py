import os
import subprocess
import time

from alive_progress import alive_bar

extract = "sakskobing"  # sakskobing or denmark

osm_data_dir = "/Users/magganielsen/LocalDocs/Masterprosjekt/OSM"
src_path = os.path.join(osm_data_dir, f"{extract}", f"{extract}-230901.osm.pbf")
proj_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out_dir = os.path.join(proj_root_dir, "output")
dst_path = os.path.join(out_dir, f"{extract}-230901.gpkg")
cleaned_dst_path = os.path.join(out_dir, f"{extract}-230901-cleaned.gpkg")

if __name__ == "__main__":
    # ogr2ogr -f "GPKG" output.gpkg input.osm.pbf
    config = {
        "OSM_CONFIG_FILE": os.path.join(osm_data_dir, "osmconf.ini"),
        "OSM_MAX_TMPFILE_SIZE": "4000",
    }
    os.environ.update(config)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    command = "ogr2ogr"
    args = [
        "-f",
        "GPKG",
        "-preserve_fid",
        dst_path,
        src_path,
    ]
    ### STAGE 1: Convert OSM file to GeoPackage ###
    if not os.path.exists(dst_path):
        with (
            alive_bar(
                monitor=False,
                elapsed="{elapsed}",
                stats=False,
                monitor_end=False,
                stats_end=False,
                elapsed_end="Total time: {elapsed}",
                dual_line=True,
            ) as bar,
            subprocess.Popen(
                [command] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=2,
            ) as proc,
        ):
            assert proc.stdout is not None
            bar.title("Converting OSM to GPKG")
            while proc.poll() is None:
                bar()
                time.sleep(0.02)
        # TODO: Handle incomplete linear ring error. See ogr2ogr stderr output.
        # TODO: Print output from ogr2ogr to console. Both stdout and stderr.

    ### STAGE 2: Clean feature types. Keep only simple points, lines adn polygons.
