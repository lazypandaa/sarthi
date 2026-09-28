package ai.sarthi.app.ui.screens

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import ai.sarthi.app.data.model.UserProfile
import ai.sarthi.app.ui.components.ButtonKind
import ai.sarthi.app.ui.components.MarkdownText
import ai.sarthi.app.ui.components.SarthiButton
import ai.sarthi.app.ui.components.SarthiCard
import ai.sarthi.app.ui.components.SarthiHeader
import ai.sarthi.app.ui.components.SarthiIcon
import ai.sarthi.app.ui.theme.SarthiBg
import ai.sarthi.app.ui.theme.SarthiGreen
import ai.sarthi.app.ui.theme.SarthiLine
import ai.sarthi.app.ui.theme.SarthiMint
import ai.sarthi.app.ui.theme.SarthiMuted
import ai.sarthi.app.ui.theme.SarthiRed
import ai.sarthi.app.ui.theme.SarthiSurface
import ai.sarthi.app.ui.theme.SarthiText

@Composable
fun VoiceScreen(
    user: UserProfile,
    isRecording: Boolean,
    recordingDurationSec: Int,
    question: String,
    answer: String,
    isPlayingAudio: Boolean,
    onToggleRecord: () -> Unit,
    onSendText: (String) -> Unit,
    onTogglePlayAudio: () -> Unit,
    onBack: () -> Unit
) {
    var textInput by remember { mutableStateOf("") }
    var feedbackGiven by remember { mutableStateOf(false) }

    val infiniteTransition = rememberInfiniteTransition(label = "mic_pulse")
    val pulseScale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = 1.15f,
        animationSpec = infiniteRepeatable(
            animation = tween(800, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulse"
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(SarthiBg)
            .verticalScroll(rememberScrollState())
            .padding(bottom = 90.dp)
    ) {
        SarthiHeader(
            title = "Ask Sarthi Voice AI",
            onBack = onBack
        )

        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 20.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(modifier = Modifier.height(10.dp))

            // Multilingual badge
            Row(
                modifier = Modifier
                    .clip(RoundedCornerShape(100.dp))
                    .background(SarthiMint)
                    .padding(horizontal = 12.dp, vertical = 6.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                SarthiIcon(name = "spark", size = 15.dp, tint = SarthiGreen)
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    text = "SARTHI MULTILINGUAL AI (${user.language.uppercase()})",
                    fontSize = 10.sp,
                    fontWeight = FontWeight.ExtraBold,
                    color = SarthiGreen,
                    letterSpacing = 0.5.sp
                )
            }

            Spacer(modifier = Modifier.height(14.dp))

            Text(
                text = if (isRecording) "Sarthi is listening..." else "What would you like to know?",
                fontSize = 22.sp,
                fontWeight = FontWeight.ExtraBold,
                color = SarthiText,
                textAlign = TextAlign.Center
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = if (isRecording) "Speak naturally in Hindi, Telugu, or English — Tap mic to finish"
                else "Ask about crops, fertilizer schedules, mandi prices, or pest management.",
                fontSize = 11.5.sp,
                color = SarthiMuted,
                textAlign = TextAlign.Center,
                lineHeight = 16.sp
            )

            Spacer(modifier = Modifier.height(30.dp))

            // ================= BIG MIC BUTTON =================
            Box(
                modifier = Modifier
                    .size(96.dp)
                    .then(if (isRecording) Modifier.scale(pulseScale) else Modifier)
                    .shadow(12.dp, CircleShape)
                    .clip(CircleShape)
                    .background(if (isRecording) SarthiRed else SarthiGreen)
                    .clickable { onToggleRecord() },
                contentAlignment = Alignment.Center
            ) {
                SarthiIcon(
                    name = "mic",
                    size = 44.dp,
                    tint = Color.White
                )
            }

            Spacer(modifier = Modifier.height(14.dp))

            Text(
                text = if (isRecording) {
                    val m = recordingDurationSec / 60
                    val s = recordingDurationSec % 60
                    "🔴 Recording (${String.format("%d:%02d", m, s)}) — Tap to stop"
                } else "Tap microphone to speak or type below",
                fontSize = 11.sp,
                fontWeight = if (isRecording) FontWeight.Bold else FontWeight.Medium,
                color = if (isRecording) SarthiRed else SarthiMuted
            )

            Spacer(modifier = Modifier.height(20.dp))

            // Text input fallback
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                OutlinedTextField(
                    value = textInput,
                    onValueChange = { textInput = it },
                    placeholder = { Text("Or type your question here...", fontSize = 12.sp, color = SarthiMuted) },
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(12.dp),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = SarthiGreen,
                        unfocusedBorderColor = SarthiLine,
                        focusedContainerColor = SarthiSurface,
                        unfocusedContainerColor = SarthiSurface
                    ),
                    maxLines = 1
                )
                Spacer(modifier = Modifier.width(8.dp))
                SarthiButton(
                    text = "Ask",
                    onClick = {
                        if (textInput.isNotBlank()) {
                            onSendText(textInput)
                            textInput = ""
                        }
                    },
                    modifier = Modifier.height(52.dp)
                )
            }

            // Question Transcript Card
            if (question.isNotBlank()) {
                Spacer(modifier = Modifier.height(16.dp))
                SarthiCard {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Text(
                            text = "YOU ASKED",
                            fontSize = 8.5.sp,
                            fontWeight = FontWeight.Bold,
                            color = SarthiMuted,
                            letterSpacing = 0.5.sp
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = "“$question”",
                            fontSize = 13.sp,
                            fontWeight = FontWeight.Bold,
                            color = SarthiText
                        )
                    }
                }
            }

            // Answer Card
            if (answer.isNotBlank()) {
                Spacer(modifier = Modifier.height(12.dp))
                SarthiCard(
                    backgroundColor = Color(0xFFF0F8F3),
                    borderColor = Color(0xFFC0E4D0)
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "SARTHI AI SAYS",
                                fontSize = 8.5.sp,
                                fontWeight = FontWeight.ExtraBold,
                                color = SarthiGreen,
                                letterSpacing = 0.5.sp
                            )

                            // Play Voice Button
                            Row(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(6.dp))
                                    .background(SarthiGreen)
                                    .clickable { onTogglePlayAudio() }
                                    .padding(horizontal = 8.dp, vertical = 4.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                SarthiIcon(
                                    name = if (isPlayingAudio) "pause" else "play",
                                    size = 12.dp,
                                    tint = Color.White
                                )
                                Spacer(modifier = Modifier.width(4.dp))
                                Text(
                                    text = if (isPlayingAudio) "Pause Audio" else "Play Voice",
                                    color = Color.White,
                                    fontSize = 10.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }

                        Spacer(modifier = Modifier.height(8.dp))

                        MarkdownText(
                            markdown = answer,
                            baseFontSize = 12.5.sp,
                            baseColor = SarthiText
                        )

                        // Feedback row
                        Spacer(modifier = Modifier.height(10.dp))
                        if (!feedbackGiven) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.End,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                SarthiButton(
                                    text = "Helpful",
                                    icon = "thumbup",
                                    kind = ButtonKind.Soft,
                                    onClick = { feedbackGiven = true },
                                    modifier = Modifier.height(32.dp)
                                )
                                Spacer(modifier = Modifier.width(6.dp))
                                SarthiButton(
                                    text = "Not fit",
                                    icon = "thumbdown",
                                    kind = ButtonKind.Ghost,
                                    onClick = { feedbackGiven = true },
                                    modifier = Modifier.height(32.dp)
                                )
                            }
                        } else {
                            Text(
                                text = "✓ Feedback saved to Sarthi Memory",
                                color = SarthiGreen,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                }
            }
        }
    }
}
