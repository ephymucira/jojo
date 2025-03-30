import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_URL = "http://127.0.0.1:5000"

# Main App Class
class CashlessFareApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cashless Fare Collection")
        self.geometry("400x500")
        self.configure(bg="#f0f0f0")

        # Title Label
        ttk.Label(self, text="Cashless Fare Collection", font=("Arial", 16, "bold")).pack(pady=10)

        # Tabs
        self.tab_control = ttk.Notebook(self)
        self.register_tab = ttk.Frame(self.tab_control)
        self.login_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.register_tab, text="Register")
        self.tab_control.add(self.login_tab, text="Login")
        self.tab_control.pack(expand=1, fill="both")

        self.create_register_tab()
        self.create_login_tab()

    # Register Tab UI
    def create_register_tab(self):
        frame = ttk.Frame(self.register_tab, padding=20)
        frame.pack(pady=20)

        ttk.Label(frame, text="Name").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_name = ttk.Entry(frame, width=30)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Email").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_email = ttk.Entry(frame, width=30)
        self.entry_email.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Password").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_password = ttk.Entry(frame, show="*", width=30)
        self.entry_password.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Role").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.role_var = tk.StringVar(value="passenger")
        self.role_menu = ttk.Combobox(frame, textvariable=self.role_var, values=["passenger", "tout", "admin"], width=28)
        self.role_menu.grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(frame, text="Register", command=self.register, style="TButton").grid(row=4, columnspan=2, pady=10)

    # Login Tab UI
    def create_login_tab(self):
        frame = ttk.Frame(self.login_tab, padding=20)
        frame.pack(pady=30)

        ttk.Label(frame, text="Email").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.login_email = ttk.Entry(frame, width=30)
        self.login_email.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Password").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.login_password = ttk.Entry(frame, show="*", width=30)
        self.login_password.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(frame, text="Login", command=self.login, style="TButton").grid(row=2, columnspan=2, pady=10)

    # Registration Logic
    def register(self):
        name, email, password, role = self.entry_name.get(), self.entry_email.get(), self.entry_password.get(), self.role_var.get()
        if not email or not password or not role:
            messagebox.showerror("Error", "All fields are required")
            return

        response = requests.post(f"{API_URL}/register", json={"name": name, "email": email, "password": password, "role": role})

        if response.status_code == 201:
            messagebox.showinfo("Success", "Registration successful!")
        else:
            messagebox.showerror("Error", response.json().get("error", "Registration failed"))

    # Login Logic
    def login(self):
        email, password = self.login_email.get(), self.login_password.get()
        if not email or not password:
            messagebox.showerror("Error", "Email and password are required")
            return

        response = requests.post(f"{API_URL}/login", json={"email": email, "password": password})
        if response.status_code == 200:
            role = response.json().get("role")
            if role == "admin":
                self.open_admin_dashboard()
            elif role == "tout":
                self.open_tout_dashboard()
            else:
                self.open_passenger_dashboard()
        else:
            messagebox.showerror("Error", response.json().get("error", "Login failed"))

    # Admin Dashboard
    def open_admin_dashboard(self):
        admin_window = tk.Toplevel(self)
        admin_window.title("Admin Dashboard")
        admin_window.geometry("400x300")

        ttk.Label(admin_window, text="Admin Panel", font=("Arial", 14, "bold")).pack(pady=10)
        ttk.Button(admin_window, text="View Total Fare Collection", command=self.view_fare_summary).pack(pady=5)
        ttk.Button(admin_window, text="Track Buses", command=self.track_buses).pack(pady=5)

    def view_fare_summary(self):
        response = requests.get(f"{API_URL}/get_fare_summary")
        fares = response.json()

        fare_window = tk.Toplevel(self)
        ttk.Label(fare_window, text="Total Fare Collection", font=("Arial", 12, "bold")).pack()
        for fare in fares:
            ttk.Label(fare_window, text=f"Bus {fare['bus_id']}: {fare['total_fare_collected']}").pack()

    def track_buses(self):
        response = requests.get(f"{API_URL}/get_bus_locations")
        buses = response.json()

        bus_window = tk.Toplevel(self)
        ttk.Label(bus_window, text="Bus Tracking", font=("Arial", 12, "bold")).pack()
        for bus in buses:
            ttk.Label(bus_window, text=f"Bus {bus['bus_id']}: {bus['latitude']}, {bus['longitude']}").pack()

    # Tout Dashboard
    def open_tout_dashboard(self):
        tout_window = tk.Toplevel(self)
        tout_window.title("Tout Dashboard")
        tout_window.geometry("400x200")

        ttk.Label(tout_window, text="Total Collection Today", font=("Arial", 12, "bold")).pack()
        ttk.Button(tout_window, text="View Total Fare Collected", command=self.view_tout_fare).pack(pady=5)

    def view_tout_fare(self):
        response = requests.get(f"{API_URL}/get_tout_fare")
        total_fare = response.json().get("total_fare_collected")
        messagebox.showinfo("Total Fare Collected", f"Total Fare Collected: {total_fare}")

    # Passenger Dashboard
    def open_passenger_dashboard(self):
        passenger_window = tk.Toplevel(self)
        passenger_window.title("Passenger Dashboard")
        passenger_window.geometry("400x250")

        ttk.Label(passenger_window, text="Select Pickup & Destination", font=("Arial", 12, "bold")).pack()

        ttk.Label(passenger_window, text="Pickup Point").pack()
        pickup_entry = ttk.Entry(passenger_window)
        pickup_entry.pack()

        ttk.Label(passenger_window, text="Destination").pack()
        destination_entry = ttk.Entry(passenger_window)
        destination_entry.pack()

        ttk.Button(passenger_window, text="Calculate Fare",
                   command=lambda: self.calculate_fare(pickup_entry.get(), destination_entry.get())).pack()

    def calculate_fare(self, pickup, destination):
        response = requests.get(f"{API_URL}/calculate_fare", params={"pickup": pickup, "destination": destination})
        fare = response.json().get("fare")
        messagebox.showinfo("Fare Calculation", f"Estimated Fare: {fare}")


# Run the App
if __name__ == "__main__":
    app = CashlessFareApp()
    app.mainloop()
