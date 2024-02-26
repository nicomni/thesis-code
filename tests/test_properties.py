from thesis import properties as props


def test_diff_props():
    props_v1 = {"key1": "value", "key2": "value2", "key3": "value3"}
    props_v2 = {"key1": "value2", "key2": "value2", "key4": "value4"}
    got = list(props.diff(props_v1, props_v2))
    assert (props.ChangeType.UPDATE, "key1", "value2") in got
    assert (props.ChangeType.DELETE, "key3") in got
    assert (props.ChangeType.INSERT, "key4", "value4") in got
