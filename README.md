# Django Blog Project

A feature-rich blog application built with Django, providing users with the ability to create, edit, and manage blog posts with categories, tags, and user authentication.

## 🚀 Features
- 📝 **Post Management:** Create, update, delete, and view blog posts.
- 🔖 **Tag & Category Support:** Categorize posts and use tags for better filtering.
- 🔐 **User Authentication:** Secure login and registration for managing posts.
- ❤️ **Like & Bookmark System:** Users can like and bookmark their favorite posts.
- 📆 **Archives:** View posts by date.
- 🔎 **Search & Filtering:** Find posts easily by title, category, or tag.
- 🏷 **Slug-Based URLs:** SEO-friendly URLs for each post.

## 🛠 Technologies Used
- **Backend:** Django, Django ORM, Django Taggit
- **Frontend:** Bootstrap, HTML, CSS
- **Database:** SQLite (default) / PostgreSQL (optional)
- **Authentication:** Django Authentication System

## 📦 Installation
### 1. Clone the Repository
```bash
git clone https://github.com/sajjadkargar6131/blog
cd blog
```
### 2. Create a Virtual Environment & Activate It
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
### 4. Apply Migrations & Run Server
```bash
python manage.py migrate
python manage.py runserver
```
Now, open your browser and go to `http://127.0.0.1:8000/` 🎉

## 🔧 Configuration
- **Superuser Creation:**
```bash
python manage.py createsuperuser
```
- **Static Files (Production Use):**
```bash
python manage.py collectstatic
```

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing
Contributions are welcome! Feel free to fork the repo, open issues, or submit pull requests.

## 📩 Contact
For any inquiries or issues, reach out at: `sajjad71kargar@gmail.com`
