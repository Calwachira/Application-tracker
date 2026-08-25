"""
DATA ANALYST Job Application Tracker
A desktop app (CustomTkinter + SQLite) for tracking up to thousands of
job applications: add/edit/delete, search & filter, status pipeline,
and a live stats dashboard.

Run:
    pip install customtkinter
    python app.py
"""

import customtkinter as ctk
import sqlite3
import csv
import os
from datetime import datetime
from tkinter import ttk, messagebox, filedialog

# ----------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "applications.db")

STATUSES = ["Wishlist", "Applied", "Screening", "Interview", "Offer", "Rejected", "Withdrawn"]

STATUS_COLORS = {
    "Wishlist":  "#6b7280",
    "Applied":   "#3b82f6",
    "Screening": "#eab308",
    "Interview": "#f97316",
    "Offer":     "#22c55e",
    "Rejected":  "#ef4444",
    "Withdrawn": "#9333ea",
}

FIELDS = [
    ("company", "Company"),
    ("role", "Role / Title"),
    ("status", "Status"),
    ("date_applied", "Date Applied"),
    ("location", "Location"),
    ("salary", "Salary / Rate"),
    ("source", "Source"),
    ("url", "Job URL"),
    ("contact", "Contact"),
    ("notes", "Notes"),
]


# ----------------------------------------------------------------------
# Data layer
# ----------------------------------------------------------------------
class Database:
    def __init__(self, path=DB_FILE):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Applied',
                date_applied TEXT,
                location TEXT,
                salary TEXT,
                source TEXT,
                url TEXT,
                contact TEXT,
                notes TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        self.conn.commit()

    def add(self, data: dict):
        now = datetime.now().isoformat(timespec="seconds")
        cols = ["company", "role", "status", "date_applied", "location",
                "salary", "source", "url", "contact", "notes"]
        values = [data.get(c, "") for c in cols]
        self.conn.execute(
            f"INSERT INTO applications ({', '.join(cols)}, created_at, updated_at) "
            f"VALUES ({', '.join('?' for _ in cols)}, ?, ?)",
            values + [now, now],
        )
        self.conn.commit()

    def update(self, row_id: int, data: dict):
        now = datetime.now().isoformat(timespec="seconds")
        cols = ["company", "role", "status", "date_applied", "location",
                "salary", "source", "url", "contact", "notes"]
        set_clause = ", ".join(f"{c} = ?" for c in cols)
        values = [data.get(c, "") for c in cols]
        self.conn.execute(
            f"UPDATE applications SET {set_clause}, updated_at = ? WHERE id = ?",
            values + [now, row_id],
        )
        self.conn.commit()

    def delete(self, row_id: int):
        self.conn.execute("DELETE FROM applications WHERE id = ?", (row_id,))
        self.conn.commit()

    def all(self, search="", status_filter="All", sort_by="date_applied", descending=True):
        query = "SELECT * FROM applications WHERE 1=1"
        params = []
        if search:
            query += " AND (company LIKE ? OR role LIKE ? OR location LIKE ? OR notes LIKE ?)"
            like = f"%{search}%"
            params += [like, like, like, like]
        if status_filter != "All":
            query += " AND status = ?"
            params.append(status_filter)
        safe_sort = sort_by if sort_by in {
            "company", "role", "status", "date_applied", "location", "created_at"
        } else "date_applied"
        query += f" ORDER BY {safe_sort} {'DESC' if descending else 'ASC'}"
        return self.conn.execute(query, params).fetchall()

    def get(self, row_id: int):
        return self.conn.execute("SELECT * FROM applications WHERE id = ?", (row_id,)).fetchone()

    def stats(self):
        rows = self.conn.execute(
            "SELECT status, COUNT(*) as n FROM applications GROUP BY status"
        ).fetchall()
        counts = {s: 0 for s in STATUSES}
        for r in rows:
            counts[r["status"]] = r["n"]
        total = sum(counts.values())
        return counts, total


