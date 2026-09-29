import { useEffect, useMemo, useState } from "react";
import { MarkdownPreview, looksLikeMarkdown } from "./MarkdownPreview";
import type { ArtifactRef, Initiative, RoomMessage, TimelineEvent } from "../types";

type Props = {
  stageId: string;
  stageLabel: string;
  initiative: Initiative;
  messages: RoomMessage[];
  lang: "zh" | "en";
  onClose: () => void;
  onOpenArtifact: (path: string) => Promise<string>;
  onRevealPath?: (path: string) => void;
  workspaceArtifactsDir?: string | null;
  labels: {
    title: string;
    loop: string;
    docs: string;
    empty: string;
    close: string;
    role: string;
    executor: string;
    chat: string;
    consult: string;
    reveal?: string;
  };
};

function isMarkdown(path: string, kind: string): boolean {
  return looksLikeMarkdown(path) || looksLikeMarkdown(kind);
}

export function StageInspect({
  stageId,
  stageLabel,
  initiative,
  messages,
  lang,
  onClose,
  onOpenArtifact,
  onRevealPath,
  workspaceArtifactsDir,
  labels,
}: Props) {
  const [docPath, setDocPath] = useState<string | null>(null);
  const [docBody, setDocBody] = useState("");
  const [docBusy, setDocBusy] = useState(false);
  const [docErr, setDocErr] = useState("");

  const events = useMemo(() => {
    const tl = (initiative.timeline || []) as TimelineEvent[];
    return tl.filter((e) => e.stage === stageId);
  }, [initiative.timeline, stageId]);

  const docs = useMemo(() => {
    return (initiative.artifacts || []).filter((a) => a.stage === stageId);
  }, [initiative.artifacts, stageId]);

  const stageChats = useMemo(() => {
    return messages.filter((m) => {
      const metaStage = m.meta?.stage;
      if (m.msg_type === "consult" || m.msg_type === "consult_reply") {
        return metaStage === stageId;
      }
      return (
        m.msg_type === "stage" &&
        (metaStage === stageId || m.text.startsWith(`[${stageId}]`))
      );
    });
  }, [messages, stageId]);

  const consultThread = useMemo(() => {
    return messages.filter(
      (m) =>
        (m.msg_type === "consult" || m.msg_type === "consult_reply") &&
        m.meta?.stage === stageId,
    );
  }, [messages, stageId]);

  const loops = useMemo(() => {
    return events.filter((e) => e.kind === "info" || e.kind === "error").length;
  }, [events]);

  const roleAgent = useMemo(() => {
    const specs = initiative.meta?.pipeline_specs as { id: string; role?: string }[] | undefined;
    const proposal = initiative.meta?.pipeline_proposal as
      | { stages?: { id: string; role?: string }[] }
      | undefined;
    const stages = Array.isArray(specs) && specs.length ? specs : proposal?.stages || [];
    const spec = stages.find((s) => s.id === stageId);
    const roleId = spec?.role || events.find((e) => e.role)?.role;
    return initiative.roles?.find((r) => r.role === roleId) || null;
  }, [initiative, stageId, events]);

  useEffect(() => {
    setDocPath(null);
    setDocBody("");
    setDocErr("");
  }, [stageId]);

  async function loadDoc(a: ArtifactRef) {
    setDocBusy(true);
    setDocErr("");
    setDocPath(a.path);
    try {
      const body = await onOpenArtifact(a.path);
      setDocBody(body);
    } catch (err) {
      setDocErr(err instanceof Error ? err.message : String(err));
      setDocBody("");
    } finally {
      setDocBusy(false);
    }
  }

  return (
    <section className="stage-inspect panel" aria-label={labels.title}>
      <div className="stage-inspect-head">
        <div>
          <div className="panel-label">
            {labels.title} · {stageLabel}
          </div>
          <p className="stage-inspect-meta">
            <code>{stageId}</code>
            {roleAgent ? (
              <span>
                {labels.role}: {roleAgent.title}
                {roleAgent.executor ? (
                  <>
                    {" "}
                    · {labels.executor}: <code>{roleAgent.executor}</code>
                  </>
                ) : null}
              </span>
            ) : null}
            <span>
              {labels.loop}: {loops}
            </span>
            {initiative.current_stage === stageId ? (
              <span className="stage-inspect-live">
                {lang === "zh" ? "当前节点" : "current"}
              </span>
            ) : null}
          </p>
        </div>
        <button type="button" className="btn ghost" onClick={onClose}>
          {labels.close}
        </button>
      </div>

      <div className="stage-inspect-grid">
        <div className="stage-inspect-col">
          <div className="panel-label">{labels.consult}</div>
          {consultThread.length === 0 ? (
            <p className="empty-queue">{labels.empty}</p>
          ) : (
            <ol className="stage-loop consult-thread">
              {consultThread.map((m) => (
                <li
                  key={m.id}
                  className={`kind-consult ${m.msg_type === "consult_reply" ? "reply" : "ask"}`}
                >
                  <div className="stage-loop-meta">
                    <strong>{m.msg_type === "consult_reply" ? "A" : "Q"}</strong>
                    <span>{m.actor_name}</span>
                    {m.role ? <code>@{m.role}</code> : null}
                    {m.at ? <em>{new Date(m.at).toLocaleString()}</em> : null}
                  </div>
                  <p>{m.text}</p>
                </li>
              ))}
            </ol>
          )}
          <div className="panel-label" style={{ marginTop: "1rem" }}>
            {labels.loop}
          </div>
          {events.length === 0 && stageChats.length === 0 ? (
            <p className="empty-queue">{labels.empty}</p>
          ) : (
            <ol className="stage-loop">
              {events.map((e, i) => {
                const executor = (e.data?.executor as string | undefined) || undefined;
                const status = (e.data?.status as string | undefined) || undefined;
                const attempt = e.data?.qa_attempt;
                return (
                  <li key={e.id || `${e.at}-${i}`} className={`kind-${e.kind}`}>
                    <div className="stage-loop-meta">
                      <strong>{e.kind}</strong>
                      {e.role ? <span>{e.role}</span> : null}
                      {executor ? <code>{executor}</code> : null}
                      {status ? <span className={`st-${status}`}>{status}</span> : null}
                      {attempt != null ? <span>#{String(attempt)}</span> : null}
                      {e.at ? <em>{new Date(e.at).toLocaleString()}</em> : null}
                    </div>
                    <p>{e.message}</p>
                    {e.data && Object.keys(e.data).length > 0 && e.kind === "hitl" ? (
                      <pre className="stage-loop-data">
                        {JSON.stringify(
                          {
                            action: e.data.action,
                            note: e.data.note,
                            prompt: e.data.prompt,
                            message: e.data.message,
                          },
                          null,
                          2,
                        )}
                      </pre>
                    ) : null}
                  </li>
                );
              })}
              {stageChats
                .filter((m) => m.msg_type === "stage")
                .map((m) => (
                <li key={m.id} className="kind-chat">
                  <div className="stage-loop-meta">
                    <strong>{labels.chat}</strong>
                    <span>{m.actor_name}</span>
                    {m.at ? <em>{new Date(m.at).toLocaleString()}</em> : null}
                  </div>
                  <p>{m.text.replace(new RegExp(`^\\[${stageId}\\]\\s*`), "")}</p>
                </li>
              ))}
            </ol>
          )}
        </div>

        <div className="stage-inspect-col">
          <div className="panel-label row-between">
            <span>{labels.docs}</span>
            {onRevealPath && workspaceArtifactsDir ? (
              <button
                type="button"
                className="btn ghost tiny"
                onClick={() => onRevealPath(`${workspaceArtifactsDir}/${stageId}`)}
              >
                {labels.reveal || (lang === "zh" ? "打开目录" : "Open folder")}
              </button>
            ) : null}
          </div>
          {docs.length === 0 ? (
            <p className="empty-queue">{labels.empty}</p>
          ) : (
            <div className="stage-docs">
              {docs.map((a) => (
                <button
                  key={a.path}
                  type="button"
                  className={docPath === a.path ? "active" : undefined}
                  onClick={() => void loadDoc(a)}
                >
                  <span className="art-kind">{a.kind}</span>
                  <span className="art-path">{a.path.split("/").pop()}</span>
                </button>
              ))}
            </div>
          )}
          {docBusy ? <p className="muted">…</p> : null}
          {docErr ? <p className="error">{docErr}</p> : null}
          {docBody ? (
            isMarkdown(docPath || "", "") ? (
              <MarkdownPreview text={docBody} className="stage-doc-body" />
            ) : (
              <pre className="preview stage-doc-body">{docBody}</pre>
            )
          ) : null}
        </div>
      </div>
    </section>
  );
}
