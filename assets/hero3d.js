/* ============================================================================
   AUGENTIC AI — CINEMATIC WEBGL HERO
   ----------------------------------------------------------------------------
   A single Three.js scene that replaces the old 2D hero canvases:

     · Twin icosahedral lattice cages with silhouette-weighted (fresnel) edges
     · A displaced, self-illuminated core that breathes on simplex noise
     · Integration tiles — the site's own SVG icons rasterised onto beveled
       metal slabs, orbiting on inclined rings, draggable and throwable
     · Proximity energy links with pulses that travel between tiles
     · A pointer-reactive GPU particle field
     · Three-point cinematic lighting + IBL, ACES tone mapping,
       unreal bloom, chromatic aberration, vignette and film grain
     · A "field scan" intro that reveals the lattice from the ground up

   Degrades safely: no WebGL, reduced-motion, or a load failure all leave the
   original CSS/DOM hero untouched.
   ========================================================================= */

import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const hero = document.getElementById('hero');
const canvas = document.getElementById('hero3dCanvas');
if (!hero || !canvas) throw new Error('hero3d: mount points missing');

const REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const MOBILE = window.matchMedia('(max-width: 820px)').matches;

/* ── palette ─────────────────────────────────────────────────────────────── */
const GOLD = new THREE.Color('#D4AF37');
const GOLD_HOT = new THREE.Color('#FFF1A8');
const RIM_COOL = new THREE.Color('#7FA8FF');

const THEME = {
  dark: {
    clear: 0x0a0a0a,
    cage: new THREE.Color('#D4AF37'),
    link: new THREE.Color('#D4AF37'),
    tile: new THREE.Color('#0b0b0c'),
    particle: new THREE.Color('#E9C766'),
    bloom: MOBILE ? 0.55 : 0.7,
    grain: 0.045,
    vignette: 0.62,
    exposure: 1.06,
    cageOpacity: 0.9,
    cageFresnel: 1.35,
    tileMetal: 0.72,
    tileEnv: 1.15,
    tileRough: 0.34,
    particleAlpha: 1,
    iconBase: [0.79, 0.67, 0.37],
    iconHot: [1.0, 0.96, 0.82],
    edgeColor: new THREE.Color('#D4AF37'),
    edgeBase: 0.55,
  },
  light: {
    clear: 0xfafaf7,
    cage: new THREE.Color('#8A6A14'),
    link: new THREE.Color('#7A5F12'),
    tile: new THREE.Color('#17171a'),
    particle: new THREE.Color('#8A6A14'),
    bloom: MOBILE ? 0.14 : 0.2,
    grain: 0.018,
    vignette: 0.26,
    exposure: 1.0,
    cageOpacity: 0.95,
    cageFresnel: 0.8,   // widen the silhouette band — no glow to carry it here
    tileMetal: 0.35,    // keep the slabs reading as cards, not mirrors
    tileEnv: 0.22,
    tileRough: 0.52,
    particleAlpha: 0.8,
    iconBase: [0.34, 0.27, 0.08], // dark icons: nothing to add light to here
    iconHot: [0.62, 0.48, 0.12],
    edgeColor: new THREE.Color('#8A6A14'),
    edgeBase: 0.7,
  },
};
let theme = document.body.classList.contains('light') ? THEME.light : THEME.dark;

/* ── renderer ────────────────────────────────────────────────────────────── */
const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: !MOBILE,
  powerPreference: 'high-performance',
  stencil: false,
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, MOBILE ? 1.5 : 2));
renderer.setSize(hero.offsetWidth, hero.offsetHeight, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = theme.exposure;
renderer.setClearColor(theme.clear, 1);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, hero.offsetWidth / hero.offsetHeight, 0.1, 120);
camera.position.set(0, 0, 16);

/* Image-based lighting so the metal actually reads as metal. */
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

/* ── three-point cinematic lighting ──────────────────────────────────────── */
scene.add(new THREE.HemisphereLight(0xffe9b0, 0x050505, 0.35));

const keyLight = new THREE.DirectionalLight(0xffd98a, 2.4); // warm key, upper right
keyLight.position.set(7, 9, 8);
scene.add(keyLight);

const rimLight = new THREE.DirectionalLight(RIM_COOL, 1.9); // cool rim from behind
rimLight.position.set(-8, 2, -7);
scene.add(rimLight);

const fillLight = new THREE.DirectionalLight(0xffffff, 0.35);
fillLight.position.set(-4, -5, 6);
scene.add(fillLight);

/* Two orbiting practicals drag live speculars across the slabs. */
const practicalA = new THREE.PointLight(0xffc84d, 90, 40, 2);
const practicalB = new THREE.PointLight(0x9fc2ff, 55, 40, 2);
scene.add(practicalA, practicalB);

