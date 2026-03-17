/**
 * File overview: Shared hook for object-shaped session storage state with safe parsing and persistence.
 */

import { useEffect, useState } from 'react';

function safeLoad(key, fallback) {
  if (typeof window === 'undefined') return fallback;
  try {
    // This hook is intentionally object-only so feature state can evolve by key
    // without every caller re-parsing storage manually.
    const raw = window.sessionStorage.getItem(key);
    if (!raw) return fallback;
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === 'object') return parsed;
    return fallback;
  } catch {
    return fallback;
  }
}

export function useSessionStorageObject(key, defaultValue = {}) {
  const [value, setValue] = useState(() => safeLoad(key, defaultValue));

  useEffect(() => {
    if (typeof window === 'undefined') return;
    window.sessionStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue];
}
