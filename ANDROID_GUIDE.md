# 📱 Android App Development Guide

## تطبيق أندرويد - دليل التطوير

### 🏗️ البنية المعمارية

```
SubtitleTranslatorPro/
│
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/subtitletranslator/
│   │   │   │   ├── MainActivity.java
│   │   │   │   ├── ui/
│   │   │   │   │   ├── UploadActivity.java
│   │   │   │   │   ├── TranslationActivity.java
│   │   │   │   │   ├── EditorActivity.java
│   │   │   │   │   └── ResultsActivity.java
│   │   │   │   ├── api/
│   │   │   │   │   ├── ApiClient.java
│   │   │   │   │   └── ApiService.java
│   │   │   │   ├── models/
│   │   │   │   │   ├── SubtitleFile.java
│   │   │   │   │   ├── TranslationJob.java
│   │   │   │   │   └── SubtitleEntry.java
│   │   │   │   └── utils/
│   │   │   │       ├── FileHelper.java
│   │   │   │       └── NetworkHelper.java
│   │   │   ├── res/
│   │   │   │   ├── layout/
│   │   │   │   ├── values/
│   │   │   │   └── drawable/
│   │   │   └── AndroidManifest.xml
│   │   └── build.gradle
│   └── build.gradle
└── settings.gradle
```

---

## 🔌 API Integration

### Base URL Configuration

```java
public class ApiConfig {
    // للتطوير المحلي
    public static final String BASE_URL_LOCAL = "http://localhost:5000/api/";
    
    // للخادم الإنتاجي
    public static final String BASE_URL_PRODUCTION = "https://your-domain.com/api/";
    
    // الاستخدام الحالي
    public static String getCurrentBaseUrl() {
        return BuildConfig.DEBUG ? BASE_URL_LOCAL : BASE_URL_PRODUCTION;
    }
}
```

### API Client (Retrofit)

```java
// ApiClient.java
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;
import okhttp3.OkHttpClient;
import okhttp3.logging.HttpLoggingInterceptor;

public class ApiClient {
    private static Retrofit retrofit = null;
    
    public static Retrofit getClient() {
        if (retrofit == null) {
            HttpLoggingInterceptor logging = new HttpLoggingInterceptor();
            logging.setLevel(HttpLoggingInterceptor.Level.BODY);
            
            OkHttpClient client = new OkHttpClient.Builder()
                .addInterceptor(logging)
                .build();
            
            retrofit = new Retrofit.Builder()
                .baseUrl(ApiConfig.getCurrentBaseUrl())
                .addConverterFactory(GsonConverterFactory.create())
                .client(client)
                .build();
        }
        return retrofit;
    }
    
    public static ApiService getApiService() {
        return getClient().create(ApiService.class);
    }
}
```

### API Service Interface

```java
// ApiService.java
import retrofit2.Call;
import retrofit2.http.*;
import okhttp3.MultipartBody;
import okhttp3.RequestBody;

public interface ApiService {
    
    @GET("languages")
    Call<LanguagesResponse> getLanguages();
    
    @GET("services")
    Call<ServicesResponse> getServices();
    
    @Multipart
    @POST("upload")
    Call<UploadResponse> uploadFiles(
        @Part List<MultipartBody.Part> files
    );
    
    @POST("translate")
    Call<TranslateResponse> startTranslation(
        @Body TranslationRequest request
    );
    
    @GET("status/{jobId}")
    Call<StatusResponse> getStatus(
        @Path("jobId") String jobId
    );
    
    @GET("edit/{jobId}")
    Call<EditDataResponse> getEditData(
        @Path("jobId") String jobId
    );
    
    @POST("save/{jobId}")
    Call<SaveResponse> saveEdited(
        @Path("jobId") String jobId,
        @Body SaveRequest request
    );
    
    @GET("download/{jobId}")
    Call<ResponseBody> downloadResults(
        @Path("jobId") String jobId
    );
    
    @DELETE("delete/{jobId}")
    Call<DeleteResponse> deleteJob(
        @Path("jobId") String jobId
    );
}
```

---

## 📊 Models

### SubtitleFile Model

