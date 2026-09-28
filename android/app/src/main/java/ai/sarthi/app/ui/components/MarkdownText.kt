package ai.sarthi.app.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import ai.sarthi.app.ui.theme.SarthiGreen
import ai.sarthi.app.ui.theme.SarthiGreenDark
import ai.sarthi.app.ui.theme.SarthiLine
import ai.sarthi.app.ui.theme.SarthiMint
import ai.sarthi.app.ui.theme.SarthiMuted
import ai.sarthi.app.ui.theme.SarthiText

// ─── Token types ─────────────────────────────────────────────────────────────
private sealed class MdBlock {
    data class Heading1(val text: String) : MdBlock()
    data class Heading2(val text: String) : MdBlock()
    data class Heading3(val text: String) : MdBlock()
    data class BulletItem(val text: String, val depth: Int = 0) : MdBlock()
    data class NumberedItem(val number: Int, val text: String) : MdBlock()
    data class Paragraph(val text: String) : MdBlock()
    data object HorizontalRule : MdBlock()
    data class CodeLine(val code: String) : MdBlock()
    data object BlankLine : MdBlock()
}

// ─── Parser ───────────────────────────────────────────────────────────────────
private fun parse(markdown: String): List<MdBlock> {
    val blocks = mutableListOf<MdBlock>()
    val lines = markdown.lines()
    var i = 0
    while (i < lines.size) {
        val raw = lines[i]
        val line = raw.trimEnd()
        when {
            // Horizontal rule
            line.matches(Regex("^[-*_]{3,}\\s*$")) -> blocks.add(MdBlock.HorizontalRule)

            // H1 ## or #
            line.startsWith("# ") -> blocks.add(MdBlock.Heading1(line.removePrefix("# ").trim()))

            // H2
            line.startsWith("## ") -> blocks.add(MdBlock.Heading2(line.removePrefix("## ").trim()))

            // H3 / H4 / H5 / H6 — all rendered as Heading3
            line.startsWith("### ") ||
            line.startsWith("#### ") ||
            line.startsWith("##### ") ||
            line.startsWith("###### ") -> {
                val text = line.trimStart('#').trim()
                blocks.add(MdBlock.Heading3(text))
            }

            // Bullet list item (-, *, +) with optional indentation
            line.matches(Regex("^(\\s*)[-*+] .+")) -> {
                val depth = line.indexOfFirst { !it.isWhitespace() } / 2
                val text = line.trimStart().removePrefix("-").removePrefix("*").removePrefix("+").trim()
                blocks.add(MdBlock.BulletItem(text, depth))
            }

            // Numbered list item
            line.matches(Regex("^\\d+\\. .+")) -> {
                val num = line.substringBefore(".").trim().toIntOrNull() ?: 1
                val text = line.substringAfter(". ").trim()
                blocks.add(MdBlock.NumberedItem(num, text))
            }

            // Inline code block (backtick fenced)
            line.startsWith("```") -> {
                // Skip fence lines
            }

            // Blank line
            line.isBlank() -> blocks.add(MdBlock.BlankLine)

            // Default paragraph
            else -> blocks.add(MdBlock.Paragraph(line))
        }
        i++
    }
    // Collapse consecutive blank lines into one
    return blocks.zipWithNext { a, b ->
        if (a is MdBlock.BlankLine && b is MdBlock.BlankLine) null else a
    }.filterNotNull() + listOfNotNull(blocks.lastOrNull())
}

// ─── Inline span builder ──────────────────────────────────────────────────────
// Handles **bold**, *italic*, ***bold+italic***, `code` within a single line.
@Composable
private fun inlineText(
    raw: String,
    baseFontSize: TextUnit = 13.sp,
    baseColor: Color = SarthiText,
    baseFontWeight: FontWeight = FontWeight.Normal
) = buildAnnotatedString {
    // Strip outer ** / * that wrap an entire heading (e.g., **1. Crop Name**)
    val text = raw

    var pos = 0
    while (pos < text.length) {
        when {
            // Bold+Italic ***text***
            text.startsWith("***", pos) -> {
                val end = text.indexOf("***", pos + 3)
                if (end != -1) {
                    withStyle(SpanStyle(fontWeight = FontWeight.Bold, fontStyle = FontStyle.Italic)) {
                        append(text.substring(pos + 3, end))
                    }
                    pos = end + 3
                } else { append(text[pos]); pos++ }
            }
            // Bold **text**
            text.startsWith("**", pos) -> {
                val end = text.indexOf("**", pos + 2)
                if (end != -1) {
                    withStyle(SpanStyle(fontWeight = FontWeight.Bold, color = baseColor)) {
                        append(text.substring(pos + 2, end))
                    }
                    pos = end + 2
                } else { append(text[pos]); pos++ }
            }
            // Italic *text* or _text_
            (text[pos] == '*' || text[pos] == '_') -> {
                val marker = text[pos].toString()
                val end = text.indexOf(marker, pos + 1)
                if (end != -1) {
                    withStyle(SpanStyle(fontStyle = FontStyle.Italic)) {
                        append(text.substring(pos + 1, end))
                    }
                    pos = end + 1
                } else { append(text[pos]); pos++ }
            }
            // Inline code `code`
            text[pos] == '`' -> {
                val end = text.indexOf('`', pos + 1)
                if (end != -1) {
                    withStyle(SpanStyle(
                        fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                        background = Color(0xFFEEF2EE),
                        color = SarthiGreen,
                        fontSize = (baseFontSize.value - 0.5f).sp
                    )) {
                        append(text.substring(pos + 1, end))
                    }
                    pos = end + 1
                } else { append(text[pos]); pos++ }
            }
            else -> { append(text[pos]); pos++ }
        }
    }
}

