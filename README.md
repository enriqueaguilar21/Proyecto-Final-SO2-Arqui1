# Proyecto-Final-SO2-Arqui1
PROYECTO Robótica y Servidor Web Linux

Este repositorio contiene el código fuente de los tres componentes principales del sistema (Frontend, Backend y Base de Datos) desplegados en un entorno contenerizado.

## 1. Dirección IP pública del servidor
Los servicios se encuentran en ejecución y accesibles a través de la siguiente dirección IP pública:

**[INGRESA AQUÍ LA IP PROPORCIONADA POR EL AUTOR ]** *(Ejemplola: http://203.0.113.50)*

*(Nota: Si tu frontend y backend corren en puertos específicos, agrégalos aquí. Ejemplo: Frontend en el puerto 80, Backend en el 3000).*

## 2. Diseño de la Arquitectura del Sistema

A continuación se presenta el diagrama de arquitectura implementado en la nube. El sistema sigue un modelo de tres capas contenerizado:
```mermaid
graph TD;
    Cliente([Navegador Web / Cliente]) -->|Peticiones HTTP| Frontend;
    
    subgraph Servidor Linux en la Nube
        Frontend[Contenedor Frontend] -->|API REST| Backend;
        Backend[Contenedor Backend] -->|Consultas| DB[(Contenedor Base de Datos)];
    end
```
Descripción del Flujo de Trabajo y Tolerancia a Fallos:
Flujo Normal: El cliente interactúa con la interfaz web (Frontend), la cual realiza peticiones HTTP/REST hacia la API del Backend. El backend procesa las solicitudes y gestiona el almacenamiento o lectura de eventos en la Base de Datos.

Caída del Backend: Si el contenedor del backend se detiene, la interfaz web permanece accesible, pero las acciones que requieran procesamiento lógico fallarán y no se registrarán nuevos eventos.

Caída de la Base de Datos: Si la base de datos se detiene, el backend sigue recibiendo las peticiones del frontend o de fuentes externas, pero los logs reportarán errores de conexión y los eventos no se almacenarán de forma permanente.

Caída del Frontend: Si la interfaz web se cae, el acceso visual queda interrumpido. Sin embargo, el backend y la base de datos continúan operativos, permitiendo la recepción y almacenamiento automático de eventos a través de peticiones directas a la API (vía cURL o Postman).

## 3. Tecnologías Utilizadas

El sistema ha sido desarrollado utilizando un ecosistema de herramientas robustas y modernas, unificando toda la lógica de programación bajo el lenguaje **Python** y estructurando el proyecto en una arquitectura contenerizada de tres capas.

### Infraestructura y Despliegue
* **Proveedor de Nube:** AWS (Amazon Web Services) mediante una instancia EC2.
* **Sistema Operativo:** Ubuntu Server (Linux) como entorno base del servidor.
* **Orquestación y Contenedores:** Docker y Docker Compose, permitiendo el aislamiento y ejecución independiente de cada componente (Frontend, Backend y Base de Datos).

### Frontend (Capa de Presentación)
* **Lenguajes:** HTML5 y CSS3 para la estructura, maquetación e interfaz gráfica expuesta al usuario.
* **Servidor Web:** Nginx, encargado de servir los archivos estáticos del frontend de manera eficiente y actuar como puerta de enlace.

### Backend (Capa de Lógica de Negocio)
* **Lenguaje de Programación:** Python 3.x.
* **Framework:** Flask, utilizado para la construcción de la API REST, procesamiento de la lógica del sistema y gestión del flujo de los eventos.

### Base de Datos (Capa de Persistencia)
* **Motor de Base de Datos:** MongoDB (NoSQL), seleccionado por su flexibilidad para el almacenamiento de registros y eventos mediante documentos JSON/BSON.

---

## 4. Instrucciones de Uso y Pruebas del Sistema

**⚠️ Nota importante sobre la Dirección IP:**
Actualmente, el sistema no cuenta con un dominio propio y está alojado en una instancia en la nube con una **IP pública dinámica**. Esto significa que cada vez que la instancia se detiene y se reinicia, la dirección IP cambia. Para acceder al sistema, asegúrese de utilizar la IP proporcionada en la **Sección 1** de este documento. En caso de que el enlace no responda, contacte al autor para obtener la dirección IP vigente.

### Acceso al Sistema
1. Abra un navegador web.
2. Ingrese a la dirección: `http://<TU_IP_ACTUAL_AQUI>` (Ejemplo: `http://54.219.xxx.xxx`).
3. Se mostrará la interfaz principal (Frontend servido por Nginx).

### Flujo Básico de Uso
1. **Generación de Eventos:** En la interfaz web, utilice los controles disponibles para registrar un nuevo evento.
2. **Confirmación:** El sistema enviará la petición al Backend (Flask), el cual procesará la información y devolverá un mensaje de éxito en pantalla.
3. **Persistencia:** Si accede a la base de datos (MongoDB), podrá verificar que el documento JSON con la información del evento se ha guardado correctamente.

### Pruebas de Tolerancia a Fallos (Demostración)
El sistema está diseñado en contenedores aislados. Para comprobar el comportamiento ante fallos, puede ejecutar los siguientes comandos en la terminal del servidor:

* **Prueba de caída del Backend:**
  Ejecute `docker stop backend_container`. Si intenta enviar un evento desde la página web, la interfaz seguirá funcionando, pero mostrará un error de conexión, demostrando que no se registran eventos falsos.
  *(Para restaurar: `docker start backend_container`)*

* **Prueba de caída de Base de Datos:**
  Ejecute `docker stop mongodb_container`. Al enviar un evento desde la web o mediante API, el Backend lo recibirá, pero los logs (`docker logs <nombre_contenedor_backend>`) mostrarán un error al intentar persistir los datos, demostrando que no se almacenan.
  *(Para restaurar: `docker start mongodb_container`)*

* **Prueba de caída del Frontend:**
  Ejecute `docker stop frontend_container`. La página web dejará de cargar en el navegador. Sin embargo, si se envía una petición `POST` directamente a la API del Backend (por ejemplo, usando Postman o cURL a `http://<IP_ACTUAL>:<PUERTO_BACKEND>/endpoint`), el evento se procesará y guardará correctamente en la base de datos.
