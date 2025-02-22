import customtkinter as ctk
from plyer import notification
import json
import os
import pygame

# Initialize pygame mixer
pygame.mixer.init()

# Load or create a configuration file
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    else:
        return {
            "work_time": 25,  # In minutes
            "short_break": 5,  # In minutes
            "long_break": 15,  # In minutes
            "theme": "dark"
        }

def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file)

# Function to play sound using pygame
def play_sound():
    pygame.mixer.music.load("alert.mp3")
    pygame.mixer.music.play()

# Pomodoro Timer Application
class PomodoroTimer(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Load user settings
        self.config_data = load_config()

        # Set theme
        theme = self.config_data.get("theme", "dark")
        ctk.set_appearance_mode(theme)

        self.title("Pomodoro Timer")
        self.geometry("550x400")

        # Timer variables
        self.work_time = self.config_data["work_time"] * 60
        self.break_time = self.config_data["short_break"] * 60
        self.long_break_time = self.config_data["long_break"] * 60
        self.time_left = self.work_time
        self.sessions_completed = 0
        self.timer_running = False

        # UI Elements
        self.label = ctk.CTkLabel(self, text=self.format_time(), font=("Arial", 40))
        self.label.pack(pady=20)

        # Progress Tracker
        self.session_label = ctk.CTkLabel(self, text="Sessions Completed: 0", font=("Arial", 20))
        self.session_label.pack(pady=10)

        # Input fields for custom settings
        self.create_settings()

        # Control Buttons
        self.start_button = ctk.CTkButton(self, text="Start", command=self.start_timer)
        self.start_button.pack(side="left", padx=10, pady=10)

        self.pause_button = ctk.CTkButton(self, text="Pause", command=self.pause_timer)
        self.pause_button.pack(side="left", padx=10, pady=10)

        self.reset_button = ctk.CTkButton(self, text="Reset", command=self.reset_timer)
        self.reset_button.pack(side="left", padx=10, pady=10)

        # Theme Switcher
        self.theme_switch = ctk.CTkSwitch(self, text="Dark Mode", command=self.toggle_theme)
        if theme == "dark":
            self.theme_switch.select()
        self.theme_switch.place(x=10, y=10) 

    def create_settings(self):
        self.work_time_entry = ctk.CTkEntry(self, placeholder_text="Work Time (min)")
        self.work_time_entry.pack(pady=5)

        self.short_break_entry = ctk.CTkEntry(self, placeholder_text="Short Break (min)")
        self.short_break_entry.pack(pady=5)

        self.long_break_entry = ctk.CTkEntry(self, placeholder_text="Long Break (min)")
        self.long_break_entry.pack(pady=5)

        self.save_button = ctk.CTkButton(self, text="Save Settings", command=self.save_settings)
        self.save_button.pack(pady=10)

    def save_settings(self):
        work_time = self.work_time_entry.get()
        short_break = self.short_break_entry.get()
        long_break = self.long_break_entry.get()

        if work_time.isdigit():
            self.work_time = int(work_time) * 60
            self.config_data["work_time"] = int(work_time)
        if short_break.isdigit():
            self.break_time = int(short_break) * 60
            self.config_data["short_break"] = int(short_break)
        if long_break.isdigit():
            self.long_break_time = int(long_break) * 60
            self.config_data["long_break"] = int(long_break)

        save_config(self.config_data)

    def toggle_theme(self):
        if self.theme_switch.get():
            ctk.set_appearance_mode("dark")
            self.config_data["theme"] = "dark"
        else:
            ctk.set_appearance_mode("light")
            self.config_data["theme"] = "light"
        save_config(self.config_data)

    def format_time(self):
        mins, secs = divmod(self.time_left, 60)
        return f"{mins:02d}:{secs:02d}"

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.countdown()

    def pause_timer(self):
        self.timer_running = False

    def reset_timer(self):
        self.timer_running = False
        self.time_left = self.work_time
        self.label.configure(text=self.format_time())

    def countdown(self):
        if self.timer_running and self.time_left > 0:
            self.time_left -= 1
            self.label.configure(text=self.format_time())
            self.after(1000, self.countdown)
        elif self.time_left == 0:
            self.sessions_completed += 1
            self.session_label.configure(text=f"Sessions Completed: {self.sessions_completed}")
            self.timer_running = False
            self.send_notification("Pomodoro Completed!", "Take a break!")
            play_sound()  # Use pygame for sound alert

            # Handle long break
            if self.sessions_completed % 4 == 0:
                self.time_left = self.long_break_time
            else:
                self.time_left = self.break_time

            self.label.configure(text=self.format_time())
            self.start_timer()

    def send_notification(self, title, message):
        notification.notify(
            title=title,
            message=message,
            timeout=10
        )


# Run the app
if __name__ == "__main__":
    app = PomodoroTimer()
    app.mainloop()
