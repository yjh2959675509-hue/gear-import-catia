"""自动递增命名管理。

每个 CATPart 文件独立计数：扫描已有"齿轮(N)"找到最大编号 + 1。
重名时自动跳到下一个编号。
"""


def get_next_gear_name(part) -> str:
    """扫描 Part 中已有 Bodies 和 HybridBodies，找到下一个可用名称。

    Args:
        part: CATIA Part COM 对象

    Returns:
        "齿轮（N）" 格式的名称
    """
    existing = set()

    # 扫描 Bodies
    try:
        for i in range(1, part.Bodies.Count + 1):
            existing.add(part.Bodies.Item(i).Name)
    except Exception:
        pass

    # 扫描 HybridBodies
    try:
        for i in range(1, part.HybridBodies.Count + 1):
            existing.add(part.HybridBodies.Item(i).Name)
    except Exception:
        pass

    # 找最大编号
    max_n = 0
    for name in existing:
        if name.startswith("齿轮（") and name.endswith("）"):
            try:
                n = int(name[3:-1])
                if n > max_n:
                    max_n = n
            except ValueError:
                continue

    # 返回下一个
    n = max_n + 1
    while f"齿轮（{n}）" in existing:
        n += 1
    return f"齿轮（{n}）"
