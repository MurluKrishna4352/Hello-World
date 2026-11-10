// Virtual-staging renderer: builds kid-friendly furniture in a camera matched to a real video frame.
// World: x right (along main wall), y up, z towards camera. Metres. Objects are built facing +z with base at y=0.
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

window.__DONE = false;
window.onerror = (m) => { window.__ERR = String(m); };

const q = new URLSearchParams(location.search);
const job = await (await fetch(q.get('job'))).json();

for (const [fam, file, w] of [['Poppins', 'Poppins-Bold.ttf', 700], ['Poppins', 'Poppins-Medium.ttf', 500],
                              ['Inter', 'Inter-ExtraBold.otf', 800], ['Lora', 'Lora-Variable.ttf', 600]]) {
  const ff = new FontFace(fam, `url(/web/fonts/${file})`, { weight: String(w) });
  await ff.load(); document.fonts.add(ff);
}

// ---------------------------------------------------------------- renderer + camera
const W = job.width, H = job.height;
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(W, H);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.setClearColor(0x000000, 0);
document.body.appendChild(renderer.domElement);

const camera = new THREE.PerspectiveCamera();
camera.matrixAutoUpdate = false;
camera.matrixWorldAutoUpdate = false;
camera.matrix.fromArray(job.camera.viewInverse);
camera.matrixWorld.fromArray(job.camera.viewInverse);
camera.matrixWorldInverse.fromArray(job.camera.view);
camera.projectionMatrix.fromArray(job.camera.projection);
camera.projectionMatrixInverse.copy(camera.projectionMatrix).invert();

const scene = new THREE.Scene();
const L = job.light || {};
scene.add(new THREE.HemisphereLight(L.sky || '#fffaf0', L.ground || '#c9b9a0', L.hemi ?? 1.5));
const amb = new THREE.AmbientLight('#ffffff', L.ambient ?? 0.35); scene.add(amb);
const sun = new THREE.DirectionalLight(L.sunColor || '#fff1dc', L.sun ?? 1.8);
const room = job.room || { W: 4, H: 3, D: 6 };
const tgt = new THREE.Vector3(room.W / 2, 0, (room.z0 || 0) + 1.5);
const sd = L.dir || [-0.4, 1.0, 0.6];
sun.position.set(tgt.x + sd[0] * 8, sd[1] * 8, tgt.z + sd[2] * 8);
sun.target.position.copy(tgt);
sun.castShadow = true;
sun.shadow.mapSize.set(4096, 4096);
const sc = sun.shadow.camera; sc.left = -7; sc.right = 7; sc.top = 7; sc.bottom = -7; sc.near = 0.5; sc.far = 30;
sun.shadow.radius = L.shadowRadius ?? 6; sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.02;
scene.add(sun, sun.target);
if (L.fill) { const f = new THREE.PointLight('#fff6e8', L.fill, 0, 1.2); f.position.set(...(L.fillPos || [room.W / 2, room.H - 0.3, 2.5])); scene.add(f); }

// shadow catchers (planes matching the real room surfaces)
function catcher(w, h, pos, rot, opacity) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.ShadowMaterial({ opacity, transparent: true }));
  m.position.set(...pos); m.rotation.set(...rot); m.receiveShadow = true; m.renderOrder = -1; scene.add(m);
}
const z0 = room.z0 || 0, D = room.D || 6;
if (job.catchers !== false) {
  const so = L.shadowOpacity ?? 0.32, x0 = room.x0 || 0;
  catcher(room.W, D, [x0 + room.W / 2, 0.0005, z0 + D / 2], [-Math.PI / 2, 0, 0], so);            // floor
  if (!room.noBack) catcher(room.W, room.H, [x0 + room.W / 2, room.H / 2, z0 + 0.0005], [0, 0, 0], so * 0.8); // back wall
  if (!room.noLeft) catcher(D, room.H, [x0 + 0.0005, room.H / 2, z0 + D / 2], [0, Math.PI / 2, 0], so * 0.8);
  if (!room.noRight) catcher(D, room.H, [x0 + room.W - 0.0005, room.H / 2, z0 + D / 2], [0, -Math.PI / 2, 0], so * 0.8);
}

// ---------------------------------------------------------------- helpers
let seed = 12345;
const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
const C = (c) => new THREE.Color(c);
const matCache = {};
function mat(color, o = {}) {
  const k = JSON.stringify([color, o]);
  if (!matCache[k]) matCache[k] = new THREE.MeshStandardMaterial({ color: C(color), roughness: o.rough ?? 0.6,
    metalness: o.metal ?? 0, emissive: C(o.emissive || '#000000'), emissiveIntensity: o.ei ?? 1, side: o.side ?? THREE.FrontSide,
    transparent: !!o.opacity, opacity: o.opacity ?? 1 });
  return matCache[k];
}
function mesh(geo, m, parent, pos = [0, 0, 0], rot = [0, 0, 0]) {
  const x = new THREE.Mesh(geo, m); x.position.set(...pos); x.rotation.set(...rot);
  x.castShadow = true; x.receiveShadow = true; parent.add(x); return x;
}
function rbox(w, h, d, r = 0.01) { return new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2.01, h / 2.01, d / 2.01)); }
function cyl(rt, rb, h, seg = 24) { return new THREE.CylinderGeometry(rt, rb, h, seg); }

function canvasTex(w, h, draw) {
  const cv = document.createElement('canvas'); cv.width = w; cv.height = h;
  const g = cv.getContext('2d'); draw(g, w, h);
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
}
function rr(g, x, y, w, h, r) { g.beginPath(); g.roundRect(x, y, w, h, r); }
const PAL = ['#ff6b6b', '#ffa94d', '#ffd43b', '#69db7c', '#4dabf7', '#9775fa', '#f783ac', '#38d9a9'];

// ---------------------------------------------------------------- builders (return Group, base y=0, front +z)
const B = {};

B.box = (o) => { const g = new THREE.Group(); const [w, h, d] = o.size; mesh(rbox(w, h, d, o.radius ?? 0.02), mat(o.color || '#fff', o), g, [0, h / 2, 0]); g.userData.depth = d; return g; };

B.table = (o) => {
  const g = new THREE.Group(); const w = o.w ?? 1.2, d = o.d ?? 0.6, h = o.h ?? 0.5;
  const top = o.round ? cyl(w / 2, w / 2, 0.035, 48) : rbox(w, 0.035, d, 0.015);
  mesh(top, mat(o.top || '#ffffff', { rough: 0.4 }), g, [0, h - 0.0175, 0]);
  if (o.edge) mesh(o.round ? cyl(w / 2 + 0.01, w / 2 + 0.01, 0.02, 48) : rbox(w + 0.02, 0.02, d + 0.02, 0.01), mat(o.edge), g, [0, h - 0.045, 0]);
  const lc = mat(o.legs || '#ffd43b', { rough: 0.5 });
  const lx = o.round ? w * 0.3 : w / 2 - 0.06, lz = o.round ? w * 0.3 : d / 2 - 0.06;
  for (const [sx, sz] of [[1, 1], [1, -1], [-1, 1], [-1, -1]]) mesh(cyl(0.022, 0.022, h - 0.035), lc, g, [sx * lx, (h - 0.035) / 2, sz * lz]);
  g.userData.depth = d; return g;
};