/* ── shared GLSL: Ashima simplex noise ───────────────────────────────────── */
const SNOISE = /* glsl */ `
vec3 mod289(vec3 x){return x-floor(x*(1.0/289.0))*289.0;}
vec4 mod289(vec4 x){return x-floor(x*(1.0/289.0))*289.0;}
vec4 permute(vec4 x){return mod289(((x*34.0)+1.0)*x);}
vec4 taylorInvSqrt(vec4 r){return 1.79284291400159-0.85373472095314*r;}
float snoise(vec3 v){
  const vec2 C=vec2(1.0/6.0,1.0/3.0); const vec4 D=vec4(0.0,0.5,1.0,2.0);
  vec3 i=floor(v+dot(v,C.yyy)); vec3 x0=v-i+dot(i,C.xxx);
  vec3 g=step(x0.yzx,x0.xyz); vec3 l=1.0-g;
  vec3 i1=min(g.xyz,l.zxy); vec3 i2=max(g.xyz,l.zxy);
  vec3 x1=x0-i1+C.xxx; vec3 x2=x0-i2+C.yyy; vec3 x3=x0-D.yyy;
  i=mod289(i);
  vec4 p=permute(permute(permute(
      i.z+vec4(0.0,i1.z,i2.z,1.0))
    + i.y+vec4(0.0,i1.y,i2.y,1.0))
    + i.x+vec4(0.0,i1.x,i2.x,1.0));
  float n_=0.142857142857; vec3 ns=n_*D.wyz-D.xzx;
  vec4 j=p-49.0*floor(p*ns.z*ns.z);
  vec4 x_=floor(j*ns.z); vec4 y_=floor(j-7.0*x_);
  vec4 x=x_*ns.x+ns.yyyy; vec4 y=y_*ns.x+ns.yyyy; vec4 h=1.0-abs(x)-abs(y);
  vec4 b0=vec4(x.xy,y.xy); vec4 b1=vec4(x.zw,y.zw);
  vec4 s0=floor(b0)*2.0+1.0; vec4 s1=floor(b1)*2.0+1.0; vec4 sh=-step(h,vec4(0.0));
  vec4 a0=b0.xzyw+s0.xzyw*sh.xxyy; vec4 a1=b1.xzyw+s1.xzyw*sh.zzww;
  vec3 p0=vec3(a0.xy,h.x); vec3 p1=vec3(a0.zw,h.y);
  vec3 p2=vec3(a1.xy,h.z); vec3 p3=vec3(a1.zw,h.w);
  vec4 norm=taylorInvSqrt(vec4(dot(p0,p0),dot(p1,p1),dot(p2,p2),dot(p3,p3)));
  p0*=norm.x; p1*=norm.y; p2*=norm.z; p3*=norm.w;
  vec4 m=max(0.6-vec4(dot(x0,x0),dot(x1,x1),dot(x2,x2),dot(x3,x3)),0.0); m=m*m;
  return 42.0*dot(m*m,vec4(dot(p0,x0),dot(p1,x1),dot(p2,x2),dot(p3,x3)));
}`;

/* ── lattice cages ───────────────────────────────────────────────────────── */
/* Edge alpha is weighted by the fresnel term so only the silhouette burns in —
   the cage reads as a glowing orb outline instead of wireframe soup. */
function makeCage(radius, detail, opacity, colour) {
  const geo = new THREE.WireframeGeometry(new THREE.IcosahedronGeometry(radius, detail));
  const mat = new THREE.ShaderMaterial({
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    uniforms: {
      uReveal: { value: -1.4 },
      uOpacity: { value: opacity },
      uColor: { value: colour.clone() },
      uRadius: { value: radius },
      uTime: { value: 0 },
      uFresnel: { value: theme.cageFresnel },
    },
    vertexShader: /* glsl */ `
      varying vec3 vLocal;
      varying vec3 vWorldDir;
      varying vec3 vNormalApprox;
      void main(){
        vLocal = position;
        vec4 world = modelMatrix * vec4(position, 1.0);
        vWorldDir = normalize(world.xyz - cameraPosition);
        vNormalApprox = normalize(mat3(modelMatrix) * normalize(position));
        gl_Position = projectionMatrix * viewMatrix * world;
      }`,
    fragmentShader: /* glsl */ `
      uniform float uReveal, uOpacity, uRadius, uTime, uFresnel;
      uniform vec3 uColor;
      varying vec3 vLocal;
      varying vec3 vWorldDir;
      varying vec3 vNormalApprox;
      void main(){
        // field-scan reveal, bottom to top
        float y = vLocal.y / uRadius;
        float d = uReveal - y;
        float vis  = smoothstep(0.0, 0.10, d);
        float band = exp(-pow(d * 9.0, 2.0));

        // silhouette weighting
        float fres = 1.0 - abs(dot(vNormalApprox, vWorldDir));
        fres = pow(clamp(fres, 0.0, 1.0), uFresnel);

        // slow travelling shimmer around the shell
        float shimmer = 0.75 + 0.25 * sin(vLocal.y * 0.6 + vLocal.x * 0.3 - uTime * 0.9);

        vec3 col = mix(uColor, vec3(1.0, 0.96, 0.82), band * 0.85);
        float a = uOpacity * vis * fres * shimmer + band * fres * 0.9;
        if (a < 0.002) discard;
        gl_FragColor = vec4(col, a);
      }`,
  });
  return new THREE.LineSegments(geo, mat);
}

const cageOuter = makeCage(13.5, MOBILE ? 1 : 2, theme.cageOpacity, theme.cage);
const cageInner = makeCage(7.2, MOBILE ? 1 : 2, theme.cageOpacity * 0.42, theme.cage);
scene.add(cageOuter, cageInner);

/* ── the core ────────────────────────────────────────────────────────────── */
const coreGroup = new THREE.Group();
coreGroup.position.set(0, 0.2, -26);
scene.add(coreGroup);

const coreMat = new THREE.ShaderMaterial({
  transparent: true,
  depthWrite: false,
  blending: THREE.AdditiveBlending,
  uniforms: {
    uTime: { value: 0 },
    uIgnite: { value: 0 },
    uColor: { value: GOLD.clone() },
    uHot: { value: GOLD_HOT.clone() },
  },
  vertexShader: SNOISE + /* glsl */ `
    uniform float uTime;
    varying vec3 vNormalW;
    varying vec3 vViewDir;
    varying float vNoise;
    void main(){
      float n = snoise(normal * 1.9 + vec3(0.0, 0.0, uTime * 0.18));
      vNoise = n;
      vec3 displaced = position + normal * n * 0.09;
      vec4 world = modelMatrix * vec4(displaced, 1.0);
      vNormalW = normalize(mat3(modelMatrix) * normal);
      vViewDir = normalize(cameraPosition - world.xyz);
      gl_Position = projectionMatrix * viewMatrix * world;
    }`,
  fragmentShader: /* glsl */ `
    uniform float uIgnite, uTime;
    uniform vec3 uColor, uHot;
    varying vec3 vNormalW;
    varying vec3 vViewDir;
    varying float vNoise;
    void main(){
      float fres = pow(1.0 - clamp(dot(vNormalW, vViewDir), 0.0, 1.0), 2.6);
      float veins = smoothstep(0.15, 0.75, vNoise);
      float pulse = 0.82 + 0.18 * sin(uTime * 1.3);
      vec3 col = mix(uColor, uHot, veins * 0.65 + fres * 0.35);
      float a = (fres * 0.85 + veins * 0.30) * uIgnite * pulse;
      gl_FragColor = vec4(col * (0.6 + fres), a);
    }`,
});
const coreAura = new THREE.Mesh(new THREE.IcosahedronGeometry(1.7, MOBILE ? 24 : 48), coreMat);
coreGroup.add(coreAura);

