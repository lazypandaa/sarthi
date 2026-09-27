package ai.sarthi.app.ui

import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import ai.sarthi.app.BuildConfig
import ai.sarthi.app.R
import ai.sarthi.app.SarthiApplication
import ai.sarthi.app.databinding.ActivityMainBinding
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val apiClient by lazy { SarthiApplication.instance.apiClient }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupUI()
        verifyBackendConnectivity()
    }

    private fun setupUI() {
        binding.tvBackendUrl.text = "Backend: ${BuildConfig.BASE_URL}"
        binding.tvApiStatus.text = "Connecting to Azure services..."
        binding.progressBar.visibility = View.VISIBLE
    }

    private fun verifyBackendConnectivity() {
        lifecycleScope.launch {
            try {
                val response = withContext(Dispatchers.IO) {
                    apiClient.agriDataApi.checkHealth()
                }

                if (response.isSuccessful && response.body()?.status == "healthy") {
                    val db = response.body()?.database ?: "connected"
                    binding.tvApiStatus.text = "Connected • $db"
                    binding.tvApiStatus.setTextColor(getColor(R.color.success))
                } else {
                    binding.tvApiStatus.text = "Backend reachable (HTTP ${response.code()})"
                    binding.tvApiStatus.setTextColor(getColor(R.color.secondary))
                }
            } catch (e: Exception) {
                binding.tvApiStatus.text = "Connection error: ${e.localizedMessage ?: "Network error"}"
                binding.tvApiStatus.setTextColor(getColor(R.color.error))
            } finally {
                binding.progressBar.visibility = View.GONE
            }
        }
    }
}
