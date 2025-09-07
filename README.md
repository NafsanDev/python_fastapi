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
1. Create a virtual environment <br>
    python -m venv venv <br>
    source venv/bin/activate   # Linux / macOS <br>
    venv\Scripts\activate      # Windows

2. Install dependencies <br>
    pip install -r requirements.txt

3. Run the app <br>
    uvicorn myapi:app --reload   # Secure version <br>
    or <br>
    uvicorn sqlapi:app --reload  # SQL version <br>
    or <br>
    uvicorn hardcodedapi:app --reload  # Hardcoded JSON version<br>

4. API TEST <br>
   Goto http://127.0.0.1:8000/docs

