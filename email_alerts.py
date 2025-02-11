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
TODAY =  pd.Timestamp.today().normalize()   # Ensure TODAY is a pandas datetime type
WARRANTY_ALERT_DAYS = 30    # Notify if warranty expires in 30 days
LICENSE_ALERT_DAYS = 30     # Notify if license expires in 30 days

# Ensure PurchaseDate is datetime format
df["PurchaseDate"] = pd.to_datetime(df["PurchaseDate"], errors="coerce")

# Ensure WarrantyYears is numeric
df["WarrantyYears"] = pd.to_numeric(df["WarrantyYears"], errors="coerce")

# Calculate Expiring Warranties
expiring_warranties = df[
    (df["PurchaseDate"] + pd.to_timedelta(df["WarrantyYears"] * 365, unit="D") - pd.Timedelta(days=WARRANTY_ALERT_DAYS)) <= TODAY
]

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
message = "Subject: IT Assset Alert(s)\n\n"

if not expiring_warranties.empty:
    message += "! Expiring Warranties:**\n"
    for _, row in expiring_warranties.iterrows():
        expiry_date = row["PurchaseDate"] + pd.to_timedelta(row["WarrantyYears"] * 365, unit="D")
        message += f"- {row['Type']} ({row['Model']}): Expires on {expiry_date.date()}\n"

if not expiring_licenses.empty:
    message += "\n! **Expiring Software Licenses:**\n"
    for _, row in expiring_licenses.iterrows():
        message += f"- {row['Type']} ({row['Model']}): License expires on {row['License Expiration'].date()}\n"
    
if not offline_devices.empty or not new_offline_devices.empty:
    message += "\n!!! **Offline Devices Detected:**\n"
    for _, row in pd.concat([offline_devices, new_offline_devices]).iterrows():
        message += f"- {row['Type']} ({row['Model']}) | IP: {row['IP Address']}\n"


# Send Email if Alerts Exist
if "!" in message or "!!!" in message:
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, message.encode("utf-8"))
        server.quit()
        print("** Alert email sent successfully.")
    except Exception as e:
        print(f"** Failed to send email: {e}")
else:
    print("** No alerts to send today.")