# Data Analyst Job Application Tracker

A desktop app for tracking your job applications — built with **Python**,
**CustomTkinter** (modern dark-themed UI), and **SQLite** (local storage,
no server needed, scales fine to thousands of rows).

## Features

- **Add / Edit / Delete** applications with company, role, status, date
  applied, location, salary, source, job URL, contact, and notes.
- **Status pipeline**: Wishlist → Applied → Screening → Interview → Offer,
  plus Rejected / Withdrawn — each with its own color in the table.
- **Live sidebar dashboard**: count of applications per status + total.
- **Search** across company, role, location, and notes as you type.
- **Filter** by status and **sort** by any column.
- **Export to CSV** for backup or further analysis (e.g. in Excel/Power BI).
- Local SQLite database (`applications.db`) — your data stays on your machine.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Requires Python 3.9+. Tkinter ships with most Python installs (on Linux you
may need `sudo apt install python3-tk` if it's missing).

## Usage

1. Click **+ Add Application** to log a new application.
2. Double-click any row (or select it and click **Edit**) to update it —
   e.g. moving it from "Applied" to "Interview" as you hear back.
3. Use the search box and status dropdown to filter your list.
4. Click **⭳ Export CSV** any time to save a snapshot you can open in Excel
   or import into Power BI.

## File structure

```
job_tracker/
├── app.py              # main application
├── requirements.txt
├── applications.db      # created automatically on first run
└── README.md
```

## Notes on scaling to ~1,000+ entries

- SQLite comfortably handles tens of thousands of rows; the table view
  only renders what's currently filtered/sorted, so performance stays
  smooth well past 1,000 applications.
- All searching/filtering/sorting happens in SQL, not in Python loops,
  so it stays fast as your tracker grows.
