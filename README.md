# Tupie Platform

Tupie is a community-sharing platform designed to **reduce waste and help those in need**.  
The name **Tupie** comes from the Swahili words **"Tupa" (throw away)** and **"Mie" (me)** – meaning *"If you want to throw away something I might use, give it to me instead."*

## 🌍 Project Goal
- Reduce unnecessary waste in communities
- Help people access free items they might need
- Create a sustainable and caring community

## 🚀 Features (Planned)
- Users can list unwanted items for free
- Others can browse and request items
- Search & category filters for easy discovery
- Location-based listing for nearby items

## 🛠️ Tech Stack
- Python (Django/Flask)
- HTML, CSS, JavaScript
- SQLite/PostgreSQL for database

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/msomea/tupie.git
   cd tupie
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install locations table into your default database,
   database dump is included in dtbase directory (postgres):
   ```bash
   psql -U your_user -d your_dat_base -f location_tables.sql
   ```
5. Run the development server (Django example):
   ```bash
   python manage.py runserver
   ```

## 🤝 Contributing
Feel free to contribute by suggesting new features or improving the codebase.

## 📜 License
MIT License
