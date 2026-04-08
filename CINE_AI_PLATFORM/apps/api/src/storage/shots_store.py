from typing import Any, Dict, List, Optional, Protocol


class ShotsStore(Protocol):
    def list_shots(self) -> List[Dict[str, Any]]:
        ...

    def get_shot(self, shot_id: str) -> Optional[Dict[str, Any]]:
        ...

    def create_shot(self, shot: Dict[str, Any]) -> Dict[str, Any]:
        ...

    def replace_shot(self, shot_id: str, shot: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        ...

    def delete_shot(self, shot_id: str) -> bool:
        ...