/* Hard inner shell — a real lit surface so the core has weight. */
const coreShell = new THREE.Mesh(
  new THREE.IcosahedronGeometry(1.15, 2),
  new THREE.MeshPhysicalMaterial({
    color: 0x0d0d0f,
    metalness: 1,
    roughness: 0.18,
    clearcoat: 1,
    clearcoatRoughness: 0.1,
    envMapIntensity: 1.6,
    emissive: GOLD.clone(),
    emissiveIntensity: 0,
    flatShading: true,
  })
);
coreGroup.add(coreShell);

/* Bloom seed — a soft sprite that gives the bloom pass something to smear. */
const glowTex = (() => {
  const c = document.createElement('canvas');
  c.width = c.height = 256;
  const g = c.getContext('2d').createRadialGradient(128, 128, 0, 128, 128, 128);
  g.addColorStop(0, 'rgba(240,200,110,0.55)');
  g.addColorStop(0.25, 'rgba(212,175,55,0.22)');
  g.addColorStop(0.6, 'rgba(190,150,45,0.07)');
  g.addColorStop(1, 'rgba(212,175,55,0)');
  const ctx = c.getContext('2d');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 256, 256);
  return new THREE.CanvasTexture(c);
})();
const coreGlow = new THREE.Sprite(
  new THREE.SpriteMaterial({ map: glowTex, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, opacity: 0 })
);
coreGlow.scale.set(26, 26, 1);
coreGroup.add(coreGlow);

/* ── integration tiles ───────────────────────────────────────────────────── */
/* The icons are lifted straight out of the existing DOM markup so the 3D scene
   and the no-WebGL fallback can never drift apart. */
function svgToTexture(svgEl, filled) {
  const clone = svgEl.cloneNode(true);
  clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
  clone.setAttribute('width', '160');
  clone.setAttribute('height', '160');
  if (!clone.getAttribute('viewBox')) clone.setAttribute('viewBox', '0 0 24 24');
  if (filled) {
    clone.setAttribute('fill', '#ffffff');
    clone.setAttribute('stroke', 'none');
  } else {
    clone.setAttribute('fill', 'none');
    clone.setAttribute('stroke', '#ffffff');
    clone.setAttribute('stroke-width', clone.getAttribute('stroke-width') || '1.5');
    clone.setAttribute('stroke-linecap', 'round');
    clone.setAttribute('stroke-linejoin', 'round');
  }
  const url = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(new XMLSerializer().serializeToString(clone));

  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const c = document.createElement('canvas');
      c.width = c.height = 160;
      const ctx = c.getContext('2d');
      ctx.drawImage(img, 16, 16, 128, 128);
      const tex = new THREE.CanvasTexture(c);
      tex.colorSpace = THREE.SRGBColorSpace;
      tex.anisotropy = renderer.capabilities.getMaxAnisotropy();
      resolve(tex);
    };
    img.onerror = () => resolve(null);
    img.src = url;
  });
}

function roundedRect(w, h, r) {
  const s = new THREE.Shape();
  const x = -w / 2, y = -h / 2;
  s.moveTo(x + r, y);
  s.lineTo(x + w - r, y);
  s.quadraticCurveTo(x + w, y, x + w, y + r);
  s.lineTo(x + w, y + h - r);
  s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  s.lineTo(x + r, y + h);
  s.quadraticCurveTo(x, y + h, x, y + h - r);
  s.lineTo(x, y + r);
  s.quadraticCurveTo(x, y, x + r, y);
  return s;
}

const TILE = 1.05;
const tileGeo = new THREE.ExtrudeGeometry(roundedRect(TILE, TILE, TILE * 0.24), {
  depth: 0.1,
  bevelEnabled: true,
  bevelThickness: 0.035,
  bevelSize: 0.035,
  bevelSegments: 3,
  curveSegments: 14,
});
tileGeo.center();
const tileEdgeGeo = new THREE.EdgesGeometry(tileGeo, 40);
const iconPlaneGeo = new THREE.PlaneGeometry(TILE * 0.62, TILE * 0.62);

const nodes = [];
const nodesGroup = new THREE.Group();
scene.add(nodesGroup);

const domIcons = Array.from(document.querySelectorAll('.floating-icon'));
const iconSources = domIcons.length
  ? domIcons
  : []; /* if the markup ever changes, the scene simply runs without tiles */

const NODE_COUNT = MOBILE ? Math.min(10, iconSources.length) : iconSources.length;

