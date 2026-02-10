#!/usr/bin/env python3
"""
Retry/fallback tuning for pipeline nodes and agents.
"""

PIPELINE_RETRY_DELAY_SEC = 0.0

NODE_RETRIES = {
    "multimodal": 1,
    "planner": 1,
}

AGENT_RETRIES = 1

NODE_TIMEOUT_SEC = {
    "multimodal": 60,
    "planner": 60,
}

AGENT_TIMEOUT_SEC = 120
