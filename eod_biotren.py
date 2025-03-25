import streamlit as st
from supabase import create_client
import requests
import folium
from streamlit_folium import st_folium

def reset_all():
    st.session_state.clear()
    st.session_state["genero"] = ""
    st.session_state["edad"] = None
    st.session_state["sentido"] = ""
    st.session_state["linea"] = ""
    st.session_state["direccion_origen"] = ""
    st.session_state["comuna_origen"] = ""
    st.session_state["coords_origen"] = None
    st.session_state["estacion_origen"] = ""
    st.session_state["modo_llegada"] = ""
    st.session_state["direccion_destino"] = ""
    st.session_state["comuna_destino"] = ""
    st.session_state["coords_destino"] = None
    st.session_state["estacion_destino"] = ""
    st.session_state["modo_salida"] = ""
    st.session_state["proposito"] = ""
    st.session_state["veh_hogar"] = ""
    st.session_state["ingreso"] = ""
    st.rerun()

def geocode_address(address: str):
    """
    Obtiene las coordenadas (latitud, longitud) de una dirección usando la API de geocodificación de Mapbox.
    
    :param address: Dirección completa incluyendo comuna.
    :param mapbox_token: Token de acceso de Mapbox.
    :return: Una tupla (latitud, longitud) o None si no se encontró la dirección.
    """
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json"
    params = {
        "access_token": 'pk.eyJ1IjoiZmVsaXhxdWl0cmFsOTciLCJhIjoiY204bmtrbjRrMDFxNTJscHQ1cWMweGNmMCJ9.ZzNW3H8NgfXUkBsHRBun8A',
        "country": "CL",  # Puedes ajustar el país según sea necesario
        "limit": 1
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data["features"]:
            lon, lat = data["features"][0]["geometry"]["coordinates"]
            return lat, lon
    
    return None

# Configurar Supabase
SUPABASE_URL = "https://ormqsziqbzhingbjmcpx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ybXFzemlxYnpoaW5nYmptY3B4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI4MzEzMzEsImV4cCI6MjA1ODQwNzMzMX0.3X6-VZNQgBzIdB0lvv6RE_be9kXgJcA9vV-QmdgEaZM"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def guardar_respuestas(respuestas):
    try:
        response = supabase.table("eod_biotren").insert(respuestas).execute()
        st.success("Respuesta guardada exitosamente")
        reset_all()
    except Exception as e:
        st.error("Error al guardar la respuesta")
    
def encuesta():
    
    # Obtener el parámetro user_id de la URL
    encuestador = st.query_params.encuestador  # Si no hay user_id, asignar 'desconocido'
    
    st.title("Encuesta Origen Destino Biotren")
    
    genero = st.selectbox("Género", ["", "Masculino", "Femenino"], key="genero")
    sentido = st.selectbox("Sentido del viaje", ["", "Sube", "Baja", "Combina"], key="sentido")
    linea = st.selectbox("Línea del Biotren", ["", "Línea 1", "Línea 2"], key="linea")
    edad = st.number_input("Edad", 14, 100, None, step = None, format = "%d", key="edad")
    

    comunas_list = ["1 - Chiguayante", 
                    "2 - Concepción", 
                    "3 - Coronel", 
                    "4 - Hualpén", 
                    "5 - Hualqui", 
                    "6 - Lota", 
                    "7 - Penco", 
                    "8 - San Pedro de la Paz", 
                    "9 - Talcahuano", 
                    "10 - Tomé"]
    estaciones_list = ["1-Mercado de Talcahuano",
                       "2-El Arenal",
                       "3-Higueras",
                       "4-Los Cóndores",
                       "5-UTF Santa María",
                       "6-Lorenzo Arenas",
                       "7-Concepción",
                       "8-Chiguayante",
                       "9-Pedro Medina",
                       "10-Manquimávida",
                       "11-La Leonora",
                       "12-Hualqui",
                       "13-Juan Pablo II",
                       "14-Diagonal Biobío",
                       "15-Alborada",
                       "16-Costa Mar",
                       "17-El Parque",
                       "18-Lomas Coloradas",
                       "19-Cardenal R. Silva Henríquez",
                       "20-Hito Galvarino",
                       "21-Los Canelos",
                       "22-Huinca",
                       "23-Cristo Redentor",
                       "24-Laguna Quiñenco",
                       "25-Coronel"]
    modos_list = ["1 - Ninguno",
                  "2 - Taxibus",
                  "3 - Taxicolectivo",
                  "4 - Vehículo Particular",
                  "5 - Otro"]
    
    rangos_ingreso_list = ["1 - Menos de 300.000 $/mes",
                           "2 - Entre 300.001 y 500.000 $/mes",
                           "3 - Entre 500.001 y 800.000 $/mes",
                           "4 - Entre 800.001 y 1.200.000 $/mes",
                           "5 - Entre 1.200.001 y 1.560.000 $/mes",
                           "6 - Entre 1.560.001 y 2.000.000 $/mes",
                           "7 - Entre 2.000.001 y 2.500.000 $/mes",
                           "8 - Más de 2.500.000 $/mes"]

    st.subheader("¿Cuál es el origen de su viaje?")
    direccion_origen = st.text_input("Calle y Número / Intersección / Hito", key="direccion_origen")
    comuna_origen = st.selectbox("Comuna de origen", [""] + comunas_list, key="comuna_origen")

    geocoding_origin_button = st.button("Georreferenciar origen")
    

    if geocoding_origin_button:
        lat_lon_orig = geocode_address(direccion_origen + ", " + comuna_origen.split(" - ")[1]+ ",BioBio, Chile")
        if lat_lon_orig:
            st.success(f"Ubicación encontrada: {lat_lon_orig}")
            st.session_state.coords_origen = lat_lon_orig
            st.session_state.center_map_origen = lat_lon_orig
            st.session_state.zoom_map_origen = 13
        else:
            st.error("No se encontró la ubicación")

    map_origen = folium.Map(location = st.session_state["center_map_origen"], zoom_start= st.session_state["zoom_map_origen"])

    if st.session_state.coords_origen:
        folium.Marker(
            location=st.session_state.coords_origen,
            popup="Origen",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(map_origen)

    st_folium(map_origen, width=300, height = 300 ,returned_objects=[], key="map_origen")

    st.subheader("¿En que estación abordó el servicio del biotren?")
    estacion_origen = st.selectbox("Estación donde abordó el Biotren", [""] + estaciones_list, key="estacion_origen")

    st.subheader("¿Cómo llegó a la estación?¿Qué medio de transporte utilizó?")
    modo_llegada = st.selectbox("Medio de transporte para llegar a la estación", [""] + modos_list, key="modo_llegada")

    
    st.subheader("¿Cuál es el destino de su viaje?")
    direccion_destino = st.text_input("Calle y Número / Intersección / Hito", key="direccion_destino")
    comuna_destino = st.selectbox("Comuna de destino", [""] + comunas_list, key="comuna_destino")

    geocoding_destiny_button = st.button("Georreferenciar destino")

    if geocoding_destiny_button:
        lat_lon_des = geocode_address(direccion_destino + ", " + comuna_destino.split(" - ")[1] + ",BioBio, Chile")
        if lat_lon_des:
            st.success(f"Ubicación encontrada: {lat_lon_des}")
            st.session_state.coords_destino = lat_lon_des
            st.session_state.center_map_destino = lat_lon_des
            st.session_state.zoom_map_destino = 13
        else:
            st.error("No se encontró la ubicación")

    map_destino = folium.Map(location = st.session_state["center_map_destino"], zoom_start= st.session_state["zoom_map_destino"])

    if st.session_state.coords_destino:
        folium.Marker(
            location=st.session_state.coords_destino,
            popup="Destino",
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(map_destino)

    st_folium(map_destino, width=300, height = 300 ,returned_objects=[], key="map_destino")

    st.subheader("¿En que estación se bajó del servicio del biotren?")
    estacion_destino = st.selectbox("Estación donde se bajó del Biotren", [""] + estaciones_list, key="estacion_destino")

    st.subheader("¿Toma locomoción para llegar a su destino? ¿Cuál?")
    modo_salida = st.selectbox("Medio de transporte para llegar a su destino", [""] + modos_list, key="modo_salida")

    st.subheader("¿Cuál es el propósito de su viaje?")
    proposito = st.selectbox("Propósito de su viaje", ["", "1 - Trabajo", "2 - Estudio", "3 - Otro"], key="proposito")

    st.subheader("¿En su hogar posee vehículo motorizado?¿Cuántos?")
    veh_hogar = st.selectbox("Vehículo en el hogar", ["", "No, Ninguno", "Sí, 1", "Sí, 2 o más"], key="veh_hogar")

    st.subheader("¿En qué rango se encuentra su ingreso familiar mensual?")
    ingreso = st.selectbox("Ingreso familiar mensual", [""] + rangos_ingreso_list, key="ingreso")

    if st.button("Enviar Encuesta"):
        respuestas = {
            "encuestador": encuestador,
            "genero": genero,
            "edad": edad,
            "sentido_viaje": sentido,
            "linea_biotren": linea,
            "direccion_origen": direccion_origen,
            "comuna_origen": comuna_origen,
            "coords_origen": st.session_state.coords_origen if st.session_state.coords_origen else (0,0),
            "estacion_origen": estacion_origen,
            "modo_llegada": modo_llegada,
            "direccion_destino": direccion_destino,
            "comuna_destino": comuna_destino,
            "coords_destino": st.session_state.coords_destino if st.session_state.coords_destino else (0,0),
            "estacion_destino": estacion_destino,
            "modo_salida": modo_salida,
            "proposito_viaje": proposito,
            "vehiculos_hogar": veh_hogar,
            "ingreso_familiar": ingreso
        }

        guardar_respuestas(respuestas)



if "coords_origen" not in st.session_state:
    st.session_state.coords_origen = None

if "coords_destino" not in st.session_state:
    st.session_state.coords_destino = None

if "center_map_origen" not in st.session_state:
    st.session_state.center_map_origen = (-36.82366462475327, -73.05557506871361)

if "zoom_map_origen" not in st.session_state:
    st.session_state.zoom_map_origen = 11.5

if "center_map_destino" not in st.session_state:
    st.session_state.center_map_destino = (-36.82366462475327, -73.05557506871361)

if "zoom_map_destino" not in st.session_state:
    st.session_state.zoom_map_destino = 11.5

if __name__ == "__main__":
    encuesta()
