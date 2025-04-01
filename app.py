import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import calendar
import unicodedata

# Ruta donde se almacenan los datos
data_file = "registros_entrenadores.csv"

# Colores del Club Baloncesto Calatayud
COLOR_AZUL = "#0033A0"
COLOR_ROSA = "#FF69B4"
COLOR_BLANCO = "#FFFFFF"

# Funciones auxiliares
def eliminar_tildes(texto):
    return unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')

def guardar_datos(data):
    if os.path.exists(data_file):
        df_existente = pd.read_csv(data_file)
        df_nuevo = pd.concat([df_existente, data], ignore_index=True)
    else:
        df_nuevo = data
    df_nuevo.to_csv(data_file, index=False)

def obtener_dias_del_mes(year, month_index):
    dias = []
    for day in range(1, calendar.monthrange(year, month_index)[1] + 1):
        weekday = calendar.weekday(year, month_index, day)
        nombre_dia = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"][weekday]
        dias.append(f"{nombre_dia}-{str(day).zfill(2)}")
    return dias

# Configuracion de pagina
st.set_page_config(page_title="Registro de Entrenamientos y Partidos", layout="centered")

st.markdown(f"""
    <h1 style='text-align: center; color: {COLOR_AZUL};'>Registro mensual de entrenadores</h1>
""", unsafe_allow_html=True)

# Autenticacion
password = st.text_input("Introduce la contrasena", type="password")

if password == "cbcentrenador" or password == "cbcadmin":
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #555;'>Por favor, rellena el formulario correspondiente al mes actual.</h3>", unsafe_allow_html=True)

    with st.form("registro_form"):
        nombre = st.text_input("Nombre")
        apellidos = st.text_input("Apellidos")

        categoria = st.selectbox("Categoria", [
            "benjamin 1", "benjamin 2y3", "alevin femenino", "alevin masculino",
            "infantil femenino", "infantil masculino", "cadete femenino", "cadete masculino",
            "junior masculino", "senior masculino", "escuela"
        ])

        rol = st.selectbox("Rol", ["Principal", "Ayudante"])

        # Selección del mes
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        selected_month = st.selectbox("Mes", meses)
        month_index = meses.index(selected_month) + 1
        year = 2025

        dias_del_mes = obtener_dias_del_mes(year, month_index)
        num_dias = st.number_input("Numero de dias entrenados (haz clic para ver el calendario)", min_value=0, max_value=len(dias_del_mes), step=1)

        with st.expander("Ver dias del mes"):
            st.write(", ".join(dias_del_mes))

        partidos_casa = st.number_input("Partidos dirigidos en casa", min_value=0, step=1)
        partidos_fuera = st.number_input("Partidos dirigidos fuera", min_value=0, step=1)

        submitted = st.form_submit_button("Enviar")

        if submitted:
            if not nombre or not apellidos:
                st.warning("Por favor, completa tu nombre y apellidos.")
            elif num_dias == 0:
                st.warning("Debes indicar al menos un día de entrenamiento.")
            else:
                nombre_clean = eliminar_tildes(nombre)
                apellidos_clean = eliminar_tildes(apellidos)
                categoria_clean = eliminar_tildes(categoria)
                rol_clean = eliminar_tildes(rol)
                mes_clean = eliminar_tildes(selected_month)

                nueva_fila = pd.DataFrame([{
                    "Nombre": nombre_clean,
                    "Apellidos": apellidos_clean,
                    "Categoria": categoria_clean,
                    "Rol": rol_clean,
                    "Horas entrenadas": num_dias,
                    "Partidos casa": partidos_casa,
                    "Partidos fuera": partidos_fuera,
                    "Mes": mes_clean,
                    "Fecha registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])

                guardar_datos(nueva_fila)
                st.success("Registro guardado con exito. ¡Gracias!")

    if password == "cbcadmin":
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:{COLOR_AZUL};'>Acceso administrador</h3>", unsafe_allow_html=True)
        if os.path.exists(data_file):
            df = pd.read_csv(data_file)
            st.dataframe(df)
            st.download_button("Descargar CSV", data=df.to_csv(index=False), file_name="registros_entrenadores.csv", mime="text/csv")
        else:
            st.info("Aun no hay registros guardados.")

elif password != "":
    st.error("Contrasena incorrecta.")