B.chair = (o) => {
  const g = new THREE.Group(); const s = o.scale ?? 1, c = mat(o.color || '#4dabf7', { rough: 0.45 });
  const sh = 0.3 * s, sw = 0.3 * s, sdp = 0.3 * s;
  mesh(rbox(sw, 0.03 * s, sdp, 0.012 * s), c, g, [0, sh, 0]);
  mesh(rbox(sw, 0.2 * s, 0.025 * s, 0.012 * s), c, g, [0, sh + 0.17 * s, -sdp / 2 + 0.012 * s], [-0.12, 0, 0]);
  const lc = mat(o.legs || '#dee2e6', { metal: 0.3, rough: 0.4 });
  for (const [sx, sz] of [[1, 1], [1, -1], [-1, 1], [-1, -1]]) mesh(cyl(0.012 * s, 0.012 * s, sh), lc, g, [sx * (sw / 2 - 0.03 * s), sh / 2, sz * (sdp / 2 - 0.03 * s)]);
  if (o.tablet) mesh(rbox(0.32 * s, 0.02 * s, 0.22 * s, 0.01), mat('#f1f3f5'), g, [sw / 2 + 0.05 * s, sh + 0.22 * s, 0.05 * s]);
  g.userData.depth = sdp; return g;
};

B.cubeShelf = (o) => {
  const g = new THREE.Group(); const cols = o.cols ?? 3, rows = o.rows ?? 2, cell = o.cell ?? 0.34, d = o.d ?? 0.32, t = 0.022;
  const W = cols * cell + t, Hh = rows * cell + t + (o.plinth ?? 0.04); const fm = mat(o.color || '#f8f9fa', { rough: 0.5 });
  const y0 = o.plinth ?? 0.04;
  mesh(rbox(W, t, d, 0.006), fm, g, [0, Hh - t / 2, 0]);
  for (let r = 0; r <= rows; r++) mesh(rbox(W, t, d, 0.004), fm, g, [0, y0 + r * cell + t / 2, 0]);
  for (let c = 0; c <= cols; c++) mesh(rbox(t, rows * cell + t, d, 0.004), fm, g, [-W / 2 + c * cell + t / 2, y0 + (rows * cell + t) / 2, 0]);
  mesh(new THREE.BoxGeometry(W, Hh, 0.01), fm, g, [0, Hh / 2, -d / 2 + 0.005]);
  mesh(rbox(W - 0.02, y0, d - 0.02, 0.005), mat(o.plinthColor || '#dee2e6'), g, [0, y0 / 2, 0]);
  const bins = o.bins || PAL; let k = 0;
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
    const cx = -W / 2 + t + c * cell + (cell - t) / 2, cy = y0 + t + r * cell + (cell - t) / 2;
    const mode = (o.fill || 'bins');
    if (mode === 'bins' || (mode === 'mixed' && (r + c) % 2 === 0)) {
      const bc = bins[k++ % bins.length];
      const bh = (cell - t) * 0.9, bw = (cell - t) * 0.94;
      mesh(rbox(bw, bh, d * 0.86, 0.02), mat(bc, { rough: 0.9 }), g, [cx, cy - (cell - t) * 0.05, 0.02]);
      mesh(rbox(bw * 0.3, 0.02, 0.01, 0.005), mat('#ffffff', { rough: 0.9 }), g, [cx, cy + bh * 0.15, d * 0.45 + 0.02]);
    } else if (mode === 'books' || mode === 'mixed') {
      let x = cx - (cell - t) / 2 + 0.01;
      while (x < cx + (cell - t) / 2 - 0.03) {
        const bw2 = 0.015 + rnd() * 0.025, bh2 = (cell - t) * (0.55 + rnd() * 0.35);
        mesh(new THREE.BoxGeometry(bw2, bh2, d * 0.7), mat(PAL[Math.floor(rnd() * PAL.length)], { rough: 0.7 }), g, [x + bw2 / 2, cy - (cell - t) / 2 + bh2 / 2, 0]);
        x += bw2 + 0.002;
      }
    } else if (mode === 'toys') {
      const tc = PAL[Math.floor(rnd() * PAL.length)];
      if (rnd() > 0.5) mesh(new THREE.SphereGeometry((cell - t) * 0.28, 24, 16), mat(tc, { rough: 0.4 }), g, [cx, cy - (cell - t) * 0.2, 0]);
      else for (let i = 0; i < 3; i++) mesh(rbox(0.07, 0.07, 0.07, 0.01), mat(PAL[(k + i) % PAL.length]), g, [cx - 0.07 + i * 0.075, cy - (cell - t) / 2 + 0.035, 0]);
      k++;
    }
  }
  if (o.topToys) {
    mesh(new THREE.SphereGeometry(0.08, 24, 16), mat('#ff6b6b', { rough: 0.35 }), g, [-W / 4, Hh + 0.08, 0]);
    for (let i = 0; i < 4; i++) mesh(rbox(0.07, 0.07, 0.07, 0.01), mat(PAL[i + 2]), g, [W / 6 + (i % 2) * 0.08, Hh + 0.035 + Math.floor(i / 2) * 0.072, 0]);
  }
  g.userData.depth = d; return g;
};

B.slide = (o) => {
  const g = new THREE.Group(); const ph = o.h ?? 0.7, pw = 0.52, pd = 0.42;
  const side = mat(o.side || '#4dabf7', { rough: 0.35 }), chute = mat(o.chute || '#ffd43b', { rough: 0.3 }), step = mat(o.step || '#ff6b6b', { rough: 0.35 });
  // platform + 4 posts + guard rails
  mesh(rbox(pw, 0.05, pd, 0.02), step, g, [0, ph, 0]);
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) mesh(cyl(0.028, 0.028, ph + 0.3, 16), side, g, [sx * (pw / 2), (ph + 0.3) / 2, sz * (pd / 2)]);
  for (const sx of [-1, 1]) { mesh(rbox(0.04, 0.05, pd + 0.06, 0.02), side, g, [sx * pw / 2, ph + 0.3, 0]); mesh(rbox(0.035, 0.18, pd - 0.04, 0.015), side, g, [sx * pw / 2, ph + 0.13, 0]); }
  mesh(rbox(pw + 0.06, 0.05, 0.04, 0.02), side, g, [0, ph + 0.3, -pd / 2]);
  // ladder at the back (two stringers + 3 steps)
  const la = 0.32; const lg = new THREE.Group(); lg.position.set(0, 0, -pd / 2); g.add(lg);
  for (const sx of [-1, 1]) { const st = mesh(rbox(0.04, ph / Math.cos(la) + 0.05, 0.05, 0.02), side, lg, [sx * (pw / 2 - 0.02), ph / 2, -Math.tan(la) * ph / 2]); st.rotation.x = -la; }
  for (let i = 1; i <= 3; i++) { const y = ph * i / 4; mesh(rbox(pw - 0.06, 0.035, 0.14, 0.015), step, lg, [0, y, -Math.tan(la) * (ph - y) - 0.03]); }
  // chute with raised sides
  const len = o.len ?? 1.3, ang = Math.atan2(ph - 0.06, len * 0.93);
  const cg = new THREE.Group(); cg.position.set(0, ph / 2 + 0.03, pd / 2 + (len * Math.cos(ang)) / 2 - 0.02); cg.rotation.x = ang; g.add(cg);
  mesh(rbox(pw - 0.06, 0.03, len, 0.012), chute, cg, [0, 0, 0]);
  for (const sx of [-1, 1]) mesh(rbox(0.035, 0.1, len, 0.016), chute, cg, [sx * (pw / 2 - 0.03), 0.045, 0]);
  const lip = mesh(rbox(pw - 0.04, 0.03, 0.18, 0.012), chute, g, [0, 0.07, pd / 2 + len * Math.cos(ang) + 0.04]);
  g.userData.depth = pd + len; return g;
};

