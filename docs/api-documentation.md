# GastroAssist API Documentation

## Overview

The GastroAssist API provides intelligent question answering capabilities specifically for gastroenterology, combining a curated knowledge base with dynamic search to deliver accurate, source-attributed responses.

- **Base URL**: `http://localhost:8000`
- **API Version**: 0.1.0
- **Documentation URL**: `http://localhost:8000/docs` (Swagger UI)
- **ReDoc URL**: `http://localhost:8000/redoc` (ReDoc alternative UI)

## Authentication

GastroAssist API uses API key authentication. 

```
Authorization: Bearer YOUR_API_KEY
```

API keys can be obtained through the administrative interface. Contact the system administrator to receive your API key.

## Endpoints

### Health Check

#### GET /

Returns basic information about the API and confirms it's operational.

**Request:**
```http
GET / HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "name": "GastroAssist AI API",
  "status": "online",
  "version": "0.1.0",
  "documentation": "/docs",
  "health": "ok"
}
```

**Status Codes:**
- `200 OK` - API is functioning correctly

### Process Query

#### POST /api/query

Processes a gastroenterology-related query and returns an answer with source attributions.

**Request:**
```http
POST /api/query HTTP/1.1
Host: localhost:8000
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "text": "What are the latest guidelines for H. pylori treatment?",
  "user_id": "user-12345",
  "context": {
    "patient_age": 45,
    "patient_history": ["previous H. pylori infection", "peptic ulcer disease"],
    "preferred_sources": ["AGA", "ACG"]
  }
}
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| text | string | Yes | The medical query text |
| user_id | string | Yes | Unique identifier for the requesting user |
| context | object | No | Optional contextual information to enhance the response |

**Context Object Properties:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| patient_age | integer | No | Age of the patient if relevant |
| patient_history | array of strings | No | Relevant medical history |
| preferred_sources | array of strings | No | Preferred medical sources/authorities |

**Response:**
```json
{
  "answer": "Current guidelines for H. pylori treatment recommend quadruple therapy as first-line treatment in most regions due to increasing clarithromycin resistance. The ACG and AGA recommend bismuth quadruple therapy (PPI, bismuth, tetracycline, and metronidazole) for 14 days. In regions with low clarithromycin resistance, triple therapy with a PPI, clarithromycin, and amoxicillin or metronidazole may still be used. Post-treatment testing to confirm eradication is recommended.",
  "sources": [
    {
      "title": "ACG Clinical Guidelines: Treatment of Helicobacter pylori Infection",
      "url": "https://journals.lww.com/ajg/Fulltext/2017/02000/ACG_Clinical_Guideline__Treatment_of_Helicobacter.12.aspx",
      "snippet": "The ACG now recommends bismuth quadruple therapy as first-line treatment in areas with high clarithromycin resistance...",
      "confidence": 0.95
    },
    {
      "title": "AGA Clinical Practice Update on the Management of Helicobacter pylori Infection",
      "url": "https://www.gastrojournal.org/article/S0016-5085(17)35531-2/fulltext",
      "snippet": "For first-line treatment, clinicians should use clarithromycin triple therapy only in regions where clarithromycin resistance is low...",
      "confidence": 0.92
    }
  ],
  "confidence_score": 0.93
}
```

**Status Codes:**
- `200 OK` - Query successfully processed
- `400 Bad Request` - Invalid query parameters
- `401 Unauthorized` - Missing or invalid API key
- `500 Internal Server Error` - Server-side processing error

### User Management

#### POST /api/users

Creates a new user in the system.

**Request:**
```http
POST /api/users HTTP/1.1
Host: localhost:8000
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "username": "dr.smith",
  "email": "dr.smith@hospital.org",
  "full_name": "Dr. Jane Smith",
  "specialty": "Gastroenterology",
  "role": "physician"
}
```

**Response:**
```json
{
  "user_id": "user-67890",
  "username": "dr.smith",
  "email": "dr.smith@hospital.org",
  "created_at": "2025-05-07T10:30:45Z",
  "status": "active"
}
```

**Status Codes:**
- `201 Created` - User successfully created
- `400 Bad Request` - Invalid user data
- `401 Unauthorized` - Missing or invalid API key
- `409 Conflict` - Username or email already exists

#### GET /api/users/{user_id}

Retrieves information about a specific user.

**Request:**
```http
GET /api/users/user-67890 HTTP/1.1
Host: localhost:8000
Authorization: Bearer YOUR_API_KEY
```

**Response:**
```json
{
  "user_id": "user-67890",
  "username": "dr.smith",
  "email": "dr.smith@hospital.org",
  "full_name": "Dr. Jane Smith",
  "specialty": "Gastroenterology",
  "role": "physician",
  "created_at": "2025-05-07T10:30:45Z",
  "last_login": "2025-05-07T14:15:22Z",
  "status": "active"
}
```

**Status Codes:**
- `200 OK` - User found
- `401 Unauthorized` - Missing or invalid API key
- `404 Not Found` - User not found

### Query History

#### GET /api/users/{user_id}/history

Retrieves query history for a specific user.

**Request:**
```http
GET /api/users/user-67890/history HTTP/1.1
Host: localhost:8000
Authorization: Bearer YOUR_API_KEY
```

**Query Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| limit | integer | No | Maximum number of history items to return (default: 20) |
| offset | integer | No | Number of items to skip (for pagination, default: 0) |
| start_date | string (ISO 8601) | No | Filter by start date |
| end_date | string (ISO 8601) | No | Filter by end date |

**Response:**
```json
{
  "count": 35,
  "next": "/api/users/user-67890/history?limit=20&offset=20",
  "previous": null,
  "results": [
    {
      "query_id": "query-12345",
      "query_text": "What are the latest guidelines for H. pylori treatment?",
      "timestamp": "2025-05-07T14:10:23Z",
      "sources_count": 2,
      "confidence_score": 0.93
    },
    {
      "query_id": "query-12344",
      "query_text": "When should a colonoscopy be performed after removal of adenomatous polyps?",
      "timestamp": "2025-05-06T11:22:17Z",
      "sources_count": 3,
      "confidence_score": 0.89
    },
    // Additional history items...
  ]
}
```

**Status Codes:**
- `200 OK` - History retrieved successfully
- `401 Unauthorized` - Missing or invalid API key
- `404 Not Found` - User not found

### Feedback Management

#### POST /api/feedback

Submits feedback for a specific query response.

**Request:**
```http
POST /api/feedback HTTP/1.1
Host: localhost:8000
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "query_id": "query-12345",
  "user_id": "user-67890",
  "rating": 4,
  "accuracy_score": 4,
  "relevance_score": 5,
  "sources_quality_score": 4,
  "comments": "Good answer but missed mentioning concomitant PPI usage recommendations."
}
```

**Response:**
```json
{
  "feedback_id": "feedback-56789",
  "query_id": "query-12345",
  "timestamp": "2025-05-07T15:45:32Z",
  "status": "received"
}
```

**Status Codes:**
- `201 Created` - Feedback successfully submitted
- `400 Bad Request` - Invalid feedback data
- `401 Unauthorized` - Missing or invalid API key
- `404 Not Found` - Query ID not found

## Error Responses

All error responses follow this standard format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional error details if available
    }
  }
}
```

