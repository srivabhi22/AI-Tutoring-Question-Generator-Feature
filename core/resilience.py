#!/usr/bin/env python3
"""
Shared retry/fallback helpers for pipeline nodes and agents.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Callable, Any, Optional, Dict

logger = logging.getLogger(__name__)


def run_with_retry(
    label: str,
    fn: Callable[[], Any],
    *,
    retries: int = 0,
    delay_sec: float = 0.0,
    timeout_sec: Optional[float] = None,
    fallback: Optional[Callable[[Exception], Any]] = None,
) -> tuple[Any, Dict[str, Any]]:
    attempt = 0
    last_exc: Optional[Exception] = None
    max_attempts = max(0, retries) + 1
    start = time.time()
    used_fallback = False
    timed_out = False

    while attempt < max_attempts:
        try:
            if timeout_sec and timeout_sec > 0:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(fn)
                    result = future.result(timeout=timeout_sec)
            else:
                result = fn()
            duration_ms = int((time.time() - start) * 1000)
            return result, {
                "label": label,
                "attempts": attempt + 1,
                "retries": max_attempts - 1,
                "fallback_used": False,
                "timeout": False,
                "error": None,
                "duration_ms": duration_ms,
            }
        except TimeoutError as exc:
            timed_out = True
            last_exc = exc
            logger.exception(
                "%s timed out on attempt %d/%d",
                label,
                attempt + 1,
                max_attempts,
            )
            if attempt + 1 < max_attempts and delay_sec > 0:
                time.sleep(delay_sec)
            attempt += 1
        except Exception as exc:
            last_exc = exc
            logger.exception(
                "%s failed on attempt %d/%d",
                label,
                attempt + 1,
                max_attempts,
            )
            if attempt + 1 < max_attempts and delay_sec > 0:
                time.sleep(delay_sec)
            attempt += 1

    if fallback is not None and last_exc is not None:
        logger.warning("%s failed; using fallback", label)
        used_fallback = True
        result = fallback(last_exc)
        duration_ms = int((time.time() - start) * 1000)
        return result, {
            "label": label,
            "attempts": max_attempts,
            "retries": max_attempts - 1,
            "fallback_used": used_fallback,
            "timeout": timed_out,
            "error": str(last_exc),
            "duration_ms": duration_ms,
        }

    if last_exc is not None:
        raise last_exc
    raise RuntimeError(f"{label} failed without exception context")
