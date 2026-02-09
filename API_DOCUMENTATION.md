# 🔌 API Documentation

## Subtitle Translator Pro - REST API Reference

Base URL: `http://localhost:5000/api`

---

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Languages](#get-supported-languages)
3. [Services](#get-translation-services)
4. [Upload Files](#upload-subtitle-files)
5. [Start Translation](#start-translation)
6. [Check Status](#check-translation-status)
7. [Get Edit Data](#get-edit-data)
8. [Save Edits](#save-edited-subtitles)
9. [Download Results](#download-translated-files)
10. [Delete Job](#delete-translation-job)

---

## 🔐 Authentication

Currently, the API does not require authentication for local usage. For production deployment, consider implementing:
- API Keys
- JWT Tokens
- OAuth 2.0

---

## 📚 Endpoints

### Get Supported Languages

**Endpoint:** `GET /api/languages`

**Description:** Returns a list of all supported languages.

**Request:**
```bash
curl -X GET http://localhost:5000/api/languages
```

**Response:**
```json
{
  "success": true,
  "languages": {
    "ar": "Arabic (العربية)",
    "en": "English",
    "es": "Spanish (Español)",
    "fr": "French (Français)",
    "de": "German (Deutsch)",
    "it": "Italian (Italiano)",
    "pt": "Portuguese (Português)",
    "ru": "Russian (Русский)",
    "zh": "Chinese (中文)",
    "ja": "Japanese (日本語)",
    "ko": "Korean (한국어)",
    "tr": "Turkish (Türkçe)",
    "hi": "Hindi (हिन्दी)"
  }
}
```

**Status Codes:**
- `200 OK`: Success

---

### Get Translation Services

**Endpoint:** `GET /api/services`

**Description:** Returns information about available translation services.

**Request:**
```bash
curl -X GET http://localhost:5000/api/services
```

**Response:**
```json
{
  "success": true,
  "services": {
    "google": {
      "available": true,
      "type": "free",
      "supports_context": false
    },
    "gemini": {
      "available": true,
      "type": "paid",
      "supports_context": true
    },
    "deepl": {
      "available": false,
      "type": "paid",
      "supports_context": false
    }
  }
}
```

**Status Codes:**
- `200 OK`: Success

---

### Upload Subtitle Files

**Endpoint:** `POST /api/upload`

**Description:** Upload subtitle files for translation.

**Request:**
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "files=@subtitle1.srt" \
  -F "files=@subtitle2.srt" \
  -F "files=@episode3.vtt"
```

**Parameters:**
- `files` (required): One or more subtitle files (multipart/form-data)
  - Max files: 20
  - Max size per file: 1 MB
  - Supported formats: .srt, .vtt, .ass, .sub, .sbv, .stl

**Response:**
```json
{
  "success": true,
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "files": [
    {
      "name": "subtitle1.srt",
      "format": "srt",
      "size": 12345,
      "path": "/uploads/a1b2c3d4.../subtitle1.srt"
    },
    {
      "name": "subtitle2.srt",
      "format": "srt",
      "size": 23456,
      "path": "/uploads/a1b2c3d4.../subtitle2.srt"
    }
  ]
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Maximum 20 files allowed"
}
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Invalid files or limits exceeded

---

### Start Translation

**Endpoint:** `POST /api/translate`

**Description:** Start translation job for uploaded files.

**Request:**
```bash
curl -X POST http://localhost:5000/api/translate \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "source_lang": "en",
    "target_lang": "ar",
    "service": "google",
    "use_context": false
  }'
```

**Parameters:**
- `job_id` (required): Job ID from upload response
- `source_lang` (required): Source language code (e.g., "en", "ar")
- `target_lang` (required): Target language code
- `service` (required): Translation service ("google", "gemini", "deepl")
- `use_context` (optional): Enable context preservation (default: false, only works with "gemini")

**Response:**
```json
{
  "success": true,
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "Translation started"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Missing required fields"
}
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Missing fields or invalid job_id

---

### Check Translation Status

**Endpoint:** `GET /api/status/{job_id}`

**Description:** Check the status and progress of a translation job.

**Request:**
```bash
curl -X GET http://localhost:5000/api/status/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Response (In Progress):**
```json
{
  "success": true,
  "job": {
    "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "status": "processing",
    "progress": 45,
    "total_files": 2,
    "source_lang": "en",
    "target_lang": "ar",
    "service": "google",
    "results": [],
    "error": null,
    "created_at": "2024-02-09T12:00:00",
    "completed_at": null
  }
}
```

**Response (Completed):**
```json
{
  "success": true,
  "job": {
    "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "status": "completed",
    "progress": 100,
    "total_files": 2,
    "source_lang": "en",
    "target_lang": "ar",
    "service": "google",
    "results": [
      {
        "original_name": "subtitle1.srt",
        "translated_name": "subtitle1_translated.srt",
        "path": "/outputs/a1b2c3d4.../subtitle1_translated.srt",
        "entries": 150,
        "status": "completed"
      },
      {
        "original_name": "subtitle2.srt",
        "translated_name": "subtitle2_translated.srt",
        "path": "/outputs/a1b2c3d4.../subtitle2_translated.srt",
        "entries": 200,
        "status": "completed"
      }
    ],
    "error": null,
    "created_at": "2024-02-09T12:00:00",
    "completed_at": "2024-02-09T12:05:30"
  }
}
```

**Status Values:**
- `pending`: Job is waiting to start
- `processing`: Translation in progress
- `completed`: Translation completed successfully
- `failed`: Translation failed

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: Job not found

---

### Get Edit Data

**Endpoint:** `GET /api/edit/{job_id}`

**Description:** Get subtitle data for editing.

**Request:**
```bash
curl -X GET http://localhost:5000/api/edit/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Response:**
```json
{
  "success": true,
  "files": [
    {
      "filename": "subtitle1_translated.srt",
      "entries": [
        {
          "index": 1,
          "start_time": "00:00:01,000",
          "end_time": "00:00:03,500",
          "text": "مرحباً بكم في الفيلم"
        },
        {
          "index": 2,
          "start_time": "00:00:04,000",
          "end_time": "00:00:07,000",
          "text": "هذه قصة مذهلة"
        }
      ]
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Job not ready
- `404 Not Found`: Job not found

---

### Save Edited Subtitles

**Endpoint:** `POST /api/save/{job_id}`

**Description:** Save edited subtitle data.

**Request:**
```bash
curl -X POST http://localhost:5000/api/save/a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
  -H "Content-Type: application/json" \
  -d '{
    "files": [
      {
        "filename": "subtitle1_translated.srt",
        "entries": [
          {
            "index": 1,
            "start_time": "00:00:01,000",
            "end_time": "00:00:03,500",
            "text": "النص المعدل هنا"
          }
        ]
      }
    ]
  }'
```

**Parameters:**
- `files` (required): Array of files with edited entries

**Response:**
```json
{
  "success": true,
  "message": "Files saved successfully"
}
```

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: Job not found
- `500 Internal Server Error`: Save failed

---

### Download Translated Files

**Endpoint:** `GET /api/download/{job_id}`

**Description:** Download all translated files as a ZIP archive.

**Request:**
```bash
curl -O http://localhost:5000/api/download/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Response:**
- Binary ZIP file containing all translated subtitle files
- Filename: `translated_subtitles.zip`

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Job not ready

---

### Delete Translation Job

**Endpoint:** `DELETE /api/delete/{job_id}`

**Description:** Delete a translation job and all associated files.

**Request:**
```bash
curl -X DELETE http://localhost:5000/api/delete/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Response:**
```json
{
  "success": true,
  "message": "Job deleted"
}
```

**Status Codes:**
- `200 OK`: Success

---

## 📊 Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `200 OK`: Request successful
- `400 Bad Request`: Invalid parameters or request
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## 🔄 Rate Limiting

Default rate limits:
- 100 requests per minute per IP
- Configurable in `.env` file

When rate limit is exceeded:
```json
{
  "success": false,
  "error": "Rate limit exceeded. Please try again later."
}
```

---

## 💡 Best Practices

1. **Polling for Status**
   - Poll `/api/status/{job_id}` every 1-2 seconds
   - Stop polling when status is "completed" or "failed"

2. **File Upload**
   - Validate file format before upload
   - Check file size (max 1MB per file)
   - Handle upload errors gracefully

3. **Error Handling**
   - Always check `success` field in response
   - Display user-friendly error messages
   - Implement retry logic for network errors

4. **Context Preservation**
   - Only enable with Gemini service
   - Increases translation time but improves quality

---

## 🔐 Security Considerations

For production deployment:

1. **API Key Authentication**
```bash
curl -H "X-API-Key: your-api-key" http://your-domain.com/api/...
```

2. **HTTPS Only**
   - Always use HTTPS in production
   - Never send API keys over HTTP

3. **Input Validation**
   - File size limits enforced
   - File format validation
   - Sanitize all inputs

4. **Rate Limiting**
   - Implement per-user rate limits
   - Use Redis for distributed rate limiting

---

## 📝 Example Workflow

Complete translation workflow:

```bash
# 1. Upload files
curl -X POST http://localhost:5000/api/upload \
  -F "files=@episode1.srt" \
  -F "files=@episode2.srt"

# Response: {"success": true, "job_id": "abc123..."}

# 2. Start translation
curl -X POST http://localhost:5000/api/translate \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "abc123...",
    "source_lang": "en",
    "target_lang": "ar",
    "service": "google"
  }'

# 3. Check status (repeat until completed)
curl http://localhost:5000/api/status/abc123...

# 4. Download results
curl -O http://localhost:5000/api/download/abc123...
```

---

**For more information, see README.md and ANDROID_GUIDE.md**
