🔐 Secure FastAPI Project - Python

A secure, production-ready **FastAPI** backend built with:

- **FastAPI** – high-performance Python web framework
- **OAuth2 + JWT** – authentication and authorization
- **Passlib** – password hashing
- **SQLAlchemy** – ORM for database interactions
- **Pydantic** – request/response validation

This project is designed as a starting point for building APIs with **secure user authentication**, database models, and role-based access.

---

To run the project:
1. Create a virtual environment
    python -m venv venv
    source venv/bin/activate   # Linux / macOS
    venv\Scripts\activate      # Windows

2. Install dependencies
    pip install -r requirements.txt

3. Run the app
    uvicorn myapi:app --reload

4. API TEST <br>
   Goto http://127.0.0.1:8000/docs