B.ballPit = (o) => {
  const g = new THREE.Group(); const r = o.r ?? 0.6, h = o.h ?? 0.32, t = 0.09;
  const prof = [new THREE.Vector2(r - t, 0), new THREE.Vector2(r, 0), new THREE.Vector2(r, h - 0.03), new THREE.Vector2(r - 0.02, h), new THREE.Vector2(r - t + 0.02, h), new THREE.Vector2(r - t, h - 0.03)];
  mesh(new THREE.LatheGeometry(prof, 64), mat(o.color || '#f783ac', { rough: 0.85 }), g);
  mesh(cyl(r - t, r - t, 0.01, 48), mat(o.color || '#f783ac', { rough: 0.9 }), g, [0, 0.005, 0]);
  const br = 0.036, n = o.n ?? 380;
  const im = new THREE.InstancedMesh(new THREE.SphereGeometry(br, 14, 10), new THREE.MeshStandardMaterial({ roughness: 0.25 }), n);
  const m4 = new THREE.Matrix4(); const cols = o.balls || ['#ff6b6b', '#ffd43b', '#4dabf7', '#69db7c', '#ffffff', '#f783ac'];
  for (let i = 0; i < n; i++) {
    const a = rnd() * Math.PI * 2, rr2 = Math.sqrt(rnd()) * (r - t - br), y = br + rnd() * (h * 0.72);
    m4.makeTranslation(Math.cos(a) * rr2, y, Math.sin(a) * rr2); im.setMatrixAt(i, m4); im.setColorAt(i, C(cols[i % cols.length]));
  }
  im.castShadow = true; im.receiveShadow = true; g.add(im); g.userData.depth = r * 2; return g;
};

B.softBlocks = (o) => {
  const g = new THREE.Group(); const cs = o.colors || ['#ff8787', '#74c0fc', '#ffe066', '#8ce99a', '#b197fc'];
  const items = o.items || [
    ['cube', [0, 0, 0], 0.35, 0], ['cube', [0.4, 0, 0.05], 0.35, 1], ['cube', [0.2, 0.35, 0.02], 0.35, 2],
    ['wedge', [-0.45, 0, 0.1], 0.35, 3], ['cyl', [0.0, 0, 0.5], 0.3, 4], ['arch', [0.6, 0, 0.55], 0.4, 0]];
  for (const [kind, p, s, ci] of items) {
    const m = mat(cs[ci % cs.length], { rough: 0.9 });
    if (kind === 'cube') mesh(rbox(s, s, s, 0.05), m, g, [p[0], p[1] + s / 2, p[2]], [0, (p[2] * 3) % 0.5, 0]);
    else if (kind === 'cyl') mesh(new THREE.CylinderGeometry(s / 2, s / 2, s * 1.6, 32), m, g, [p[0], p[1] + s / 2, p[2]], [0, 0.3, Math.PI / 2]);
    else if (kind === 'wedge') { const sh = new THREE.Shape(); sh.moveTo(0, 0); sh.lineTo(s * 1.4, 0); sh.lineTo(0, s); sh.lineTo(0, 0);
      const geo = new THREE.ExtrudeGeometry(sh, { depth: s, bevelEnabled: true, bevelSize: 0.02, bevelThickness: 0.02, bevelSegments: 3 });
      mesh(geo, m, g, [p[0] - s * 0.7, p[1], p[2] - s / 2]); }
    else if (kind === 'arch') { const sh = new THREE.Shape(); sh.moveTo(-s, 0); sh.lineTo(s, 0); sh.lineTo(s, s * 0.9); sh.lineTo(-s, s * 0.9); sh.lineTo(-s, 0);
      const hole = new THREE.Path(); hole.absarc(0, 0, s * 0.55, 0, Math.PI, false); sh.holes.push(hole);
      const geo = new THREE.ExtrudeGeometry(sh, { depth: s * 0.7, bevelEnabled: true, bevelSize: 0.02, bevelThickness: 0.02, bevelSegments: 3, curveSegments: 24 });
      mesh(geo, m, g, [p[0], p[1], p[2] - s * 0.35], [0, 0.4, 0]); }
  }
  g.userData.depth = 0.8; return g;
};

B.teepee = (o) => {
  const g = new THREE.Group(); const h = o.h ?? 1.55, r = o.r ?? 0.55;
  const tex = canvasTex(1024, 512, (c, w, hh) => { const st = o.stripes || ['#ffffff', '#ffd8a8', '#ffffff', '#a5d8ff'];
    for (let i = 0; i < 16; i++) { c.fillStyle = st[i % st.length]; c.fillRect(0, i * hh / 16, w, hh / 16 + 1); }
    c.fillStyle = 'rgba(255,107,107,0.9)'; for (let x = 0; x < w; x += 64) { c.beginPath(); c.moveTo(x, hh); c.lineTo(x + 32, hh - 50); c.lineTo(x + 64, hh); c.fill(); } });
  const geo = new THREE.ConeGeometry(r, h, 6, 1, true, Math.PI * 0.35, Math.PI * 1.55);
  mesh(geo, new THREE.MeshStandardMaterial({ map: tex, side: THREE.DoubleSide, roughness: 0.95 }), g, [0, h / 2, 0], [0, Math.PI, 0]);
  const pm = mat('#c8a165', { rough: 0.7 });
  for (let i = 0; i < 5; i++) { const a = i / 5 * Math.PI * 2 + 0.3; const p = new THREE.Mesh(cyl(0.012, 0.016, h * 1.25, 8), pm); p.castShadow = true;
    p.position.set(Math.cos(a) * r * 0.42, h * 0.55, Math.sin(a) * r * 0.42); p.lookAt(new THREE.Vector3(0, h * 1.6, 0)); p.rotateX(Math.PI / 2); g.add(p); }
  mesh(cyl(r * 0.8, r * 0.8, 0.06, 32), mat('#ffe8cc', { rough: 0.95 }), g, [0, 0.03, 0]);
  mesh(new THREE.SphereGeometry(0.13, 20, 14).scale(1, 0.55, 1), mat('#ffc9c9', { rough: 0.95 }), g, [0.12, 0.1, 0.1]);
  g.userData.depth = r * 2; return g;
};

