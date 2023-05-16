#!/bin/bash

# Function to retrieve the current public IP address
get_pr_ip() {
    curl -sS http://169.254.169.254/latest/meta-data/local-ipv4
}

# Define the port to check
PORT=5000

while true; do
    # Retrieve the current public IP address
    CURRENT_IP="172.31.3.223"

    # Function to check if the IP and port are responsive
    check_availability() {
        nc -zv -w 5 $CURRENT_IP $PORT > /dev/null 2>&1
    }

    # Check if the IP and port are responsive
    if check_availability; then
        echo "IP $CURRENT_IP is responsive"
    else
        echo "IP $CURRENT_IP is not responsive. Restarting app2.service..."
        
        # Restart the app2.service
        systemctl restart app2.service
        
        # Wait for the service to start
        sleep 5
        
        # Retrieve the new public IP address after restart
        NEW_IP=$(get_pr_ip)
        
        # Check if the new IP and port are responsive
        if check_availability; then
            echo "Restart successful. New IP $NEW_IP is now responsive."
        else
            echo "Restart failed. New IP $NEW_IP is still not responsive."
        fi
    fi
    
    # Wait for 10 seconds before running the loop again
    sleep 10
done
