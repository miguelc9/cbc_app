import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import calendar
import unicodedata

# Ruta donde se almacenan los datos
data_file = "registros_entrenadores.csv"

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

# Configuracion de pagina
st.set_page_config(page_title="Registro de Entrenamientos y Partidos", layout="centered")
st.title("Registro mensual de entrenadores")

# Autenticacion
password = st.text_input("Introduce la contrasena", type="password")

if password == "cbcentrenador" or password == "cbcadmin":
    st.markdown("---")
    st.markdown("Por favor, rellena el formulario correspondiente al mes actual.")

    # Seleccion de mes y generacion de calendario tipo cuadrícula
    st.markdown("### Selecciona el mes y los dias entrenados")
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    selected_month = st.selectbox("Mes", meses)
    month_index = meses.index(selected_month) + 1
    year = 2025
    days_in_month = calendar.monthrange(year, month_index)[1]

    st.markdown("#### Haz clic en los días entrenados")
    if "dias" not in st.session_state:
        st.session_state.dias = set()

    cols = st.columns(7)
    week_day = calendar.monthrange(year, month_index)[0]  # 0 = lunes

    # Espacios en blanco hasta el primer día del mes
    for i in range(week_day):
        cols[i].empty()

    for day in range(1, days_in_month + 1):
        i = (week_day + day - 1) % 7
        if cols[i].button(str(day), key=f"day_{month_index}_{day}"):
            st.session_state.dias.symmetric_difference_update({day})

        if (week_day + day) % 7 == 0:
            cols = st.columns(7)

    selected_days = sorted(st.session_state.get("dias", set()))
    st.write(f"**Días seleccionados:** {', '.join(str(d) for d in selected_days)}")

    # Formulario principal (sin botones dentro)
    with st.form("registro_form"):
        nombre = st.text_input("Nombre")
        apellidos = st.text_input("Apellidos")

        categoria = st.selectbox("Categoria", [
            "benjamin 1", "benjamin 2y3", "alevin femenino", "alevin masculino",
            "infantil femenino", "infantil masculino", "cadete femenino", "cadete masculino",
            "junior masculino", "senior masculino", "escuela"
        ])

        rol = st.selectbox("Rol", ["Principal", "Ayudante"])

        partidos_casa = st.number_input("Partidos dirigidos en casa", min_value=0, step=1)
        partidos_fuera = st.number_input("Partidos dirigidos fuera", min_value=0, step=1)

        submitted = st.form_submit_button("Enviar")

        if submitted:
            if not nombre or not apellidos:
                st.warning("Por favor, completa tu nombre y apellidos.")
            elif len(selected_days) == 0:
                st.warning("Debes seleccionar al menos un día de entrenamiento.")
            else:
                nombre_clean = eliminar_tildes(nombre)
                apellidos_clean = eliminar_tildes(apellidos)
                categoria_clean = eliminar_tildes(categoria)
                rol_clean = eliminar_tildes(rol)

                fechas_entrenamiento = [f"{str(day).zfill(2)}-{str(month_index).zfill(2)}" for day in selected_days]

                nueva_fila = pd.DataFrame([{
                    "Nombre": nombre_clean,
                    "Apellidos": apellidos_clean,
                    "Categoria": categoria_clean,
                    "Rol": rol_clean,
                    "Horas entrenadas": len(selected_days),
                    "Partidos casa": partidos_casa,
                    "Partidos fuera": partidos_fuera,
                    "Mes": eliminar_tildes(selected_month),
                    "Dias entrenados": ", ".join(fechas_entrenamiento),
                    "Fecha registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])

                guardar_datos(nueva_fila)
                st.session_state.dias.clear()
                st.success("Registro guardado con exito. ¡Gracias!")

    if password == "cbcadmin":
        st.markdown("---")
        st.markdown("### Acceso administrador")
        if os.path.exists(data_file):
            df = pd.read_csv(data_file)
            st.dataframe(df)
            st.download_button("Descargar CSV", data=df.to_csv(index=False), file_name="registros_entrenadores.csv", mime="text/csv")
        else:
            st.info("Aun no hay registros guardados.")

elif password != "":
    st.error("Contrasena incorrecta.")


