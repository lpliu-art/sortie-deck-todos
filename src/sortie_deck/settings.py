from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TDT_", env_file=".env", extra="ignore")

    data_dir: Path = REPO_ROOT / "data"
    host: str = "127.0.0.1"
    port: int = 8787
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"
    postgres_uri: str | None = None
    deploy_executor: str = "mock"  # mock | deploy_shell
    eng_concurrency: int = 3
    webhook_timeout: float = 5.0
    # development | production — production refuses empty / default token secrets
    env: str = "development"
    token_secret: str = "tdt-dev-secret"
    # json (default) | sqlite — initiative persistence backend
    storage: str = "json"
    # Optional LLM features (require TDT_LLM_API_KEY / OPENAI_API_KEY, or Claude CLI fallback)
    # Defaults on: plan_pipeline_smart / room replies fall back to heuristic/templates when unavailable
    pipeline_llm: bool = True
    room_llm: bool = True
    # When true, LlmClient may use `claude -p` if no HTTP API key is set
    llm_cli_fallback: bool = True
    # OpenAI-compatible HTTP (also read by LlmClient; prefer these over bare os.environ)
    llm_api_key: str | None = None
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    # mock | claude_code | cursor_cli | auto (detect CLI on PATH)
    default_coding_executor: str = "auto"
    # Claude Code --permission-mode for non-interactive -p runs in worktrees
    # acceptEdits | auto | bypassPermissions | default | dontAsk | plan
    coding_permission_mode: str = "acceptEdits"
    # Stage timeout for coding CLI (seconds)
    coding_timeout_seconds: float = 900.0
    # When true, coding executors list/call MCP tools from toolkit bindings
    mcp_runtime: bool = False
    # Run queue: inline (default create_task) | sqlite (lease + worker loop)
    run_backend: str = "inline"
    worker_id: str = "worker-1"
    run_lease_seconds: int = 120
    # Artifacts: local | s3
    artifact_backend: str = "local"
    s3_bucket: str | None = None
    s3_prefix: str = "artifacts"
    s3_endpoint: str | None = None
    s3_region: str = "us-east-1"
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    # Org policy JSON path (empty = disabled)
    org_policy_path: Path | None = None
    # Enterprise knowledge: local catalog | WeKnora (Tencent OSS)
    # Sortie Deck imports + catalogs; retrieval uses WeKnora hybrid-search when enabled
    kb_backend: str = "local"  # local | weknora
    weknora_base_url: str | None = None  # e.g. http://127.0.0.1:8080
    weknora_api_key: str | None = None
    weknora_kb_id: str | None = None
    # Chat bridges
    slack_signing_secret: str | None = None
    feishu_verification_token: str | None = None
    # Production polish
    log_level: str = "INFO"
    stage_timeout_seconds: float = 900.0

    def resolved_token_secret(self) -> str:
        secret = (self.token_secret or "").strip()
        if self.env.strip().lower() == "production" and (
            not secret or secret == "tdt-dev-secret"
        ):
            raise RuntimeError(
                "TDT_TOKEN_SECRET must be set to a non-default value when TDT_ENV=production"
            )
        return secret or "tdt-dev-secret"

    @property
    def artifacts_dir(self) -> Path:
        return self.data_dir / "artifacts"

    @property
    def checkpoint_db(self) -> Path:
        return self.data_dir / "checkpoints.sqlite"

    @property
    def initiatives_db(self) -> Path:
        return self.data_dir / "initiatives.json"

    @property
    def initiatives_sqlite(self) -> Path:
        return self.data_dir / "initiatives.sqlite"

    @property
    def runs_sqlite(self) -> Path:
        return self.data_dir / "runs.sqlite"

    @property
    def worktrees_dir(self) -> Path:
        return self.data_dir / "worktrees"

    @property
    def rooms_dir(self) -> Path:
        return self.data_dir / "rooms"

    @property
    def users_db(self) -> Path:
        return self.data_dir / "users.json"

    @property
    def knowledge_db(self) -> Path:
        return self.data_dir / "knowledge.json"

    @property
    def memory_db(self) -> Path:
        return self.data_dir / "memory.json"

    @property
    def agents_db(self) -> Path:
        return self.data_dir / "agents.json"

    @property
    def toolkit_db(self) -> Path:
        return self.data_dir / "toolkit.json"

    @property
    def bridges_db(self) -> Path:
        return self.data_dir / "bridges.json"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
