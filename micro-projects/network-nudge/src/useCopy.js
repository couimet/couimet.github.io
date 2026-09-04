// Shared clipboard-copy hook with the app's transient feedback idiom: writes
// text to the clipboard, flips a `copied` flag for two seconds, and swallows
// clipboard failures (unavailable API, permissions) as a no-op.
import { useCallback, useEffect, useRef, useState } from 'react';

const FEEDBACK_MS = 2000;

export function useCopy() {
  const [copied, setCopied] = useState(false);
  const timeoutRef = useRef(null);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  const copy = useCallback(async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      timeoutRef.current = setTimeout(() => setCopied(false), FEEDBACK_MS);
      return true;
    } catch {
      // clipboard unavailable — no-op
      return false;
    }
  }, []);

  return { copied, copy };
}
