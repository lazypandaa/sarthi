package ai.sarthi.app.audio

import android.content.Context
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.util.Base64
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream

/**
 * Handles decoding and playback of voice responses synthesized by Sarvam Bulbul TTS
 * and returned by Sarthi's backend in Base64 audio format.
 */
class AudioPlayerManager(private val context: Context) {

    private var mediaPlayer: MediaPlayer? = null
    var isPlaying = false
        private set

    suspend fun playBase64Audio(
        base64Audio: String,
        onCompletion: (() -> Unit)? = null
    ): Result<Unit> = withContext(Dispatchers.IO) {
        try {
            stop()

            val audioBytes = Base64.decode(base64Audio, Base64.DEFAULT)
            val tempAudioFile = File(context.cacheDir, "sarthi_response_${System.currentTimeMillis()}.wav")

            FileOutputStream(tempAudioFile).use { fos ->
                fos.write(audioBytes)
            }

            withContext(Dispatchers.Main) {
                mediaPlayer = MediaPlayer().apply {
                    setAudioAttributes(
                        AudioAttributes.Builder()
                            .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                            .setUsage(AudioAttributes.USAGE_ASSISTANCE_NAVIGATION_GUIDANCE)
                            .build()
                    )
                    setDataSource(tempAudioFile.absolutePath)
                    prepare()
                    setOnCompletionListener {
                        this@AudioPlayerManager.isPlaying = false
                        onCompletion?.invoke()
                        tempAudioFile.delete()
                    }
                    start()
                    this@AudioPlayerManager.isPlaying = true
                }
            }

            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun stop() {
        try {
            if (mediaPlayer?.isPlaying == true) {
                mediaPlayer?.stop()
            }
            mediaPlayer?.release()
        } catch (e: Exception) {
            // Ignore on cleanup
        } finally {
            mediaPlayer = null
            isPlaying = false
        }
    }
}
