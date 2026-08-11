# MRS - Sistema de Recomendación de Películas

Proyecto de reingeniería sobre el repo original de raviraj-p (https://github.com/raviraj-p/MRS). Es una app en Flask que recomienda películas según género, título o rating, usando datos locales (SQLite/CSV) y la API de TMDB.

## Cómo estaba antes

El código original funcionaba, pero tenía varios problemas típicos de un proyecto que creció sin mucho orden:

- Todas las rutas (la página principal, los endpoints de recomendaciones y las llamadas a TMDB) estaban metidas en un solo archivo, `app/routes/recommendations.py`, con un único Blueprint. No había separación entre "esto sirve HTML" y "esto sirve JSON".
- La API key de TMDB estaba escrita directamente en `config.py`, en texto plano, subida al repo.
- Había un bug que nunca se notó: la ruta de recomendaciones intentaba pasarle 5 argumentos a una función que solo aceptaba 3 (`genre, n, min_rating`). Si alguien mandaba `start_year` o `end_year` en la URL, la app tronaba.
- Cada vez que alguien pedía recomendaciones, se releía y reprocesaba desde cero el CSV completo de películas — nada de caché.
- Había un test que ni siquiera podía correr porque importaba una función que no existe en el proyecto.

## Qué cambié

**Blueprints separados.** Ahora hay dos: `main` (solo la vista HTML de la página principal) y `api` (todos los endpoints JSON, bajo el prefijo `/api/`). Cada uno vive en su propia carpeta dentro de `app/blueprints/`.

**Cliente de TMDB aparte.** Las llamadas a la API externa (buscar película, traer detalles, traer recomendaciones) ahora están en `app/clients/tmdb_client.py`, en vez de mezcladas con las rutas de Flask.

**Config con variables de entorno.** La API key y demás datos sensibles ya no están en el código — se leen de un archivo `.env` (que no se sube al repo, ver `.gitignore`). Usa `.env.example` como plantilla. También agregué configuraciones separadas para desarrollo, testing y producción.

**Arreglé el bug de los 5 argumentos**, quitando los parámetros de año que nunca funcionaron.

**Caché en el procesamiento de datos**, con `lru_cache`, para no reprocesar el CSV en cada request.

**Agregué `/api/health`**, un endpoint simple para monitoreo (lo voy a necesitar para el despliegue en producción más adelante).

**Arreglé el test roto** y dejé una prueba básica funcionando; la suite completa de pruebas la agrego en la siguiente fase del proyecto.