B.beanbag = (o) => { const g = new THREE.Group(); const r = o.r ?? 0.33;
  const geo = new THREE.SphereGeometry(r, 40, 24); const p = geo.attributes.position;
  for (let i = 0; i < p.count; i++) { const y = p.getY(i); p.setY(i, y < 0 ? y * 0.45 : y * 0.75 - (Math.abs(p.getX(i)) < r * 0.4 && p.getZ(i) > 0 ? r * 0.12 : 0)); }
  geo.computeVertexNormals(); mesh(geo, mat(o.color || '#ffa94d', { rough: 0.95 }), g, [0, r * 0.45, 0]); g.userData.depth = r * 2; return g; };

B.rug = (o) => { const g = new THREE.Group(); const w = o.w ?? 2, d = o.d ?? 1.5;
  const style = o.style || 'rainbow';
  const tex = canvasTex(2048, Math.round(2048 * d / w), (c, tw, th) => {
    if (style === 'alphabet') { c.fillStyle = o.bg || '#e7f5ff'; c.fillRect(0, 0, tw, th); const L = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split(''); const n = 7, m = Math.ceil(L.length / n);
      const cw = tw / n, ch = th / m; L.forEach((ch2, i) => { const x = (i % n) * cw, y = Math.floor(i / n) * ch; c.fillStyle = PAL[i % PAL.length]; rr(c, x + 10, y + 10, cw - 20, ch - 20, 28); c.fill();
        c.fillStyle = '#fff'; c.font = `700 ${Math.floor(ch * 0.6)}px Poppins`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(ch2, x + cw / 2, y + ch / 2 + 6); });
      c.strokeStyle = '#1c7ed6'; c.lineWidth = 30; c.strokeRect(0, 0, tw, th); }
    else if (style === 'rainbow') { c.fillStyle = '#fff4e6'; c.fillRect(0, 0, tw, th); const cols = ['#ff8787', '#ffc078', '#ffe066', '#8ce99a', '#74c0fc', '#b197fc'];
      cols.forEach((cc, i) => { c.beginPath(); c.strokeStyle = cc; c.lineWidth = th * 0.08; c.arc(tw / 2, th * 0.95, th * (0.75 - i * 0.09), Math.PI, 0); c.stroke(); });
      c.strokeStyle = '#ffa94d'; c.lineWidth = 24; c.strokeRect(12, 12, tw - 24, th - 24); }
    else if (style === 'plain') { c.fillStyle = o.color || '#d0ebff'; c.fillRect(0, 0, tw, th); c.strokeStyle = o.border || '#74c0fc'; c.lineWidth = 40; c.strokeRect(20, 20, tw - 40, th - 40); }
    else if (style === 'road') { c.fillStyle = '#b2f2bb'; c.fillRect(0, 0, tw, th); c.strokeStyle = '#495057'; c.lineWidth = th * 0.16; c.beginPath(); c.moveTo(0, th * 0.5); c.bezierCurveTo(tw * 0.3, th * 0.1, tw * 0.6, th * 0.9, tw, th * 0.45); c.stroke();
      c.setLineDash([40, 30]); c.strokeStyle = '#fff'; c.lineWidth = 8; c.stroke(); c.setLineDash([]); for (let i = 0; i < 6; i++) { c.fillStyle = '#2f9e44'; c.beginPath(); c.arc(tw * (0.1 + i * 0.16), th * (i % 2 ? 0.2 : 0.82), 40, 0, 7); c.fill(); } }
  });
  const m = new THREE.Mesh(o.round ? new THREE.CircleGeometry(w / 2, 64) : new THREE.PlaneGeometry(w, d), new THREE.MeshStandardMaterial({ map: tex, roughness: 1 }));
  m.rotation.x = -Math.PI / 2; m.position.y = 0.006; m.receiveShadow = true; g.add(m); g.userData.depth = d; return g; };

function boardTex(kind, tw, th, o = {}) {
  return canvasTex(tw, th, (c, w, h) => {
    if (kind === 'whiteboard') { c.fillStyle = '#fbfcfd'; c.fillRect(0, 0, w, h); c.font = `700 ${h * 0.22}px Poppins`; c.textBaseline = 'middle';
      const s = o.text || 'A  B  C'; let x = w * 0.08; s.split('').forEach((ch, i) => { c.fillStyle = PAL[i % PAL.length]; c.fillText(ch, x, h * 0.32); x += c.measureText(ch).width; });
      c.font = `500 ${h * 0.13}px Poppins`; c.fillStyle = '#1c7ed6'; c.fillText(o.text2 || '1 + 2 = 3', w * 0.1, h * 0.68);
      c.fillStyle = '#ffd43b'; c.beginPath(); c.arc(w * 0.82, h * 0.6, h * 0.14, 0, 7); c.fill(); c.strokeStyle = '#ffd43b'; c.lineWidth = 8; for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4; c.beginPath(); c.moveTo(w * 0.82 + Math.cos(a) * h * 0.18, h * 0.6 + Math.sin(a) * h * 0.18); c.lineTo(w * 0.82 + Math.cos(a) * h * 0.25, h * 0.6 + Math.sin(a) * h * 0.25); c.stroke(); } }
    else if (kind === 'art') { c.fillStyle = o.bg || '#ffe3e3'; c.fillRect(0, 0, w, h); const n = o.n ?? 6; const cols = Math.ceil(n / 2);
      for (let i = 0; i < n; i++) { const x = (i % cols) * w / cols + w * 0.03, y = Math.floor(i / cols) * h / 2 + h * 0.06, pw = w / cols - w * 0.06, ph = h / 2 - h * 0.12;
        c.save(); c.translate(x + pw / 2, y + ph / 2); c.rotate((rnd() - 0.5) * 0.12); c.fillStyle = '#fff'; c.fillRect(-pw / 2, -ph / 2, pw, ph);
        c.fillStyle = PAL[i % 8]; c.beginPath(); c.arc(-pw * 0.12, -ph * 0.05, ph * 0.22, 0, 7); c.fill(); c.fillStyle = '#69db7c'; c.fillRect(-pw / 2, ph * 0.2, pw, ph * 0.3);
        c.fillStyle = '#ffd43b'; c.beginPath(); c.arc(pw * 0.3, -ph * 0.28, ph * 0.12, 0, 7); c.fill(); c.fillStyle = '#e03131'; c.beginPath(); c.arc(0, -ph / 2 + 6, 7, 0, 7); c.fill(); c.restore(); }
      if (o.title) { c.fillStyle = '#c92a2a'; c.font = `700 ${h * 0.09}px Poppins`; c.textAlign = 'center'; c.fillText(o.title, w / 2, h * 0.98); } }
    else if (kind === 'slide') { const gr = c.createLinearGradient(0, 0, w, h); gr.addColorStop(0, '#f8f9fa'); gr.addColorStop(1, '#e7f5ff'); c.fillStyle = gr; c.fillRect(0, 0, w, h);
      c.fillStyle = '#1971c2'; c.fillRect(0, 0, w, h * 0.16); c.fillStyle = '#fff'; c.font = `700 ${h * 0.08}px Poppins`; c.textBaseline = 'middle'; c.fillText(o.title || 'Teacher Training Programme', w * 0.05, h * 0.08);
      c.fillStyle = '#343a40'; c.font = `500 ${h * 0.065}px Poppins`; (o.lines || ['Early Childhood Care & Education', 'Play-based learning methods', 'Classroom management', 'Child safety & first aid']).forEach((t, i) => { c.fillStyle = PAL[i]; c.beginPath(); c.arc(w * 0.07, h * (0.3 + i * 0.15), h * 0.025, 0, 7); c.fill(); c.fillStyle = '#343a40'; c.fillText(t, w * 0.11, h * (0.3 + i * 0.15)); });
      c.fillStyle = '#ffd43b'; c.beginPath(); c.arc(w * 0.86, h * 0.62, h * 0.16, 0, 7); c.fill(); c.fillStyle = '#ff6b6b'; c.fillRect(w * 0.76, h * 0.8, w * 0.2, h * 0.06); }
    else if (kind === 'welcome') { c.fillStyle = o.bg || '#ffffff'; c.fillRect(0, 0, w, h); c.textAlign = 'center'; c.textBaseline = 'middle'; const s = o.text || 'WELCOME'; c.font = `700 ${h * 0.5}px Poppins`;
      let tw = c.measureText(s).width, x = w / 2 - tw / 2; c.textAlign = 'left'; s.split('').forEach((ch, i) => { c.fillStyle = PAL[i % PAL.length]; c.fillText(ch, x, h * 0.55); x += c.measureText(ch).width; }); }
    else if (kind === 'notice') { c.fillStyle = '#c8a165'; c.fillRect(0, 0, w, h); c.fillStyle = '#b08850'; for (let i = 0; i < 300; i++) c.fillRect(rnd() * w, rnd() * h, 3, 3);
      const items = o.items || ['Timetable', 'Menu', 'Events', 'Notices']; items.forEach((t, i) => { const x = w * 0.05 + (i % 2) * w * 0.48, y = h * 0.08 + Math.floor(i / 2) * h * 0.46;
        c.save(); c.translate(x, y); c.rotate((rnd() - 0.5) * 0.08); c.fillStyle = ['#fff9db', '#e7f5ff', '#ebfbee', '#fff0f6'][i % 4]; c.fillRect(0, 0, w * 0.42, h * 0.38);
        c.fillStyle = '#343a40'; c.font = `700 ${h * 0.07}px Poppins`; c.fillText(t, w * 0.03, h * 0.1); c.fillStyle = '#adb5bd'; for (let l = 0; l < 4; l++) c.fillRect(w * 0.03, h * (0.16 + l * 0.05), w * (0.3 - (l % 2) * 0.08), 6);
        c.fillStyle = '#e03131'; c.beginPath(); c.arc(w * 0.21, 8, 9, 0, 7); c.fill(); c.restore(); }); }
    else if (kind === 'tv') { c.fillStyle = '#111'; c.fillRect(0, 0, w, h); c.fillStyle = '#74c0fc'; c.fillRect(w * 0.03, h * 0.05, w * 0.94, h * 0.9); c.fillStyle = '#ffd43b'; c.beginPath(); c.arc(w * 0.3, h * 0.4, h * 0.18, 0, 7); c.fill(); c.fillStyle = '#69db7c'; c.fillRect(w * 0.03, h * 0.7, w * 0.94, h * 0.25); }
    else if (kind === 'mirror') { const gr = c.createLinearGradient(0, 0, w, h); gr.addColorStop(0, '#dee2e6'); gr.addColorStop(0.5, '#f8f9fa'); gr.addColorStop(1, '#ced4da'); c.fillStyle = gr; c.fillRect(0, 0, w, h); }
    else if (kind === 'blank') { c.fillStyle = o.bg || '#fff'; c.fillRect(0, 0, w, h); }
  });
}

