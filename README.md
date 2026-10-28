# Red Topológica Interestelar — prototipo 3D

Aplicación web para visualizar una red de nodos y corredores en 3D, experimentar con perturbaciones y observar corredores que superan un umbral de ruptura.

## Publicarla sin instalar programas en tu computadora

1. Descomprime este ZIP.
2. Crea un repositorio en https://github.com/new
3. Sube `app.py` y `requirements.txt` a la raíz del repositorio.
4. Abre https://share.streamlit.io/ e inicia sesión con GitHub.
5. Pulsa **Create app**, selecciona el repositorio, la rama `main` y el archivo `app.py`.
6. Pulsa **Deploy**. Al terminar tendrás un enlace web para abrir la simulación.

Documentación oficial: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app

## Incluye
- Visualización 3D interactiva con Plotly (rotación y zoom).
- Nodos numerados y corredores activos.
- Perturbación inicial configurable.
- Propagación heurística por pasos.
- Umbral para marcar corredores como rotos.
- Métricas de conectividad.

## Limitaciones
Es una primera maqueta visual. Los nodos permanecen fijos; la tensión se representa con color y tamaño. La propagación y ruptura son reglas simplificadas para explorar ideas, no un modelo físico validado. No incluye todavía distancia efectiva, resonancia ni dinámica mecánica completa.
