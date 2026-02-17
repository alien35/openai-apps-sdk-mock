#!/bin/bash
# Test the minimal fields config endpoint

echo "Testing /api/minimal-fields-config endpoint..."
echo ""

# Start the server in background
uvicorn insurance_server_python.main:app --port 8000 &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Test the endpoint
echo "GET /api/minimal-fields-config"
curl -s http://localhost:8000/api/minimal-fields-config | python -m json.tool | head -30

# Cleanup
kill $SERVER_PID 2>/dev/null

echo ""
echo "✅ Test complete"