B.board = (o) => { // wall-mounted panel: whiteboard / art / slide / welcome / notice / tv
  const g = new THREE.Group(); const w = o.w ?? 1.5, h = o.h ?? 1.0, t = o.t ?? 0.025, fr = o.frame ?? 0.03;
  if (fr > 0) mesh(rbox(w + fr * 2, h + fr * 2, t, 0.01), mat(o.frameColor || '#adb5bd', { metal: o.frameMetal ?? 0.4, rough: 0.35 }), g, [0, 0, t / 2]);
  const face = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshStandardMaterial({ map: boardTex(o.kind || 'whiteboard', 1600, Math.round(1600 * h / w), o), roughness: o.gloss ? 0.25 : 0.8, emissive: o.glow ? C('#ffffff') : C('#000000'), emissiveIntensity: o.glow ?? 0, emissiveMap: o.glow ? null : null }));
  if (o.glow) face.material.emissiveMap = face.material.map;
  face.position.set(0, 0, t + 0.002); face.receiveShadow = true; g.add(face);
  if (o.tray) mesh(rbox(w * 0.6, 0.03, 0.07, 0.01), mat('#adb5bd', { metal: 0.4 }), g, [0, -h / 2 - fr - 0.015, 0.045]);
  g.userData.depth = t * 2; g.userData.centered = true; return g; };

B.screen = (o) => { const g = new THREE.Group(); const w = o.w ?? 2.0, h = o.h ?? 1.2;
  mesh(rbox(w + 0.16, 0.09, 0.1, 0.03), mat('#f1f3f5', { rough: 0.4 }), g, [0, h / 2 + 0.06, 0.05]);
  const face = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshStandardMaterial({ map: boardTex('slide', 1600, Math.round(1600 * h / w), o), roughness: 0.9, emissive: C('#ffffff'), emissiveIntensity: 0.55 }));
  face.material.emissiveMap = face.material.map; face.position.set(0, 0, 0.06); g.add(face);
  mesh(rbox(w * 0.98, 0.02, 0.02, 0.008), mat('#495057'), g, [0, -h / 2 - 0.01, 0.06]);
  g.userData.depth = 0.12; g.userData.centered = true; return g; };

B.projector = (o) => { const g = new THREE.Group();
  mesh(rbox(0.32, 0.1, 0.26, 0.03), mat('#f8f9fa', { rough: 0.35 }), g, [0, -0.05, 0]);
  mesh(cyl(0.035, 0.035, 0.03, 24), mat('#212529', { rough: 0.2 }), g, [0.08, -0.05, 0.135], [Math.PI / 2, 0, 0]);
  mesh(cyl(0.012, 0.012, o.drop ?? 0.4), mat('#adb5bd', { metal: 0.6 }), g, [0, (o.drop ?? 0.4) / 2, 0]);
  g.userData.depth = 0.26; return g; };

