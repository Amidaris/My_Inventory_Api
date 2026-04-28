# Invoice API

## Running Locally
1.  **Clone the repository:**

    ```bash
    git clone git@github.com:Amidaris/My_Invoice_Api.git
    ```

2.  **Create a virtual environment:**

    ```bash
    # On Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Run PostgreSQL with Docker:**

    ```bash
    docker compose up -d
    ```

5.  **Verify the database is running:**

    ```bash
    docker exec -it my_invoice_postgres psql -U postgres -d invoice_database
    ```

     Expected response:
    invoice_database =#

6.  **Run the application:**

    ```bash
    uvicorn api.app.main:app --reload
    ```

7. **Swagger Documentation**

    ```bash
    http://127.0.0.1:8000/docs
    ```
    
    
