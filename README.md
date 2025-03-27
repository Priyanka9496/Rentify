# Rentify Property Listings Application

This is a Django-based web application for listing, viewing, and booking properties.

## Features
- **User Authentication:** Users can sign up, log in, and log out.
- **Property Listings:** Users can view available properties.
- **Add Property:** Authenticated users can list new properties.
- **Bookings:** Users can view and manage their bookings.
- **Profile Management:** Users can view and update their profile information.
- **Chatbot Integration:** Engage with a chatbot for queries.

## 🛠 Technologies Used
- **Backend:** Django (Python)
- **Frontend:** HTML, CSS (Tailwind CSS), JavaScript
- **Database:** SQLite (for development)
- **Authentication:** Django's built-in authentication system

## Setup Instructions

1. **Clone the Repository**
```bash
git@github.com:Priyanka9496/Rentify.git
cd repository-name
```

2. **Create a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate   # For Linux/Mac
venv\Scripts\activate      # For Windows
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Apply Migrations**
```bash
python manage.py migrate
```

5. **Run the Development Server**
```bash
python manage.py runserver
```

6. **Access the Application**
- Navigate to `http://127.0.0.1:8000/` in your browser.

## 🔐 Environment Variables
Create a `.env` file and add:
```
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

## 📝 Folder Structure
```
project/
├── accounts/          # User authentication & profiles
├── listings/          # Property listings and bookings
├── templates/         # HTML templates
├── static/            # Static files (CSS, JS, Images)
├── manage.py
├── requirements.txt   # Project dependencies
└── README.md          # Project information
```

##  API Endpoints
- `/` - Home page
- `/listings/` - Property listings
- `/accounts/profile/` - User profile page
- `/chatbot/api/` - Chatbot interaction API

##  Future Enhancements
- Add image uploads for property listings.
- Integrate payment gateway for bookings.
- Improve chatbot functionality with AI integration.

##  Contribution Guidelines
1. Fork the repo.
2. Create a new branch.
3. Commit your changes.
4. Push the branch.
5. Create a Pull Request.

## 📄 License
This project is licensed under the [MIT License](LICENSE).

---

> Made with ❤️ by Priyanka.
