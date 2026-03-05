/* Hook for JSON object persistence in localStorage. */

import { useEffect, useState } from 'react';

function safeLoad(key, fallback) {
  if (typeof window === 'undefined') return fallback;
  try {
    const raw = window.localStorage.getItem(key);
    if (!raw) return fallback;
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === 'object') return parsed;
    return fallback;
  } catch {
    return fallback;
  }
}

export function useLocalStorageObject(key, defaultValue = {}) {
  const [value, setValue] = useState(() => safeLoad(key, defaultValue));

  useEffect(() => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue];
}
