import typing as t
import dataclasses


@dataclasses.dataclass
class Message:
    id: t.Optional[int]
    content: str
    role: str
    created: str
    discussion_id: int


@dataclasses.dataclass
class Answer:
    content: str
    in_used_tokens: int
    out_used_tokens: int