// ─── Public composable ────────────────────────────────────────────────────────

/**
 * Renders a Markdown string as properly formatted Compose UI.
 * Supports: # headings, **bold**, *italic*, `code`, - bullets,
 * 1. numbered lists, --- dividers, blank lines.
 */
@Composable
fun MarkdownText(
    markdown: String,
    modifier: Modifier = Modifier,
    baseColor: Color = SarthiText,
    baseFontSize: TextUnit = 13.sp
) {
    val blocks = parse(markdown)

    Column(modifier = modifier) {
        for (block in blocks) {
            when (block) {
                // ── H1 ──────────────────────────────────────────────────────
                is MdBlock.Heading1 -> {
                    Spacer(Modifier.height(10.dp))
                    Text(
                        text = inlineText(block.text, 18.sp, SarthiGreenDark, FontWeight.Bold),
                        fontSize = 18.sp,
                        fontWeight = FontWeight.ExtraBold,
                        color = SarthiGreenDark,
                        lineHeight = 24.sp
                    )
                    Spacer(Modifier.height(2.dp))
                    Box(
                        Modifier
                            .fillMaxWidth()
                            .height(2.dp)
                            .background(SarthiLine, RoundedCornerShape(1.dp))
                    )
                    Spacer(Modifier.height(4.dp))
                }

                // ── H2 ──────────────────────────────────────────────────────
                is MdBlock.Heading2 -> {
                    Spacer(Modifier.height(8.dp))
                    Text(
                        text = inlineText(block.text, 15.sp, SarthiGreen, FontWeight.Bold),
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Bold,
                        color = SarthiGreen,
                        lineHeight = 20.sp
                    )
                    Spacer(Modifier.height(4.dp))
                }

                // ── H3 ──────────────────────────────────────────────────────
                is MdBlock.Heading3 -> {
                    Spacer(Modifier.height(6.dp))
                    Text(
                        text = inlineText(block.text, 13.5.sp, SarthiGreenDark, FontWeight.SemiBold),
                        fontSize = 13.5.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = SarthiGreenDark,
                        lineHeight = 19.sp
                    )
                    Spacer(Modifier.height(2.dp))
                }

                // ── Bullet ──────────────────────────────────────────────────
                is MdBlock.BulletItem -> {
                    Spacer(Modifier.height(3.dp))
                    Row(
                        verticalAlignment = Alignment.Top,
                        modifier = Modifier.padding(start = (block.depth * 14).dp)
                    ) {
                        Spacer(Modifier.width(2.dp))
                        Box(
                            modifier = Modifier
                                .padding(top = 6.dp)
                                .size(5.dp)
                                .background(SarthiGreen, CircleShape)
                        )
                        Spacer(Modifier.width(8.dp))
                        Text(
                            text = inlineText(block.text, baseFontSize, baseColor),
                            fontSize = baseFontSize,
                            color = baseColor,
                            lineHeight = (baseFontSize.value * 1.45f).sp
                        )
                    }
                }

                // ── Numbered ────────────────────────────────────────────────
                is MdBlock.NumberedItem -> {
                    Spacer(Modifier.height(3.dp))
                    Row(verticalAlignment = Alignment.Top) {
                        Box(
                            modifier = Modifier
                                .padding(top = 2.dp)
                                .size(20.dp)
                                .background(SarthiMint, CircleShape),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = "${block.number}",
                                fontSize = 9.sp,
                                fontWeight = FontWeight.Bold,
                                color = SarthiGreen
                            )
                        }
                        Spacer(Modifier.width(8.dp))
                        Text(
                            text = inlineText(block.text, baseFontSize, baseColor),
                            fontSize = baseFontSize,
                            color = baseColor,
                            lineHeight = (baseFontSize.value * 1.45f).sp
                        )
                    }
                }

                // ── Paragraph ───────────────────────────────────────────────
                is MdBlock.Paragraph -> {
                    Text(
                        text = inlineText(block.text, baseFontSize, baseColor),
                        fontSize = baseFontSize,
                        color = baseColor,
                        lineHeight = (baseFontSize.value * 1.5f).sp
                    )
                }

                // ── Horizontal Rule ─────────────────────────────────────────
                is MdBlock.HorizontalRule -> {
                    Spacer(Modifier.height(8.dp))
                    Box(
                        Modifier
                            .fillMaxWidth()
                            .height(1.dp)
                            .background(SarthiLine)
                    )
                    Spacer(Modifier.height(8.dp))
                }

                // ── Blank line ──────────────────────────────────────────────
                is MdBlock.BlankLine -> Spacer(Modifier.height(5.dp))

                // ── Code block line ─────────────────────────────────────────
                is MdBlock.CodeLine -> {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(Color(0xFFEEF2EE), RoundedCornerShape(6.dp))
                            .padding(8.dp)
                    ) {
                        Text(
                            text = block.code,
                            fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                            fontSize = 11.sp,
                            color = SarthiGreen
                        )
                    }
                }
            }
        }
    }
}
