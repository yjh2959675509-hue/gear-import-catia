"""齿轮 3D 预览 — OpenGL 渲染 v5。

核心: 统一 Mesh + 端盖纯平法线 + 全分辨率边界 + 16 层切片
"""

import math
from collections import namedtuple

from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent, QWheelEvent
from OpenGL.GL import *
from OpenGL.GLU import *
from gear.params import GearParams

MeshData = namedtuple("MeshData", ["vertices", "indices", "normals", "vertex_count", "index_count"])

def _pol(r, a): return r*math.cos(a), r*math.sin(a)
def _dst(x, y): return math.sqrt(x*x+y*y), math.atan2(y, x)
def _rot(pts, th):
    c, s = math.cos(th), math.sin(th)
    return [(x*c-y*s, x*s+y*c) for x, y in pts]


# ── 主构建器 ─────────────────────────────────────

class GearMeshBuilder:
    def __init__(self):
        self._max_steps = 64
        self._arc_step = 0.10
        self._n_slices = 16

    def build(self, p: GearParams):
        Rb, Ra, Rf, B, z = p.Rb, p.Ra, p.Rf, p.face_width, p.z
        pf, cp = max(p.pf, 0.001), 2*math.pi/z
        th_tooth = cp / 2

        # ── 齿形 2D 轮廓 ──
        pts, th_full, th_pitch = [], None, None
        for i in range(self._max_steps):
            phi = math.pi*i/(self._max_steps-1)
            x=Rb*math.cos(phi)+phi*Rb*math.sin(phi)
            y=Rb*math.sin(phi)-phi*Rb*math.cos(phi)
            d, a = _dst(x, y)
            if th_pitch is None and d>=p.R: th_pitch=a; th_full=th_pitch*2+th_tooth
            if th_pitch is not None and a>=th_full/2: break
            pts.append(_pol(Ra,a) if d>=Ra else (_pol(Rf,a) if d<=Rf else (x,y)))
        if th_full is None: th_full=cp*0.6

        half=_rot(pts, -th_full/2)
        tooth=half+[(x,-y) for x,y in reversed(half)]
        rlen=(cp-th_full)*Rf; rpts=[]; nr=int(rlen/self._arc_step)+2
        for i in range(nr):
            th=th_full/2+(cp-th_full)*i/(nr-1); ap=(th-th_full/2)*Rf
            inf=min(rlen-ap,ap)<pf
            r=Rf+(pf-math.sqrt(max(0,pf*pf-(pf-min(ap,rlen-ap))**2))) if inf else Rf
            rpts.append(_pol(r,th))
        mid=len(rpts)//2; unit=rpts[:mid]+tooth+rpts[mid:]
        ring=[]
        for k in range(z): ring+=_rot(unit, k*cp)

        # ── 完整边界 (DP 已在每齿渐开线上做过) ──
        bnd = ring
        M = len(bnd)

        # ── Body + 端面合并: 所有三角形在同一顶点数组中, 无 z-fighting ──
        all_verts = []  # [slice0_pts | slice1_pts | ... | sliceN_pts | bot_center | top_center]
        all_idx = []

        # 侧面切片顶点
        slice_bases = []
        for s in range(self._n_slices):
            y = B * s / (self._n_slices - 1)
            tw = y * math.tan(p.beta) / max(Ra, 0.001)
            ct, st = math.cos(tw), math.sin(tw)
            si = len(all_verts) // 3
            slice_bases.append(si)
            for cx, cy in bnd:
                all_verts.extend([cx*ct - cy*st, y, cx*st + cy*ct])

        # 侧面三角形
        body_start = len(all_idx)
        for s in range(self._n_slices - 1):
            b0, b1 = slice_bases[s], slice_bases[s+1]
            for j in range(M):
                jn = (j + 1) % M
                all_idx.extend([b0+j, b0+jn, b1+j, b1+j, b0+jn, b1+jn])
        body_end = len(all_idx)

        # 底面: 独立顶点 (中心 + 边界副本), 法线纯 -Y → 无放射状条纹
        bot_face_start = len(all_verts) // 3
        # 底面中心
        all_verts.extend([0.0, 0.0, 0.0])
        # 底面边界副本 (与 body 切片0 相同位置, 但独立顶点)
        for j in range(M):
            all_verts.extend([all_verts[slice_bases[0]*3+j*3],
                              all_verts[slice_bases[0]*3+j*3+1],
                              all_verts[slice_bases[0]*3+j*3+2]])
        # 底面三角形
        bot_start = len(all_idx)
        for j in range(M):
            jn = (j + 1) % M
            all_idx.extend([bot_face_start, bot_face_start+1+jn, bot_face_start+1+j])
        bot_end = len(all_idx)

        # 顶面: 独立顶点, 法线纯 +Y
        top_face_start = len(all_verts) // 3
        # 顶面中心
        all_verts.extend([0.0, B, 0.0])
        # 顶面边界副本: 直接复制 body 最后一层切片 (已含扭转), 不再额外扭转
        last_slice = slice_bases[-1]
        for j in range(M):
            all_verts.extend([all_verts[last_slice*3+j*3],
                              all_verts[last_slice*3+j*3+1],
                              all_verts[last_slice*3+j*3+2]])
        # 顶面三角形
        top_start = len(all_idx)
        for j in range(M):
            jn = (j + 1) % M
            all_idx.extend([top_face_start, top_face_start+1+j, top_face_start+1+jn])
        top_end = len(all_idx)

        # ── 法线计算 ──
        nv = len(all_verts) // 3
        norms = [(0.0, 0.0, 0.0)] * nv
        for i in range(0, len(all_idx), 3):
            i0, i1, i2 = all_idx[i], all_idx[i+1], all_idx[i+2]
            v0 = (all_verts[i0*3], all_verts[i0*3+1], all_verts[i0*3+2])
            v1 = (all_verts[i1*3], all_verts[i1*3+1], all_verts[i1*3+2])
            v2 = (all_verts[i2*3], all_verts[i2*3+1], all_verts[i2*3+2])
            e1 = (v1[0]-v0[0], v1[1]-v0[1], v1[2]-v0[2])
            e2 = (v2[0]-v0[0], v2[1]-v0[1], v2[2]-v0[2])
            fn = (e1[1]*e2[2]-e1[2]*e2[1],
                  e1[2]*e2[0]-e1[0]*e2[2],
                  e1[0]*e2[1]-e1[1]*e2[0])
            nl = math.sqrt(fn[0]**2+fn[1]**2+fn[2]**2)
            if nl > 1e-9:
                fn = (fn[0]/nl, fn[1]/nl, fn[2]/nl)
            norms[i0] = (norms[i0][0]+fn[0], norms[i0][1]+fn[1], norms[i0][2]+fn[2])
            norms[i1] = (norms[i1][0]+fn[0], norms[i1][1]+fn[1], norms[i1][2]+fn[2])
            norms[i2] = (norms[i2][0]+fn[0], norms[i2][1]+fn[1], norms[i2][2]+fn[2])
        all_n = []
        for n in norms:
            nl = math.sqrt(n[0]**2+n[1]**2+n[2]**2)
            all_n.extend([n[0]/nl, n[1]/nl, n[2]/nl] if nl > 1e-9 else [0.0, 0.0, 0.0])

        # 覆盖端面顶点法线为纯垂直 → 消除放射状条纹
        # 底面: 中心 + M 个边界点
        for k in range(1 + M):
            idx = bot_face_start + k
            all_n[idx*3] = 0.0; all_n[idx*3+1] = -1.0; all_n[idx*3+2] = 0.0
        # 顶面: 中心 + M 个边界点
        for k in range(1 + M):
            idx = top_face_start + k
            all_n[idx*3] = 0.0; all_n[idx*3+1] = 1.0; all_n[idx*3+2] = 0.0

        seg = {
            'body': (body_start, body_end - body_start),
            'caps_bot': (bot_start, bot_end - bot_start),
            'caps_top': (top_start, top_end - top_start),
        }
        return MeshData(all_verts, all_idx, all_n, nv, len(all_idx)), seg


