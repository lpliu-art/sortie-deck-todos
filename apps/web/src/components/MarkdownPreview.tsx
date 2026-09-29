import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type Props = {
  text: string;
  className?: string;
};

/** Renders chat / agent / artifact text as Markdown (GFM: tables, strikethrough, etc.). */
export function MarkdownPreview({ text, className }: Props) {
  return (
    <div className={className ? `md-preview ${className}` : "md-preview"}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          a: ({ href, children }) => (
            <a href={href} target="_blank" rel="noreferrer noopener">
              {children}
            </a>
          ),
        }}
      >
        {text}
      </ReactMarkdown>
    </div>
  );
}

export function looksLikeMarkdown(pathOrKind: string): boolean {
  const name = pathOrKind.toLowerCase();
  return (
    name.endsWith(".md") ||
    name.endsWith(".markdown") ||
    name.includes(".md/") ||
    /(^|[\/_])(readme|changelog|prd|design|test_cases|test_plan|handoff|selftest|intake)(\.|$)/i.test(
      name,
    )
  );
}
