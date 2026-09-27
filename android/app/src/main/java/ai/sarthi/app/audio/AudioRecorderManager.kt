package ai.sarthi.app.audio

import android.content.Context
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream
import java.io.RandomAccessFile

/**
 * Manages audio recording in 16kHz Mono 16-bit PCM WAV format.
 * Tailored for seamless ingestion by Sarvam Saaras STT via Sarthi's /process-audio backend.
 */
class AudioRecorderManager(private val context: Context) {

    private var audioRecord: AudioRecord? = null
    private var isRecording = false
    private var recordingFile: File? = null

    private val sampleRate = 16000
    private val channelConfig = AudioFormat.CHANNEL_IN_MONO
    private val audioFormat = AudioFormat.ENCODING_PCM_16BIT

    suspend fun startRecording(): Result<File> = withContext(Dispatchers.IO) {
        try {
            val minBufferSize = AudioRecord.getMinBufferSize(sampleRate, channelConfig, audioFormat)
            val bufferSize = minBufferSize.coerceAtLeast(sampleRate * 2)

            audioRecord = AudioRecord(
                MediaRecorder.AudioSource.MIC,
                sampleRate,
                channelConfig,
                audioFormat,
                bufferSize
            )

            if (audioRecord?.state != AudioRecord.STATE_INITIALIZED) {
                return@withContext Result.failure(IllegalStateException("AudioRecord failed to initialize"))
            }

            val outputFile = File(context.cacheDir, "sarthi_query_${System.currentTimeMillis()}.wav")
            recordingFile = outputFile
            isRecording = true

            audioRecord?.startRecording()

            // Write raw PCM with placeholder WAV header
            val outputStream = FileOutputStream(outputFile)
            writeWavHeader(outputStream, sampleRate, 1, 16, 0)

            val buffer = ByteArray(bufferSize)
            var totalAudioLen: Long = 0

            while (isRecording) {
                val read = audioRecord?.read(buffer, 0, buffer.size) ?: -1
                if (read > 0) {
                    outputStream.write(buffer, 0, read)
                    totalAudioLen += read
                }
            }

            outputStream.close()

            // Update WAV header with actual data length
            updateWavHeader(outputFile, totalAudioLen)

            Result.success(outputFile)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun stopRecording() {
        isRecording = false
        try {
            audioRecord?.stop()
            audioRecord?.release()
        } catch (e: Exception) {
            // Ignore on cleanup
        } finally {
            audioRecord = null
        }
    }

    private fun writeWavHeader(
        out: FileOutputStream,
        sampleRate: Int,
        channels: Int,
        bitsPerSample: Int,
        dataLength: Long
    ) {
        val byteRate = (sampleRate * channels * bitsPerSample / 8).toLong()
        val totalDataLen = dataLength + 36
        val header = ByteArray(44)

        // RIFF chunk descriptor
        header[0] = 'R'.code.toByte()
        header[1] = 'I'.code.toByte()
        header[2] = 'F'.code.toByte()
        header[3] = 'F'.code.toByte()
        header[4] = (totalDataLen and 0xff).toByte()
        header[5] = (totalDataLen shr 8 and 0xff).toByte()
        header[6] = (totalDataLen shr 16 and 0xff).toByte()
        header[7] = (totalDataLen shr 24 and 0xff).toByte()
        header[8] = 'W'.code.toByte()
        header[9] = 'A'.code.toByte()
        header[10] = 'V'.code.toByte()
        header[11] = 'E'.code.toByte()

        // "fmt " sub-chunk
        header[12] = 'f'.code.toByte()
        header[13] = 'm'.code.toByte()
        header[14] = 't'.code.toByte()
        header[15] = ' '.code.toByte()
        header[16] = 16 // 16 for PCM
        header[17] = 0
        header[18] = 0
        header[19] = 0
        header[20] = 1 // Audio format 1 = PCM
        header[21] = 0
        header[22] = channels.toByte()
        header[23] = 0
        header[24] = (sampleRate and 0xff).toByte()
        header[25] = (sampleRate shr 8 and 0xff).toByte()
        header[26] = (sampleRate shr 16 and 0xff).toByte()
        header[27] = (sampleRate shr 24 and 0xff).toByte()
        header[28] = (byteRate and 0xff).toByte()
        header[29] = (byteRate shr 8 and 0xff).toByte()
        header[30] = (byteRate shr 16 and 0xff).toByte()
        header[31] = (byteRate shr 24 and 0xff).toByte()
        header[32] = (channels * bitsPerSample / 8).toByte() // Block align
        header[33] = 0
        header[34] = bitsPerSample.toByte()
        header[35] = 0

        // "data" sub-chunk
        header[36] = 'd'.code.toByte()
        header[37] = 'a'.code.toByte()
        header[38] = 't'.code.toByte()
        header[39] = 'a'.code.toByte()
        header[40] = (dataLength and 0xff).toByte()
        header[41] = (dataLength shr 8 and 0xff).toByte()
        header[42] = (dataLength shr 16 and 0xff).toByte()
        header[43] = (dataLength shr 24 and 0xff).toByte()

        out.write(header, 0, 44)
    }

    private fun updateWavHeader(file: File, dataLength: Long) {
        val totalDataLen = dataLength + 36
        val raf = RandomAccessFile(file, "rw")
        try {
            raf.seek(4)
            raf.write((totalDataLen and 0xff).toInt())
            raf.write((totalDataLen shr 8 and 0xff).toInt())
            raf.write((totalDataLen shr 16 and 0xff).toInt())
            raf.write((totalDataLen shr 24 and 0xff).toInt())

            raf.seek(40)
            raf.write((dataLength and 0xff).toInt())
            raf.write((dataLength shr 8 and 0xff).toInt())
            raf.write((dataLength shr 16 and 0xff).toInt())
            raf.write((dataLength shr 24 and 0xff).toInt())
        } finally {
            raf.close()
        }
    }
}