**Common Error Codes:**
- `AUTHENTICATION_ERROR` - Missing or invalid API key
- `VALIDATION_ERROR` - Invalid request parameters
- `RESOURCE_NOT_FOUND` - Requested resource not found
- `PROCESSING_ERROR` - Error during query processing
- `RATE_LIMIT_EXCEEDED` - API rate limit exceeded
- `SERVER_ERROR` - Internal server error

## Rate Limiting

The API implements rate limiting to ensure service stability:

- **Standard tier**: 60 requests per minute
- **Professional tier**: 120 requests per minute
- **Enterprise tier**: Custom limits based on contract

Rate limit headers are included in each response:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1620406893
```

## Webhooks

GastroAssist supports webhooks for integrating with external systems.

### Available Webhook Events

- `query.processed` - Triggered when a query has been successfully processed
- `feedback.submitted` - Triggered when feedback is submitted
- `user.created` - Triggered when a new user is created

### Webhook Configuration

Configure webhooks through the administrative interface or via the API:

```http
POST /api/webhooks HTTP/1.1
Host: localhost:8000
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "url": "https://your-system.com/webhooks/gastroassist",
  "events": ["query.processed", "feedback.submitted"],
  "secret": "your_webhook_secret",
  "active": true,
  "description": "Integration with hospital EMR system"
}
```

## SDK Libraries

Official client libraries are available for easy integration:

- **Python**: `pip install gastroassist-client`
- **JavaScript/TypeScript**: `npm install gastroassist-client`
- **Java**: Available via Maven Central

## Example Code

### Python Example

```python
from gastroassist_client import GastroAssistAPI

# Initialize the client
client = GastroAssistAPI(api_key="YOUR_API_KEY")

# Submit a query
response = client.query(
    text="What is the recommended screening interval for colorectal cancer in patients with a family history?",
    user_id="user-67890",
    context={
        "patient_age": 45,
        "patient_history": ["family history of colorectal cancer"]
    }
)

# Process the response
print(f"Answer: {response.answer}")
print(f"Confidence: {response.confidence_score}")
print("Sources:")
for source in response.sources:
    print(f"- {source.title} ({source.confidence})")
```

### JavaScript/TypeScript Example

```javascript
import { GastroAssistAPI } from 'gastroassist-client';

// Initialize the client
const client = new GastroAssistAPI({
  apiKey: 'YOUR_API_KEY'
});

// Submit a query
async function queryGastroAssist() {
  try {
    const response = await client.query({
      text: 'What is the recommended screening interval for colorectal cancer in patients with a family history?',
      userId: 'user-67890',
      context: {
        patientAge: 45,
        patientHistory: ['family history of colorectal cancer']
      }
    });
    
    // Process the response
    console.log(`Answer: ${response.answer}`);
    console.log(`Confidence: ${response.confidenceScore}`);
    console.log('Sources:');
    response.sources.forEach(source => {
      console.log(`- ${source.title} (${source.confidence})`);
    });
  } catch (error) {
    console.error('Error querying GastroAssist:', error);
  }
}

queryGastroAssist();
```

## Further Resources

- [System Architecture Documentation](https://github.com/your-organization/gastroassist/blob/main/docs/architecture/system-overview.md)
- [Development Setup Guide](https://github.com/your-organization/gastroassist/blob/main/docs/development/setup-guide.md)
- [Troubleshooting](https://github.com/your-organization/gastroassist/blob/main/docs/troubleshooting.md)
- [Official Website](https://gastroassist.ai)

## Support

For additional support:

- Email: support@gastroassist.ai
- Developer Forum: https://developers.gastroassist.ai/forum
- GitHub Issues: https://github.com/your-organization/gastroassist/issues