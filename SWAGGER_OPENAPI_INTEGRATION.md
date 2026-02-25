# Swagger/OpenAPI Integration

## Overview

The Insurance MCP Server now includes full OpenAPI 3.0 specification and interactive API documentation via Swagger UI and ReDoc.

## Endpoints Added

### 1. OpenAPI Specification
**URL:** `http://localhost:8000/openapi.json`

Returns the complete OpenAPI 3.0 specification in JSON format.

```bash
curl http://localhost:8000/openapi.json
```

### 2. Swagger UI (Interactive Documentation)
**URL:** `http://localhost:8000/docs`

Interactive API documentation where you can:
- Browse all available endpoints
- See request/response schemas
- Try out API calls directly in the browser
- View example requests and responses

**Usage:**
1. Start the server: `uvicorn insurance_server_python.main:app --port 8000`
2. Open browser: http://localhost:8000/docs
3. Explore and test endpoints interactively

### 3. ReDoc (Alternative Documentation UI)
**URL:** `http://localhost:8000/redoc`

Alternative documentation interface with:
- Clean, responsive layout
- Better for API reference documentation
- Easier to navigate large APIs
- No interactive testing (read-only)

**Usage:**
1. Start the server: `uvicorn insurance_server_python.main:app --port 8000`
2. Open browser: http://localhost:8000/redoc

## API Documentation Structure

### Health Endpoints
- `GET /` - Root endpoint with service information
- `GET /health` - Health check for container orchestration

### Quote Endpoints
- `GET /api/quick-quote-carriers` - Carrier estimates by state

### Asset Endpoints
- `GET /assets/images/{filename}` - Static image serving

## OpenAPI Spec Features

### Complete Schema Definitions
- Request parameters with types and defaults
- Response schemas with examples
- Error responses (404, 500, etc.)
- Content-Type specifications

### Organized by Tags
- **Health**: Service status endpoints
- **Configuration**: Wizard and field configs
- **Quotes**: Insurance quote endpoints
- **Assets**: Static file serving

### Query Parameters Documented
Example for `/api/quick-quote-carriers`:
- `state` (string, default: "CA") - State code
- `zip_code` (string, default: "90210") - ZIP code
- `city` (string, default: "Beverly Hills") - City name

## Using the OpenAPI Spec

### 1. API Client Generation
Generate API clients in any language:

```bash
# Install OpenAPI Generator
npm install @openapitools/openapi-generator-cli -g

# Generate Python client
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -o ./client-python

# Generate TypeScript client
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-axios \
  -o ./client-typescript
```

### 2. API Testing
Import into Postman, Insomnia, or other API testing tools:
- File → Import → Enter URL: `http://localhost:8000/openapi.json`

### 3. Contract Testing
Use the spec for contract testing:

```python
import requests

# Validate response against OpenAPI spec
from openapi_core import create_spec
from openapi_core.validation.response.validators import ResponseValidator

spec_url = "http://localhost:8000/openapi.json"
spec = create_spec(requests.get(spec_url).json())
validator = ResponseValidator(spec)

response = requests.get("http://localhost:8000/health")
result = validator.validate(response)
```

## Example: Testing with Swagger UI

1. **Start the server:**
   ```bash
   cd /Users/alexanderleon/mi/openai-apps-sdk-examples
   uvicorn insurance_server_python.main:app --port 8000
   ```

2. **Open Swagger UI:**
   - Navigate to: http://localhost:8000/docs

3. **Try an endpoint:**
   - Click on `GET /api/quick-quote-carriers`
   - Click "Try it out"
   - Modify parameters (e.g., state: "TX")
   - Click "Execute"
   - View the response

4. **Check health:**
   - Click on `GET /health`
   - Click "Try it out"
   - Click "Execute"
   - Should return: `{"status": "healthy"}`

## Customizing the OpenAPI Spec

The OpenAPI spec is generated in `insurance_server_python/main.py`:

```python
def generate_openapi_spec():
    """Generate OpenAPI 3.0 specification for the API."""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Insurance MCP Server API",
            "version": "1.0.0",
            # ...
        },
        # ...
    }
```

### To Add a New Endpoint:
1. Add your route to `main.py`
2. Add the endpoint documentation to `generate_openapi_spec()`
3. Restart the server
4. Refresh `/docs` to see the new endpoint

### Example: Adding a New Endpoint

```python
# 1. Add the route
@app.route("/api/new-endpoint", methods=["GET"])
def new_endpoint():
    return {"message": "Hello from new endpoint"}

# 2. Add to generate_openapi_spec() in paths section
"/api/new-endpoint": {
    "get": {
        "summary": "New endpoint",
        "description": "Description of what it does",
        "tags": ["Configuration"],
        "responses": {
            "200": {
                "description": "Success response",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "message": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
    }
}
```

## Benefits

### For Development
- ✅ Interactive testing without Postman/curl
- ✅ Always up-to-date documentation
- ✅ Easy to share API spec with team

### For Integration
- ✅ Auto-generate client SDKs
- ✅ Import into API testing tools
- ✅ Contract testing support

### For Documentation
- ✅ Two UI options (Swagger + ReDoc)
- ✅ Clear parameter descriptions
- ✅ Example values provided
- ✅ Response schema documentation

## Production Considerations

### 1. Security
In production, consider:
- Removing `/docs` and `/redoc` endpoints
- Or adding authentication to documentation endpoints
- Rate limiting for `/openapi.json`

### 2. Custom Domain
Update the servers section in `generate_openapi_spec()`:

```python
"servers": [
    {
        "url": "https://api.yourdomain.com",
        "description": "Production server"
    },
    {
        "url": "http://localhost:8000",
        "description": "Local development"
    }
]
```

### 3. Versioning
Track API version in the spec:

```python
"info": {
    "version": "2.0.0",  # Increment on breaking changes
    # ...
}
```

## Troubleshooting

### Issue: Swagger UI shows blank page
**Solution:** Check browser console for CORS errors. The app already has CORS middleware configured.

### Issue: OpenAPI spec doesn't load
**Solution:** Ensure server is running and accessible at http://localhost:8000/openapi.json

### Issue: Endpoints don't appear in docs
**Solution:** Verify the endpoint is added to both:
1. As a route in `main.py`
2. In the `paths` section of `generate_openapi_spec()`

## Files Modified

- `insurance_server_python/main.py`
  - Added `generate_openapi_spec()` function
  - Added `/openapi.json` endpoint
  - Added `/docs` endpoint (Swagger UI)
  - Added `/redoc` endpoint (ReDoc UI)

## Testing

All existing tests continue to pass:
```bash
pytest insurance_server_python/tests/
# 100 passed
```

The new endpoints don't require tests as they serve static documentation.
