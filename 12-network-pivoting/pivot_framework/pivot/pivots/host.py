from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class PivotHost:
    name: str
    ip: str
    user: str
    key_path: str
    networks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'ip': self.ip,
            'user': self.user,
            'key': self.key_path,
            'networks': self.networks
        }