import streamlit as st
import pandas as pd
import plotly.express as px



st.set_page_config(layout="wide")

config = {'scrollZoom': True, 'displaylogo': False, 'responsive':True,
          'editable': True,
          'toImageButtonOptions': {
             'format': 'png', # one of png, svg, jpeg, webp
             'filename': 'custom_image',
             'height': None,
             'width': None,
             'scale': 3 # Multiply title/legend/axis/canvas sizes by this factor
  }}

def filtros(datos):
	lista_filtros = []

	col_preguntas = int(st.number_input('Ingrese un número', 1,50,5))
	lista_preguntas = list(datos.iloc[:,col_preguntas:].columns)
	lista_agrupadores = list(datos.iloc[:,1:col_preguntas].columns)

	pregunta = st.selectbox("Seleccione qué pregunta desea analizar: ", lista_preguntas)
	lista_filtros.append(st.selectbox("Qué desea ver en el eje x", ["Pregunta"] +lista_agrupadores))
	lista_filtros.append(st.selectbox("Dividir por color", [" ", "Pregunta"] +lista_agrupadores))
	lista_filtros.append(st.selectbox("Dividir por columna", [" ", "Pregunta"] +lista_agrupadores))
	lista_filtros.append(st.selectbox("Sub gráficas por fila",[" ", "Pregunta"] + lista_agrupadores))

	filtros_def = [None if x == ' ' else x for x in lista_filtros ]
	filtros_def = [pregunta if x == "Pregunta" else x for x in filtros_def ]
	indices = set(filtros_def).difference([None])

	return pregunta, filtros_def, indices	

def main():
	st.write("""# ESTE ES EL CAMBIO DE MARIANA""")

	file = st.file_uploader('File uploader')
	if file:
		datos = pd.read_excel(file)
		pregunta, filtros_def, indices = filtros(datos)
		ejex, color, columna, fila = filtros_def

		datos[pregunta] = datos[pregunta].astype(str)
		pivot = datos.pivot_table(index = indices,
								  values= "ID de respuesta", aggfunc="count").reset_index()
		#st.write(pivot)
		fig = px.bar(pivot, x=ejex, 
					 y="ID de respuesta", color=color,
					 facet_row=fila, facet_col=columna, barmode="group")
		fig.update_layout(legend=dict(
			orientation="h",
			yanchor="bottom",
			y=1.02,
			xanchor="right",
			x=1))
		st.plotly_chart(fig, use_container_width = True, config= config)

if __name__=="__main__":
	main()