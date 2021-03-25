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
	lista_preguntas = list(datos.iloc[:,5:].columns)
	pregunta = st.selectbox("Seleccione la pregunta: ", lista_preguntas)

	return pregunta	

def main():
	st.write("""# Visualizaciones """)

	file = st.file_uploader('File uploader')
	if file:
		datos = pd.read_excel(file)
		pregunta = filtros(datos)
		pivot = datos.pivot_table(index = pregunta, values= "ID de respuesta", aggfunc="count")
		st.write(pivot)
		fig = px.bar(pivot)
		fig.update_layout(legend=dict(
			orientation="h",
			yanchor="bottom",
			y=1.02,
			xanchor="right",
			x=1))
		st.plotly_chart(fig, use_container_width = True, config= config)

if __name__=="__main__":
	main()