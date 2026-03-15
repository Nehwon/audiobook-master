#!/bin/sh

# Health check script for frontend
# Check if nginx is running and responding

# Check nginx process
if ! pgrep nginx > /dev/null; then
    echo "Nginx is not running"
    exit 1
fi

# Check if we can access the health endpoint
if ! curl -f http://localhost/health > /dev/null 2>&1; then
    echo "Health check failed"
    exit 1
fi

echo "Frontend is healthy"
exit 0
