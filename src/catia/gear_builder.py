"""CATIA 齿轮几何体构建器。

将参考代码 cyl_gear.vb 的算法完整平移为 Python COM 调用。

关键顺序 (必须严格遵守):
  1. 创建 HybridBody + 线框
  2. 创建 Body + 实体 (Pad → Pocket/Slot → Pattern)
  3. Body 保留独立 (不 merge 到 MainBody)
"""

import math
import win32com.client
from typing import Tuple, Dict

from gear.params import GearParams
from gear.involute import generate_involute_points
from catia.naming import get_next_gear_name

PI = math.pi


class GearBuilder:
    """在 CATIA PartDocument 中构建齿轮."""

    def __init__(self, params: GearParams, partdoc):
        self.p = params
        self.partdoc = partdoc
        self.part = partdoc.Part
        self.hsf = self.part.HybridShapeFactory
        self.sf = self.part.ShapeFactory
        self._wf: Dict = {}  # 线框引用缓存

    def build(self, H: float = 0.0):
        """执行齿轮构建。"""
        B = self.p.face_width
        z = self.p.z

        # Step 1: 命名
        body_name = get_next_gear_name(self.part)

        # Step 2: 构建线框 (必须在创建 Body 之前)
        hb = self._build_wireframe(H, B, body_name)

        # Step 3: 创建实体 Body
        gear_body = self._build_solid(body_name, hb, B, z)

        # Step 4: 回切到 MainBody, 清理
        self.part.InWorkObject = self.part.MainBody
        self.part.Update()

        return gear_body

    # ── 线框构建 ─────────────────────────────────────

    def _build_wireframe(self, H: float, B: float, name: str = ""):
        """构建齿形线框 — 严格遵循 VB 参考代码顺序."""
        p = self.p
        hsf = self.hsf
        part = self.part

        hybrid_bodies = part.HybridBodies
        hb = hybrid_bodies.Add()
        if name:
            hb.Name = name

        # --- 基准点 (0, H+B, 0) ---
        ref_pt = hsf.AddNewPointCoord(0.0, H + B, 0.0)
        hb.AppendHybridShape(ref_pt)
        ref_pt.Name = "基准点"

        # --- 渐开线点 (15个) ---
        points = generate_involute_points(p.Rb, p.Ra, 15)
        t_points = []
        for i, (px, py) in enumerate(points):
            pt = hsf.AddNewPointCoord(-px, H + B, py)
            hb.AppendHybridShape(pt)
            pt.Name = f"point_T{i}"
            t_points.append(pt)

        # --- 渐开线样条 ---
        spline = hsf.AddNewSpline()
        for pt in t_points:
            spline.AddPointWithConstraintExplicit(pt, None, -1.0, 1, None, 0.0)
        hb.AppendHybridShape(spline)

        # --- 设 InWorkObject 为基准点 ---
        part.InWorkObject = ref_pt
        part.Update()

        # --- 参考平面 (ZX 偏移 H+B) ---
        ref1 = part.CreateReferenceFromObject(ref_pt)
        oe = part.OriginElements
        zx_plane = oe.PlaneZX
        ref2_zx = part.CreateReferenceFromObject(zx_plane)
        plane_offset = hsf.AddNewPlaneOffset(ref2_zx, H + B, False)
        ref2 = part.CreateReferenceFromObject(plane_offset)
        hb.AppendHybridShape(plane_offset)
        part.Update()

        # --- 四个圆 ---
        circle_Rf = _circle(hsf, ref1, ref2, p.Rf, "齿根圆_Rf", hb)
        circle_Ra = _circle(hsf, ref1, ref2, p.Ra, "齿顶圆_Ra", hb)
        circle_R = _circle(hsf, ref1, ref2, p.R, "分度圆_R", hb)
        circle_Rb = _circle(hsf, ref1, ref2, p.Rb, "基圆_Rb", hb)

        # --- 样条与分度圆交点 ---
        intersection_pt = hsf.AddNewIntersection(spline, circle_R)
        intersection_pt.PointType = 0
        hb.AppendHybridShape(intersection_pt)
        intersection_pt.Name = "样条与分度圆交点"

        # --- 分度圆上偏移点 (齿槽宽) ---
        # S = PI * m / 2 (标准齿轮: 齿厚 = 齿槽)
        S = math.pi * p.m / 2.0
        p_on_curve = hsf.AddNewPointOnCurveWithReferenceFromDistance(
            circle_R, intersection_pt, S, False)
        p_on_curve.DistanceType = 1
        hb.AppendHybridShape(p_on_curve)
        p_on_curve.Name = "齿厚偏移点"

        # --- 齿厚弦长 ---
        line_chord = hsf.AddNewLinePtPt(intersection_pt, p_on_curve)
        hb.AppendHybridShape(line_chord)
        line_chord.Name = "齿厚弦长"

        # --- 弦长中点 ---
        midpoint = hsf.AddNewPointOnCurveFromPercent(line_chord, 0.5, False)
        hb.AppendHybridShape(midpoint)
        midpoint.Name = "齿厚弦长的中点"

        # --- 齿厚对称线 ---
        sym_line = hsf.AddNewLinePtPt(ref_pt, midpoint)
        hb.AppendHybridShape(sym_line)
        sym_line.Name = "齿厚对称线"

        # --- 0点处切线 ---
        tangent_0 = hsf.AddNewLineTangencyOnSupport(
            spline, t_points[0], ref2, 0.0, abs(p.Rb - p.Rf) + 10, True)
        hb.AppendHybridShape(tangent_0)
        tangent_0.Name = "0点处切线"
        part.Update()

        # --- 齿根圆角 ---
        pf = p.pf
        if p.Rb > p.Rf + pf:
            corner = hsf.AddNewCorner(tangent_0, circle_Rf, None, pf, 1, -1, False)
            corner.DiscriminationIndex = 1; corner.BeginOfCorner = 1
            corner.FirstTangentOrientation = 1; corner.SecondTangentOrientation = -1
        elif p.Rb > p.Rf:
            corner = hsf.AddNewCorner(spline, circle_Rf, None, pf, 1, -1, False)
            corner.DiscriminationIndex = 1; corner.BeginOfCorner = 2
            corner.FirstTangentOrientation = 1; corner.SecondTangentOrientation = -1
        else:
            corner = hsf.AddNewCorner(spline, circle_Rf, None, pf, 1, -1, False)
            corner.DiscriminationIndex = 1; corner.BeginOfCorner = 1
            corner.FirstTangentOrientation = 1; corner.SecondTangentOrientation = -1
        hb.AppendHybridShape(corner)
        corner.Name = "齿根圆角"

        # --- 对称镜像 ---
        sym_spline = hsf.AddNewSymmetry(spline, sym_line)
        sym_spline.VolumeResult = False
        hb.AppendHybridShape(sym_spline)
        sym_spline.Name = "样条线的对称线"

        sym_corner = hsf.AddNewSymmetry(corner, sym_line)
        sym_corner.VolumeResult = False
        hb.AppendHybridShape(sym_corner)
        sym_corner.Name = "齿根圆角镜像"

        # --- 齿根半圆 + Split ---
        half_Rf = hsf.AddNewCircleCtrRadWithAngles(
            ref_pt, ref2, False, p.Rf, 0.0, 180.0)
        half_Rf.SetLimitation(0)
        hb.AppendHybridShape(half_Rf)
        half_Rf.Name = "齿根半圆"

        split1 = hsf.AddNewHybridSplit(half_Rf, corner, -1)
        hsf.GSMVisibility(half_Rf, 0)
        hb.AppendHybridShape(split1)

        split2 = hsf.AddNewHybridSplit(split1, sym_corner, 1)
        hsf.GSMVisibility(split1, 0)
        hb.AppendHybridShape(split2)
        split2.Name = "齿根弧长"

        # --- 齿顶半圆 + 交点 ---
        half_Ra = hsf.AddNewCircleCtrRadWithAngles(
            ref_pt, ref2, False, p.Ra, 0.0, 180.0)
        half_Ra.SetLimitation(0)
        hb.AppendHybridShape(half_Ra)
        half_Ra.Name = "齿顶半圆"

        intersec_Ra = hsf.AddNewIntersection(spline, half_Ra)
        intersec_Ra.PointType = 0
        hb.AppendHybridShape(intersec_Ra)
        intersec_Ra.Name = "样条与齿顶圆交点_1"

        # --- 齿顶直线 ---
        top_mirror = hsf.AddNewSymmetry(t_points[-1], sym_line)
        top_mirror.VolumeResult = False
        hb.AppendHybridShape(top_mirror)
        top_mirror.Name = "顶部镜像点"

        line_top = hsf.AddNewLinePtPt(t_points[-1], top_mirror)
        hb.AppendHybridShape(line_top)
        line_top.Name = "齿槽顶直线"
        part.Update()

        # --- 组装齿形轮廓 ---
        if p.Rb < p.Rf + pf:
            split_right = hsf.AddNewHybridSplit(spline, corner, -1)
            hsf.GSMVisibility(spline, 0)
            hb.AppendHybridShape(split_right)
            split_right.Name = "右侧齿面"

            split_left = hsf.AddNewHybridSplit(sym_spline, sym_corner, -1)
            hsf.GSMVisibility(sym_spline, 0)
            hb.AppendHybridShape(split_left)
            split_left.Name = "左侧齿面"

            assemble = hsf.AddNewJoin(split_right, line_top)
            assemble.AddElement(split_left)
        else:
            split_tangent = hsf.AddNewHybridSplit(tangent_0, corner, -1)
            hb.AppendHybridShape(split_tangent)
            split_tangent.Name = "过度线"

            assemble = hsf.AddNewJoin(spline, line_top)
            assemble.AddElement(sym_spline)

            sym_tangent = hsf.AddNewSymmetry(split_tangent, sym_line)
            sym_tangent.VolumeResult = False
            hb.AppendHybridShape(sym_tangent)
            sym_tangent.Name = "过度线的对称线"

            assemble.AddElement(sym_tangent)
            assemble.AddElement(split_tangent)

        assemble.AddElement(sym_corner)
        assemble.AddElement(split2)
        assemble.AddElement(corner)
        assemble.SetConnex(1)
        assemble.SetManifold(1)
        assemble.SetSimplify(0)
        assemble.SetSuppressMode(0)
        assemble.SetDeviation(0.001)
        assemble.SetAngularToleranceMode(0)
        assemble.SetAngularTolerance(0.5)
        assemble.SetFederationPropagation(0)
        hb.AppendHybridShape(assemble)
        assemble.Name = "齿形"

        # --- 齿轮轴线 ---
        direction = hsf.AddNewDirectionByCoord(0.0, 1.0, 0.0)
        axis_line = hsf.AddNewLinePtDir(ref1, direction, 0.0, B, True)
        hb.AppendHybridShape(axis_line)
        axis_line.Name = "齿轮轴线"

        # --- 设 InWorkObject 为齿根圆 ---
        part.InWorkObject = circle_Rf
        part.Update()

        # 保存引用
        self._wf = {
            "hb": hb,
            "assemble": assemble,
            "circle_Ra": circle_Ra,
            "direction": direction,
            "intersec_Ra": intersec_Ra,
            "axis_line": axis_line,
            "zx_plane": zx_plane,
            "ref1": ref1,
            "helix_pitch": p.P_helix,
        }
        return hb

    # ── 实体构建 ─────────────────────────────────────

    def _build_solid(self, body_name: str, hb, B: float, z: int):
        """创建 Body + Pad/Pocket/Slot + CircPattern."""
        p = self.p
        sf = self.sf
        part = self.part
        wf = self._wf

        # 创建 Body
        bodies = part.Bodies
        gear_body = bodies.Add()
        gear_body.Name = body_name
        part.InWorkObject = gear_body

        # 齿轮毛坯: Pad (from 齿顶圆)
        ref_Ra = part.CreateReferenceFromObject(wf["circle_Ra"])
        pad = sf.AddNewPadFromRef(ref_Ra, B)
        limit = pad.FirstLimit
        limit.Dimension.Value = B
        part.Update()

        # 切齿槽
        ref_none1 = part.CreateReferenceFromName("")
        ref_none2 = part.CreateReferenceFromName("")

        if p.is_helical:
            # 螺旋线 + Slot
            helix = _create_helix(self.hsf, wf, B)
            hb.AppendHybridShape(helix)
            helix.Name = "齿顶圆上螺旋线"
            slot = sf.AddNewSlotFromRef(wf["assemble"], helix)
            slot.ReferenceSurfaceElement = wf["zx_plane"]
        else:
            # Pocket (直齿)
            pocket = sf.AddNewPocketFromRef(wf["assemble"], B)
            pocket.FirstLimit.LimitMode = 1
            slot = pocket

        part.Update()

        # 圆周阵列
        circ_pattern = sf.AddNewCircPattern(
            slot, 1, 2, 20.0, 45.0, 1, 1,
            ref_none1, ref_none2, True, 0.0, True)

        circ_pattern.CircularPatternParameters = 1

        angular_rep = circ_pattern.AngularRepartition
        angular_rep.InstancesCount.Value = z
        angular_rep.AngularSpacing.Value = 360.0 / z
        angular_rep.InstancesCount.Value = z
        circ_pattern.SetRotationAxis(wf["direction"])
        part.Update()

        # 隐藏线框
        sel = self.partdoc.Selection
        sel.Add(hb)
        sel.VisProperties.SetShow(1)
        sel.Clear()

        return gear_body


# ── 辅助函数 ───────────────────────────────────────────

def _circle(hsf, ref_ctr, ref_plane, radius: float, name: str, hb):
    """创建整圆并添加到 HybridBody."""
    c = hsf.AddNewCircleCtrRad(ref_ctr, ref_plane, False, radius)
    c.SetLimitation(1)
    c.Name = name
    hb.AppendHybridShape(c)
    return c


def _create_helix(hsf, wf, B: float):
    """创建螺旋线 (斜齿轮)."""
    helix = hsf.AddNewHelix(
        wf["axis_line"], True, wf["intersec_Ra"],
        wf["helix_pitch"] if "helix_pitch" in wf else 850.86,
        10.0, True, 0.0, 0.0, False)
    helix.PitchLawType = 0
    helix.SetStartingAngle(0.0)
    helix.SetHeight(3 * B)
    return helix
