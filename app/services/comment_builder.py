from __future__ import annotations


def build_comment(talk_ok_score: int) -> str:
    if talk_ok_score <= 20:
        return "今はかなり話しかけにくそうです"
    if talk_ok_score <= 40:
        return "少し様子を見たほうがよさそうです"
    if talk_ok_score <= 60:
        return "タイミング次第では話しかけられそうです"
    if talk_ok_score <= 80:
        return "比較的話しかけやすそうです"
    return "今ならかなり話しかけやすそうです"
