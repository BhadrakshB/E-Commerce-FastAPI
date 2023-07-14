# E-Commerce Backend Project using FastAPI

This repository contains the backend code for an E-Commerce application built using FastAPI.

## Prerequisites

Before running the project, ensure that you have the following prerequisites installed:

- Python (3.8 or higher)
- pip package manager

## Installation

1. Clone the repository to your local machine using the following command:

   ```bash
   git clone https://github.com/BhadrakshB/E-Commerce-FastAPI
   ```

2. Create a virtual environment to isolate project dependencies:

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   - For Windows:
     ```bash
     venv\Scripts\activate
     ```
   
   - For Unix/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install the project dependencies from the requirements.txt file:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Create a file 'e_commerce_api/secret_key.py'
2. Generate a secret key by running the 'secret_key_generation.py'
3. Create a variable "SECRET_KEY" with the value from step 2 and store it in 'e_commerce_api/secret_key.py'

## Running the Server

To start the backend server, run the following command:

```bash
uvicorn main:app --reload
```

The server will be running at `http://localhost:8000`.

## API Documentation

Once the server is running, you can access the API documentation by visiting `http://localhost:8000/docs` in your web browser. The API documentation provides detailed information about the available endpoints, request/response schemas, and allows you to interact with the API.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://www.sqlalchemy.org/

---

By following these steps, you will be able to run the E-Commerce Backend project on your local system. If you encounter any difficulties or have questions, please don't hesitate to reach out. Enjoy building your E-Commerce application!
