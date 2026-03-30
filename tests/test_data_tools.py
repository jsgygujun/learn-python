"""测试 data_tools 模块"""
import pytest
from python_mastery.data_tools import flatten, group_by, safe_get


class TestFlatten:
    def test_simple(self):
        assert flatten([[1, 2], [3, 4]]) == [1, 2, 3, 4]

    def test_empty(self):
        assert flatten([]) == []
        assert flatten([[]]) == []

    def test_single(self):
        assert flatten([[1]]) == [1]


class TestGroupBy:
    def test_basic(self):
        items = [
            {"name": "a", "type": "x"},
            {"name": "b", "type": "x"},
            {"name": "c", "type": "y"},
        ]
        result = group_by(items, "type")
        assert len(result["x"]) == 2
        assert len(result["y"]) == 1


class TestSafeGet:
    def test_nested(self):
        data = {"a": {"b": {"c": 1}}}
        assert safe_get(data, "a", "b", "c") == 1

    def test_missing(self):
        data = {"a": 1}
        assert safe_get(data, "b", default="N/A") == "N/A"

    def test_none_default(self):
        assert safe_get({}, "key", default=None) is None