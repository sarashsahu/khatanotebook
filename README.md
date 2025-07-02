# 💰 Khata Notebook

A smart personal ledger web app to keep track of your debts and credits with individual people. Built with **Flask**, **SQLite**, and a modern responsive frontend with **dark mode**, full **CRUD operations**, and **Excel export** support.


## ✨ Features

- ✅ Email-based login and OTP verification
- ✅ Add entries per person (reason, amount, type)
- ✅ View current balance per person
- ✅ Edit or delete individual entries
- ✅ Delete all entries for a person
- ✅ Export data to Excel file
- ✅ Responsive UI with dark mode toggle
- ✅ Indian currency formatting
- ✅ Input sanitization and auto-uppercase

---

## 🚀 Live Demo

Coming soon...

---

## 🧱 Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **Database**: SQLite (via SQLAlchemy ORM)
- **OTP**: Email-based OTP authentication (SMTP)
- **Excel Export**: `openpyxl`

---


## 📁 Project Structure

```
khata-notebook/
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
├── static/
│   └── style.css (if separated)
├── app.py
├── requirements.txt
├── khata.db (generated after first run)
└── README.md
```

---

## ✅ To Do

* [ ] Add password-based login (optional)
* [ ] Host on Render/Vercel/Heroku
* [ ] Add charts for visualization
* [ ] Add user profile management

---

## 📝 License

MIT License

---

## 📧 Contact

Built by [Sarash Sahu](https://www.linkedin.com/in/sarashsahu)
📧 [sarashsahu2016@gmail.com](mailto:sarashsahu2016@gmail.com)

