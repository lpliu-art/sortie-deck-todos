import type { I18nKey } from "../i18n";
import type { PublicUser } from "../types";

function initialsOf(name: string): string {
  const cleaned = (name || "?").trim();
  if (!cleaned) return "?";
  if (/[\u4e00-\u9fff]/.test(cleaned)) return cleaned.slice(0, 1);
  const parts = cleaned.split(/\s+/).filter(Boolean);
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return cleaned.slice(0, 2).toUpperCase();
}

function operatorPortrait(user: PublicUser): string {
  if (user.role === "admin") return "/avatars/admin.webp";
  return "/avatars/operator.webp";
}

export function OperatorChip({
  user,
  tr,
}: {
  user: PublicUser;
  tr: (key: I18nKey | string) => string;
}) {
  const src = operatorPortrait(user);
  const glyph = initialsOf(user.display_name || user.username);

  return (
    <div className="operator-chip">
      <span
        className={`operator-avatar has-img role-${user.role === "admin" ? "admin" : "member"}`}
        aria-hidden
      >
        <img src={src} alt="" />
        <span className="operator-avatar-fallback">{glyph}</span>
      </span>
      <span className="operator-meta">
        <strong className="operator-name">{user.display_name}</strong>
        <span className="operator-role">
          {user.role === "admin" ? tr("adminRole") : tr("memberRole")}
          <span className="operator-callsign">@{user.username}</span>
        </span>
      </span>
    </div>
  );
}
