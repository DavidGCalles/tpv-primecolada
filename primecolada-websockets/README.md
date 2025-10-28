# Primecolada Websockets

Este servicio gestiona la comunicación en tiempo real entre el backend y los clientes mediante WebSockets.

## Cambios recientes

- La URL del backend ahora se configura mediante las variables de entorno `BACKEND_HOST` y `BACKEND_PORT`.
- Compatible con despliegue multi-contenedor en Cloud Run y con Docker Compose local.
- Ejemplo de configuración en `docker-compose.yml`:

```yaml
websockets:
  environment:
    - BACKEND_HOST=backend
    - BACKEND_PORT=5000
```

En Cloud Run, estas variables se definen como `localhost` para comunicación interna.

## Uso

Este servicio se despliega junto con el backend y el frontend. Consulta la raíz del proyecto para instrucciones de despliegue.