# ----------------------------------------------------------------------
# Edit / Add dialog
# ----------------------------------------------------------------------
class ApplicationDialog(ctk.CTkToplevel):
    def __init__(self, master, db: Database, on_saved, row=None):
        super().__init__(master)
        self.db = db
        self.on_saved = on_saved
        self.row = row
        self.title("Edit Application" if row else "Add Application")
        self.geometry("460x620")
        self.resizable(False, False)
        self.grab_set()

        self.entries = {}
        container = ctk.CTkScrollableFrame(self, width=420, height=560)
        container.pack(padx=12, pady=12, fill="both", expand=True)

        for key, label in FIELDS:
            ctk.CTkLabel(container, text=label, anchor="w",
                         font=ctk.CTkFont(size=13, weight="bold")).pack(fill="x", pady=(8, 2))
            if key == "status":
                widget = ctk.CTkOptionMenu(container, values=STATUSES)
                widget.set(row["status"] if row else "Applied")
            elif key == "notes":
                widget = ctk.CTkTextbox(container, height=90)
                if row and row["notes"]:
                    widget.insert("1.0", row["notes"])
            elif key == "date_applied":
                frame = ctk.CTkFrame(container, fg_color="transparent")
                frame.pack(fill="x")
                widget = ctk.CTkEntry(frame, placeholder_text="YYYY-MM-DD")
                widget.pack(side="left", fill="x", expand=True)
                today_btn = ctk.CTkButton(frame, text="Today", width=60,
                                           command=lambda w=widget: (w.delete(0, "end"),
                                                                      w.insert(0, datetime.now().strftime("%Y-%m-%d"))))
                today_btn.pack(side="left", padx=(6, 0))
                if row and row["date_applied"]:
                    widget.insert(0, row["date_applied"])
                self.entries[key] = widget
                continue
            else:
                widget = ctk.CTkEntry(container)
                if row and row[key]:
                    widget.insert(0, row[key])
            widget.pack(fill="x")
            self.entries[key] = widget

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=(0, 12))
        ctk.CTkButton(btn_row, text="Save", command=self.save).pack(side="right", padx=(6, 0))
        ctk.CTkButton(btn_row, text="Cancel", fg_color="gray40", hover_color="gray30",
                      command=self.destroy).pack(side="right")

    def save(self):
        data = {}
        for key, _ in FIELDS:
            widget = self.entries[key]
            if isinstance(widget, ctk.CTkTextbox):
                data[key] = widget.get("1.0", "end").strip()
            elif isinstance(widget, ctk.CTkOptionMenu):
                data[key] = widget.get()
            else:
                data[key] = widget.get().strip()

        if not data["company"] or not data["role"]:
            messagebox.showwarning("Missing info", "Company and Role are required.")
            return

        if self.row:
            self.db.update(self.row["id"], data)
        else:
            self.db.add(data)

        self.on_saved()
        self.destroy()


