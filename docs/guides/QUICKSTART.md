# Quickstart

1. Create and activate a virtual environment.
2. Install runtime dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and configure an LLM provider and `SECRET_KEY`.
4. Initialize the database:

   ```powershell
   python -m database.init_db
   ```

5. Start the API:

   ```powershell
   python -m uvicorn backend.main:app --reload --port 8000
   ```

6. In a second terminal, start the React UI:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

Open `http://localhost:5173`. The API documentation is available at `http://localhost:8000/docs`.