```java
public class SubtitleFile {
    private String name;
    private String format;
    private long size;
    private String path;
    private String uri; // For Android URI
    
    // Constructor, getters, setters
    public SubtitleFile(String name, String format, long size) {
        this.name = name;
        this.format = format;
        this.size = size;
    }
    
    // Getters and Setters
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public String getFormat() { return format; }
    public void setFormat(String format) { this.format = format; }
    
    public long getSize() { return size; }
    public void setSize(long size) { this.size = size; }
    
    public String getFormattedSize() {
        return String.format("%.2f KB", size / 1024.0);
    }
}
```

### TranslationJob Model

```java
public class TranslationJob {
    private String jobId;
    private String status; // pending, processing, completed, failed
    private int progress;
    private int totalFiles;
    private String sourceLang;
    private String targetLang;
    private String service;
    private List<TranslationResult> results;
    private String error;
    
    // Constructor, getters, setters
    // ...
}
```

### SubtitleEntry Model

```java
public class SubtitleEntry {
    private int index;
    private String startTime;
    private String endTime;
    private String text;
    
    // Constructor
    public SubtitleEntry(int index, String startTime, String endTime, String text) {
        this.index = index;
        this.startTime = startTime;
        this.endTime = endTime;
        this.text = text;
    }
    
    // Getters and Setters
    // ...
}
```

---

## 🎨 UI Screens

### 1. MainActivity (Home Screen)

**Features:**
- Welcome screen
- Quick start button
- Recent translations
- Settings access

**Layout:** `activity_main.xml`
```xml
<?xml version="1.0" encoding="utf-8"?>
<androidx.coordinatorlayout.widget.CoordinatorLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    
    <com.google.android.material.appbar.AppBarLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content">
        
        <com.google.android.material.appbar.MaterialToolbar
            android:id="@+id/toolbar"
            android:layout_width="match_parent"
            android:layout_height="?attr/actionBarSize"
            app:title="@string/app_name" />
    </com.google.android.material.appbar.AppBarLayout>
    
    <androidx.core.widget.NestedScrollView
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        app:layout_behavior="@string/appbar_scrolling_view_behavior">
        
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:padding="16dp">
            
            <!-- Hero Section -->
            <com.google.android.material.card.MaterialCardView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginBottom="16dp">
                
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:orientation="vertical"
                    android:padding="24dp">
                    
                    <TextView
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="🎬 Subtitle Translator Pro"
                        android:textSize="24sp"
                        android:textStyle="bold" />
                    
                    <TextView
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginTop="8dp"
                        android:text="ترجمة احترافية للأفلام"
                        android:textSize="16sp" />
                    
                    <com.google.android.material.button.MaterialButton
                        android:id="@+id/btnStart"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:layout_marginTop="16dp"
                        android:text="🚀 بدء الترجمة"
                        android:textSize="16sp" />
                </LinearLayout>
            </com.google.android.material.card.MaterialCardView>
            
            <!-- Recent Translations -->
            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="📋 الترجمات الأخيرة"
                android:textSize="18sp"
                android:textStyle="bold"
                android:layout_marginBottom="8dp" />
            
            <androidx.recyclerview.widget.RecyclerView
                android:id="@+id/recyclerRecent"
                android:layout_width="match_parent"
                android:layout_height="wrap_content" />
        </LinearLayout>
    </androidx.core.widget.NestedScrollView>
</androidx.coordinatorlayout.widget.CoordinatorLayout>
```

### 2. UploadActivity

**Features:**
- File picker
- Drag and drop support
- File list with preview
- Remove files option

### 3. TranslationActivity

**Features:**
- Language selection
- Service selection
- Context preservation toggle
- Translation progress
- Real-time status updates

### 4. EditorActivity

**Features:**
- Subtitle editor
- Time adjustment
- Text editing
- Save changes

### 5. ResultsActivity

**Features:**
- Download results
- Share files
- Open editor
- Delete project

---

## 🔧 Key Features Implementation

### File Upload

