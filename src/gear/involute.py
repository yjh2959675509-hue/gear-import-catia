"""渐开线齿廓点生成.

渐开线参数方程 (从基圆展开):
  x(t) = Rb * sin(t) - t*Rb * cos(t)
  y(t) = Rb * cos(t) + t*Rb * sin(t)
其中 t 是展开角, 0 <= t <= t_max.
"""

import math


def generate_involute_points(Rb: float, Ra: float, n_points: int = 15):
    """生成渐开线上的点。

    Args:
        Rb: 基圆半径
        Ra: 齿顶圆半径
        n_points: 点数 (含 t=0, 共 n_points 个点)

    Returns:
        list of (x, y): 渐开线上的点坐标 (未镜像, 右旋齿面)
    """
    if Rb <= 0:
        raise ValueError(f"Rb={Rb} 必须 > 0")

    # 齿顶圆处展开角，扩展到 1.15 倍以确保齿顶弦超出圆柱面
    if Rb > Ra:
        t_max = 0.0
    else:
        t_max = math.sqrt((Ra / Rb) ** 2 - 1.0) * 1.15

    points = []
    for i in range(n_points):
        t = t_max * i / (n_points - 1)
        x = Rb * math.sin(t) - t * Rb * math.cos(t)
        y = Rb * math.cos(t) + t * Rb * math.sin(t)
        points.append((x, y))

    return points
