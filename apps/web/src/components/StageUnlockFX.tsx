import { useEffect, useRef } from "react";
import * as THREE from "three";

type Props = {
  /** 0–100 horizontal position inside the rail */
  xPct: number;
  label: string;
  lang: "zh" | "en";
  onDone: () => void;
};

/**
 * Lightweight Three.js level-unlock burst over the pipeline rail.
 * Particles + expanding ring; self-disposes after ~1.8s.
 */
export function StageUnlockFX({ xPct, label, lang, onDone }: Props) {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const onDoneRef = useRef(onDone);
  onDoneRef.current = onDone;

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;

    const w = Math.max(host.clientWidth, 2);
    const h = Math.max(host.clientHeight, 2);
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(w, h, false);
    renderer.setClearColor(0x000000, 0);
    host.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    const camera = new THREE.OrthographicCamera(-w / 2, w / 2, h / 2, -h / 2, 0.1, 100);
    camera.position.z = 10;

    const cx = -w / 2 + (w * Math.min(100, Math.max(0, xPct))) / 100;
    const cy = h / 2 - 20; // near hex dots

    const count = reduce ? 24 : 96;
    const positions = new Float32Array(count * 3);
    const velocities: { x: number; y: number; life: number }[] = [];
    for (let i = 0; i < count; i++) {
      positions[i * 3] = cx;
      positions[i * 3 + 1] = cy;
      positions[i * 3 + 2] = 0;
      const ang = Math.random() * Math.PI * 2;
      const spd = 40 + Math.random() * 160;
      velocities.push({
        x: Math.cos(ang) * spd,
        y: Math.sin(ang) * spd * 0.65,
        life: 0.55 + Math.random() * 0.9,
      });
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    const mat = new THREE.PointsMaterial({
      size: reduce ? 3 : 4.5,
      color: 0x3dffa8,
      transparent: true,
      opacity: 1,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      sizeAttenuation: false,
    });
    const points = new THREE.Points(geo, mat);
    scene.add(points);

    // Secondary ice sparkles
    const iceMat = new THREE.PointsMaterial({
      size: reduce ? 2 : 3,
      color: 0x7eb6ff,
      transparent: true,
      opacity: 0.95,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      sizeAttenuation: false,
    });
    const iceGeo = geo.clone();
    const ice = new THREE.Points(iceGeo, iceMat);
    scene.add(ice);

    const ringGeo = new THREE.RingGeometry(6, 10, 48);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x3dffa8,
      transparent: true,
      opacity: 0.9,
      side: THREE.DoubleSide,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.position.set(cx, cy, 0);
    scene.add(ring);

    const ring2Geo = new THREE.RingGeometry(4, 6, 40);
    const ring2Mat = new THREE.MeshBasicMaterial({
      color: 0xe8a04a,
      transparent: true,
      opacity: 0.75,
      side: THREE.DoubleSide,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });
    const ring2 = new THREE.Mesh(ring2Geo, ring2Mat);
    ring2.position.set(cx, cy, 0);
    scene.add(ring2);

    let raf = 0;
    const t0 = performance.now();
    const dur = reduce ? 900 : 1800;

    const tick = (now: number) => {
      const t = (now - t0) / 1000;
      const dt = 1 / 60;
      const pos = geo.getAttribute("position") as THREE.BufferAttribute;
      const icePos = iceGeo.getAttribute("position") as THREE.BufferAttribute;
      for (let i = 0; i < count; i++) {
        const v = velocities[i];
        v.life -= dt;
        if (v.life <= 0) {
          pos.setXYZ(i, cx, cy, 0);
          icePos.setXYZ(i, cx, cy, 0);
          continue;
        }
        const px = pos.getX(i) + v.x * dt;
        const py = pos.getY(i) + v.y * dt;
        v.y -= 90 * dt;
        pos.setXYZ(i, px, py, 0);
        icePos.setXYZ(i, px * 0.98 + cx * 0.02, py * 0.98 + cy * 0.02, 0);
      }
      pos.needsUpdate = true;
      icePos.needsUpdate = true;

      const fade = Math.max(0, 1 - t / (dur / 1000));
      mat.opacity = fade;
      iceMat.opacity = fade * 0.85;
      const scale = 1 + t * 9;
      ring.scale.setScalar(scale);
      ringMat.opacity = fade * 0.85;
      ring2.scale.setScalar(1 + t * 5.5);
      ring2Mat.opacity = fade * 0.65;
      ring.rotation.z = t * 1.2;
      ring2.rotation.z = -t * 0.8;

      renderer.render(scene, camera);
      if (now - t0 < dur) {
        raf = requestAnimationFrame(tick);
      } else {
        onDoneRef.current();
      }
    };
    raf = requestAnimationFrame(tick);

    const onResize = () => {
      const nw = Math.max(host.clientWidth, 2);
      const nh = Math.max(host.clientHeight, 2);
      renderer.setSize(nw, nh, false);
      camera.left = -nw / 2;
      camera.right = nw / 2;
      camera.top = nh / 2;
      camera.bottom = -nh / 2;
      camera.updateProjectionMatrix();
    };
    window.addEventListener("resize", onResize);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", onResize);
      geo.dispose();
      iceGeo.dispose();
      mat.dispose();
      iceMat.dispose();
      ringGeo.dispose();
      ringMat.dispose();
      ring2Geo.dispose();
      ring2Mat.dispose();
      renderer.dispose();
      if (renderer.domElement.parentNode === host) host.removeChild(renderer.domElement);
    };
  }, [xPct]);

  return (
    <div className="stage-unlock-fx" aria-live="polite">
      <div className="stage-unlock-canvas" ref={hostRef} />
      <div className="stage-unlock-banner">
        <span className="stage-unlock-kicker">{lang === "zh" ? "关卡解锁" : "STAGE CLEAR"}</span>
        <strong>{label}</strong>
      </div>
    </div>
  );
}