B.cubbies = (o) => { // wall unit: cubby shelf + hooks with bags + bench
  const g = new THREE.Group(); const n = o.n ?? 5, cw = o.cw ?? 0.32, d = 0.3, W = n * cw;
  const wood = mat(o.color || '#f8f9fa', { rough: 0.5 }), acc = o.accent || PAL;
  const yTop = o.top ?? 1.45; const ch = 0.28;
  mesh(rbox(W + 0.04, 0.025, d, 0.006), wood, g, [0, yTop + ch, 0]); mesh(rbox(W + 0.04, 0.025, d, 0.006), wood, g, [0, yTop, 0]);
  for (let i = 0; i <= n; i++) mesh(rbox(0.02, ch, d, 0.004), wood, g, [-W / 2 + i * cw, yTop + ch / 2, 0]);
  mesh(new THREE.BoxGeometry(W + 0.04, ch + 0.02, 0.01), wood, g, [0, yTop + ch / 2, -d / 2]);
  mesh(rbox(W + 0.04, 0.12, 0.02, 0.01), mat(o.rail || '#ffe066', { rough: 0.5 }), g, [0, yTop - 0.2, -d / 2 + 0.01]);
  for (let i = 0; i < n; i++) {
    const x = -W / 2 + cw * (i + 0.5);
    mesh(rbox(cw * 0.75, ch * 0.65, d * 0.7, 0.03), mat(acc[i % acc.length], { rough: 0.9 }), g, [x, yTop + ch * 0.34, 0]);
    mesh(cyl(0.012, 0.012, 0.08, 10), mat('#868e96', { metal: 0.6 }), g, [x, yTop - 0.2, -d / 2 + 0.06], [Math.PI / 2, 0, 0]);
    if (o.bags !== false) { const bc = acc[(i + 3) % acc.length];
      mesh(rbox(0.24, 0.3, 0.1, 0.05), mat(bc, { rough: 0.8 }), g, [x, yTop - 0.42, -d / 2 + 0.08]);
      mesh(rbox(0.16, 0.1, 0.03, 0.02), mat(acc[(i + 5) % acc.length], { rough: 0.8 }), g, [x, yTop - 0.48, -d / 2 + 0.14]);
    }
    const tag = new THREE.Mesh(new THREE.PlaneGeometry(0.12, 0.06), mat('#ffffff', { rough: 0.9 })); tag.position.set(x, yTop - 0.2, -d / 2 + 0.022); g.add(tag);
  }
  if (o.bench !== false) { mesh(rbox(W + 0.04, 0.05, 0.36, 0.015), mat(o.benchColor || '#c8a165', { rough: 0.55 }), g, [0, 0.3, 0.03]);
    for (let i = 0; i < n; i++) { const x = -W / 2 + cw * (i + 0.5); mesh(rbox(cw - 0.03, 0.27, 0.33, 0.008), wood, g, [x, 0.135, 0.03]);
      mesh(rbox(0.1, 0.05, 0.18, 0.02), mat(acc[(i + 2) % acc.length], { rough: 0.6 }), g, [x - 0.06, 0.045, 0.06]); mesh(rbox(0.1, 0.05, 0.18, 0.02), mat(acc[(i + 2) % acc.length], { rough: 0.6 }), g, [x + 0.06, 0.045, 0.06]); } }
  g.userData.depth = 0.36; return g; };

B.shoeRack = (o) => B.cubbies({ ...o, top: 0.9, bags: false, n: o.n ?? 4 });

B.sinkStation = (o) => { const g = new THREE.Group(); const w = o.w ?? 1.1, h = o.h ?? 0.58, d = 0.42;
  mesh(rbox(w, h - 0.04, d, 0.02), mat(o.cabinet || '#ffffff', { rough: 0.45 }), g, [0, (h - 0.04) / 2, 0]);
  for (let i = 0; i < 2; i++) mesh(rbox(w / 2 - 0.03, h - 0.12, 0.012, 0.006), mat(PAL[(o.ci ?? 4) + i], { rough: 0.45 }), g, [-w / 4 + i * w / 2, (h - 0.04) / 2, d / 2 + 0.004]);
  mesh(rbox(w + 0.04, 0.05, d + 0.04, 0.015), mat('#e9ecef', { rough: 0.25 }), g, [0, h - 0.015, 0]);
  for (const sx of [-0.25, 0.25]) { mesh(cyl(0.13, 0.11, 0.06, 32), mat('#ffffff', { rough: 0.15 }), g, [sx * w, h + 0.0, 0.02]);
    const tap = new THREE.Group(); tap.position.set(sx * w, h, -d / 2 + 0.08); g.add(tap); mesh(cyl(0.015, 0.015, 0.16, 12), mat('#ced4da', { metal: 0.9, rough: 0.2 }), tap, [0, 0.08, 0]); mesh(cyl(0.013, 0.013, 0.1, 12), mat('#ced4da', { metal: 0.9, rough: 0.2 }), tap, [0, 0.16, 0.05], [Math.PI / 2, 0, 0]); }
  mesh(rbox(0.07, 0.14, 0.07, 0.02), mat('#ff8787', { rough: 0.3 }), g, [0, h + 0.07, -d / 2 + 0.1]);
  g.userData.depth = d; return g; };

B.stool = (o) => { const g = new THREE.Group(); const c = mat(o.color || '#69db7c', { rough: 0.5 });
  mesh(rbox(0.36, 0.06, 0.24, 0.02), c, g, [0, 0.2, 0]); mesh(rbox(0.36, 0.06, 0.2, 0.02), c, g, [0, 0.1, 0.08]);
  for (const sx of [-1, 1]) mesh(rbox(0.04, 0.23, 0.26, 0.015), c, g, [sx * 0.16, 0.115, 0.02]); g.userData.depth = 0.3; return g; };

B.plant = (o) => { const g = new THREE.Group(); const h = o.h ?? 0.9, pc = mat(o.pot || '#ffffff', { rough: 0.4 });
  mesh(cyl(0.13, 0.1, 0.26, 28), pc, g, [0, 0.13, 0]); const lm = mat(o.leaf || '#40c057', { rough: 0.7 });
  for (let i = 0; i < 9; i++) { const a = i / 9 * Math.PI * 2, lh = h * (0.55 + rnd() * 0.45); const leaf = new THREE.Mesh(new THREE.SphereGeometry(0.05, 12, 8).scale(1, lh / 0.1, 0.35), lm);
    leaf.position.set(Math.cos(a) * 0.05, 0.26 + lh / 2, Math.sin(a) * 0.05); leaf.rotation.set(Math.sin(a) * 0.25, a, Math.cos(a) * 0.25); leaf.castShadow = true; g.add(leaf); }
  g.userData.depth = 0.26; return g; };

B.easel = (o) => { const g = new THREE.Group(); const wd = mat('#e8c08a', { rough: 0.6 });
  for (const sx of [-1, 1]) { const l = mesh(rbox(0.04, 1.2, 0.03, 0.01), wd, g, [sx * 0.25, 0.58, 0.05]); l.rotation.set(-0.15, 0, sx * -0.08); }
  const back = mesh(rbox(0.04, 1.15, 0.03, 0.01), wd, g, [0, 0.55, -0.2]); back.rotation.x = 0.3;
  const paper = new THREE.Mesh(new THREE.PlaneGeometry(0.52, 0.62), new THREE.MeshStandardMaterial({ map: boardTex('art', 520, 620, { n: 1, bg: '#fff' }), roughness: 0.9 }));
  paper.position.set(0, 0.82, 0.09); paper.rotation.x = -0.15; paper.castShadow = true; g.add(paper);
  mesh(rbox(0.6, 0.04, 0.08, 0.01), wd, g, [0, 0.49, 0.12], [-0.15, 0, 0]); g.userData.depth = 0.4; return g; };

