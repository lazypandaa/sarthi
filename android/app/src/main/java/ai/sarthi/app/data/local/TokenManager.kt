package ai.sarthi.app.data.local

import android.content.Context
import android.content.SharedPreferences

class TokenManager(context: Context) {

    private val prefs: SharedPreferences =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    var token: String?
        get() = prefs.getString(KEY_TOKEN, null)
        set(value) = prefs.edit().putString(KEY_TOKEN, value).apply()

    var userPhone: String?
        get() = prefs.getString(KEY_PHONE, null)
        set(value) = prefs.edit().putString(KEY_PHONE, value).apply()

    var userLanguage: String
        get() = prefs.getString(KEY_LANG, "hi") ?: "hi"
        set(value) = prefs.edit().putString(KEY_LANG, value).apply()

    var userLocation: String?
        get() = prefs.getString(KEY_LOCATION, null)
        set(value) = prefs.edit().putString(KEY_LOCATION, value).apply()

    fun clear() {
        prefs.edit().clear().apply()
    }

    val isLoggedIn: Boolean
        get() = !token.isNullOrBlank()

    companion object {
        private const val PREFS_NAME = "sarthi_prefs"
        private const val KEY_TOKEN = "access_token"
        private const val KEY_PHONE = "user_phone"
        private const val KEY_LANG = "user_language"
        private const val KEY_LOCATION = "user_location"
    }
}