# ----------------------------------------------------------------------
# Main App
# ----------------------------------------------------------------------
class TrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = Database()

        self.title("Data Analyst Job Application Tracker")
        self.geometry("1180x700")
        self.minsize(980, 600)

        self.selected_id = None
        self._build_layout()
        self.refresh()

    # -------------------- layout --------------------
    def _build_layout(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main()

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="📊 Job Tracker",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 4), padx=20, anchor="w")
        ctk.CTkLabel(sidebar, text="Data Analyst applications",
                     font=ctk.CTkFont(size=12), text_color="gray60").pack(padx=20, anchor="w")

        ctk.CTkButton(sidebar, text="+ Add Application", height=38,
                      command=self.open_add_dialog).pack(padx=20, pady=(20, 10), fill="x")
        ctk.CTkButton(sidebar, text="⭳ Export CSV", height=32, fg_color="gray30",
                      hover_color="gray25", command=self.export_csv).pack(padx=20, pady=(0, 20), fill="x")

        ctk.CTkLabel(sidebar, text="OVERVIEW", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="gray50").pack(padx=20, pady=(10, 6), anchor="w")

        self.stats_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        self.stats_frame.pack(padx=14, fill="x")

        self.total_label = ctk.CTkLabel(sidebar, text="", font=ctk.CTkFont(size=13, weight="bold"))
        self.total_label.pack(padx=20, pady=(14, 4), anchor="w")

    def _build_main(self):
        main = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        main.grid_rowconfigure(2, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # --- toolbar ---
        toolbar = ctk.CTkFrame(main, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())
        search_entry = ctk.CTkEntry(toolbar, placeholder_text="🔍 Search company, role, location, notes...",
                                     width=340, textvariable=self.search_var)
        search_entry.pack(side="left")

        self.status_filter = ctk.CTkOptionMenu(toolbar, values=["All"] + STATUSES,
                                                command=lambda _: self.refresh())
        self.status_filter.set("All")
        self.status_filter.pack(side="left", padx=10)

        self.sort_var = ctk.CTkOptionMenu(
            toolbar,
            values=["date_applied", "company", "role", "status", "created_at"],
            command=lambda _: self.refresh(),
        )
        self.sort_var.set("date_applied")
        self.sort_var.pack(side="left", padx=(0, 10))

        ctk.CTkButton(toolbar, text="Edit", width=70, command=self.open_edit_dialog).pack(side="right", padx=(6, 0))
        ctk.CTkButton(toolbar, text="Delete", width=70, fg_color="#b91c1c", hover_color="#991b1b",
                      command=self.delete_selected).pack(side="right")

        # --- table ---
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", fieldbackground="#2b2b2b",
                         foreground="white", rowheight=28, borderwidth=0, font=("Helvetica", 11))
        style.configure("Treeview.Heading", background="#1f1f1f", foreground="gray80",
                         font=("Helvetica", 11, "bold"), borderwidth=0)
        style.map("Treeview", background=[("selected", "#3b82f6")])

        columns = ("company", "role", "status", "date_applied", "location", "salary")
        headers = {"company": "Company", "role": "Role", "status": "Status",
                   "date_applied": "Applied", "location": "Location", "salary": "Salary"}
        widths = {"company": 180, "role": 200, "status": 110, "date_applied": 100,
                  "location": 150, "salary": 110}

        table_frame = ctk.CTkFrame(main, fg_color="transparent")
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        for c in columns:
            self.tree.heading(c, text=headers[c])
            self.tree.column(c, width=widths[c], anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)

        for status, color in STATUS_COLORS.items():
            self.tree.tag_configure(status, foreground=color)

        self.tree.bind("<Double-1>", lambda e: self.open_edit_dialog())
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        self.row_count_label = ctk.CTkLabel(main, text="", font=ctk.CTkFont(size=11), text_color="gray50")
        self.row_count_label.grid(row=3, column=0, sticky="w", pady=(6, 0))

    # -------------------- behaviour --------------------
    def _on_select(self, _event=None):
        sel = self.tree.selection()
        self.selected_id = int(sel[0]) if sel else None

    def refresh(self):
        rows = self.db.all(
            search=self.search_var.get().strip(),
            status_filter=self.status_filter.get(),
            sort_by=self.sort_var.get(),
        )
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert(
                "", "end", iid=str(r["id"]),
                values=(r["company"], r["role"], r["status"],
                        r["date_applied"] or "", r["location"] or "", r["salary"] or ""),
                tags=(r["status"],),
            )
        self.row_count_label.configure(text=f"{len(rows)} application(s) shown")
        self._refresh_stats()

    def _refresh_stats(self):
        for w in self.stats_frame.winfo_children():
            w.destroy()
        counts, total = self.db.stats()
        for status in STATUSES:
            n = counts.get(status, 0)
            row = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            dot = ctk.CTkLabel(row, text="●", text_color=STATUS_COLORS[status], width=14)
            dot.pack(side="left")
            ctk.CTkLabel(row, text=status, anchor="w").pack(side="left", padx=(2, 0))
            ctk.CTkLabel(row, text=str(n), text_color="gray60").pack(side="right")
        self.total_label.configure(text=f"Total: {total}")

    def open_add_dialog(self):
        ApplicationDialog(self, self.db, self.refresh)

    def open_edit_dialog(self):
        if self.selected_id is None:
            messagebox.showinfo("No selection", "Select an application first.")
            return
        row = self.db.get(self.selected_id)
        ApplicationDialog(self, self.db, self.refresh, row=row)

    def delete_selected(self):
        if self.selected_id is None:
            messagebox.showinfo("No selection", "Select an application first.")
            return
        if messagebox.askyesno("Delete", "Delete this application? This can't be undone."):
            self.db.delete(self.selected_id)
            self.selected_id = None
            self.refresh()

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv")],
                                             initialfile="job_applications.csv")
        if not path:
            return
        rows = self.db.all(sort_by="date_applied")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([label for _, label in FIELDS])
            for r in rows:
                writer.writerow([r[key] or "" for key, _ in FIELDS])
        messagebox.showinfo("Exported", f"Saved to {path}")


if __name__ == "__main__":
    app = TrackerApp()
    app.mainloop()
