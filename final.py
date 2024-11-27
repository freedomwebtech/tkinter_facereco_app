import win32event
import win32api
import sys
from winerror import ERROR_ALREADY_EXISTS
mutex = win32event.CreateMutex(None, False, 'name')
last_error = win32api.GetLastError()
if last_error == ERROR_ALREADY_EXISTS:
   sys.exit(0)

import os
import cv2
import face_recognition
import pandas as pd
from tkinter import *
from tkinter import messagebox
from datetime import datetime
import hashlib

# Directories and Files
KNOWN_FACES_DIR = './pictures_of_people_i_know/'
REGISTER_CSV_FILE = "register_users.csv"
LOG_CSV_FILE = "login_logout_logs.csv"

# Create directories if they don't exist
if not os.path.exists(KNOWN_FACES_DIR):
    os.makedirs(KNOWN_FACES_DIR)

# Function to hash the password securely
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to register user
def register_user():
    def capture_face():
        name = name_entry.get()
        password = password_entry.get()

        if not name or not password:
            messagebox.showerror("Error", "Name and Password are required!")
            return

        # Hash the password before saving
        hashed_password = hash_password(password)

        # Get current date and time
        now = datetime.now()
        register_date = now.strftime("%Y-%m-%d")
        register_time = now.strftime("%H:%M:%S")

        # Save to register_users.csv
        user_data = pd.DataFrame([[name, hashed_password, register_date, register_time]], 
                                 columns=["Name", "Hashed_Password", "Register_Date", "Register_Time"])
        if os.path.exists(REGISTER_CSV_FILE):
            existing_data = pd.read_csv(REGISTER_CSV_FILE)
            if name in existing_data["Name"].values:
                messagebox.showerror("Error", "User already exists!")
                return
            user_data = pd.concat([existing_data, user_data], ignore_index=True)
        user_data.to_csv(REGISTER_CSV_FILE, index=False)

        # Capture face image
        cap = cv2.VideoCapture(0)
        messagebox.showinfo("Info", "Press 'S' to save your face image or 'Q' to quit.")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("Register Face", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('s'):
                # Save the captured face image
                face_image_path = os.path.join(KNOWN_FACES_DIR, f"{name}.jpg")
                cv2.imwrite(face_image_path, frame)
                messagebox.showinfo("Success", f"Face image saved for {name}! Registration completed.")
                break
            elif key == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    # Registration UI
    reg_window = Toplevel(app)
    reg_window.title("Register User")
    reg_window.geometry("400x300")
    Label(reg_window, text="Enter Name:").pack(pady=10)
    name_entry = Entry(reg_window)
    name_entry.pack(pady=5)
    Label(reg_window, text="Enter Password:").pack(pady=10)
    password_entry = Entry(reg_window, show="*")
    password_entry.pack(pady=5)
    Button(reg_window, text="Capture Face", command=capture_face).pack(pady=20)

# Function to log user actions
def log_event(name, action):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    log_data = pd.DataFrame([[name, date, time, action]], columns=["Name", "Date", "Time", "Action"])

    if os.path.exists(LOG_CSV_FILE):
        existing_logs = pd.read_csv(LOG_CSV_FILE)
        log_data = pd.concat([existing_logs, log_data], ignore_index=True)
    log_data.to_csv(LOG_CSV_FILE, index=False)

# Function to login user
def login_user():
    name = name_entry_login.get()
    password = password_entry_login.get()

    if not name or not password:
        messagebox.showerror("Error", "Name and Password are required!")
        return

    hashed_password = hash_password(password)

    # Validate name and hashed password
    if os.path.exists(REGISTER_CSV_FILE):
        users_df = pd.read_csv(REGISTER_CSV_FILE)
        user_row = users_df[(users_df["Name"] == name) & (users_df["Hashed_Password"] == hashed_password)]
        if not user_row.empty:
            known_faces = []
            known_names = []
            for filename in os.listdir(KNOWN_FACES_DIR):
                if filename.endswith(".jpg"):
                    image = face_recognition.load_image_file(os.path.join(KNOWN_FACES_DIR, filename))
                    encoding = face_recognition.face_encodings(image)[0]
                    known_faces.append(encoding)
                    known_names.append(filename.split(".")[0])

            cap = cv2.VideoCapture(0)
            messagebox.showinfo("Info", "Looking for your face to login...")
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                rgb_frame = frame[:, :, ::-1]
                face_locations = face_recognition.face_locations(rgb_frame)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    matches = face_recognition.compare_faces(known_faces, face_encoding)
                    if True in matches:
                        match_index = matches.index(True)
                        matched_name = known_names[match_index]
                        if matched_name == name:
                            log_event(matched_name, "Login")
                            messagebox.showinfo("Success", f"Welcome {matched_name}!")
                            cap.release()
                            cv2.destroyAllWindows()
                            return
            cap.release()
            cv2.destroyAllWindows()
            messagebox.showerror("Error", "Face not recognized!")
        else:
            messagebox.showerror("Error", "Invalid name or password!")
    else:
        messagebox.showerror("Error", "No registered users found!")

# Function to logout user
def logout_user():
    name = name_entry_logout.get()
    password = password_entry_logout.get()

    if not name or not password:
        messagebox.showerror("Error", "Name and Password are required!")
        return

    hashed_password = hash_password(password)

    # Validate name and hashed password
    if os.path.exists(REGISTER_CSV_FILE):
        users_df = pd.read_csv(REGISTER_CSV_FILE)
        user_row = users_df[(users_df["Name"] == name) & (users_df["Hashed_Password"] == hashed_password)]
        if not user_row.empty:
            log_event(name, "Logout")
            messagebox.showinfo("Success", f"{name} has logged out.")
        else:
            messagebox.showerror("Error", "Invalid name or password!")
    else:
        messagebox.showerror("Error", "No registered users found!")

# Main Tkinter application
app = Tk()
app.title("Face Recognition Attendance System")
app.geometry("600x500")

# Register button
Button(app, text="Register", command=register_user, width=20).pack(pady=10)

# Login section
Label(app, text="Enter Name to Login:").pack(pady=10)
name_entry_login = Entry(app)
name_entry_login.pack(pady=5)
Label(app, text="Enter Password:").pack(pady=10)
password_entry_login = Entry(app, show="*")
password_entry_login.pack(pady=5)
Button(app, text="Login", command=login_user, width=20).pack(pady=10)

# Logout section
Label(app, text="Enter Name to Logout:").pack(pady=10)
name_entry_logout = Entry(app)
name_entry_logout.pack(pady=5)
Label(app, text="Enter Password:").pack(pady=10)
password_entry_logout = Entry(app, show="*")
password_entry_logout.pack(pady=5)
Button(app, text="Logout", command=logout_user, width=20).pack(pady=10)

app.mainloop()
