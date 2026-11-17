from __future__ import annotations

from sortie_deck.llm import LlmClient
from sortie_deck.models import Initiative, RoleAgent, RoleId
from sortie_deck.rooms import RoomStore


async def craft_discussion_reply_llm(
    *,
    ini: Initiative,
    role: RoleAgent,
    text: str,
    author_name: str,
    rooms: RoomStore,
    memory_block: str = "",
    client: LlmClient | None = None,
) -> str | None:
    """Optional LLM discussion reply. Returns None to fall back to templates."""
    llm = client or LlmClient()
    if not llm.enabled:
        return None
    recent = rooms.list(ini.id)[-8:]
    history = "\n".join(f"{m.actor_name}: {m.text[:400]}" for m in recent)
    system = (
        f"You are {role.title} ({role.role.value}) on Sortie Deck mission «{ini.title}».\n"
        f"Persona:\n{role.persona or 'Helpful specialist.'}\n"
        "Reply in the same language as the human message. Keep under 180 words. "
        "Be concrete; suggest next squad commands (/confirm /start) when relevant."
    )
    user = (
        f"Brief:\n{ini.brief[:1200]}\n\n"
        f"Memory:\n{memory_block[:800] or '(none)'}\n\n"
        f"Recent chat:\n{history or '(empty)'}\n\n"
        f"{author_name} says:\n{text}"
    )
    try:
        return (await llm.chat_text(system=system, user=user, temperature=0.4)).strip()
    except Exception:
        return None


def craft_discussion_reply_template(
    ini: Initiative, role: RoleAgent, text: str, author_name: str
) -> str:
    brief = ini.brief[:280]
    if role.role == RoleId.PRODUCT:
        return (
            f"收到 {author_name} 的讨论。围绕「{ini.title}」，我建议先对齐：\n"
            f"1) 目标用户与成功标准\n2) 范围 / 非目标\n3) 验收条目\n\n"
            f"当前 brief：{brief}\n"
            f"补充意见：{text[:200]}\n"
            f"确认后可 `/start` 进入 PRD 产出。"
        )
    if role.role == RoleId.DESIGN:
        return (
            f"设计侧会先把「{ini.title}」拆成主流程与关键屏态（空/错/成），"
            f"并标出 iOS / Android / Web 差异。补充：{text[:160]}"
        )
    if role.role.value in {
        RoleId.ENG.value,
        RoleId.ENG_IOS.value,
        RoleId.ENG_ANDROID.value,
        RoleId.ENG_WEB.value,
        RoleId.ENG_BACKEND.value,
        RoleId.ENG_AGENT.value,
    }:
        return (
            f"{role.title}看法：需要明确接口边界与是否动现有模块。"
            f"建议拆成可并行任务，流水线启动后我会按 PRD/设计实现（executor=`{role.executor}`）。"
        )
    if role.role == RoleId.QA:
        return (
            "测试侧会关注验收标准可测性、失败回环到研发的条件。"
            "请在讨论里标出必须覆盖的风险路径。"
        )
    return "发布侧需要预发环境与回滚策略。流水线到 deploy 门禁时请人工确认。"
