from datetime import datetime
import xml.etree.ElementTree as ET

from thesis.osm import ChangeType

NODE_ELEMENT_TAG = "node"


def changed_nodes(osc_file_path: str):
    tree = ET.parse(osc_file_path)
    root = tree.getroot()

    for change in root:
        change_type = ChangeType[change.tag.upper()]
        for element in change:
            if element.tag != NODE_ELEMENT_TAG:
                continue
            node_id = int(element.attrib["id"])
            timestamp = datetime.fromisoformat(element.attrib["timestamp"])
            yield (node_id, change_type, timestamp)
