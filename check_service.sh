#!/bin/bash

# Define the IP address and port to check
IP_ADDRESS="https://demo.knowledge-vortex.com"

# Function to check if the IP and port are responsive
check_availability() {
    nc -zv -w 5 $IP_ADDRESS  > /dev/null 2>&1
}

# Infinite loop to check every 10 seconds
while true; do
    # Check if the IP and port are responsive
    if check_availability; then
        echo "IP is responsive"
    else
        echo "IP is not responsive. Restarting app2.service..."
        
        # Restart the app2.service
       sudo systemctl restart app2.service
        
        # Check if the restart was successful
        if check_availability; then
            echo "Restart successful. IP is now responsive."
        else
            echo "Restart failed. IP is still not responsive."
        fi
    fi
    
    # Wait for 10 seconds before checking again
    sleep 10
done
