import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB_NAME = "mini_jira.db"

# -------------------------------------------------------
# Initialization of  Database
# -------------------------------------------------------
def initialize_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        title TEXT NOT NULL,
        status TEXT CHECK(status IN ('To Do', 'In Progress', 'Done')) NOT NULL,
        severity TEXT CHECK(severity IN ('Low', 'Medium', 'High')) NOT NULL,
        assignee TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

# -------------------------------------------------------
# Database Logic Functions
# -------------------------------------------------------
def create_project(name, description):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO projects (name, description) VALUES (?, ?)", (name, description))
    conn.commit()
    conn.close()

def get_all_projects():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects")
    projects = cursor.fetchall()
    conn.close()
    return projects

def create_ticket(project_id, title, status, severity, assignee):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tickets (project_id, title, status, severity, assignee)
        VALUES (?, ?, ?, ?, ?)
    """, (project_id, title, status, severity, assignee))
    conn.commit()
    conn.close()

def get_tickets_by_project(project_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE project_id = ?", (project_id,))
    tickets = cursor.fetchall()
    conn.close()
    return tickets

# -------------------------------------------------------
# GUI Interface
# -------------------------------------------------------
class WelcomePage:
    def __init__(self, root):
        self.root = root
        self.root.title("Welcome to Mini JIRA")
        self.root.geometry("500x400")
        self.root.configure(bg="#F0F2FF")
        self.root.resizable(False, False)
        self.root.attributes("-alpha", 0.0)  

    
        self.fade_in()

        
        tk.Label(root, text="🐞 Mini JIRA Clone", font=("Segoe UI", 20, "bold"),
                 fg="#211C84", bg="#F0F2FF").pack(pady=20)

        
        tk.Label(root, text="Bug tracking made easy ",
                 font=("Segoe UI", 13, "bold"), bg="#F0F2FF").pack(pady=5)

        
        tk.Label(root, text="Group Members:", font=("Segoe UI", 10, "bold"),
                 fg="#211C84", bg="#F0F2FF").pack(pady=(15, 2))

        members = ["• Ameerah Adisa", "• Ezenwa Obasi", "• Miracle Nwachukwu", "• David Akindipe", "• Akinlaja Akintude", "• Sharon Nelson"]  
        for member in members:
            tk.Label(root, text=member, font=("Segoe UI", 10),
                     bg="#F0F2FF").pack()

    
        tk.Label(root, text="", bg="#F0F2FF").pack(pady=10)

        
        self.start_btn = tk.Button(root, text="Enter App", font=("Segoe UI", 11, "bold"),
                                   bg="#211C84", fg="white", activebackground="#3A36B1",
                                   width=15, command=self.start_main_app)
        self.start_btn.pack(pady=1)

        
        self.start_btn.bind("<Enter>", self.on_hover)
        self.start_btn.bind("<Leave>", self.on_leave)

    def fade_in(self):
        alpha = self.root.attributes("-alpha")
        if alpha < 1.0:
            alpha += 0.05
            self.root.attributes("-alpha", alpha)
            self.root.after(50, self.fade_in)  

    def on_hover(self, event):
        self.start_btn.config(bg="#3A36B1")

    def on_leave(self, event):
        self.start_btn.config(bg="#211C84")

    def start_main_app(self):
        self.root.destroy()
        main_root = tk.Tk()
        app = MiniJiraApp(main_root)
        main_root.mainloop()


class MiniJiraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini JIRA Clone")
        self.root.geometry("650x550")
        self.root.resizable(False, False)

        

        self.selected_project_id = None

        tk.Label(root, text="🐞 Mini JIRA Clone", font=("Segoe UI", 16, "bold"), fg="white",
        bg="#211C84").pack(pady=10)

        # ---------------- Project Creation ----------------
        self.project_frame = tk.LabelFrame(root, text="Create New Project", fg="#211C84",font=("Segoe UI", 10, "bold"))
        self.project_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(self.project_frame, text="Name:").grid(row=0, column=0, sticky="e")
        self.project_name = tk.Entry(self.project_frame, width=40)
        self.project_name.grid(row=0, column=1, padx=5)

        tk.Label(self.project_frame, text="Description:").grid(row=1, column=0, sticky="e")
        self.project_desc = tk.Entry(self.project_frame, width=40)
        self.project_desc.grid(row=1, column=1, padx=5)

        tk.Button(self.project_frame, text="➕ Add Project",fg = "white" , bg ="#211C84",font=("Segoe UI", 9, "bold"), command=self.add_project).grid(row=2, column=1, pady=5)

        # ---------------- Project Selector ----------------
        tk.Label(root, text="Select Project:",fg="#211C84",font=("Segoe UI", 10, "bold")).pack()
        self.project_selector = ttk.Combobox(root, state="readonly")
        self.project_selector.pack()
        self.project_selector.bind("<<ComboboxSelected>>", self.load_tickets)

        # ---------------- Ticket Creation ----------------
        self.ticket_frame = tk.LabelFrame(root, text="Add Ticket to Project",fg="#211C84",font=("Segoe UI", 10, "bold"))
        self.ticket_frame.pack(padx=10, pady=10, fill="x")

        self.ticket_title = tk.Entry(self.ticket_frame, width=40)
        self.ticket_title.grid(row=0, column=1)
        tk.Label(self.ticket_frame, text="Title:").grid(row=0, column=0)

        self.ticket_status = ttk.Combobox(self.ticket_frame, values=["To Do", "In Progress", "Done"])
        self.ticket_status.set("To Do")
        self.ticket_status.grid(row=1, column=1)
        tk.Label(self.ticket_frame, text="Status:").grid(row=1, column=0)

        self.ticket_severity = ttk.Combobox(self.ticket_frame, values=["Low", "Medium", "High"])
        self.ticket_severity.set("Low")
        self.ticket_severity.grid(row=2, column=1)
        tk.Label(self.ticket_frame, text="Severity:").grid(row=2, column=0)

        

        self.ticket_assignee = tk.Entry(self.ticket_frame, width=40)
        self.ticket_assignee.grid(row=3, column=1)
        tk.Label(self.ticket_frame, text="Assignee:").grid(row=3, column=0)

        tk.Button(self.ticket_frame, text="🐛 Add Ticket", fg = "white" , bg ="#211C84",font=("Segoe UI", 9, "bold"), command=self.add_ticket).grid(row=4, column=1, pady=5)

        # ---------------- Ticket List ----------------
        tk.Label(root, text="Tickets:",fg="#211C84",font=("Segoe UI", 10, "bold")).pack()
        self.ticket_listbox = tk.Listbox(root, width=85, height=10)
        self.ticket_listbox.pack(padx=10, pady=10)

        self.load_projects()

    def add_project(self):
        name = self.project_name.get().strip()
        desc = self.project_desc.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Project name is required.")
            return
        create_project(name, desc)
        self.project_name.delete(0, tk.END)
        self.project_desc.delete(0, tk.END)
        self.load_projects()
        messagebox.showinfo("Success", "Project created successfully.")

    def load_projects(self):
        projects = get_all_projects()
        self.project_map = {}
        values = []

        for p in projects:
            label = f"{p[1]} (ID {p[0]})"
            self.project_map[label] = p[0]
            values.append(label)

        self.project_selector["values"] = values
        if values:
            self.project_selector.current(0)
            self.load_tickets()

    def add_ticket(self):
        selected = self.project_selector.get()
        if not selected:
            messagebox.showwarning("No Project", "Please select a project first.")
            return

        project_id = self.project_map[selected]
        title = self.ticket_title.get().strip()
        status = self.ticket_status.get()
        severity = self.ticket_severity.get()
        assignee = self.ticket_assignee.get().strip()

        if not title:
            messagebox.showwarning("Input Error", "Ticket title is required.")
            return

        create_ticket(project_id, title, status, severity, assignee)
        self.ticket_title.delete(0, tk.END)
        self.ticket_assignee.delete(0, tk.END)
        self.load_tickets()
        messagebox.showinfo("Success", "Ticket added successfully.")

    def load_tickets(self, event=None):
        selected = self.project_selector.get()
        if not selected:
            return
        project_id = self.project_map[selected]
        tickets = get_tickets_by_project(project_id)

        self.ticket_listbox.delete(0, tk.END)
        if tickets:
            for t in tickets:
                summary = f"[{t[3]}][{t[4]}] {t[2]} → {t[5]}"
                self.ticket_listbox.insert(tk.END, summary)
        else:
            self.ticket_listbox.insert(tk.END, "No tickets for this project.")

# -------------------------------------------------------
# APP STARTUP
# -------------------------------------------------------
if __name__ == "__main__":
    initialize_database()
    welcome_root = tk.Tk()
    WelcomePage(welcome_root)
    welcome_root.mainloop()

