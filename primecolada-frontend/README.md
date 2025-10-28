# Primecolada Frontend

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

This is the frontend for the TPV Primecolada application, built with Vue.js.

## Getting Started

### Prerequisites

-   Node.js
-   npm

### Installation

1.  Navigate to the `primecolada-frontend` directory.
2.  Install the dependencies:

    ```bash
    npm install
    ```

### Development

To run the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173` by default (or whatever port Vite assigns).

### Building for Production

To build the application for production:

```bash
npm run build
```

The production-ready files will be located in the `dist` directory.

## Dependencies

-   `axios`: For making HTTP requests to the backend.
-   `qrcode`: To generate QR codes.
-   `socket.io-client`: For real-time communication with the backend.
-   `vue`: The core Vue.js library.
-   `vue-router`: For handling routing within the application.

## Docker

The frontend can also be run in a Docker container. The `Dockerfile` and `nginx.conf` are provided for this purpose. When using `docker-compose` from the root directory, the frontend will be served at `http://localhost:8080`.

# Cambios recientes

- El frontend ahora puede ser desplegado como parte de un servicio multi-contenedor en Cloud Run.
- Variables de entorno para comunicación interna entre contenedores (ejemplo: `BACKEND_HOST=localhost`).
- Se añadió el manifiesto `cloudrun-service.yaml` y se actualizó el proceso de Cloud Build.
