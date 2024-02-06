# Server Quality Lab (SQL)
import platform
import time
import logging
import smtplib
from email.mime.text import MIMEText
import tkinter as tk
from tkinter import scrolledtext, Entry, messagebox
import threading
import psutil
import datetime
import json


#notes daemonMode loginPass noPower SSH-multiServer

#Easy edit here :)
sender_email =''
sender_password ='' #If its gmial use key :)
recipient_email =''
smpt_port = ''
smpt_server = ''
STATIC_PASSWORD = '' #LoginPass
maxcpu = 1 #for cpu high usage alert
maxram = 75 #for RAM high usage alert


logging.basicConfig(filename='App.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_new_setting():
    global sender_email, sender_password, recipient_email, smpt_port, smpt_server, STATIC_PASSWORD
    try:
        with open('email_settings.json', 'r') as json_file:
            settings = json.load(json_file)
            sender_email = settings['sender_email']
            sender_password = settings['sender_password']
            recipient_email = settings['recipient_email']
            smpt_port = settings['smtp_port']
            smpt_server = settings['smtp_server']
            STATIC_PASSWORD = settings['static_password']
            logging.info(f"Settings loaded: {settings}")
    except Exception as e:
        logging.error(f"Failed to load settings: {e}")

def send_email(subject, body, sender_email, sender_password, recipient_email):
    try:
        server = smtplib.SMTP_SSL(smpt_server, smpt_port)
        server.login(sender_email, sender_password)
        message = MIMEText(body)
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = recipient_email
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit()
        logging.info(f"Email sent successfully with subject '{subject}' and body '{body}'")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")


def monitor_usage():
    while True:
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        logging.info(f"Current CPU Usage: {cpu_usage}")
        if cpu_usage > maxcpu:  # Cpu high usage alert
            alert_message = f"High CPU Usage Alert - Current Usage: {cpu_usage}%"
            send_email("High CPU Usage Alert", alert_message, sender_email, sender_password, recipient_email)
            logging.warning(f"Sent email alert: {alert_message}")
        time.sleep(30) 
        if ram_usage > maxram: # RAM high usage alert
            alert_message = f"High RAM usage Alert - Current Usage: {ram_usage}%"
            send_email("High RAM Usage Alert", alert_message, sender_email, sender_password, recipient_email)
            logging.warning(f"Sent email alert: {alert_message}")
        time.sleep(30)


def get_system_info():
    cpu_percent = psutil.cpu_percent(interval=1)
    ram_percent = psutil.virtual_memory().percent
    uptime = str(datetime.timedelta(seconds=int(time.time() - psutil.boot_time())))
    logging.info(f"System info: CPU usage: {cpu_percent}%, RAM usage: {ram_percent}%, Uptime: {uptime}")
    return {
        'CPUUsage': f"{cpu_percent:.2f}%",
        'RAMUsage': f"{ram_percent:.2f}%",
        'Uptime': uptime
    }


def show_system_info():
    info = f"Device: {platform.node()}\n"
    info += f"CPU: {psutil.cpu_count(logical=True)} cores ({platform.processor()})\n"
    info += f"Total RAM: {psutil.virtual_memory().total / (1024**3):.2f} GB\n"
    
    messagebox.showinfo("System Information", info)


def update_gui():
    system_info = get_system_info()
    cpu_label.config(text=f"CPU Usage: {system_info['CPUUsage']}")
    ram_label.config(text=f"RAM Usage: {system_info['RAMUsage']}")
    uptime_label.config(text=f"System Uptime: {system_info['Uptime']}")
    window.after(1000, update_gui)

def update_log_display():
    try:
        with open('App.log', 'r') as log_file:
            log_contents = log_file.read()
        log_display.config(state=tk.NORMAL)
        log_display.delete(1.0, tk.END)
        log_display.insert(tk.END, log_contents)
        log_display.config(state=tk.DISABLED)
    except Exception as e:
        logging.error(f"Failed to update log display: {e}")

def change_logging_level(level):
    logging_level = getattr(logging, level)
    logging.getLogger().setLevel(logging_level)

def clear_log_display():
    with open('App.log', 'w') as file:
        file.write("")  
    update_log_display()  

def send_manual_alert():
    recipient_email = recipient_entry.get()
    if recipient_email:
        alert_message = "This is a manual alert. Please take necessary actions."
        send_email("Manual Alert", alert_message, sender_email, sender_password, recipient_email)
        logging.info(f"Sent manual email alert to {recipient_email}")
    else:
        messagebox.showerror("Error", "Recipient email not provided.")


def keep_updating_log():
    while True:
        update_log_display()
        time.sleep(5)


def verify_password():
    entered_password = password_entry.get()
    if entered_password == STATIC_PASSWORD:
        login_window.destroy()
        open_main_window()
    else:
        messagebox.showerror("Error", "Incorrect Password")

def show_login_window():
    global login_window, password_entry
    login_window = tk.Tk()
    login_window.title("Login")
    tk.Label(login_window, text="Enter App Password:").pack()

    password_entry = tk.Entry(login_window, show="*", width=20)
    password_entry.pack()

    tk.Button(login_window, text="Login", command=verify_password).pack()

    login_window.mainloop()

def edit_email_settings():
    global email_settings_window, smtp_server_entry, smtp_port_entry, sender_email_entry, sender_password_entry, recipient_email_entry
    email_settings_window = tk.Toplevel(window)
    email_settings_window.title("Email Settings")

    tk.Label(email_settings_window, text="SMTP Server:").pack()
    smtp_server_entry = tk.Entry(email_settings_window)
    smtp_server_entry.pack()

    tk.Label(email_settings_window, text="SMTP Port:").pack()
    smtp_port_entry = tk.Entry(email_settings_window)
    smtp_port_entry.pack()

    tk.Label(email_settings_window, text="Sender Email:").pack()
    sender_email_entry = tk.Entry(email_settings_window)
    sender_email_entry.pack()

    tk.Label(email_settings_window, text="Sender Password (KEY for gmail):").pack()
    sender_password_entry = tk.Entry(email_settings_window, show="*")
    sender_password_entry.pack()

    tk.Label(email_settings_window, text="Recipient Email:").pack()
    recipient_email_entry = tk.Entry(email_settings_window)
    recipient_email_entry.pack()

    tk.Button(email_settings_window, text="Save Settings", command=save_email_settings).pack()

def save_email_settings():
    smtp_server = smtp_server_entry.get()
    smtp_port = smtp_port_entry.get()
    sender_email = sender_email_entry.get()
    sender_password = sender_password_entry.get()
    recipient_email = recipient_email_entry.get()
    settings = {
        "smtp_server": smtp_server,
        "smtp_port": smtp_port,
        "sender_email": sender_email,
        "sender_password": sender_password,
        "recipient_email": recipient_email
    }
    with open('email_settings.json', 'w') as json_file:
        json.dump(settings, json_file, indent=2)
    logging.info(f"Email settings updated: {settings}")
    email_settings_window.destroy()

def edit_static_password():
    def save_new_static_password():
        global STATIC_PASSWORD
        new_password = new_password_entry.get()
        if new_password:
            STATIC_PASSWORD = new_password
            with open('email_settings.json', 'r+') as json_file:
                settings = json.load(json_file)
                settings['static_password'] = new_password
                json_file.seek(0)  # Reset file pointer to the beginning of the file
                json.dump(settings, json_file, indent=4)
                json_file.truncate()  # Remove any remaining part of the old content
            static_password_window.destroy()
            logging.info("Static password updated successfully.")
        else:
            messagebox.showerror("Error", "New password cannot be empty.")

    static_password_window = tk.Toplevel(window)
    static_password_window.title("Edit Static Password")

    tk.Label(static_password_window, text="New Static Password:").pack()

    new_password_entry = tk.Entry(static_password_window, show="*", width=20)
    new_password_entry.pack()

    tk.Button(static_password_window, text="Save", command=save_new_static_password).pack()

def settings_window():
    settings_window = tk.Toplevel(window)
    settings_window.title("Settings")
    settings_window.geometry("300x150")

    edit_email_settings_button = tk.Button(settings_window, text="Edit Email Settings", command=edit_email_settings, font=("Helvetica", 12))
    edit_email_settings_button.pack(pady=10)

    edit_static_password_button = tk.Button(settings_window, text="Edit Static Pass", command=edit_static_password, font=("Helvetica", 12))
    edit_static_password_button.pack(pady=10)

    show_system_info_button = tk.Button(settings_window, text="Show System Info", command=show_system_info, font=("Helvetica", 12))
    show_system_info_button.pack(pady=10)

def open_main_window():
    global window, cpu_label, ram_label, uptime_label, recipient_entry, log_display
    window = tk.Tk()
    window.title("SQL")
    font = ("Helvetica", 12)

    title_label = tk.Label(window, text="Server Quality Lab", font=("Helvetica", 16, "bold"))
    title_label.pack(pady=10)

    cpu_label = tk.Label(window, text="CPU Usage: Checking...", font=font)
    ram_label = tk.Label(window, text="RAM Usage: Checking...", font=font)
    uptime_label = tk.Label(window, text="System Uptime: Checking...", font=font)

    log_level_var = tk.StringVar(window)
    log_level_var.set("INFO")  # default log
    log_level_dropdown = tk.OptionMenu(window, log_level_var, "INFO", "WARNING", "ERROR", command=change_logging_level)
    log_level_dropdown.pack(pady=3)
    cpu_label.pack()
    ram_label.pack()
    uptime_label.pack()

    recipient_label = tk.Label(window, text="Recipient Email:", font=font)
    recipient_label.pack()

    recipient_entry = Entry(window, font=font)
    recipient_entry.pack()

    log_display = scrolledtext.ScrolledText(window, state='disabled', height=10, wrap=tk.WORD, font=font)
    log_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    clear_log_button = tk.Button(window, text="Clear Log", command=clear_log_display, font=font)
    clear_log_button.pack(pady=5)

    send_alert_button = tk.Button(window, text="Send Manual Alert", command=send_manual_alert, font=font, fg="red")
    send_alert_button.pack(pady=5)

    settings_button = tk.Button(window, text="Settings", command=settings_window, font=font)
    settings_button.pack(pady=5)


    window.after(1000, update_gui)

    log_thread = threading.Thread(target=keep_updating_log, daemon=True)
    log_thread.start()

    cpu_thread = threading.Thread(target=monitor_usage, daemon=True)
    cpu_thread.start()

    window.mainloop()

#deamon mode IF i (remembered)

if __name__ == "__main__":
    load_new_setting()
    show_login_window()
