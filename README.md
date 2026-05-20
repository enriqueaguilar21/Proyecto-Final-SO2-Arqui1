# Proyecto-Final-SO2-Arqui1
PROYECTO Robótica y Servidor Web Linux

Este repositorio contiene el código fuente de los tres componentes principales del sistema (Frontend, Backend y Base de Datos) desplegados en un entorno contenerizado.

## 1. Dirección IP pública del servidor
Los servicios se encuentran en ejecución y accesibles a través de la siguiente dirección IP pública:

**[INGRESA AQUÍ TU IP PÚBLICA]** *(Ejemplo: http://203.0.113.50)*

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

## 4. Instrucciones de Despliegue Rápido

Para replicar o levantar este entorno en el servidor Ubuntu de AWS, ejecute los siguientes comandos en la terminal:

1. **Clonar el repositorio:**
   ```bash
   git clone <URL_DE_TU_REPOSITORIO>
   cd <NOMBRE_DE_LA_CARPETA>
