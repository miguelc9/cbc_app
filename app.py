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

        categorias = [
            "benjamin 1", "benjamin 2y3", "alevin femenino", "alevin masculino",
            "infantil femenino", "infantil masculino", "cadete femenino", "cadete masculino",
            "junior masculino", "senior masculino", "escuela"
        ]

        bloques = []
        num_bloques = st.number_input("¿Cuántas categorías diferentes quieres registrar?", min_value=1, step=1)

        for i in range(num_bloques):
            with st.expander(f"Categoría #{i+1}", expanded=True):
                categoria = st.selectbox(f"Categoria", categorias, key=f"categoria_{i}")
                rol = st.selectbox("Rol", ["Principal", "Ayudante"], key=f"rol_{i}")
                meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                selected_month = st.selectbox("Mes", meses, key=f"mes_{i}")
                month_index = meses.index(selected_month) + 1
                year = 2025

                num_dias = st.number_input("Numero de dias entrenados", min_value=0, max_value=31, step=1, key=f"dias_{i}")

                partidos_casa = st.number_input("Partidos dirigidos en casa", min_value=0, step=1, key=f"casa_{i}")
                partidos_fuera = st.number_input("Partidos dirigidos fuera", min_value=0, step=1, key=f"fuera_{i}")

                bloques.append({
                    "Categoria": categoria,
                    "Rol": rol,
                    "Mes": selected_month,
                    "Horas entrenadas": num_dias,
                    "Partidos casa": partidos_casa,
                    "Partidos fuera": partidos_fuera
                })

        submitted = st.form_submit_button("Enviar")

        if submitted:
            if not nombre or not apellidos:
                st.warning("Por favor, completa tu nombre y apellidos.")
            else:
                nombre_clean = eliminar_tildes(nombre)
                apellidos_clean = eliminar_tildes(apellidos)

                registros = []
                for b in bloques:
                    if b["Horas entrenadas"] > 0:
                        fila = {
                            "Nombre": nombre_clean,
                            "Apellidos": apellidos_clean,
                            "Categoria": eliminar_tildes(b["Categoria"]),
                            "Rol": eliminar_tildes(b["Rol"]),
                            "Horas entrenadas": b["Horas entrenadas"],
                            "Partidos casa": b["Partidos casa"],
                            "Partidos fuera": b["Partidos fuera"],
                            "Mes": eliminar_tildes(b["Mes"]),
                            "Fecha registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        registros.append(fila)

                if registros:
                    guardar_datos(pd.DataFrame(registros))
                    st.success("Registro guardado con exito. ¡Gracias!")
                else:
                    st.warning("Debes introducir al menos una categoria con dias entrenados.")

    if password == "cbcadmin":
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:{COLOR_AZUL};'>Acceso administrador</h3>", unsafe_allow_html=True)
        if os.path.exists(data_file):
            df = pd.read_csv(data_file)
            st.dataframe(df)
            st.download_button("Descargar CSV", data=df.to_csv(index=False), file_name="registros_entrenadores.csv", mime="text/csv")
            if st.button("Eliminar todos los registros"):
                os.remove(data_file)
                st.success("Todos los registros han sido eliminados correctamente.")
        else:
            st.info("Aun no hay registros guardados.")

elif password != "":
    st.error("Contrasena incorrecta.")


