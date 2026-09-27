# Sarthi Proguard Rules
-keepattributes *Annotation*
-keepclassmembers class * {
    @com.google.gson.annotations.SerializedName <fields>;
}
-keep class ai.sarthi.app.data.model.** { *; }
-dontwarn okhttp3.**
-dontwarn retrofit2.**
