# Primecolada Backend

> [!WARNING]
> ##  Network Configuration & Access
>
> When accessing this application from a device other than the host machine (e.g., a mobile phone or another computer on the same network), the default `localhost` configuration will not work.
>
> ### What you need to do:
>
> 1.  **Use Host's IP Address**: Replace `localhost` with the local IP address of the machine running the Docker containers.
>     -   **Windows**: Open Command Prompt and run `ipconfig`. Look for the "IPv4 Address".
>     -   **macOS/Linux**: Open a terminal and run `ifconfig` or `ip addr`.
>
> 2.  **Configure Environment Variables**: In the `.env.production` file in `primecolada-frontend`, ensure `VITE_API_BASE_URL` points to your host's IP address and the backend port (e.g., `http://192.168.1.100:5000`).
>
> 3.  **Check Firewall Settings**: Ensure your operating system's firewall (e.g., Windows Firewall) allows incoming connections on the ports used by this application (default is `8080` for the frontend and `5000` for the backend). You may need to create a new rule to allow traffic on these ports.

This is the backend for the TPV Primecolada application, built with Flask.

## Getting Started

### Prerequisites

-   Python 3
-   pip

### Installation

1.  Navigate to the `primecolada-backend` directory.
2.  Create a virtual environment:

    ```bash
    python -m venv venv
    ```

3.  Activate the virtual environment:

    -   **Windows**: `venv\Scripts\activate`
    -   **macOS/Linux**: `source venv/bin/activate`

4.  Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

### Development

To run the development server:

```bash
flask run
```

The application will be available at `http://localhost:5000`.

## Dependencies

-   `Flask`: The core web framework.
-   `google-cloud-firestore`: To interact with Google Cloud Firestore.
-   `python-dotenv`: To manage environment variables.
-   `Flask-Swagger-UI`: To serve Swagger UI for API documentation.
-   `Flask-SocketIO`: For real-time communication with the frontend.
-   `Flask-Cors`: To handle Cross-Origin Resource Sharing (CORS).

## Docker

The backend can also be run in a Docker container. The `Dockerfile` is provided for this purpose. When using `docker-compose` from the root directory, the backend will be available at `http://localhost:5000`.

# Cambios recientes

- El backend ahora puede ser desplegado como parte de un servicio multi-contenedor en Cloud Run.
- Variables de entorno para comunicación interna entre contenedores (ejemplo: `BACKEND_HOST=localhost`).
- Se añadió el manifiesto `cloudrun-service.yaml` y se actualizó el proceso de Cloud Build.
- Es necesario asignar el rol "Cloud Datastore User" a la cuenta de servicio para acceso a Firestore.
