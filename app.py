import streamlit as st
import pandas as pd
import os
from datetime import datetime
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

def calcular_pagos(df, mes):
    df_mes = df[df["Mes"] == mes]
    pagos = {}

    for _, row in df_mes.iterrows():
        key = (row["Nombre"], row["Apellidos"])
        horas = row["Horas entrenadas"]
        casa = row["Partidos casa"]
        fuera = row["Partidos fuera"]
        rol = row["Rol"]

        if rol == "Principal":
            total = horas * 8 + casa * 16 + fuera * 26
        elif rol == "Ayudante":
            total = horas * 6 + casa * 10 + 0
        else:
            total = 0

        if key in pagos:
            pagos[key] += total
        else:
            pagos[key] = total

    resultado = []
    for (nombre, apellidos), total in pagos.items():
        resultado.append({
            "Nombre": nombre,
            "Apellidos": apellidos,
            "Total (€)": round(total, 2)
        })

    return pd.DataFrame(resultado)

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

    # Control dinámico de número de bloques
    if "num_bloques" not in st.session_state:
        st.session_state.num_bloques = 1

    st.session_state.num_bloques = st.number_input(
        "¿Cuántas categorías diferentes quieres registrar?", min_value=1, step=1, value=st.session_state.num_bloques
    )

    with st.form("registro_form"):
        nombre = st.text_input("Nombre")
        apellidos = st.text_input("Apellidos")

        categorias = [
            "benjamin 1", "benjamin 2y3", "alevin femenino", "alevin masculino",
            "infantil femenino", "infantil masculino", "cadete femenino", "cadete masculino",
            "junior masculino", "senior masculino", "escuela"
        ]

        bloques = []
        for i in range(st.session_state.num_bloques):
            with st.expander(f"Categoría #{i+1}", expanded=True):
                categoria = st.selectbox(f"Categoria", categorias, key=f"categoria_{i}")
                rol = st.selectbox("Rol", ["Principal", "Ayudante"], key=f"rol_{i}")
                meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                selected_month = st.selectbox("Mes", meses, key=f"mes_{i}")
                year = 2025

                num_dias = st.number_input("Numero de dias entrenados", min_value=0, step=1, key=f"dias_{i}")
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

            if st.button("🗑️ Eliminar todos los registros"):
                os.remove(data_file)
                st.success("Todos los registros han sido eliminados.")

            st.markdown("---")
            st.subheader("💶 Cálculo de pagos a entrenadores")

            meses_unicos = df["Mes"].dropna().unique().tolist()
            meses_ordenados = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            meses_disponibles = [m for m in meses_ordenados if m in meses_unicos]

            if meses_disponibles:
                mes_seleccionado = st.selectbox("Selecciona un mes", meses_disponibles)
                if st.button("Calcular pagos"):
                    df_pagos = calcular_pagos(df, eliminar_tildes(mes_seleccionado))
                    if not df_pagos.empty:
                        st.dataframe(df_pagos)
                        st.download_button("Descargar pagos en CSV", data=df_pagos.to_csv(index=False), file_name=f"pagos_{mes_seleccionado}.csv", mime="text/csv")
                    else:
                        st.info("No hay registros para ese mes.")
            else:
                st.info("No hay meses disponibles para calcular pagos.")
        else:
            st.info("Aún no hay registros guardados.")

elif password != "":
    st.error("Contrasena incorrecta.")




