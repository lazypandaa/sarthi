package ai.sarthi.app

import android.app.Application
import ai.sarthi.app.data.local.TokenManager
import ai.sarthi.app.data.remote.ApiClient

class SarthiApplication : Application() {

    lateinit var tokenManager: TokenManager
        private set

    lateinit var apiClient: ApiClient
        private set

    override fun onCreate() {
        super.onCreate()
        instance = this

        tokenManager = TokenManager(this)
        apiClient = ApiClient(tokenManager)
    }

    companion object {
        lateinit var instance: SarthiApplication
            private set
    }
}