async function buildTiles() {
  const textures = await Promise.all(
    iconSources.slice(0, NODE_COUNT).map((el) =>
      svgToTexture(el.querySelector('svg'), el.classList.contains('filled'))
    )
  );

  textures.forEach((tex, i) => {
    if (!tex) return;
    const group = new THREE.Group();

    /* A soft gold halo behind each slab — without it, dark metal on a near-black
       page just disappears. */
    const haloMat = new THREE.SpriteMaterial({
      map: glowTex,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      color: GOLD.clone(),
      opacity: 0,
    });
    const halo = new THREE.Sprite(haloMat);
    halo.scale.set(TILE * 3.4, TILE * 3.4, 1);
    halo.position.z = -0.16;
    group.add(halo);

    const slabMat = new THREE.MeshPhysicalMaterial({
      color: theme.tile.clone(),
      metalness: 0.72,
      roughness: 0.34,
      clearcoat: 1,
      clearcoatRoughness: 0.18,
      envMapIntensity: 1.15,
      emissive: GOLD.clone(),
      emissiveIntensity: 0.06,
      transparent: true,
    });
    const slab = new THREE.Mesh(tileGeo, slabMat);
    group.add(slab);

    const edgeMat = new THREE.LineBasicMaterial({
      color: GOLD.clone(),
      transparent: true,
      opacity: 0.6,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });
    group.add(new THREE.LineSegments(tileEdgeGeo, edgeMat));

    const iconMat = new THREE.MeshBasicMaterial({
      map: tex,
      transparent: true,
      color: new THREE.Color('#c9ab5e'),
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    const icon = new THREE.Mesh(iconPlaneGeo, iconMat);
    icon.position.z = 0.09;
    group.add(icon);

    /* Three inclined rings in the XZ plane, tipped into view. A tile is at
       x ≈ 0 — i.e. crossing the headline — exactly when |z| is at its extreme,
       so the depth fade in the loop hides it there. The visible tiles are the
       ones out at the sides, framing the copy. */
    const ring = i % 3;
    const tilt = [0.34, -0.30, 0.26][ring]; // pitch: how much vertical sweep
    const roll = [0.18, -0.24, 0.42][ring]; // roll: cants the ring sideways

    const node = {
      group,
      slab,
      slabMat,
      edgeMat,
      iconMat,
      halo,
      haloMat,
      ring,
      baseTilt: tilt,
      baseRoll: roll,
      radius: 10,
      phase: (i / NODE_COUNT) * Math.PI * 2 + ring * 0.7,
      speed: (0.045 + (i % 5) * 0.006) * (i % 2 ? 1 : -1),
      tiltQ: new THREE.Quaternion().setFromEuler(new THREE.Euler(tilt, 0, roll)),
      wobble: Math.random() * Math.PI * 2,
      /* Per-tile spin, carried over from the old DOM tiles' rotSpeed. Without it
         every slab billboards to the identical orientation and the field goes
         flat. Roll keeps the icon readable; the pitch/yaw wobble turns the slab
         in depth so the bevel keeps catching the key light. */
      spin: Math.random() * Math.PI * 2,
      spinSpeed: (0.10 + Math.random() * 0.26) * (i % 2 ? 1 : -1),
      wobbleAmp: 0.16 + Math.random() * 0.30,
      wobbleRate: 0.4 + Math.random() * 0.45,
      offset: new THREE.Vector3(),
      velocity: new THREE.Vector3(),
      base: new THREE.Vector3(),
      hover: 0,
      appear: 0,
      visible: 0,
      delay: 0.35 + i * 0.05,
      dragging: false,
    };

    group.scale.setScalar(0.001);
    nodesGroup.add(group);
    nodes.push(node);
  });

  for (const n of nodes) pickTargets.push(n.slab);
  buildLinks();
}

/* ── energy links + travelling pulses ────────────────────────────────────── */
let links, pulses;
let linkDist = 7.2; // recomputed from the ring size in layoutRings()

function buildLinks() {
  const maxPairs = (nodes.length * (nodes.length - 1)) / 2;

  const lg = new THREE.BufferGeometry();
  lg.setAttribute('position', new THREE.BufferAttribute(new Float32Array(maxPairs * 6), 3));
  // RGBA per vertex: additive mode drives intensity through colour, normal mode
  // (light theme) drives it through alpha instead.
  lg.setAttribute('color', new THREE.BufferAttribute(new Float32Array(maxPairs * 8), 4));
  links = new THREE.LineSegments(
    lg,
    new THREE.LineBasicMaterial({
      vertexColors: true,
      transparent: true,
      opacity: 0,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    })
  );
  links.frustumCulled = false;
  scene.add(links);

  const pg = new THREE.BufferGeometry();
  pg.setAttribute('position', new THREE.BufferAttribute(new Float32Array(maxPairs * 3), 3));
  pg.setAttribute('aAlpha', new THREE.BufferAttribute(new Float32Array(maxPairs), 1));
  pulses = new THREE.Points(
    pg,
    new THREE.ShaderMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      uniforms: {
        uColor: { value: GOLD_HOT.clone() },
        uPixelRatio: { value: renderer.getPixelRatio() },
        uIntro: { value: 0 },
      },
      vertexShader: /* glsl */ `
        attribute float aAlpha;
        uniform float uPixelRatio;
        varying float vAlpha;
        void main(){
          vAlpha = aAlpha;
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          gl_Position = projectionMatrix * mv;
          gl_PointSize = 46.0 * uPixelRatio / max(-mv.z, 0.001);
        }`,
      fragmentShader: /* glsl */ `
        uniform vec3 uColor;
        uniform float uIntro;
        varying float vAlpha;
        void main(){
          float d = length(gl_PointCoord - 0.5);
          float core = 1.0 - smoothstep(0.0, 0.5, d);
          gl_FragColor = vec4(uColor, pow(core, 2.0) * vAlpha * uIntro);
        }`,
    })
  );
  pulses.frustumCulled = false;
  scene.add(pulses);
}

/* ── particle field ──────────────────────────────────────────────────────── */
const P_COUNT = MOBILE ? 900 : 2600;
const pPos = new Float32Array(P_COUNT * 3);
const pScale = new Float32Array(P_COUNT);
const pSeed = new Float32Array(P_COUNT);
for (let i = 0; i < P_COUNT; i++) {
  // Shell-biased distribution: sparse in the middle where the headline lives.
  const r = 5 + Math.pow(Math.random(), 0.6) * 16;
  const th = Math.random() * Math.PI * 2;
  const ph = Math.acos(2 * Math.random() - 1);
  pPos[i * 3] = r * Math.sin(ph) * Math.cos(th);
  pPos[i * 3 + 1] = r * Math.cos(ph) * 0.62;
  pPos[i * 3 + 2] = r * Math.sin(ph) * Math.sin(th) * 0.75 - 4;
  pScale[i] = 0.35 + Math.random() * 1.15;
  pSeed[i] = Math.random();
}
const pGeo = new THREE.BufferGeometry();
pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
pGeo.setAttribute('aScale', new THREE.BufferAttribute(pScale, 1));
pGeo.setAttribute('aSeed', new THREE.BufferAttribute(pSeed, 1));

