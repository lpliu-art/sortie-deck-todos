import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from "react";
import { api } from "../api";
import { playSfx } from "../sfx";
import { ChatComposer, type ComposerAttachment, type ComposerPayload } from "./ChatComposer";

export type BriefingAttachment = {
  name: string;
  mime: string;
  size?: number;
  kind: string;
  data_url?: string;
  text_excerpt?: string;
};

export type BriefingEvent = {
  id: string;
  kind: string;
  text: string;
  data?: Record<string, unknown>;
  at?: string;
};

export type BriefingMessage = {
  role: string;
  text: string;
  at?: string;
  attachments?: BriefingAttachment[];
};

export type BriefingSession = {
  id: string;
  status: string;
  title?: string;
  messages: BriefingMessage[];
  events: BriefingEvent[];
  draft?: Record<string, unknown>;
  initiative_id?: string | null;
};

type Props = {
  token: string;
  lang: "zh" | "en";
  busy: boolean;
  setBusy: (v: boolean) => void;
  onCreated: (initiativeId: string) => void;
  onError: (msg: string) => void;
  labels: {
    title: string;
    placeholder: string;
    hint: string;
    send: string;
    confirm: string;
    reject: string;
    restart: string;
    waterfall: string;
    attach?: string;
  };
};

function toApiAttachment(a: ComposerAttachment): BriefingAttachment {
  return {
    name: a.name,
    mime: a.mime,
    size: a.size,
    kind: a.kind,
    data_url: a.dataUrl,
    text_excerpt: a.textExcerpt,
  };
}

