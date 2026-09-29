"""Demo community executor for Sortie Deck entry points."""

from __future__ import annotations

from sortie_deck.models import StageContext, StageResult


class DemoEchoExecutor:
    """Writes a tiny echo artifact — used to verify `sortie_deck.executors` loading."""

    name = "demo_echo"

    def probe(self) -> dict[str, str]:
        return {"status": "ok", "detail": "demo echo ready"}

    async def run(self, ctx: StageContext) -> StageResult:
        body = f"# Demo echo\n\nBrief:\n{ctx.brief[:500]}\n"
        return StageResult(
            status="ok",
            message="demo_echo wrote note",
            artifacts={"demo_echo.md": body},
            proposed_next=None,
        )


def build() -> DemoEchoExecutor:
    return DemoEchoExecutor()