const particleMat = new THREE.ShaderMaterial({
  transparent: true,
  depthWrite: false,
  blending: THREE.AdditiveBlending,
  uniforms: {
    uTime: { value: 0 },
    uPointer: { value: new THREE.Vector3(0, 0, 0) },
    uPointerOn: { value: 0 },
    uPixelRatio: { value: renderer.getPixelRatio() },
    uColor: { value: theme.particle.clone() },
    uIntro: { value: 0 },
    uAlphaScale: { value: 1 },
  },
  vertexShader: /* glsl */ `
    uniform float uTime, uPointerOn, uPixelRatio;
    uniform vec3 uPointer;
    attribute float aScale, aSeed;
    varying float vAlpha;
    void main(){
      vec3 p = position;
      float s = aSeed * 6.2831;
      p.x += sin(uTime * 0.22 + s) * 0.75;
      p.y += cos(uTime * 0.18 + s * 1.7) * 0.75;
      p.z += sin(uTime * 0.15 + s * 2.3) * 0.6;

      vec3 toPointer = uPointer - p;
      float dist = length(toPointer);
      float influence = exp(-dist * dist / 34.0) * uPointerOn;
      p += normalize(toPointer + 1e-4) * influence * 2.4;

      vec4 mv = modelViewMatrix * vec4(p, 1.0);
      gl_Position = projectionMatrix * mv;

      float twinkle = 0.45 + 0.55 * sin(uTime * 1.7 + aSeed * 31.0);
      vAlpha = (0.10 + 0.55 * twinkle) + influence * 1.4;
      gl_PointSize = (9.0 + influence * 16.0) * aScale * uPixelRatio / max(-mv.z, 0.001) * 6.0;
    }`,
  fragmentShader: /* glsl */ `
    uniform vec3 uColor;
    uniform float uIntro, uAlphaScale;
    varying float vAlpha;
    void main(){
      float d = length(gl_PointCoord - 0.5);
      float a = 1.0 - smoothstep(0.0, 0.5, d);
      gl_FragColor = vec4(uColor, pow(a, 2.2) * vAlpha * uIntro * uAlphaScale);
    }`,
});
scene.add(new THREE.Points(pGeo, particleMat));

/* ── post-processing ─────────────────────────────────────────────────────── */
const composer = new EffectComposer(renderer);
composer.setPixelRatio(renderer.getPixelRatio());
composer.setSize(hero.offsetWidth, hero.offsetHeight);
composer.addPass(new RenderPass(scene, camera));

const bloom = new UnrealBloomPass(
  new THREE.Vector2(hero.offsetWidth, hero.offsetHeight),
  theme.bloom,
  0.62,
  0.58
);
composer.addPass(bloom);

