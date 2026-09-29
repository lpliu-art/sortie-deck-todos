/** Sortie Deck localStorage keys with Rally legacy fallback. */

export function lsGet(key: string, legacyKey?: string): string | null {
  const v = localStorage.getItem(key);
  if (v != null) return v;
  if (!legacyKey) return null;
  const legacy = localStorage.getItem(legacyKey);
  if (legacy != null) {
    localStorage.setItem(key, legacy);
    localStorage.removeItem(legacyKey);
  }
  return legacy;
}

export function lsSet(key: string, value: string, legacyKey?: string): void {
  localStorage.setItem(key, value);
  if (legacyKey) localStorage.removeItem(legacyKey);
}

export function lsRemove(key: string, legacyKey?: string): void {
  localStorage.removeItem(key);
  if (legacyKey) localStorage.removeItem(legacyKey);
}
