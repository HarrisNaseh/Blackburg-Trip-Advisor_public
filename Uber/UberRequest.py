#!/usr/bin/env python3
"""
UberRequest.py

A utility module for opening addresses in the Uber app via deep linking.
Handles cases where Uber app isn't installed.
"""

import urllib.parse
import webbrowser
import platform
import subprocess
import sys

def check_uber_app_installed():
    """
    Checks if the Uber app is installed based on the operating system.
    Returns: bool
    """
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        try:
            subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to count (every process whose bundle identifier is "com.ubercab.UberClient")'],
                capture_output=True, check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    elif system == "windows":
        # On Windows, we always use the web link (no deep link for Uber app)
        return False
    elif system == "linux":
        # On Linux, you may not have a native app, so this check could be skipped or modified.
        return False
    return False

def encode_location(location):
    """
    Encodes a location string to be URL-safe for the Uber website URL.
    
    Args:
        location (str): Address or location to encode.
    
    Returns:
        str: URL-encoded location.
    """
    return urllib.parse.quote(location)

def open_uber_app(pickup_address=None, dropoff_address=None):
    """
    Opens the Uber app or website with specified pickup and dropoff locations.
    
    Args:
        pickup_address (str): Starting address (optional)
        dropoff_address (str): Destination address (optional)
    """
    # Hard-coded pickup and dropoff addresses for testing
    pickup_address = "123 Main St, Springfield"
    dropoff_address = "456 Oak St, Shelbyville"
    
    # Create parameters dictionary
    params = {}
    
    # Encode the pickup and dropoff locations
    if pickup_address:
        params["pickup"] = encode_location(pickup_address)
    
    if dropoff_address:
        params["dropoff"] = encode_location(dropoff_address)
    
    # Build the query string
    query_string = urllib.parse.urlencode(params)
    
    # Check if Uber app is installed and not on Windows
    if platform.system().lower() != "windows" and check_uber_app_installed():
        # If not on Windows and Uber app is installed, use app deep linking
        uber_url = f"uber://?action=setPickup&{query_string}"
        try:
            # Attempt to open Uber app
            webbrowser.open(uber_url)
            print("Opening Uber app...")
            return
        except Exception as e:
            print(f"Error opening Uber app: {e}, falling back to website...")
    
    # Always fallback to web version, especially on Windows
    web_url = f"https://m.uber.com/ul/?{query_string}"
    print("Opening Uber website...")
    
    # Display message based on platform
    if platform.system().lower() == "darwin":
        print("Note: If you want to use the app, install it from the App Store: https://apps.apple.com/us/app/uber/id368677368")
    elif platform.system().lower() == "windows":
        print("Note: On Windows, only the website will open. You can download the app from the Microsoft Store: https://apps.microsoft.com/store/detail/uber/9WZDNCRFHXRD")
    else:
        print("Note: If you want to use the app, install it from the Google Play Store: https://play.google.com/store/apps/details?id=com.ubercab")
    
    # Open the Uber website
    webbrowser.open(web_url)

if __name__ == "__main__":
    # Example usage
    print("UberRequest.py - Open addresses in Uber")
    print("---------------------------------------")
    
    # These will be the hardcoded addresses for pickup and dropoff
    open_uber_app(
        pickup_address="123 Main St, Springfield",
        dropoff_address="456 Oak St, Shelbyville"
    )
