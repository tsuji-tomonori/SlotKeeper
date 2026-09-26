"""CDK contextの環境名から公開可能な配置設定を読み込む。秘密はここに置かない。"""

import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "environments"


@dataclass(frozen=True)
class EnvironmentConfig:
    """環境ごとに変える値だけを持つ。accountは実行時の認証情報から決める。"""

    name: str
    region: str
    log_retention_days: int
    lambda_memory_mb: int
    lambda_timeout_seconds: int
    api_throttle_rate: int
    api_throttle_burst: int


def load(name: str) -> EnvironmentConfig:
    """未知の環境名や余剰・欠落した設定を合成前に拒否する。"""
    if not re.fullmatch(r"[a-z][a-z0-9-]{1,15}", name):
        raise ValueError("環境名が不正: " + name)
    path = ROOT / (name + ".json")
    if not path.is_file():
        raise ValueError("環境設定がない: " + name)
    data = json.loads(path.read_text())
    config = EnvironmentConfig(**data)
    if config.name != name:
        raise ValueError("環境名とfile名が不一致: " + name)
    if config.log_retention_days not in (30, 90, 180, 365):
        raise ValueError("CloudWatch Logsの保持日数は30/90/180/365から選ぶ")
    if not 1 <= config.lambda_timeout_seconds <= 29:
        raise ValueError("HTTP APIの統合上限29秒を超えるtimeout")
    return config
