# Simulador de Lanzamiento de Objetos

Una aplicación interactiva desarrollada en Python utilizando Streamlit para simular y visualizar la física del lanzamiento de distintos objetos bajo condiciones reales e ideales.

## Características Principales

- **Configuración de objetos:** Ajusta el tipo de objeto, dimensiones y masa.
- **Factores ambientales:** Considera el rozamiento del aire y la velocidad y dirección del viento.
- **Mecanismos de lanzamiento:** Selecciona entre varios perfiles de fuerza (rodillos, lineal, explosión/impulso).
- **Cálculo de trayectorias:** Determina automáticamente la fuerza, el torque o la velocidad inicial necesarios para alcanzar un rango y altura determinados.
- **Visualización 3D:** Gráficos dinámicos e interactivos de la trayectoria utilizando herramientas especializadas.

## Cómo Ejecutar

1. Clona el repositorio:
   ```bash
   git clone https://github.com/ibinfelix/SimuladorLanzamiento.git
   cd SimuladorLanzamiento
   ```

2. (Opcional) Crea y activa un entorno virtual de Python.

3. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```

4. Ejecuta la aplicación de Streamlit:
   ```bash
   streamlit run app.py
   ```

## Tecnologías Utilizadas
* Python 3
* Streamlit
* NumPy / SciPy
* Plotly (para visualizaciones)

## Licencia
*Software para propósitos educativos y de simulación.*