B.desk = (o) => { const g = new THREE.Group(); const w = o.w ?? 1.2, d = o.d ?? 0.6, h = o.h ?? 0.75;
  mesh(rbox(w, 0.04, d, 0.012), mat(o.top || '#e9d8bd', { rough: 0.5 }), g, [0, h - 0.02, 0]);
  mesh(rbox(w - 0.04, h - 0.1, 0.02, 0.008), mat(o.panel || '#4dabf7', { rough: 0.5 }), g, [0, (h - 0.04) / 2 + 0.03, -d / 2 + 0.05]);
  for (const sx of [-1, 1]) mesh(rbox(0.04, h - 0.04, d - 0.04, 0.01), mat(o.legs || '#f8f9fa'), g, [sx * (w / 2 - 0.03), (h - 0.04) / 2, 0]);
  if (o.laptop) { mesh(rbox(0.32, 0.015, 0.22, 0.006), mat('#adb5bd', { metal: 0.6 }), g, [0.1, h + 0.008, 0.05]); const sc2 = mesh(rbox(0.32, 0.21, 0.01, 0.006), mat('#495057', { metal: 0.6 }), g, [0.1, h + 0.11, -0.06]); sc2.rotation.x = -0.25; }
  if (o.books) for (let i = 0; i < 3; i++) mesh(rbox(0.2, 0.03, 0.27, 0.004), mat(PAL[i * 2]), g, [-0.35, h + 0.015 + i * 0.031, 0]);
  g.userData.depth = d; return g; };

B.counter = (o) => { // reception desk
  const g = new THREE.Group(); const w = o.w ?? 1.4, h = o.h ?? 0.95, d = o.d ?? 0.5;
  mesh(rbox(w, h - 0.05, d, 0.03), mat(o.color || '#ffffff', { rough: 0.45 }), g, [0, (h - 0.05) / 2, 0]);
  const tex = boardTex('welcome', 1400, 300, { text: o.text || 'WELCOME', bg: o.panel || '#ffffff' });
  const face = new THREE.Mesh(new THREE.PlaneGeometry(w * 0.9, (h - 0.05) * 0.4), new THREE.MeshStandardMaterial({ map: tex, roughness: 0.6 })); face.position.set(0, h * 0.55, d / 2 + 0.003); g.add(face);
  mesh(rbox(w + 0.06, 0.05, d + 0.1, 0.02), mat(o.top || '#e9d8bd', { rough: 0.4 }), g, [0, h - 0.025, 0.02]);
  mesh(rbox(w * 0.98, 0.12, 0.06, 0.02), mat(o.stripe || '#74c0fc', { rough: 0.5 }), g, [0, 0.06, d / 2 + 0.01]);
  if (o.extras !== false) { mesh(cyl(0.05, 0.04, 0.12, 20), mat('#ffa94d'), g, [w * 0.35, h + 0.06, 0]); for (let i = 0; i < 6; i++) mesh(new THREE.SphereGeometry(0.03, 12, 8), mat(PAL[i]), g, [w * 0.35 + (rnd() - 0.5) * 0.06, h + 0.15 + rnd() * 0.06, (rnd() - 0.5) * 0.06]);
    mesh(rbox(0.25, 0.012, 0.18, 0.004), mat('#ffffff'), g, [-w * 0.2, h + 0.006, 0.05]); }
  g.userData.depth = d; return g; };

B.bunting = (o) => { const g = new THREE.Group(); const a = new THREE.Vector3(...o.from), b = new THREE.Vector3(...o.to), sag = o.sag ?? 0.25, n = o.n ?? 14;
  const pts = []; for (let i = 0; i <= 40; i++) { const t = i / 40; const p = a.clone().lerp(b, t); p.y -= sag * 4 * t * (1 - t); pts.push(p); }
  const curve = new THREE.CatmullRomCurve3(pts); const tube = new THREE.Mesh(new THREE.TubeGeometry(curve, 60, 0.004, 6), mat('#868e96')); g.add(tube);
  const dir = b.clone().sub(a); dir.y = 0; dir.normalize(); const yaw = Math.atan2(-dir.z, dir.x);
  for (let i = 0; i < n; i++) { const t = (i + 0.5) / n; const p = curve.getPoint(t); const s = o.size ?? 0.16;
    const shp = new THREE.Shape(); shp.moveTo(-s / 2, 0); shp.lineTo(s / 2, 0); shp.lineTo(0, -s * 1.2); shp.lineTo(-s / 2, 0);
    const f = new THREE.Mesh(new THREE.ShapeGeometry(shp), mat((o.colors || PAL)[i % (o.colors || PAL).length], { side: THREE.DoubleSide, rough: 0.9 }));
    f.position.copy(p); f.rotation.set(0, yaw, 0); f.rotateX(-0.12); f.castShadow = false; g.add(f); }
  tube.castShadow = false;
  g.userData.absolute = true; return g; };

B.cloudLamp = (o) => { const g = new THREE.Group(); const m = mat('#ffffff', { emissive: o.glow || '#fff4d6', ei: 0.9, rough: 0.9 });
  const s = o.s ?? 1; [[0, 0, 0, 0.16], [0.17, -0.02, 0, 0.12], [-0.17, -0.03, 0, 0.11], [0.08, 0.08, 0, 0.12], [-0.08, 0.07, 0, 0.1]].forEach(([x, y, z, r]) => mesh(new THREE.SphereGeometry(r * s, 24, 16), m, g, [x * s, y * s, z * s]));
  mesh(cyl(0.003, 0.003, o.drop ?? 0.5, 6), mat('#495057'), g, [0, (o.drop ?? 0.5) / 2 + 0.12 * s, 0]);
  g.traverse((x) => { x.castShadow = false; }); g.userData.depth = 0; return g; };

B.pendant = (o) => { const g = new THREE.Group(); const sh = new THREE.Mesh(new THREE.SphereGeometry(o.r ?? 0.17, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2),
  new THREE.MeshStandardMaterial({ color: C(o.color || '#ffd43b'), side: THREE.DoubleSide, roughness: 0.5 })); sh.position.y = 0; g.add(sh);
  mesh(new THREE.SphereGeometry(0.05, 16, 10), mat('#ffffff', { emissive: '#fff3bf', ei: 2 }), g, [0, -0.02, 0]);
  mesh(cyl(0.004, 0.004, o.drop ?? 0.6, 6), mat('#343a40'), g, [0, (o.drop ?? 0.6) / 2 + (o.r ?? 0.17) * 0.9, 0]); g.userData.depth = 0; return g; };

B.panelLight = (o) => { const g = new THREE.Group(); const w = o.w ?? 0.6, d = o.d ?? 0.6;
  mesh(rbox(w, 0.03, d, 0.01), mat('#ffffff', { emissive: '#ffffff', ei: o.ei ?? 1.2 }), g, [0, -0.015, 0]); g.traverse((x) => { x.castShadow = false; x.receiveShadow = false; }); g.userData.depth = 0; return g; };

B.books = (o) => { // a row of books along +x from origin, on a shelf
  const g = new THREE.Group(); let x = 0; const len = o.len ?? 0.8, d = o.d ?? 0.2, hmax = o.hmax ?? 0.25;
  while (x < len - 0.03) { const bw = 0.018 + rnd() * 0.03, bh = hmax * (0.6 + rnd() * 0.4); if (o.gaps && rnd() < 0.08) { x += 0.06; continue; }
    const tilt = rnd() < 0.06 ? 0.25 : 0; mesh(new THREE.BoxGeometry(bw, bh, d * (0.75 + rnd() * 0.2)), mat((o.colors || PAL)[Math.floor(rnd() * PAL.length)], { rough: 0.7 }), g, [x + bw / 2, bh / 2, 0], [0, 0, tilt]); x += bw + 0.003; }
  g.userData.depth = d; g.userData.absolute = !!o.absolute; return g; };

