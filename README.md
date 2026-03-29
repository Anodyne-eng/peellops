# 🍍 PeellOps

> Resource & Inventory Management System for **Peellnova Limited**

Peellnova Limited is a Ghanaian social enterprise that transforms fruit peel waste (pineapple, orange) and other natural ingredients into eco-friendly mosquito-repelling products — coils, aerosols, creams, and essences.

**PeellOps** is the internal operations platform used to track raw materials, manage production batches, monitor staff, and measure sustainability impact.

🔗 **Live Demo**: https://peellops.onrender.com

---

## Features

- **Dashboard** — Live stats, production analytics chart, recent batches, low stock alerts
- **Raw Materials** — Add, edit, delete, search and filter inventory with automatic status tracking
- **Production Batches** — Create and manage batches with progress tracking and automatic stock deduction
- **Staff Management** — Add staff with profile pictures, assign roles, manage team
- **Reports** — Operations summary and CSV export for raw materials and batches
- **Low Stock Alerts** — Visual warnings when materials drop below minimum stock level

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, Bootstrap 5, Chart.js |
| Backend | Python, Flask |
| Database | SQLite |
| Hosting | Render |

---

## How to Run Locally

**1. Clone the repository**
```bash
git clone https://github.com/Anodyne-eng/peellops.git
cd peellops
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the app**
```bash
python app.py
```

**5. Open in browser**
```
http://127.0.0.1:5000
```

---

## Project Structure
```
peellops/
├── app.py           → Flask app setup and configuration
├── models.py        → Database models (RawMaterial, Production, Staff)
├── routes.py        → All application routes and logic
├── requirements.txt → Python dependencies
├── Procfile         → Render deployment configuration
├── static/
│   └── uploads/     → Staff profile pictures
└── templates/
    ├── base.html        → Base layout with sidebar
    ├── dashboard.html   → Main dashboard
    ├── materials.html   → Raw materials inventory
    ├── batches.html     → Production batches
    ├── staff.html       → Staff management
    └── reports.html     → Reports and CSV export
```

---

## Developed By
** Michael Ampofo **

Built for Peellnnova Limited, Kumasi, Ghana.