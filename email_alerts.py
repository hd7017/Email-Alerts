import smtplib
import pandas as pd
import datetime
import socket


# Email Configuration
SMTP_SERVER = "smtp.gmail.com"  # Change smtp.______" for other emails
SMTP_PORT = 587
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"    # Use an App Password, not your actual password
EMAIL_RECEIVER = "it_admin@example.com"


# Read CSV Data
df = pd.read_csv("assets.csv", parse_dates=["PurchaseDate", "License Expiration"])


# Set Threshold Values
TODAY = datetime.date.today()
WARRANTY_ALERT_DAYS = 30    # Notify if warranty expires in 30 days
LICENSE_ALERT_DAYS = 30     # Notify if license expires in 30 days


# Check for Warranty Expirations
expiring_warranties = df[df["PurchaseDate"] + pd.to_timedelta(df["WarrantyYears"] * 365, unit="D") - pd.Timedelta(days=WARRANTY_ALERTS_DAYS) <= TODAY]

# Check for Software License Expirations
expiring_licenses = df[df["License Expiration"] - pd.Timedelta(days=LICENSE_ALERT_DAYS) <= TODAY]


# Check for Offline Devices
offline_devices = df[df["Status"].str.lower() == "offline"]

# Check Live Network Status
def is_device_online(ip):
    try:
        socket.create_connection((ip, 80), timeout = 2)
        return True
    except OSError:
        return False

df["Ping Status"] = df["IP Address"].apply(lambda ip: "Online" if is_device_online(ip) else "Offline")
new_offline_devices = df[df["Ping Status"] == "Offline"]


# Construct Email Alert Message


# Send Email if Alerts Exist