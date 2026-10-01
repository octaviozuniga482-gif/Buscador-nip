import io
import pandas as pd
import requests
import streamlit as st

# Configuración de la página web
st.set_page_config(
    page_title="Buscador NIP", page_icon="🔍", layout="centered"
)

# Enlace de Google Sheets
ENLACE_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1qzHkdQOn3B77D3tpHHEKkhgddXRi9DHdphjN-FFpgO4/edit?pli=1&gid=1470224284#gid=1470224284"


def obtener_enlace_descarga(enlace_compartir):
  try:
    enlace_compartir = enlace_compartir.strip()
    if "/edit" in enlace_compartir:
      base_url = enlace_compartir.split("/edit")[0]
      return f"{base_url}/export?format=xlsx"
    return enlace_compartir
  except:
    return enlace_compartir


# Función para descargar y leer el Excel de Google Sheets (con caché para que sea súper rápido)
@st.cache_data(ttl=60)  # Se actualiza automáticamente cada 60 segundos
def cargar_datos_sheets():
  url_descarga = obtener_enlace_descarga(ENLACE_GOOGLE_SHEETS)
  try:
    respuesta = requests.get(url_descarga, timeout=10)
    if respuesta.status_code == 200:
      nuevos_datos = pd.read_excel(
          io.BytesIO(respuesta.content), sheet_name=None, dtype=str
      )
      return nuevos_datos
    else:
      return None
  except:
    return None


st.title("🔍 Buscador de NIP")
st.write("Ingresa tu ID para consultar tu NIP.")

# Mostrar indicador de carga mientras descarga los datos
with st.spinner("Sincronizando con Google Sheets..."):
  datos_memoria = cargar_datos_sheets()

if datos_memoria is None:
  st.error("No se pudo conectar con Google Sheets. Revisa tu enlace.")
else:
  st.success("¡Sistema listo!", icon="✅")

  # Cuadro de texto para buscar (en web abre el teclado automáticamente en móviles)
  id_buscado = st.text_input("Introduce tu ID:").strip().lower()

  if st.button("Buscar", type="primary"):
    if id_buscado == "":
      st.warning("Por favor ingresa un ID válido.")
    else:
      encontrado = False
      nip_encontrado = ""

      # Copia para buscar
      copia_memoria = {k: v.copy() for k, v in datos_memoria.items()}

      for nombre_hoja, datos_hoja in copia_memoria.items():
        columnas_limpias = [
            str(col).strip().lower() for col in datos_hoja.columns
        ]
        datos_hoja.columns = columnas_limpias

        col_id = "id" if "id" in columnas_limpias else None
        col_nip = "nip" if "nip" in columnas_limpias else None

        if col_id and col_nip:
          ids_columna = (
              datos_hoja[col_id]
              .fillna("")
              .astype(str)
              .str.strip()
              .str.replace(r"\.0$", "", regex=True)
              .str.lower()
          )

          fila = datos_hoja[ids_columna == id_buscado]
          if not fila.empty:
            nip_secreto = (
                str(fila.iloc[0][col_nip]).strip().replace(".0", "")
            )
            if nip_secreto.lower() != "nan" and nip_secreto != "":
              nip_encontrado = nip_secreto
              encontrado = True
              break

      # Mostrar resultado bonito
      if encontrado:
        st.markdown(
            f"### 🎉 Resultado:\n> **NIP: {nip_encontrado}**",
            unsafe_allow_html=True,
        )
      else:
        st.error("❌ El ID ingresado no existe.")