# ── OpenGL 预览控件 ──────────────────────────────

class GearPreviewWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._params = GearParams()
        self._builder = GearMeshBuilder()
        self._rot_x, self._rot_y, self._rot_z = 30.0, 0.0, -20.0
        self._zoom = 1.0
        self._last_mouse = None
        self._dirty = True
        self._dl_body = self._dl_caps = None
        self.setMinimumSize(200, 200)

    def set_params(self, p):
        self._params = p; self._dirty = True; self.update()

    def initializeGL(self):
        # 暗背景, 高对比度
        glClearColor(0.38, 0.38, 0.40, 1.0)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glDisable(GL_CULL_FACE)
        self._lights()

    def _lights(self):
        glEnable(GL_LIGHTING)
        # ── 环境光: 极低, 避免洗白 ──
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.15, 0.15, 0.17, 1.0])

        # ── 主光 (Key): 前右上方 ──
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.8, 1.2, 0.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.82, 0.82, 0.84, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0.55, 0.55, 0.55, 1.0])

        # ── 补光 (Fill): 左下方, 柔化阴影 ──
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, [-0.7, -0.2, 0.6, 0.0])
        glLightfv(GL_LIGHT1, GL_DIFFUSE,  [0.42, 0.42, 0.44, 1.0])

        # ── 逆光 (Rim): 后方, 勾勒边缘 ──
        glEnable(GL_LIGHT2)
        glLightfv(GL_LIGHT2, GL_POSITION, [0.0, 0.3, -1.0, 0.0])
        glLightfv(GL_LIGHT2, GL_DIFFUSE,  [0.3, 0.3, 0.32, 1.0])

        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        # 高光: 中等强度 + 中等锐度
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR,  [0.28, 0.28, 0.30, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 35.0)

    def resizeGL(self, w, h):
        if w <= 0 or h <= 0:
            return
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        r = max(self._params.Ra, 1)
        gluPerspective(35, w/h, max(r*0.01, 0.5), r*50)
        glMatrixMode(GL_MODELVIEW)
        self._lights()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        r, B = max(self._params.Ra, 1), self._params.face_width
        gluLookAt(r*1.4, B*0.5+r*0.7, r*2.8, 0, B*0.5, 0, 0, 1, 0)
        glRotatef(self._rot_x, 1, 0, 0)
        glRotatef(self._rot_y, 0, 1, 0)
        glRotatef(self._rot_z, 0, 0, 1)
        glScalef(self._zoom, self._zoom, self._zoom)

        if self._dirty:
            self._rebuild()
            self._dirty = False

        if self._dl_body:
            # 三部分在同一 mesh 中, 无 z-fighting
            glCallList(self._dl_body)
            glCallList(self._dl_caps)

    def _rebuild(self):
        mesh, seg = self._builder.build(self._params)

        def _dl(ids, color):
            dl = glGenLists(1)
            glNewList(dl, GL_COMPILE)
            glColor3f(*color)
            glBegin(GL_TRIANGLES)
            v, n, ii = mesh.vertices, mesh.normals, mesh.indices
            for i in range(0, len(ids), 3):
                for k in range(3):
                    j = ii[ids[i+k]]
                    glNormal3f(n[j*3], n[j*3+1], n[j*3+2])
                    glVertex3f(v[j*3], v[j*3+1], v[j*3+2])
            glEnd()
            glEndList()
            return dl

        for d in [self._dl_body, self._dl_caps]:
            if d is not None:
                glDeleteLists(d, 1)

        b = list(range(seg['body'][0], seg['body'][0]+seg['body'][1]))
        cb = list(range(seg['caps_bot'][0], seg['caps_bot'][0]+seg['caps_bot'][1]))
        ct = list(range(seg['caps_top'][0], seg['caps_top'][0]+seg['caps_top'][1]))
        self._dl_body = _dl(b, (0.72, 0.71, 0.74))
        self._dl_caps = _dl(cb + ct, (0.72, 0.71, 0.74))

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._last_mouse = (e.x(), e.y())

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton and self._last_mouse:
            dx = e.x() - self._last_mouse[0]
            dy = e.y() - self._last_mouse[1]
            self._rot_y += dx * 0.4
            self._rot_x += dy * 0.4
            self._last_mouse = (e.x(), e.y())
            self.update()

    def mouseReleaseEvent(self, e):
        self._last_mouse = None

    def wheelEvent(self, e):
        self._zoom *= 1.001 ** e.angleDelta().y()
        self._zoom = max(0.3, min(3.0, self._zoom))
        self.update()
