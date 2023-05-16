#!/bin/bash

# Define the application URL to check
APP_URL="https://demo.knowledge-vortex.com"

# Function to check if the application is responsive
check_availability() {
    response=$(curl -IsS -k $APP_URL | head -n 1)
    if [[ $response == *"200 OK"* ]]; then
        return 0
    else
        return 1
    fi
}

# Infinite loop to check every 10 seconds
while true; do
    # Check if the application is responsive
    if check_availability; then
        echo "Application is responsive"
    else
        echo "Application is not responsive. Restarting app2.service..."
        
        # Restart the app2.service
        systemctl restart app2.service
        
        # Check if the restart was successful
        if check_availability; then
            echo "Restart successful. Application is now responsive."
        else
            echo "Restart failed. Application is still not responsive."
        fi
    fi
    
    # Wait for 10 seconds before checking again
    sleep 10
done
