# MongoADC



## Tecnología y Estructura
El backend del sistema se desarrolla en Flask, un framework de Python altamente flexible y eficiente para aplicaciones web, apoyado por una base de datos MongoDB. Esta estructura asegura un manejo robusto y seguro de la información de los usuarios.

En el frontend, se utiliza Streamlit para crear una aplicación interactiva que comunica directamente con el backend a través de rutas Flask. Este enfoque permite una experiencia de usuario fluida y enfocada en la facilidad de uso y accesibilidad.

## Instalación

Para ejecutar este proyecto, debes tener instalado Python 3.6 o superior en tu máquina. Asegúrate de tener también pip para la gestión de las librerías. Sigue los pasos a continuación para configurar el ambiente y comenzar a utilizar el chatbot.

### Pre-requisitos

Antes de instalar las librerías necesarias, verifica que tengas una versión compatible de Python ejecutando:

```bash
python --version
```

O si tienes instalaciones concurrentes de Python 2 y Python 3, es posible que necesites usar:

```bash
python3 --version
```

## Instalación de librerías
Una vez confirmado el entorno de Python, instala las siguientes librerías requeridas para el funcionamiento del proyecto:

```bash
pip install Flask Flask-pymongo streamlit sklearn pymongo pandas python-dotenv
```

Nota: Si estás usando un ambiente virtual (lo cual es recomendado), asegúrate de activarlo antes de ejecutar el comando anterior.

## Configuración de variables de entorno
Este proyecto utiliza variables de entorno para manejar configuraciones sensibles. Crea un archivo .env en la raíz del proyecto y añade las siguientes variables:

 ```ruby
MONGO_URI=url_a_tu_cluster_de_mongo
```

Reemplaza url_a_tu_cluster_de_mongo con tu verdadera url.


## Ejecución

Una vez instaladas las dependencias y configuradas las variables de entorno, puedes iniciar el backend y el frontend en dos terminales por separado:

Para el backend con Flask:

python backend/app.py 

Para el frontend con Streamlit:

streamlit run frontend/streamlit_app.py

Ahora, la aplicación debería estar corriendo en tu máquina local, y puedes interactuar con el chatbot asistente financiero desde la interfaz de usuario de Streamlit.

Este apartado proporciona a los usuarios instrucciones claras sobre cómo preparar su entorno para ejecutar tu proyecto, desde la instalación de librerías necesarias hasta la configuración de variables de entorno y la ejecución de la aplicación. Asegúrate de personalizar nombres de archivos y rutas según corresponda a tu estructura de proyecto específica.

## Preparación e Inicialización de la Base de Datos
Para comenzar a utilizar la aplicación y tener la base de datos preparada, sigue estos pasos detallados:

1. Descarga de Datos Iniciales:

- Visita la siguiente URL: [Link de descarga](https://www.kaggle.com/datasets/davidcariboo/player-scores)
- Descarga los archivos CSV: appearances, players, clubs, club_games, games y competitions.
- Almacenamiento de Datos: Ubica los archivos CSV descargados dentro de tu proyecto en el directorio src/data/. Asegúrate de que los archivos estén en el lugar correcto para su correcta lectura e importación.

2. Inicialización de la Base de Datos:

Con tu servidor Flask ya en funcionamiento, abre tu navegador preferido.
Accede a la siguiente dirección: http://localhost:5000/initialize_database
Este paso ejecutará automáticamente todas las acciones necesarias para configurar e inicializar tu base de datos MongoDB, con los datos de los archivos CSV.


## Funcionalidades de la App
La aplicación proporciona una serie de funcionalidades diseñadas para amantes del fútbol y analistas, aprovechando un conjunto de datos detallado de las cinco grandes ligas europeas desde 2012. Estas funcionalidades permiten investigar y comparar el rendimiento de los jugadores y equipos de manera profunda.

1. Obtener el 11 Ideal de un Equipo por Temporada
Los usuarios pueden seleccionar cualquier equipo de las cinco grandes ligas de fútbol europeas (Premier League, LaLiga, Serie A, Bundesliga, Ligue 1) y una temporada específica desde 2012 hasta la actualidad. La app analizará el rendimiento de los jugadores basándose en diversas métricas y clusterización para ofrecer el 11 ideal del equipo seleccionado para la temporada elegida.

¿Cómo usar?

- Selecciona un equipo y una temporada.
- La app te mostrará el 11 ideal del equipo para esa temporada.

2. Consultar la Puntuación de un Jugador
Gracias a una compleja clusterización basada en múltiples métricas de rendimiento, esta funcionalidad permite a los usuarios elegir un jugador y obtener su puntuación en un rango del 1 al 50. Aquí, 1 representa al mejor jugador y 50 al que se encuentra en la posición más baja dentro del análisis realizado.

¿Cómo usar?

- Elige un jugador de las cinco grandes ligas desde 2012.
- La app te proporcionará una puntuación que refleja su nivel y rendimiento en comparación con otros jugadores, basándose en la clusterización previamente hecha.

3. Comparar Jugadores de Diferentes Equipos
Esta funcionalidad permite a los usuarios comparar dos jugadores de diferentes equipos para determinar cuál ha tenido un mejor rendimiento. Utilizando las puntuaciones y métricas definidas en el proceso de clusterización, la app analiza y compara el rendimiento de ambos jugadores para indicar cuál es superior según los datos.

¿Cómo usar?

- Selecciona dos jugadores de cualquier equipo dentro de las ligas cubiertas y desde 2012.
- La app analizará su rendimiento y te indicará cuál de los dos es mejor según las métricas definidas.


## Uso 