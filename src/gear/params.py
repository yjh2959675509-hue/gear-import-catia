"""齿轮参数计算模块。

公式参考：
  - 参考圆半径: R = m * z / 2
  - 基圆半径:   Rb = R * cos(α)
  - 齿根圆半径: Rf = R - 1.25 * m
  - 齿顶圆半径: Ra = R + m
  - 齿槽弧长:   S = m * PI / 2
  - 齿根圆角:   pf = 0.38 * m (直齿轮) / 0.35 * m (斜齿轮)
  - 螺旋线螺距: P_helix = PI * Ra * 2 / tan(β)
"""

import math


class GearParams:
    """直齿/斜齿圆柱齿轮参数。"""

    def __init__(self, m: int = 4, z: int = 20, alpha_deg: float = 20.0,
                 beta_deg: float = 18.0, face_width: float = 10.0,
                 tooth_thickness: float = 18.0):
        self.m = m
        self.z = z
        self.alpha_deg = alpha_deg
        self.beta_deg = beta_deg
        self.face_width = face_width          # 齿宽 — 轴向长度 (参考代码 B)
        self.tooth_thickness = tooth_thickness # 齿厚 — 分度圆齿厚

        self.alpha = math.radians(alpha_deg)
        self.beta = math.radians(beta_deg)

    @property
    def R(self) -> float:
        """分度圆半径. 斜齿轮使用横向模数 (与 VB 参考一致)."""
        if abs(self.beta) < 1e-9:
            return self.m * self.z / 2.0
        return (self.m / math.cos(self.beta)) * self.z / 2.0

    @property
    def pitch_diameter(self) -> float:
        """分度圆直径 d = m * z."""
        return self.m * self.z

    @property
    def Rb(self) -> float:
        """基圆半径."""
        return self.R * math.cos(self.alpha)

    @property
    def Rf(self) -> float:
        """齿根圆半径."""
        return self.R - 1.25 * self.m

    @property
    def Ra(self) -> float:
        """齿顶圆半径."""
        return self.R + self.m

    @property
    def S(self) -> float:
        """分度圆处齿槽弧长."""
        return self.m * math.pi / 2.0

    @property
    def pf(self) -> float:
        """齿根圆角半径."""
        if abs(self.beta) < 1e-9:
            return 0.38 * self.m
        return 0.35 * self.m

    @property
    def P_helix(self) -> float:
        """齿顶圆上螺旋线螺距 (仅斜齿轮)."""
        if abs(self.beta) < 1e-9:
            return 0.0
        return math.pi * self.Ra * 2.0 / math.tan(self.beta)

    @property
    def is_helical(self) -> bool:
        return abs(self.beta) > 1e-9