B.toyBoxes = (o) => { const g = new THREE.Group(); const n = o.n ?? 3;
  for (let i = 0; i < n; i++) mesh(rbox(o.w ?? 0.3, o.h ?? 0.2, o.d ?? 0.22, 0.03), mat((o.colors || PAL)[(i * 3 + 1) % 8], { rough: 0.85 }), g, [i * ((o.w ?? 0.3) + 0.03), (o.h ?? 0.2) / 2, 0]);
  g.userData.depth = o.d ?? 0.22; return g; };

B.waterDispenser = (o) => { const g = new THREE.Group();
  mesh(rbox(0.3, 0.9, 0.3, 0.03), mat('#f8f9fa', { rough: 0.35 }), g, [0, 0.45, 0]);
  mesh(cyl(0.13, 0.13, 0.42, 32), mat('#a5d8ff', { rough: 0.05, opacity: 0.75 }), g, [0, 1.12, 0]);
  for (const [x, c] of [[-0.06, '#4dabf7'], [0.06, '#ff6b6b']]) mesh(rbox(0.04, 0.05, 0.04, 0.01), mat(c), g, [x, 0.7, 0.16]);
  g.userData.depth = 0.3; return g; };

B.lunchRack = (o) => { const g = new THREE.Group(); const w = o.w ?? 0.9, rows = o.rows ?? 2;
  for (let r = 0; r <= rows; r++) mesh(rbox(w, 0.025, 0.28, 0.006), mat('#f8f9fa'), g, [0, r * 0.25, 0]);
  for (const sx of [-1, 1]) mesh(rbox(0.025, rows * 0.25, 0.28, 0.006), mat('#f8f9fa'), g, [sx * w / 2, rows * 0.125, 0]);
  for (let r = 0; r < rows; r++) for (let i = 0; i < 4; i++) mesh(rbox(0.17, 0.11, 0.2, 0.025), mat(PAL[(r * 4 + i) % 8], { rough: 0.4 }), g, [-w / 2 + 0.13 + i * 0.21, r * 0.25 + 0.07, 0.01]);
  g.userData.depth = 0.28; g.userData.centered = true; return g; };

B.signBox = (o) => { // exterior signboard box with printed face (texture from file)
  const g = new THREE.Group(); const w = o.w, h = o.h, t = o.t ?? 0.08;
  mesh(rbox(w, h, t, 0.02), mat(o.edge || '#1c7ed6', { rough: 0.4 }), g, [0, 0, t / 2]);
  const tex = new THREE.TextureLoader().load(o.src); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  const face = new THREE.Mesh(new THREE.PlaneGeometry(w - 0.02, h - 0.02), new THREE.MeshStandardMaterial({ map: tex, roughness: 0.5, emissive: C('#ffffff'), emissiveIntensity: o.glow ?? 0.15 }));
  face.material.emissiveMap = tex; face.position.z = t + 0.002; g.add(face); g.userData.depth = t * 2; g.userData.centered = true; g.userData.needsTex = tex; return g; };

B.planter = (o) => { const g = new THREE.Group(); const w = o.w ?? 0.5, h = o.h ?? 0.4;
  mesh(rbox(w, h, o.d ?? 0.35, 0.03), mat(o.color || '#ffa94d', { rough: 0.6 }), g, [0, h / 2, 0]);
  const lms = [mat('#37b24d', { rough: 0.8 }), mat('#2f9e44', { rough: 0.8 }), mat('#51cf66', { rough: 0.8 })]; for (let i = 0; i < 26; i++) { const r = 0.045 + rnd() * 0.035; mesh(new THREE.SphereGeometry(r, 12, 8), lms[i % 3], g, [(rnd() - 0.5) * w * 0.85, h + 0.02 + rnd() * 0.16, (rnd() - 0.5) * (o.d ?? 0.35) * 0.8]); }
  if (o.flowers) for (let i = 0; i < 12; i++) { const fx = (rnd() - 0.5) * w * 0.8, fy = h + 0.12 + rnd() * 0.1, fz = (rnd() - 0.5) * 0.18 + 0.06; const fc = mat(['#ff6b6b', '#ffd43b', '#f783ac', '#ffffff', '#ffa94d'][i % 5], { rough: 0.6 }); for (let k = 0; k < 5; k++) { const a = k / 5 * Math.PI * 2; mesh(new THREE.SphereGeometry(0.014, 8, 6), fc, g, [fx + Math.cos(a) * 0.017, fy, fz + Math.sin(a) * 0.017]); } mesh(new THREE.SphereGeometry(0.01, 8, 6), mat('#fab005'), g, [fx, fy + 0.004, fz]); }
  g.userData.depth = o.d ?? 0.35; return g; };

B.mesh = (o) => { const g = new THREE.Group(); g.userData.depth = 0; return g; };

// ---------------------------------------------------------------- placement
const textures = [];
for (const o of job.objects) {
  const f = B[o.type]; if (!f) throw new Error('unknown type ' + o.type);
  if (o.seed) seed = o.seed;
  const g = f(o);
  if (g.userData.needsTex) textures.push(g.userData.needsTex);
  if (!g.userData.absolute) {
    let pos = o.pos ? [...o.pos] : [0, 0, 0], rotY = (o.rotY || 0) * Math.PI / 180;
    if (o.wall) { // place against a wall: u = along-wall coordinate, v = height (bottom, or centre for centered items)
      const d = (g.userData.depth || 0) / 2 + (o.gap ?? 0.005);
      const zw = (room.z0 || 0) + (o.wallOffset || 0);
      if (o.wall === 'back') { pos = [o.u, o.v ?? 0, zw + d]; rotY = 0; }
      else if (o.wall === 'left') { pos = [(room.x0 || 0) + d + (o.wallOffset || 0), o.v ?? 0, o.u]; rotY = Math.PI / 2; }
      else if (o.wall === 'right') { pos = [(room.x0 || 0) + room.W - d - (o.wallOffset || 0), o.v ?? 0, o.u]; rotY = -Math.PI / 2; }
      else if (o.wall === 'front') { pos = [o.u, o.v ?? 0, (room.z0 || 0) + D - d]; rotY = Math.PI; }
      if (g.userData.centered && o.wall) { /* board centre at v */ }
    }
    g.position.set(...pos); g.rotation.y = rotY;
    if (o.scale) g.scale.setScalar(o.scale);
  }
  if (o.noShadow) g.traverse((x) => { x.castShadow = false; });
  scene.add(g);
}
// wait for any image textures
await Promise.all(textures.map((t) => new Promise((res) => { if (t.image && t.image.complete) res(); else { const iv = setInterval(() => { if (t.image && t.image.complete) { clearInterval(iv); t.needsUpdate = true; res(); } }, 30); } })));
await new Promise((r) => setTimeout(r, 50));
renderer.render(scene, camera);
window.__DONE = true;
