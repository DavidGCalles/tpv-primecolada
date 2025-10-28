# TPV Primecolada

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

This is the root directory for the TPV Primecolada project.

## Project Structure

The project is divided into two main components:

-   `primecolada-backend`: A Flask-based backend application.
-   `primecolada-frontend`: A Vue.js-based frontend application.

## Getting Started

To get the project up and running, you can use Docker Compose.

```bash
docker-compose up --build
```

This will build and run both the frontend and backend services.

-   The frontend will be available at [http://localhost:8080](http://localhost:8080)
-   The backend will be available at [http://localhost:5000](http://localhost:5000)

## Services

### Backend

-   **Framework**: Flask
-   **Dependencies**:
    -   Flask
    -   google-cloud-firestore
    -   python-dotenv
    -   Flask-Swagger-UI
    -   Flask-SocketIO
    -   Flask-Cors
-   **Dockerfile**: `primecolada-backend/Dockerfile`

### Frontend

-   **Framework**: Vue.js
-   **Dependencies**:
    -   axios
    -   qrcode
    -   socket.io-client
    -   vue
    -   vue-router
-   **Dockerfile**: `primecolada-frontend/Dockerfile`

# Cambios recientes

## Despliegue Multi-Contenedor Cloud Run
- Se añadió el archivo `cloudrun-service.yaml` que define los tres contenedores (frontend, backend, websockets) y sus variables de entorno usando `localhost` para comunicación interna.
- El contenedor frontend se marca como principal (ingress), los otros como sidecars.
- Se especifica la cuenta de servicio para autenticación con Firestore.

## Cloud Build
- Se actualizó `cloudbuild.yaml` para desplegar usando el manifiesto `cloudrun-service.yaml`.
- El proceso ahora construye, sube y despliega los tres contenedores automáticamente.

## Websockets
- El servicio websockets ahora lee la URL del backend desde las variables de entorno `BACKEND_HOST` y `BACKEND_PORT`.
- Ejemplo de configuración en `docker-compose.yml` y en el manifiesto de Cloud Run.

## CI/CD
- Se recomienda crear un Trigger en Cloud Build para automatizar el despliegue al hacer push en la rama principal.

## IAM
- Es necesario asignar el rol "Cloud Datastore User" a la cuenta de servicio especificada en el manifiesto para acceso a Firestore.