export function MissionBriefingChat({
  token,
  lang,
  busy,
  setBusy,
  onCreated,
  onError,
  labels,
}: Props) {
  const [session, setSession] = useState<BriefingSession | null>(null);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [bootError, setBootError] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const locked = busy || sending;

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const s = await api<BriefingSession>("/api/briefing/sessions", {
          token,
          method: "POST",
          body: "{}",
        });
        if (!cancelled) {
          setSession(s);
          setBootError("");
        }
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        if (!cancelled) {
          setBootError(msg);
          onError(msg);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- start once per token
  }, [token]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [session?.messages, session?.events, sending]);

  async function restart() {
    setBusy(true);
    setSending(false);
    try {
      const s = await api<BriefingSession>("/api/briefing/sessions", {
        token,
        method: "POST",
        body: "{}",
      });
      setSession(s);
      setInput("");
      setBootError("");
      playSfx("whoosh");
    } catch (err) {
      onError(err instanceof Error ? err.message : String(err));
      playSfx("warn");
    } finally {
      setBusy(false);
    }
  }

  async function send(text: string, attachments: ComposerAttachment[] = []) {
    if (sending) return;
    if (!text.trim() && !attachments.length) return;
    if (!session) {
      onError(lang === "zh" ? "规划会话未就绪，请点「新会话」重试" : "Briefing session not ready — try New chat");
      playSfx("warn");
      return;
    }

    const displayText = text.trim() || (attachments.length ? `[附件 ×${attachments.length}]` : "");
    const optimistic: BriefingMessage = {
      role: "user",
      text: displayText,
      at: new Date().toISOString(),
      attachments: attachments.map(toApiAttachment),
    };

    setSending(true);
    setBusy(true);
    setInput("");
    setSession((prev) =>
      prev
        ? {
            ...prev,
            messages: [...(prev.messages || []), optimistic],
            events: [
              ...(prev.events || []),
              {
                id: `local_${Date.now()}`,
                kind: "waterfall",
                text: lang === "zh" ? "⏳ 规划官思考中…" : "⏳ Planner thinking…",
              },
            ],
          }
        : prev,
    );
    playSfx("click");

    try {
      const s = await api<BriefingSession>(`/api/briefing/sessions/${session.id}/messages`, {
        token,
        method: "POST",
        body: JSON.stringify({
          text,
          attachments: attachments.map(toApiAttachment),
        }),
      });
      setSession(s);
      playSfx(s.status === "awaiting_confirm" || s.status === "done" ? "ok" : "toggle");
      if (s.status === "done" && s.initiative_id) {
        onCreated(s.initiative_id);
      }
    } catch (err) {
      // Roll back optimistic bubble + restore draft text
      setSession((prev) =>
        prev
          ? {
              ...prev,
              messages: (prev.messages || []).filter((m) => m !== optimistic && m.at !== optimistic.at),
              events: (prev.events || []).filter((e) => !String(e.id).startsWith("local_")),
            }
          : prev,
      );
      setInput(text);
      onError(err instanceof Error ? err.message : String(err));
      playSfx("warn");
    } finally {
      setSending(false);
      setBusy(false);
    }
  }

  function onSubmit(e?: FormEvent | KeyboardEvent, payload?: ComposerPayload) {
    e?.preventDefault?.();
    void send(payload?.text ?? input, payload?.attachments ?? []);
  }

  const waterfall = (session?.events || []).filter((e) =>
    ["waterfall", "tool", "confirm", "done", "plan"].includes(e.kind),
  );
  const awaiting = session?.status === "awaiting_confirm";

  return (
    <div className="briefing">
      <div className="briefing-head">
        <div className="panel-label">{labels.title}</div>
        <button type="button" className="btn linkish" onClick={() => void restart()} disabled={locked}>
          {labels.restart}
        </button>
      </div>

      {bootError ? (
        <div className="alert bar">
          {lang === "zh" ? "规划会话启动失败：" : "Failed to start briefing: "}
          {bootError}
        </div>
      ) : null}

      <div className="briefing-waterfall" aria-label={labels.waterfall}>
        {waterfall.map((ev) => (
          <div key={ev.id} className={`wf-step kind-${ev.kind}${sending && String(ev.id).startsWith("local_") ? " live" : ""}`}>
            <span className="wf-dot" />
            <div className="wf-body">
              <strong>{ev.text}</strong>
              {ev.kind === "tool" && ev.data?.phase === "end" && ev.data?.ok === false && (
                <span className="muted"> · fail</span>
              )}
            </div>
          </div>
        ))}
        {!waterfall.length && (
          <p className="muted">{lang === "zh" ? "规划步骤将在此展开" : "Planning steps appear here"}</p>
        )}
      </div>

      <div className="briefing-chat">
        {(session?.messages || []).map((m, i) => (
          <div key={`${m.at}-${i}`} className={`briefing-bubble ${m.role}`}>
            {m.attachments && m.attachments.length > 0 ? (
              <ul className="briefing-msg-atts">
                {m.attachments.map((a, j) => (
                  <li key={`${a.name}-${j}`} className={`briefing-msg-att kind-${a.kind}`}>
                    {a.kind === "image" && a.data_url ? (
                      <a href={a.data_url} target="_blank" rel="noreferrer">
                        <img src={a.data_url} alt={a.name} />
                      </a>
                    ) : (
                      <span className="briefing-msg-file" title={a.name}>
                        {a.name}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            ) : null}
            {m.text ? <pre>{m.text}</pre> : null}
          </div>
        ))}
        {sending ? (
          <div className="briefing-bubble assistant planning" aria-live="polite">
            <pre>{lang === "zh" ? "规划官检索历史与知识库中…" : "Planner is searching history & knowledge…"}</pre>
            <span className="briefing-typing" aria-hidden>
              <i />
              <i />
              <i />
            </span>
          </div>
        ) : null}
        <div ref={bottomRef} />
      </div>

      {awaiting && !sending && (
        <div className="briefing-actions">
          <button type="button" className="btn primary" disabled={locked} onClick={() => void send("确认")}>
            {labels.confirm}
          </button>
          <button type="button" className="btn" disabled={locked} onClick={() => void send("驳回")}>
            {labels.reject}
          </button>
        </div>
      )}

      <ChatComposer
        value={input}
        onChange={setInput}
        onSubmit={onSubmit}
        placeholder={labels.placeholder}
        hint={labels.hint}
        sendLabel={sending ? (lang === "zh" ? "规划中…" : "Planning…") : labels.send}
        disabled={locked || !session || session?.status === "done"}
        mentions={[]}
        commands={[
          { id: "confirm", label: labels.confirm, hint: "confirm plan" },
          { id: "reject", label: labels.reject, hint: "reject plan" },
        ]}
        attachmentsEnabled
        attachLabel={labels.attach || (lang === "zh" ? "附件" : "Attach")}
      />
    </div>
  );
}
