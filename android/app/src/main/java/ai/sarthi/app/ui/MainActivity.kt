package ai.sarthi.app.ui

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import coil.load
import ai.sarthi.app.R
import ai.sarthi.app.SarthiApplication
import ai.sarthi.app.audio.AudioPlayerManager
import ai.sarthi.app.audio.AudioRecorderManager
import ai.sarthi.app.data.model.AdvisoryItem
import ai.sarthi.app.data.model.LoginRequest
import ai.sarthi.app.data.model.TeachMemoryRequest
import ai.sarthi.app.data.model.TextQueryRequest
import ai.sarthi.app.databinding.ActivityMainBinding
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.File

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val apiClient by lazy { SarthiApplication.instance.apiClient }
    private val tokenManager by lazy { SarthiApplication.instance.tokenManager }

    private val audioRecorder by lazy { AudioRecorderManager(this) }
    private val audioPlayer by lazy { AudioPlayerManager(this) }

    private var isRecordingAudio = false
    private var lastAudioData: String? = null

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        if (isGranted) {
            toggleVoiceRecording()
        } else {
            Toast.makeText(this, "Microphone permission is required for voice queries", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupBottomNavigation()
        setupVoiceAssistantControls()
        setupTeachMemoryControl()
        ensureAuthenticationAndLoadData()
    }

    private fun setupBottomNavigation() {
        binding.bottomNav.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home -> switchTab(0)
                R.id.nav_voice -> switchTab(1)
                R.id.nav_advisories -> switchTab(2)
                R.id.nav_memory -> switchTab(3)
            }
            true
        }
    }

    private fun switchTab(index: Int) {
        binding.viewDashboard.visibility = if (index == 0) View.VISIBLE else View.GONE
        binding.viewVoice.visibility = if (index == 1) View.VISIBLE else View.GONE
        binding.viewAdvisories.visibility = if (index == 2) View.VISIBLE else View.GONE
        binding.viewMemory.visibility = if (index == 3) View.VISIBLE else View.GONE
    }

    private fun setupVoiceAssistantControls() {
        // Floating circular mic button
        binding.btnMic.setOnClickListener {
            checkPermissionAndRecord()
        }

        // Quick prompt chips
        binding.chipSample1.setOnClickListener {
            sendTextQuery("गेहूं की फसल के लिए सबसे अच्छी खाद कौन सी है?")
        }
        binding.chipSample2.setOnClickListener {
            sendTextQuery("टमाटर की फसल में पत्ती मुड़ने का क्या कारण है?")
        }
        binding.chipSample3.setOnClickListener {
            sendTextQuery("सीहोर मंडी में आज सोयाबीन और गेहूं का क्या भाव है?")
        }

        // Text query send button
        binding.btnSendText.setOnClickListener {
            val query = binding.etTextQuery.text.toString().trim()
            if (query.isNotEmpty()) {
                sendTextQuery(query)
                binding.etTextQuery.text.clear()
            }
        }

        // Audio response playback toggle
        binding.btnPlayAudio.setOnClickListener {
            lastAudioData?.let { audioBase64 ->
                if (audioPlayer.isPlaying) {
                    audioPlayer.stop()
                    binding.btnPlayAudio.text = "🔊 आवाज सुनें"
                } else {
                    playVoiceAudio(audioBase64)
                }
            }
        }
    }

    private fun checkPermissionAndRecord() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
            toggleVoiceRecording()
        } else {
            requestPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
        }
    }

    private fun toggleVoiceRecording() {
        if (!isRecordingAudio) {
            startRecording()
        } else {
            stopRecordingAndSend()
        }
    }

    private fun startRecording() {
        isRecordingAudio = true
        binding.btnMic.setBackgroundResource(R.drawable.bg_mic_recording)
        binding.tvVoiceStatus.text = "🔴 बोल रहे हैं... भेजने के लिए पुनः टैप करें"
        binding.tvVoiceStatus.setTextColor(getColor(R.color.error))

        lifecycleScope.launch(Dispatchers.IO) {
            val result = audioRecorder.startRecording()
            if (result.isFailure) {
                withContext(Dispatchers.Main) {
                    isRecordingAudio = false
                    binding.btnMic.setBackgroundResource(R.drawable.bg_mic_circle)
                    binding.tvVoiceStatus.text = "रिकॉर्डिंग विफल रही, पुनः प्रयास करें"
                    binding.tvVoiceStatus.setTextColor(getColor(R.color.text_accent))
                }
            }
        }
    }

    private fun stopRecordingAndSend() {
        isRecordingAudio = false
        audioRecorder.stopRecording()

        binding.btnMic.setBackgroundResource(R.drawable.bg_mic_circle)
        binding.tvVoiceStatus.text = "🧠 सारथी सोच रहा है (Sarvam AI)..."
        binding.tvVoiceStatus.setTextColor(getColor(R.color.secondary))
        binding.pbVoiceLoading.visibility = View.VISIBLE

        lifecycleScope.launch {
            try {
                // Find most recent recording file
                val cacheFiles = cacheDir.listFiles { _, name -> name.startsWith("sarthi_query_") && name.endsWith(".wav") }
                val wavFile = cacheFiles?.maxByOrNull { it.lastModified() }

                if (wavFile != null && wavFile.exists() && wavFile.length() > 0) {
                    val requestFile = wavFile.asRequestBody("audio/wav".toMediaTypeOrNull())
                    val filePart = MultipartBody.Part.createFormData("file", wavFile.name, requestFile)
                    val langPart = "hi".toRequestBody("text/plain".toMediaTypeOrNull())

                    val response = withContext(Dispatchers.IO) {
                        apiClient.voiceAssistantApi.processAudio(filePart, langPart)
                    }

                    if (response.isSuccessful && response.body() != null) {
                        val body = response.body()!!
                        renderVoiceResponse(
                            transcript = body.transcript ?: "आवाज रिकॉर्डिंग",
                            responseText = body.responseText,
                            audioData = body.audioData,
                            memoryUsed = body.memoryContext?.used == true
                        )
                    } else {
                        binding.tvVoiceStatus.text = "उत्तर प्राप्त नहीं हो सका (${response.code()})"
                    }

                    wavFile.delete()
                } else {
                    binding.tvVoiceStatus.text = "ऑडियो फ़ाइल रिक्त थी"
                }
            } catch (e: Exception) {
                binding.tvVoiceStatus.text = "त्रुटि: ${e.localizedMessage ?: "नेटवर्क समस्या"}"
            } finally {
                binding.pbVoiceLoading.visibility = View.GONE
            }
        }
    }

    private fun sendTextQuery(query: String) {
        switchTab(1)
        binding.bottomNav.selectedItemId = R.id.nav_voice

        binding.tvVoiceStatus.text = "🧠 सारथी सोच रहा है (Sarvam AI)..."
        binding.tvVoiceStatus.setTextColor(getColor(R.color.secondary))
        binding.pbVoiceLoading.visibility = View.VISIBLE

        lifecycleScope.launch {
            try {
                val response = withContext(Dispatchers.IO) {
                    apiClient.voiceAssistantApi.processText(TextQueryRequest(query, "hi"))
                }

                if (response.isSuccessful && response.body() != null) {
                    val body = response.body()!!
                    renderVoiceResponse(
                        transcript = query,
                        responseText = body.responseText,
                        audioData = body.audioData,
                        memoryUsed = body.memoryContext?.used == true
                    )
                } else {
                    binding.tvVoiceStatus.text = "उत्तर प्राप्त नहीं हुआ (${response.code()})"
                }
            } catch (e: Exception) {
                binding.tvVoiceStatus.text = "त्रुटि: ${e.localizedMessage ?: "नेटवर्क समस्या"}"
            } finally {
                binding.pbVoiceLoading.visibility = View.GONE
            }
        }
    }

    private fun renderVoiceResponse(
        transcript: String,
        responseText: String,
        audioData: String?,
        memoryUsed: Boolean
    ) {
        binding.cardVoiceResult.visibility = View.VISIBLE
        binding.tvTranscript.text = transcript
        binding.tvVoiceResponse.text = responseText
        binding.tvVoiceStatus.text = "उत्तर तैयार है • बोलने के लिए माइक दबाएं"
        binding.tvVoiceStatus.setTextColor(getColor(R.color.text_accent))

        binding.tvMemoryInfluenceBadge.visibility = if (memoryUsed) View.VISIBLE else View.GONE
        binding.btnPlayAudio.visibility = if (!audioData.isNullOrBlank()) View.VISIBLE else View.GONE

        lastAudioData = audioData

        if (!audioData.isNullOrBlank()) {
            playVoiceAudio(audioData)
        }
    }

    private fun playVoiceAudio(audioBase64: String) {
        binding.btnPlayAudio.text = "⏹️ रोकें"
        lifecycleScope.launch {
            audioPlayer.playBase64Audio(audioBase64) {
                binding.btnPlayAudio.text = "🔊 आवाज सुनें"
            }
        }
    }

    private fun setupTeachMemoryControl() {
        binding.btnSaveMemory.setOnClickListener {
            val text = binding.etTeachMemory.text.toString().trim()
            if (text.isNotEmpty()) {
                binding.btnSaveMemory.isEnabled = false
                lifecycleScope.launch {
                    try {
                        val response = withContext(Dispatchers.IO) {
                            apiClient.memoryApi.teachMemory(
                                TeachMemoryRequest(
                                    farmerId = tokenManager.userPhone ?: "+919999999001",
                                    type = "constraint",
                                    content = text
                                )
                            )
                        }
                        if (response.isSuccessful) {
                            Toast.makeText(this@MainActivity, "✅ मेमोरी सुरक्षित कर ली गई!", Toast.LENGTH_SHORT).show()
                            binding.etTeachMemory.text.clear()
                        } else {
                            Toast.makeText(this@MainActivity, "सहेजने में असमर्थ (${response.code()})", Toast.LENGTH_SHORT).show()
                        }
                    } catch (e: Exception) {
                        Toast.makeText(this@MainActivity, "त्रुटि: ${e.localizedMessage}", Toast.LENGTH_SHORT).show()
                    } finally {
                        binding.btnSaveMemory.isEnabled = true
                    }
                }
            }
        }
    }

    private fun ensureAuthenticationAndLoadData() {
        lifecycleScope.launch {
            try {
                // Ensure authenticated session
                if (!tokenManager.isLoggedIn) {
                    val loginRes = withContext(Dispatchers.IO) {
                        apiClient.authApi.login(LoginRequest("+919999999001", "demoPassword123!"))
                    }
                    if (loginRes.isSuccessful && loginRes.body() != null) {
                        tokenManager.token = loginRes.body()!!.accessToken
                        tokenManager.userPhone = "+919999999001"
                        tokenManager.userLocation = "Sehore, Madhya Pradesh, India"
                    }
                }

                loadLiveDashboardData()
                loadOfficialAdvisories()
            } catch (e: Exception) {
                // Fallbacks keep UI completely interactive
            }
        }
    }

    private suspend fun loadLiveDashboardData() {
        withContext(Dispatchers.IO) {
            try {
                val weatherRes = apiClient.agriDataApi.getWeather("Sehore, Madhya Pradesh")
                if (weatherRes.isSuccessful && weatherRes.body() != null) {
                    val w = weatherRes.body()!!
                    withContext(Dispatchers.Main) {
                        binding.tvQuickWeather.text = "${w.temperature?.toInt() ?: 28}°C • ${w.condition ?: "साफ़"}"
                        binding.tvWeatherTempDetail.text = "तापमान: ${w.temperature ?: 28.4}°C • आर्द्रता: ${w.humidity?.toInt() ?: 62}% • वर्षा: ${w.rainfall ?: 0.0} mm"
                        if (!w.advisory.isNullOrBlank()) {
                            binding.tvWeatherAdvisory.text = w.advisory
                        }
                    }
                }
            } catch (e: Exception) {
                // Keep default
            }

            try {
                val soilRes = apiClient.agriDataApi.getEnvironmentalProfile("Sehore, Madhya Pradesh")
                if (soilRes.isSuccessful && soilRes.body() != null) {
                    val s = soilRes.body()!!
                    withContext(Dispatchers.Main) {
                        binding.tvSoilSummary.text = "मिट्टी: ${s.soilType ?: "मध्यम काली मिट्टी"} • pH: ${s.ph ?: 7.2} • वर्षा क्षेत्र: ${s.rainfallZone ?: "मध्यम"}"
                    }
                }
            } catch (e: Exception) {
                // Keep default
            }

            try {
                val marketsRes = apiClient.agriDataApi.getMarketPrices("Sehore")
                if (marketsRes.isSuccessful && !marketsRes.body().isNullOrEmpty()) {
                    val items = marketsRes.body()!!
                    val sb = StringBuilder()
                    items.take(4).forEach { m ->
                        sb.append("• ${m.commodity}: ₹${m.modalPrice?.toInt() ?: 4500}/Qtl (${m.market})\n")
                    }
                    if (sb.isNotEmpty()) {
                        withContext(Dispatchers.Main) {
                            binding.tvMandiList.text = sb.toString().trim()
                        }
                    }
                }
            } catch (e: Exception) {
                // Keep default
            }

            try {
                val memRes = apiClient.memoryApi.getMemorySummary("+919999999001")
                if (memRes.isSuccessful && memRes.body() != null) {
                    val count = memRes.body()!!.totalMemories
                    withContext(Dispatchers.Main) {
                        binding.tvQuickMemory.text = "$count सुरक्षित"
                    }
                }
            } catch (e: Exception) {
                // Keep default
            }
        }
    }

    private suspend fun loadOfficialAdvisories() {
        withContext(Dispatchers.IO) {
            try {
                val res = apiClient.agriDataApi.getAdvisories()
                if (res.isSuccessful && !res.body().isNullOrEmpty()) {
                    val advisories = res.body()!!
                    withContext(Dispatchers.Main) {
                        binding.advisoriesList.removeAllViews()
                        advisories.take(6).forEach { advisory ->
                            val cardView = LayoutInflater.from(this@MainActivity)
                                .inflate(R.layout.item_advisory, binding.advisoriesList, false)

                            val ivPhoto = cardView.findViewById<ImageView>(R.id.ivAdvisoryPhoto)
                            val tvCat = cardView.findViewById<TextView>(R.id.tvAdvisoryCategory)
                            val tvDate = cardView.findViewById<TextView>(R.id.tvAdvisoryDate)
                            val tvTitle = cardView.findViewById<TextView>(R.id.tvAdvisoryTitle)
                            val tvSummary = cardView.findViewById<TextView>(R.id.tvAdvisorySummary)

                            tvCat.text = advisory.category ?: "कृषि सलाह"
                            tvDate.text = advisory.date ?: "हाल ही में"
                            tvTitle.text = advisory.title
                            tvSummary.text = advisory.summary

                            if (!advisory.photoUrl.isNullOrBlank()) {
                                ivPhoto.visibility = View.VISIBLE
                                ivPhoto.load(advisory.photoUrl) {
                                    crossfade(true)
                                    placeholder(R.drawable.bg_card)
                                    error(R.drawable.bg_card)
                                }
                            } else {
                                ivPhoto.visibility = View.GONE
                            }

                            binding.advisoriesList.addView(cardView)
                        }
                    }
                }
            } catch (e: Exception) {
                // Keep fallback
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        audioPlayer.stop()
        audioRecorder.stopRecording()
    }
}
