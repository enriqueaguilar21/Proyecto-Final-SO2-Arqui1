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