```java
// UploadActivity.java
private void uploadFiles(List<Uri> fileUris) {
    List<MultipartBody.Part> parts = new ArrayList<>();
    
    for (Uri uri : fileUris) {
        try {
            InputStream inputStream = getContentResolver().openInputStream(uri);
            String fileName = getFileName(uri);
            
            RequestBody requestFile = RequestBody.create(
                MediaType.parse("application/octet-stream"),
                getBytes(inputStream)
            );
            
            MultipartBody.Part part = MultipartBody.Part.createFormData(
                "files", fileName, requestFile
            );
            parts.add(part);
            
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    
    Call<UploadResponse> call = ApiClient.getApiService().uploadFiles(parts);
    call.enqueue(new Callback<UploadResponse>() {
        @Override
        public void onResponse(Call<UploadResponse> call, Response<UploadResponse> response) {
            if (response.isSuccessful() && response.body() != null) {
                String jobId = response.body().getJobId();
                // Navigate to TranslationActivity
                Intent intent = new Intent(UploadActivity.this, TranslationActivity.class);
                intent.putExtra("JOB_ID", jobId);
                startActivity(intent);
            }
        }
        
        @Override
        public void onFailure(Call<UploadResponse> call, Throwable t) {
            Toast.makeText(UploadActivity.this, 
                "Upload failed: " + t.getMessage(), Toast.LENGTH_SHORT).show();
        }
    });
}
```

### Progress Monitoring

```java
// TranslationActivity.java
private void monitorProgress(String jobId) {
    handler.postDelayed(new Runnable() {
        @Override
        public void run() {
            Call<StatusResponse> call = ApiClient.getApiService().getStatus(jobId);
            call.enqueue(new Callback<StatusResponse>() {
                @Override
                public void onResponse(Call<StatusResponse> call, Response<StatusResponse> response) {
                    if (response.isSuccessful() && response.body() != null) {
                        TranslationJob job = response.body().getJob();
                        
                        // Update UI
                        progressBar.setProgress(job.getProgress());
                        statusText.setText("Progress: " + job.getProgress() + "%");
                        
                        if ("completed".equals(job.getStatus())) {
                            // Navigate to results
                            navigateToResults(jobId);
                        } else if ("failed".equals(job.getStatus())) {
                            showError(job.getError());
                        } else {
                            // Continue monitoring
                            monitorProgress(jobId);
                        }
                    }
                }
                
                @Override
                public void onFailure(Call<StatusResponse> call, Throwable t) {
                    showError(t.getMessage());
                }
            });
        }
    }, 1000); // Check every second
}
```

---

## 📦 Dependencies (build.gradle)

```gradle
dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.10.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    
    // Retrofit for API calls
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    implementation 'com.squareup.okhttp3:logging-interceptor:4.11.0'
    
    // RecyclerView
    implementation 'androidx.recyclerview:recyclerview:1.3.2'
    
    // File picker
    implementation 'com.github.dhaval2404:imagepicker:2.1'
    
    // Progress indicators
    implementation 'com.github.ybq:Android-SpinKit:1.4.0'
    
    // Room Database (for offline storage)
    implementation 'androidx.room:room-runtime:2.6.0'
    annotationProcessor 'androidx.room:room-compiler:2.6.0'
}
```

---

## 🔐 Permissions (AndroidManifest.xml)

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

---

## 🚀 Recommended Features

1. **Offline Mode**
   - Cache translations locally
   - Edit offline
   - Sync when online

2. **Cloud Sync**
   - Sync projects across devices
   - Backup to cloud

3. **Batch Processing**
   - Queue multiple translation jobs
   - Background processing

4. **Notifications**
   - Translation complete notifications
   - Progress notifications

5. **Dark Mode**
   - Support for dark theme
   - Automatic theme switching

---

## 📱 Testing

### Unit Tests
```java
@Test
public void testApiClient() {
    ApiService service = ApiClient.getApiService();
    assertNotNull(service);
}
```

### UI Tests
```java
@Test
public void testUploadFlow() {
    onView(withId(R.id.btnUpload)).perform(click());
    // Verify upload screen is shown
}
```

---

**استمتع بتطوير تطبيق Android احترافي! 📱**
