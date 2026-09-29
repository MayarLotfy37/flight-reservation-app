import tkinter as tk
from tkinter import ttk, messagebox
import database

class FlightApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Flight Reservation System")
        self.geometry("750x500")
        
        # Container to hold all views/pages
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for PageClass in (HomePage, BookingPage, ReservationsPage, EditPage):
            page_name = PageClass.__name__
            frame = PageClass(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomePage")

    def show_frame(self, page_name, record_id=None):
        """Raises the selected view to the top."""
        frame = self.frames[page_name]
        if hasattr(frame, 'on_show'):
            frame.on_show(record_id)
        frame.tkraise()

# --- 1. HOME PAGE ---
class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Flight Reservation System", font=("Helvetica", 18, "bold")).pack(pady=40)
        
        tk.Button(self, text="Book Flight", font=("Helvetica", 12), width=20, height=2,
                  command=lambda: controller.show_frame("BookingPage")).pack(pady=10)
        
        tk.Button(self, text="View Reservations", font=("Helvetica", 12), width=20, height=2,
                  command=lambda: controller.show_frame("ReservationsPage")).pack(pady=10)

# --- 2. BOOKING PAGE ---
class BookingPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Book a Flight", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=15)

        labels = ["Passenger Name", "Flight Number", "Departure", "Destination", "Date (YYYY-MM-DD)", "Seat Number"]
        self.entries = {}

        for i, text in enumerate(labels):
            tk.Label(self, text=text, font=("Helvetica", 10)).grid(row=i+1, column=0, sticky="e", padx=10, pady=5)
            entry = tk.Entry(self, width=30)
            entry.grid(row=i+1, column=1, padx=10, pady=5)
            self.entries[text] = entry

        tk.Button(self, text="Submit Reservation", bg="green", fg="white", command=self.save_booking).grid(row=7, column=1, pady=15, sticky="w")
        tk.Button(self, text="Back to Home", command=lambda: controller.show_frame("HomePage")).grid(row=7, column=0, pady=15)

    def save_booking(self):
        values = [self.entries[key].get().strip() for key in self.entries]
        if any(v == "" for v in values):
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        database.add_reservation(*values)
        messagebox.showinfo("Success", "Reservation created successfully!")
        
        for entry in self.entries.values():
            entry.delete(0, tk.END)
            
        self.controller.show_frame("ReservationsPage")

# --- 3. RESERVATIONS LIST PAGE ---
class ReservationsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="All Reservations", font=("Helvetica", 16, "bold")).pack(pady=10)

        columns = ("ID", "Name", "Flight", "From", "To", "Date", "Seat")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", pady=10)

        tk.Button(btn_frame, text="Back to Home", command=lambda: controller.show_frame("HomePage")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Edit Selected", command=self.edit_selected).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Delete Selected", bg="red", fg="white", command=self.delete_selected).pack(side="right", padx=10)

    def on_show(self, record_id=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in database.fetch_reservations():
            self.tree.insert("", tk.END, values=row)

    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a record to edit.")
            return
        rec_id = self.tree.item(selected[0])['values'][0]
        self.controller.show_frame("EditPage", rec_id)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a record to delete.")
            return
        
        rec_id = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this reservation?"):
            database.delete_reservation(rec_id)
            self.on_show()

# --- 4. EDIT RESERVATION PAGE ---
class EditPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_id = None

        tk.Label(self, text="Edit Reservation", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=15)

        self.labels = ["Passenger Name", "Flight Number", "Departure", "Destination", "Date (YYYY-MM-DD)", "Seat Number"]
        self.entries = {}

        for i, text in enumerate(self.labels):
            tk.Label(self, text=text, font=("Helvetica", 10)).grid(row=i+1, column=0, sticky="e", padx=10, pady=5)
            entry = tk.Entry(self, width=30)
            entry.grid(row=i+1, column=1, padx=10, pady=5)
            self.entries[text] = entry

        tk.Button(self, text="Update Record", bg="blue", fg="white", command=self.update_booking).grid(row=7, column=1, pady=15, sticky="w")
        tk.Button(self, text="Cancel", command=lambda: controller.show_frame("ReservationsPage")).grid(row=7, column=0, pady=15)

    def on_show(self, record_id=None):
        if record_id is None:
            return
        self.current_id = record_id
        record = database.fetch_reservation_by_id(record_id)
        if record:
            for entry in self.entries.values():
                entry.delete(0, tk.END)
            for i, key in enumerate(self.labels):
                self.entries[key].insert(0, record[i+1])

    def update_booking(self):
        values = [self.entries[key].get().strip() for key in self.labels]
        if any(v == "" for v in values):
            messagebox.showwarning("Input Error", "All fields are required.")
            return
        
        database.update_reservation(self.current_id, *values)
        messagebox.showinfo("Success", "Reservation updated successfully!")
        self.controller.show_frame("ReservationsPage")

if __name__ == "__main__":
    app = FlightApp()
    app.mainloop()