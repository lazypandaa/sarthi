/**
 * MarkdownRenderer.tsx
 * Renders LLM/AI markdown output as styled HTML using Sarthi design tokens.
 * Supports: # headings, **bold**, *italic*, `code`, - bullets, 1. lists, --- dividers.
 * Zero external dependencies.
 */
import React from "react";

// ─── Inline span parser ───────────────────────────────────────────────────────
function parseInline(text: string): React.ReactNode[] {
  const nodes: React.ReactNode[] = [];
  let pos = 0;
  let key = 0;

  while (pos < text.length) {
    // Bold+Italic ***text***
    if (text.startsWith("***", pos)) {
      const end = text.indexOf("***", pos + 3);
      if (end !== -1) {
        nodes.push(<strong key={key++} style={{ fontStyle: "italic" }}>{text.slice(pos + 3, end)}</strong>);
        pos = end + 3; continue;
      }
    }
    // Bold **text**
    if (text.startsWith("**", pos)) {
      const end = text.indexOf("**", pos + 2);
      if (end !== -1) {
        nodes.push(<strong key={key++}>{text.slice(pos + 2, end)}</strong>);
        pos = end + 2; continue;
      }
    }
    // Italic *text*
    if (text[pos] === "*" && text[pos + 1] !== "*") {
      const end = text.indexOf("*", pos + 1);
      if (end !== -1) {
        nodes.push(<em key={key++}>{text.slice(pos + 1, end)}</em>);
        pos = end + 1; continue;
      }
    }
    // Italic _text_
    if (text[pos] === "_") {
      const end = text.indexOf("_", pos + 1);
      if (end !== -1) {
        nodes.push(<em key={key++}>{text.slice(pos + 1, end)}</em>);
        pos = end + 1; continue;
      }
    }
    // Inline code `code`
    if (text[pos] === "`") {
      const end = text.indexOf("`", pos + 1);
      if (end !== -1) {
        nodes.push(
          <code key={key++} style={{
            fontFamily: "monospace",
            background: "var(--mint)",
            color: "var(--green)",
            padding: "1px 5px",
            borderRadius: 4,
            fontSize: "0.88em",
          }}>
            {text.slice(pos + 1, end)}
          </code>
        );
        pos = end + 1; continue;
      }
    }
    // Accumulate plain text until next special character
    let plain = "";
    while (
      pos < text.length &&
      text[pos] !== "*" && text[pos] !== "_" && text[pos] !== "`"
    ) {
      plain += text[pos++];
    }
    if (plain) nodes.push(<React.Fragment key={key++}>{plain}</React.Fragment>);
  }

  return nodes;
}

// ─── Block parser ─────────────────────────────────────────────────────────────
type Block =
  | { type: "h1" | "h2" | "h3"; text: string }
  | { type: "bullet"; text: string; depth: number }
  | { type: "numbered"; n: number; text: string }
  | { type: "hr" }
  | { type: "blank" }
  | { type: "paragraph"; text: string };

function parseBlocks(markdown: string): Block[] {
  const blocks: Block[] = [];
  const lines = markdown.split("\n");

  for (const raw of lines) {
    const line = raw.trimEnd();

    if (/^[-*_]{3,}\s*$/.test(line)) {
      blocks.push({ type: "hr" });
    } else if (line.startsWith("# ")) {
      blocks.push({ type: "h1", text: line.slice(2).trim() });
    } else if (line.startsWith("## ")) {
      blocks.push({ type: "h2", text: line.slice(3).trim() });
    } else if (/^#{3,6} /.test(line)) {
      blocks.push({ type: "h3", text: line.replace(/^#{3,6} /, "").trim() });
    } else if (/^(\s*)[-*+] .+/.test(line)) {
      const depth = Math.floor((line.length - line.trimStart().length) / 2);
      blocks.push({ type: "bullet", text: line.trimStart().slice(2).trim(), depth });
    } else if (/^\d+\. .+/.test(line)) {
      const n = parseInt(line.match(/^(\d+)\./)?.[1] ?? "1", 10);
      blocks.push({ type: "numbered", n, text: line.replace(/^\d+\. /, "").trim() });
    } else if (line.trim() === "") {
      blocks.push({ type: "blank" });
    } else {
      blocks.push({ type: "paragraph", text: line });
    }
  }

  // Collapse consecutive blanks
  return blocks.filter((b, i) =>
    !(b.type === "blank" && blocks[i - 1]?.type === "blank")
  );
}

// ─── Renderer ─────────────────────────────────────────────────────────────────
interface MarkdownRendererProps {
  text: string;
  fontSize?: number;
  color?: string;
}

export function MarkdownRenderer({ text, fontSize = 12, color = "var(--text)" }: MarkdownRendererProps) {
  const blocks = parseBlocks(text);

  return (
    <div style={{ fontSize, color, lineHeight: 1.65 }}>
      {blocks.map((block, i) => {
        switch (block.type) {
          case "h1":
            return (
              <div key={i}>
                <div style={{
                  fontSize: fontSize * 1.45,
                  fontWeight: 800,
                  color: "var(--green-dark)",
                  marginTop: 12,
                  marginBottom: 4,
                  lineHeight: 1.3,
                }}>
                  {parseInline(block.text)}
                </div>
                <div style={{ height: 2, background: "var(--line)", borderRadius: 1, marginBottom: 6 }} />
              </div>
            );

          case "h2":
            return (
              <div key={i} style={{
                fontSize: fontSize * 1.2,
                fontWeight: 700,
                color: "var(--green)",
                marginTop: 10,
                marginBottom: 4,
                lineHeight: 1.3,
              }}>
                {parseInline(block.text)}
              </div>
            );

          case "h3":
            return (
              <div key={i} style={{
                fontSize: fontSize * 1.08,
                fontWeight: 600,
                color: "var(--green-dark)",
                marginTop: 8,
                marginBottom: 2,
                lineHeight: 1.4,
              }}>
                {parseInline(block.text)}
              </div>
            );

          case "bullet":
            return (
              <div key={i} style={{
                display: "flex",
                gap: 8,
                alignItems: "flex-start",
                marginTop: 3,
                paddingLeft: block.depth * 16,
              }}>
                <span style={{
                  flexShrink: 0,
                  marginTop: "0.45em",
                  width: 5,
                  height: 5,
                  borderRadius: "50%",
                  background: "var(--green)",
                  display: "inline-block",
                }} />
                <span>{parseInline(block.text)}</span>
              </div>
            );

          case "numbered":
            return (
              <div key={i} style={{
                display: "flex",
                gap: 8,
                alignItems: "flex-start",
                marginTop: 4,
              }}>
                <span style={{
                  flexShrink: 0,
                  width: 20,
                  height: 20,
                  borderRadius: "50%",
                  background: "var(--mint)",
                  color: "var(--green)",
                  fontWeight: 700,
                  fontSize: fontSize * 0.75,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}>
                  {block.n}
                </span>
                <span style={{ paddingTop: 1 }}>{parseInline(block.text)}</span>
              </div>
            );

          case "hr":
            return (
              <div key={i} style={{
                height: 1,
                background: "var(--line)",
                margin: "10px 0",
              }} />
            );

          case "blank":
            return <div key={i} style={{ height: 5 }} />;

          case "paragraph":
          default:
            return (
              <div key={i} style={{ marginTop: 2, lineHeight: 1.6 }}>
                {parseInline(block.text)}
              </div>
            );
        }
      })}
    </div>
  );
}

export default MarkdownRenderer;
