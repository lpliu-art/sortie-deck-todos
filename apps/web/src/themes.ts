export type ThemeId = "signal" | "copper" | "ice" | "ember" | "slate";

export interface ThemeOption {
  id: ThemeId;
  labelZh: string;
  labelEn: string;
}

export const THEMES: ThemeOption[] = [
  { id: "signal", labelZh: "信号绿", labelEn: "Signal" },
  { id: "copper", labelZh: "铜门禁", labelEn: "Copper" },
  { id: "ice", labelZh: "冰蓝", labelEn: "Ice" },
  { id: "ember", labelZh: "余烬", labelEn: "Ember" },
  { id: "slate", labelZh: "岩灰", labelEn: "Slate" },
];

export interface BackgroundPreset {
  id: string;
  src: string;
  labelZh: string;
  labelEn: string;
}

/** Built-in anime wallpapers (webp) under public/backgrounds */
export const BACKGROUND_PRESETS: BackgroundPreset[] = [
  {
    id: "anime-heroine",
    src: "/backgrounds/bg-anime-heroine.webp",
    labelZh: "动图·她",
    labelEn: "Anim · Her",
  },
  {
    id: "anime-hero",
    src: "/backgrounds/bg-anime-hero.webp",
    labelZh: "动图·他",
    labelEn: "Anim · Him",
  },
];

export const THEME_STORAGE_KEY = "sortie_theme";
export const BG_STORAGE_KEY = "sortie_bg";
const LEGACY_THEME_KEY = "rally_theme";
const LEGACY_BG_KEY = "rally_bg";

function migrateGet(key: string, legacy: string): string | null {
  const v = localStorage.getItem(key);
  if (v != null) return v;
  const old = localStorage.getItem(legacy);
  if (old != null) {
    localStorage.setItem(key, old);
    localStorage.removeItem(legacy);
  }
  return old;
}

export function loadTheme(): ThemeId {
  const raw = migrateGet(THEME_STORAGE_KEY, LEGACY_THEME_KEY);
  if (THEMES.some((t) => t.id === raw)) return raw as ThemeId;
  return "signal";
}

export function loadBackground(): string {
  const stored = migrateGet(BG_STORAGE_KEY, LEGACY_BG_KEY);
  if (stored) return stored;
  return BACKGROUND_PRESETS[0]?.src || "";
}
