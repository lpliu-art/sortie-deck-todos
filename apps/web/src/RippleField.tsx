import { useEffect, useRef } from "react";

type Ripple = { id: number; x: number; y: number; kind: "hover" | "scroll" };

const MAX_RIPPLES = 14;

export function RippleField({ enabled }: { enabled: boolean }) {
  const layerRef = useRef<HTMLDivElement | null>(null);
  const idRef = useRef(0);
  const lastHover = useRef(0);
  const lastScroll = useRef(0);

  useEffect(() => {
    if (!enabled) return undefined;
    const layer = layerRef.current;
    if (!layer) return undefined;

    const spawn = (x: number, y: number, kind: Ripple["kind"]) => {
      const id = ++idRef.current;
      const el = document.createElement("span");
      el.className = `ripple ripple-${kind}`;
      el.style.left = `${x}px`;
      el.style.top = `${y}px`;
      el.dataset.id = String(id);
      layer.appendChild(el);
      while (layer.childElementCount > MAX_RIPPLES) {
        layer.firstElementChild?.remove();
      }
      window.setTimeout(() => el.remove(), kind === "scroll" ? 1100 : 900);
    };

    const onMove = (ev: PointerEvent) => {
      const now = performance.now();
      if (now - lastHover.current < 90) return;
      lastHover.current = now;
      spawn(ev.clientX, ev.clientY, "hover");
    };

    const onWheel = (ev: WheelEvent) => {
      const now = performance.now();
      if (now - lastScroll.current < 120) return;
      lastScroll.current = now;
      const x = ev.clientX || window.innerWidth * 0.5;
      const y = ev.clientY || window.innerHeight * 0.45;
      spawn(x + (Math.random() * 40 - 20), y + (Math.random() * 30 - 15), "scroll");
      spawn(x + (Math.random() * 80 - 40), y + (Math.random() * 60 - 30), "scroll");
    };

    window.addEventListener("pointermove", onMove, { passive: true });
    window.addEventListener("wheel", onWheel, { passive: true });
    return () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("wheel", onWheel);
      layer.replaceChildren();
    };
  }, [enabled]);

  return <div className="ripple-field" ref={layerRef} aria-hidden="true" />;
}