const gradePass = new ShaderPass({
  uniforms: {
    tDiffuse: { value: null },
    uTime: { value: 0 },
    uVignette: { value: theme.vignette },
    uGrain: { value: theme.grain },
    uAberration: { value: 0.0011 },
  },
  vertexShader: /* glsl */ `
    varying vec2 vUv;
    void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
  fragmentShader: /* glsl */ `
    uniform sampler2D tDiffuse;
    uniform float uTime, uVignette, uGrain, uAberration;
    varying vec2 vUv;
    void main(){
      vec2 c = vUv - 0.5;
      float r2 = dot(c, c);

      // lens chromatic aberration, strongest at the corners
      float ab = uAberration * r2 * 4.0;
      vec4 col;
      col.r = texture2D(tDiffuse, vUv - c * ab).r;
      col.g = texture2D(tDiffuse, vUv).g;
      col.b = texture2D(tDiffuse, vUv + c * ab).b;
      col.a = 1.0;

      col.rgb *= 1.0 - uVignette * smoothstep(0.10, 0.62, r2);

      // Grain scaled by local luminance so the blacks stay black.
      float lum = dot(col.rgb, vec3(0.2126, 0.7152, 0.0722));
      float n = fract(sin(dot(vUv + fract(uTime), vec2(12.9898, 78.233))) * 43758.5453);
      col.rgb += (n - 0.5) * uGrain * smoothstep(0.0, 0.22, lum);

      gl_FragColor = col;
    }`,
});
/* Order matters: OutputPass does tone mapping + sRGB encoding, so the grade has
   to come AFTER it. Added in linear HDR space, grain of this amplitude lifts the
   blacks to a flat grey once they are encoded. */
composer.addPass(new OutputPass());
composer.addPass(gradePass);

/* ── pointer + interaction ───────────────────────────────────────────────── */
const pointer = new THREE.Vector2(0, 0);       // NDC
const pointerSmooth = new THREE.Vector2(0, 0); // lerped, drives the camera
const pointerWorld = new THREE.Vector3();
let pointerActive = 0;
let pointerTargetActive = 0;

const raycaster = new THREE.Raycaster();
const dragPlane = new THREE.Plane();
const dragPoint = new THREE.Vector3();
const dragGrab = new THREE.Vector3();
let hovered = null;
let dragged = null;

function updatePointer(clientX, clientY) {
  const rect = hero.getBoundingClientRect();
  pointer.x = ((clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -((clientY - rect.top) / rect.height) * 2 + 1;
}

/* Project the pointer onto the z = -2 plane so particles chase it in world space. */
const pointerPlane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 2);
function projectPointer() {
  raycaster.setFromCamera(pointer, camera);
  raycaster.ray.intersectPlane(pointerPlane, pointerWorld);
}

hero.addEventListener('pointermove', (e) => {
  updatePointer(e.clientX, e.clientY);
  pointerTargetActive = 1;
  if (dragged) {
    raycaster.setFromCamera(pointer, camera);
    if (raycaster.ray.intersectPlane(dragPlane, dragPoint)) {
      const target = dragPoint.clone().sub(dragGrab);
      dragged.velocity.copy(target).sub(dragged.group.position).multiplyScalar(0.45);
      dragged.offset.copy(target).sub(dragged.base);
    }
  }
});

hero.addEventListener('pointerleave', () => {
  pointerTargetActive = 0;
});

hero.addEventListener('pointerdown', (e) => {
  updatePointer(e.clientX, e.clientY);
  const hit = pickNode();
  if (!hit) return;
  dragged = hit;
  hit.dragging = true;
  canvas.style.cursor = 'grabbing';
  canvas.setPointerCapture?.(e.pointerId);

  // Drag along a plane facing the camera, through the tile.
  dragPlane.setFromNormalAndCoplanarPoint(
    camera.getWorldDirection(new THREE.Vector3()).negate(),
    hit.group.position
  );
  raycaster.setFromCamera(pointer, camera);
  if (raycaster.ray.intersectPlane(dragPlane, dragPoint)) {
    dragGrab.copy(dragPoint).sub(hit.group.position);
  } else {
    dragGrab.set(0, 0, 0);
  }
});

function endDrag() {
  if (!dragged) return;
  dragged.dragging = false;
  dragged = null;
  canvas.style.cursor = hovered ? 'grab' : '';
}
window.addEventListener('pointerup', endDrag);
window.addEventListener('pointercancel', endDrag);

const pickTargets = []; // rebuilt once when the tiles are created, not per frame

function pickNode() {
  if (!pickTargets.length) return null;
  raycaster.setFromCamera(pointer, camera);
  const hits = raycaster.intersectObjects(pickTargets, false);
  if (!hits.length) return null;
  return nodes.find((n) => n.slab === hits[0].object) || null;
}

/* ── layout ──────────────────────────────────────────────────────────────── */
/* Size the orbits off the actual headline box rather than fixed world units, so
   the tiles clear the copy at every viewport instead of landing on top of it. */
const RING_SPACING = [1, 1.15, 1.32];
const _euler = new THREE.Euler();
let coreScale = 1;
const RING_PLANE_Z = -4;
const copyEls = ['.hero-content .label', '.hero-content h1', '.hero-sub', '.hero-actions']
  .map((s) => document.querySelector(s))
  .filter(Boolean);

/* The headline's bounding box, in NDC. Tiles dissolve on contact with it (see
   the loop) so no viewport can ever park a slab on top of the copy. */
const copyBox = { halfX: 0.5, halfY: 0.3, midY: 0 };

function layoutRings() {
  const dist = 16 - RING_PLANE_Z; // settled camera distance to the ring plane
  const halfH = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)) * dist;
  const halfW = halfH * camera.aspect;

  const heroW = hero.offsetWidth || 1;
  const hr = hero.getBoundingClientRect();

  let top = Infinity, bottom = -Infinity, width = 0;
  for (const el of copyEls) {
    const r = el.getBoundingClientRect();
    top = Math.min(top, r.top - hr.top);
    bottom = Math.max(bottom, r.bottom - hr.top);
    width = Math.max(width, r.width);
  }
  if (copyEls.length && hr.height) {
    copyBox.halfX = width / heroW;
    copyBox.halfY = (bottom - top) / hr.height;
    copyBox.midY = 1 - ((top + bottom) / hr.height);
  }

  /* Put the innermost ring outside the copy box's fade threshold (1.3×), so
     tiles spend their orbit visible rather than dissolved. */
  const inner = THREE.MathUtils.clamp(copyBox.halfX * halfW * 1.45, 5, halfW * 0.98);

  /* On a narrow viewport the copy eats the full width and there is no room
     beside it — so tip the rings upright and send the tiles over and under it
     instead of out to the sides. */
  const upright = THREE.MathUtils.clamp(2.6 - camera.aspect, 1, 1.9);

  for (const n of nodes) {
    n.radius = inner * RING_SPACING[n.ring];
    n.tiltQ.setFromEuler(_euler.set(n.baseTilt * upright, 0, n.baseRoll));
  }
  // Link range has to track the orbit size, or the network is either
  // fully-connected on mobile or completely disconnected on a wide monitor.
  linkDist = inner * 0.82;

  /* The core is a fixed size in world space, which means it swallows a narrow
     viewport whole. Scale it against whichever screen axis is tighter. */
  const coreDist = 16 - coreGroup.position.z;
  const coreHalfH = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)) * coreDist;
  coreScale = THREE.MathUtils.clamp(Math.min(coreHalfH * camera.aspect, coreHalfH) / 17, 0.34, 1.05);
  coreGroup.scale.setScalar(coreScale);

  /* Park the core just under the headline's last line at every viewport, rather
     than at a fixed world height that drifts onto the body copy on tall screens. */
  const h1 = copyEls.find((el) => el.tagName === 'H1');
  if (h1 && hr.height) {
    const ndcY = 1 - 2 * ((h1.getBoundingClientRect().bottom - hr.top) / hr.height);
    coreGroup.position.y = ndcY * coreHalfH;
  }
}

/* ── resize ──────────────────────────────────────────────────────────────── */
function resize() {
  const w = hero.offsetWidth;
  const h = hero.offsetHeight;
  if (!w || !h) return;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h, false);
  composer.setSize(w, h);
  bloom.setSize(w, h);
  layoutRings();
}
window.addEventListener('resize', resize);
resize();

/* ── theme sync ──────────────────────────────────────────────────────────── */
let isLight = document.body.classList.contains('light');

function applyTheme() {
  isLight = document.body.classList.contains('light');
  theme = isLight ? THEME.light : THEME.dark;

  renderer.setClearColor(theme.clear, 1);
  renderer.toneMappingExposure = theme.exposure;
  bloom.strength = theme.bloom;
  gradePass.uniforms.uGrain.value = theme.grain;
  gradePass.uniforms.uVignette.value = theme.vignette;

  /* Additive blending is a no-op against a near-white page — everything that
     glows on black has to switch to normal alpha blending on light. */
  const blending = isLight ? THREE.NormalBlending : THREE.AdditiveBlending;
  for (const m of [cageOuter.material, cageInner.material, particleMat, pulses?.material, links?.material]) {
    if (!m) continue;
    m.blending = blending;
    m.needsUpdate = true;
  }

  cageOuter.material.uniforms.uColor.value.copy(theme.cage);
  cageOuter.material.uniforms.uOpacity.value = theme.cageOpacity;
  cageOuter.material.uniforms.uFresnel.value = theme.cageFresnel;
  cageInner.material.uniforms.uColor.value.copy(theme.cage);
  cageInner.material.uniforms.uOpacity.value = theme.cageOpacity * 0.5;
  cageInner.material.uniforms.uFresnel.value = theme.cageFresnel;
  particleMat.uniforms.uColor.value.copy(theme.particle);
  particleMat.uniforms.uAlphaScale.value = theme.particleAlpha;
  if (pulses) pulses.material.uniforms.uColor.value.copy(isLight ? theme.link : GOLD_HOT);

  /* The core is a light source. On white it has nothing to illuminate, so only
     the solid faceted shell survives — it reads as a dark gem instead. */
  coreAura.visible = !isLight;
  coreGlow.visible = !isLight;

  nodes.forEach((n) => {
    n.slabMat.color.copy(theme.tile);
    n.slabMat.metalness = theme.tileMetal;
    n.slabMat.envMapIntensity = theme.tileEnv;
    n.slabMat.roughness = theme.tileRough;
    n.halo.visible = !isLight;
    n.edgeMat.color.copy(theme.edgeColor);
    n.edgeMat.blending = blending;
    n.edgeMat.needsUpdate = true;
    n.iconMat.blending = blending;
    n.iconMat.needsUpdate = true;
  });
}
new MutationObserver(applyTheme).observe(document.body, { attributes: true, attributeFilter: ['class'] });

/* ── animation loop ──────────────────────────────────────────────────────── */
const clock = new THREE.Clock();
const INTRO_DURATION = 2.9;
let elapsed = 0;
let running = true;

const inv = (x, a, b) => THREE.MathUtils.clamp((x - a) / (b - a), 0, 1);
const smootherstep = (t) => t * t * t * (t * (t * 6 - 15) + 10);

const tmpA = new THREE.Vector3();
const tmpB = new THREE.Vector3();
const lookTarget = new THREE.Object3D();
const linkColor = new THREE.Color();

function frame() {
  const dt = Math.min(clock.getDelta(), 0.05);
  elapsed += dt;

  const intro = Math.min(elapsed / INTRO_DURATION, 1);
  const ease = 1 - Math.pow(1 - intro, 3);

  /* ── camera: lerped mouse orbit ── */
  pointerSmooth.lerp(pointer, 0.045);
  pointerActive += (pointerTargetActive - pointerActive) * 0.05;
  const orbit = elapsed * 0.05;
  camera.position.x = pointerSmooth.x * 2.6 + Math.sin(orbit) * 0.55;
  camera.position.y = pointerSmooth.y * 1.7 + Math.cos(orbit * 0.8) * 0.35;
  // slow push-in during the intro, then a lazy breathing dolly
  camera.position.z = 23 - ease * 7 + Math.sin(orbit * 0.6) * 0.4;
  camera.lookAt(0, 0.2, 0);
  projectPointer();

  /* ── cages ── */
  cageOuter.rotation.y += dt * 0.028;
  cageOuter.rotation.x = Math.sin(elapsed * 0.09) * 0.09;
  cageInner.rotation.y -= dt * 0.055;
  cageInner.rotation.z = Math.sin(elapsed * 0.13) * 0.14;
  const reveal = -1.35 + Math.min(elapsed / 1.7, 1) * 2.75;
  cageOuter.material.uniforms.uReveal.value = reveal;
  cageOuter.material.uniforms.uTime.value = elapsed;
  cageInner.material.uniforms.uReveal.value = reveal + 0.25;
  cageInner.material.uniforms.uTime.value = elapsed;

  /* ── core ── */
  const ignite = THREE.MathUtils.clamp((elapsed - 0.9) / 1.5, 0, 1);
  coreMat.uniforms.uTime.value = elapsed;
  coreMat.uniforms.uIgnite.value = ignite;
  coreShell.material.emissiveIntensity = isLight ? 0 : ignite * (0.35 + 0.12 * Math.sin(elapsed * 1.4));
  coreShell.rotation.y += dt * 0.14;
  coreShell.rotation.x += dt * 0.06;
  coreGlow.material.opacity = ignite * (0.34 + 0.06 * Math.sin(elapsed * 1.1)) * coreScale;

  /* ── practicals ── */
  practicalA.position.set(Math.cos(elapsed * 0.5) * 9, Math.sin(elapsed * 0.4) * 5, 6 + Math.sin(elapsed * 0.3) * 3);
  practicalB.position.set(Math.cos(-elapsed * 0.36 + 2) * 10, Math.sin(-elapsed * 0.44) * 6, -2 + Math.cos(elapsed * 0.5) * 4);
  practicalA.intensity = 90 * ease;
  practicalB.intensity = 55 * ease;

  /* ── tiles ── */
  hovered = dragged || (pointerActive > 0.2 ? pickNode() : null);
  canvas.style.cursor = dragged ? 'grabbing' : hovered ? 'grab' : '';

  for (let i = 0; i < nodes.length; i++) {
    const n = nodes[i];

    // A circle in the XZ plane, tipped into view, then pushed behind the copy.
    const a = n.phase + elapsed * n.speed * Math.PI;
    tmpA.set(Math.cos(a) * n.radius, 0, Math.sin(a) * n.radius);
    tmpA.applyQuaternion(n.tiltQ);
    tmpA.y += Math.sin(elapsed * 0.4 + n.wobble) * 0.5 + 0.6;
    tmpA.z -= 4.0;
    n.base.copy(tmpA);

    if (!n.dragging) {
      // thrown tiles decay back into their orbit
      n.offset.addScaledVector(n.velocity, dt * 8);
      n.velocity.multiplyScalar(0.9);
      n.offset.multiplyScalar(0.965);
    }
    n.group.position.copy(n.base).add(n.offset);

    // staggered scale-in
    const t = THREE.MathUtils.clamp((elapsed - n.delay) / 0.9, 0, 1);
    n.appear = 1 - Math.pow(1 - t, 4);

    /* Depth fade. A tile swinging to the front of its ring is exactly the one
       about to cross the headline, so it dissolves into the fog instead; the
       far side of the ring is dimmed to sell the distance. */
    const z = n.group.position.z;
    let fade =
      smootherstep(inv(z, 3.5, -1.0)) * (0.35 + 0.65 * smootherstep(inv(z, -22, -11)));

    // …and dissolve on contact with the headline's screen-space box.
    tmpB.copy(n.group.position).project(camera);
    const clearance = Math.max(
      Math.abs(tmpB.x) / copyBox.halfX,
      Math.abs(tmpB.y - copyBox.midY) / copyBox.halfY
    );
    fade *= smootherstep(inv(clearance, 0.82, 1.3));

    const isHot = n === hovered;
    n.hover += ((isHot ? 1 : 0) - n.hover) * 0.14;
    n.visible = n.appear * fade;
    n.group.visible = n.visible > 0.004;
    n.group.scale.setScalar(Math.max(0.001, n.appear * (1 + n.hover * 0.22)));

    /* Billboard toward the camera with a live tilt so the bevel keeps catching
       light. The tilt has to be baked into the slerp *target* — applying it to
       the group afterwards feeds back into next frame's starting orientation
       and the tiles slowly wander edge-on. */
    lookTarget.position.copy(n.group.position);
    lookTarget.lookAt(camera.position);
    lookTarget.rotateZ(n.spin + elapsed * n.spinSpeed);
    lookTarget.rotateX(Math.sin(elapsed * n.wobbleRate + n.wobble) * n.wobbleAmp);
    lookTarget.rotateY(Math.cos(elapsed * n.wobbleRate * 0.83 + n.wobble * 1.3) * n.wobbleAmp * 1.25);
    n.group.quaternion.slerp(lookTarget.quaternion, 0.12);

    n.slabMat.emissiveIntensity = 0.05 + n.hover * 0.8;
    n.slabMat.opacity = n.visible;
    n.edgeMat.opacity = (theme.edgeBase + n.hover * (1 - theme.edgeBase)) * n.visible;
    n.haloMat.opacity = (0.16 + n.hover * 0.55) * n.visible;
    n.halo.scale.setScalar(TILE * (3.4 + n.hover * 1.4));
    const ib = theme.iconBase, ih = theme.iconHot;
    n.iconMat.color.setRGB(
      ib[0] + (ih[0] - ib[0]) * n.hover,
      ib[1] + (ih[1] - ib[1]) * n.hover,
      ib[2] + (ih[2] - ib[2]) * n.hover
    );
    n.iconMat.opacity = n.visible;
  }

  /* ── links + pulses ── */
  if (links && nodes.length > 1) {
    const lp = links.geometry.attributes.position.array;
    const lc = links.geometry.attributes.color.array;
    const pp = pulses.geometry.attributes.position.array;
    const pa = pulses.geometry.attributes.aAlpha.array;
    let li = 0;
    let pi = 0;

    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const A = nodes[i].group.position;
        const B = nodes[j].group.position;
        const d = A.distanceTo(B);
        if (d > linkDist) continue;

        let strength = (1 - d / linkDist) * 0.55;
        strength += (nodes[i].hover + nodes[j].hover) * 0.55;
        strength *= Math.min(nodes[i].visible, nodes[j].visible);
        if (strength < 0.004) continue;

        lp[li * 6] = A.x; lp[li * 6 + 1] = A.y; lp[li * 6 + 2] = A.z;
        lp[li * 6 + 3] = B.x; lp[li * 6 + 4] = B.y; lp[li * 6 + 5] = B.z;

        let alpha = 1;
        if (isLight) {
          linkColor.copy(theme.link);
          alpha = Math.min(strength, 1);
        } else {
          linkColor.copy(theme.link).lerp(GOLD_HOT, Math.min(strength, 1) * 0.5).multiplyScalar(strength);
        }
        const o = li * 8;
        lc[o] = lc[o + 4] = linkColor.r;
        lc[o + 1] = lc[o + 5] = linkColor.g;
        lc[o + 2] = lc[o + 6] = linkColor.b;
        lc[o + 3] = lc[o + 7] = alpha;
        li++;

        // one packet of energy travelling A → B
        const tp = (elapsed * 0.32 + (i * 7 + j * 13) * 0.083) % 1;
        tmpB.copy(A).lerp(B, tp);
        pp[pi * 3] = tmpB.x; pp[pi * 3 + 1] = tmpB.y; pp[pi * 3 + 2] = tmpB.z;
        pa[pi] = strength * Math.sin(tp * Math.PI) * 1.6;
        pi++;
      }
    }

    links.geometry.attributes.position.needsUpdate = true;
    links.geometry.attributes.color.needsUpdate = true;
    links.geometry.setDrawRange(0, li * 2);
    links.material.opacity = THREE.MathUtils.clamp((elapsed - 1.0) / 1.2, 0, 1);

    pulses.geometry.attributes.position.needsUpdate = true;
    pulses.geometry.attributes.aAlpha.needsUpdate = true;
    pulses.geometry.setDrawRange(0, pi);
    pulses.material.uniforms.uIntro.value = THREE.MathUtils.clamp((elapsed - 1.3) / 1.2, 0, 1);
  }

  /* ── particles ── */
  particleMat.uniforms.uTime.value = elapsed;
  particleMat.uniforms.uPointer.value.copy(pointerWorld);
  particleMat.uniforms.uPointerOn.value = pointerActive;
  particleMat.uniforms.uIntro.value = THREE.MathUtils.clamp((elapsed - 0.5) / 1.6, 0, 1);

  gradePass.uniforms.uTime.value = elapsed;

  composer.render();
}

/* Render a finished, fully-converged frame at time t. The billboard slerp and
   the hover/appear easings need several iterations to land, so a single render
   would catch every tile mid-turn — edge-on and half-faded. */
function settle(t, iterations = 60) {
  for (let i = 0; i < iterations; i++) {
    elapsed = t;
    clock.getDelta();
    frame();
  }
}

renderer.setAnimationLoop(() => {
  if (running) frame();
});

/* ── lifecycle: never burn GPU on an off-screen or hidden hero ───────────── */
new IntersectionObserver(
  (entries) => {
    running = entries[0].isIntersecting && !document.hidden;
    if (running) clock.getDelta(); // discard the paused interval
  },
  { threshold: 0 }
).observe(hero);

document.addEventListener('visibilitychange', () => {
  running = !document.hidden && hero.getBoundingClientRect().bottom > 0;
  if (running) clock.getDelta();
});

/* ── boot ────────────────────────────────────────────────────────────────── */
await buildTiles();
layoutRings();
applyTheme();

/* Hand over from the 2D fallback only once the scene is actually standing up. */
window.__hero3d = {
  renderer, scene, camera, composer, nodes, bloom, gradePass,
  get running() { return running; },
  get elapsed() { return elapsed; },
  /* Render one frame at an arbitrary point on the timeline. Useful for
     inspecting the intro, and for driving the scene when rAF is throttled. */
  seek(t) { elapsed = t; clock.getDelta(); frame(); },
  settle,
};
window.__hero3dReady = true;
window.__heroDomFx?.stop();

if (REDUCED) {
  // Compose the finished still, then stop the clock entirely.
  running = false;
  renderer.setAnimationLoop(null);
  settle(INTRO_DURATION + 4);
  window.addEventListener('resize', () => {
    resize();
    settle(INTRO_DURATION + 4);
  });
}
