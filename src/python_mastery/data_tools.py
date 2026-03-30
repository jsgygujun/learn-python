"""数据处理工具函数"""
from typing import Any


def flatten(nested: list[list[Any]]) -> list[Any]:
    """扁平化嵌套列表"""
    return [item for sublist in nested for item in sublist]


def group_by(items: list[dict], key: str) -> dict[Any, list[dict]]:
    """按指定键分组"""
    result: dict[Any, list[dict]] = {}
    for item in items:
        k = item[key]
        if k not in result:
            result[k] = []
        result[k].append(item)
    return result


def safe_get(data: dict, *keys: str, default: Any = None) -> Any:
    """安全获取嵌套字典的值"""
    for k in keys:
        if isinstance(data, dict):
            data = data.get(k, default)
        else:
            return default
    return data


# 测试
if __name__ == "__main__":
    # flatten
    print(flatten([[1, 2], [3, 4], [5]]))  # [1, 2, 3, 4, 5]

    # group_by
    users = [
        {"name": "Alice", "dept": "Eng"},
        {"name": "Bob", "dept": "Eng"},
        {"name": "Charlie", "dept": "Sales"},
    ]
    print(group_by(users, "dept"))

    # safe_get
    data = {"user": {"profile": {"name": "Alice"}}}
    print(safe_get(data, "user", "profile", "name"))  # Alice
    print(safe_get(data, "user", "missing", default="N/A"))  # N/A