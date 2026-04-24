import json
from pathlib import Path


def get_assets_json_path():
    """프로젝트 루트 기준 data/assets.json 경로"""
    base = Path(__file__).resolve().parent.parent
    return base / "data" / "assets.json"


def load_assets():
    """JSON 파일에서 금융 자산 목록 로드"""
    path = get_assets_json_path()
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_asset_by_id(asset_id):
    """asset_id에 해당하는 자산 딕셔너리 반환, 없으면 None"""
    assets = load_assets()
    for a in assets:
        if a.get("id") == asset_id:
            return a
    return None
