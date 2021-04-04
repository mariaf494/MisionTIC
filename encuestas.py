import streamlit as st
import pandas as pd
import plotly.express as px
import copy


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

@st.cache
def load_data(file):
	return pd.read_excel(file)


def filtros(datos, col_preguntas):
	lista_filtros = []

	#col_preguntas = int(st.number_input('Ingrese un número', 1,50,5))
	lista_preguntas = list(datos.iloc[:,col_preguntas:].columns)
	lista_agrupadores = list(datos.iloc[:,1:col_preguntas].columns)

	pregunta = st.selectbox("Seleccione la pregunta: ", lista_preguntas)
	lista_filtros.append(st.selectbox("Seleccione el eje x", ["Pregunta"] +lista_agrupadores))
	lista_filtros.append(st.selectbox("Dividir por color", [" ", "Pregunta"] +lista_agrupadores))
	lista_filtros.append(st.selectbox("Dividir por columna", [" ", "Pregunta"] +lista_agrupadores))
	lista_filtros.append(st.selectbox("Dividir por fila",[" ", "Pregunta"] + lista_agrupadores))

	filtros_def = [None if x == ' ' else x for x in lista_filtros ]
	filtros_def = [pregunta if x == "Pregunta" else x for x in filtros_def ]
	indices = list(set(filtros_def).difference([None]))

	return pregunta, filtros_def, indices, lista_agrupadores

def pivot_data(datos, indices, columna_unica):
	return datos.pivot_table(index = indices,
							 values= columna_unica,
							 aggfunc="count").reset_index()

def relative_bar_chart(columna_total=None, columna_unica=None, pivot=None,
					   ejex=None, color=None, fila=None, columna=None, indices=None):
	if columna_total == "Total":
		total = pivot[columna_unica].sum()
		pivot['Frecuencia'] = pivot[columna_unica] / total
	else:
		total = pivot.pivot_table(index=columna_total,
								values=columna_unica, 
				 				aggfunc='sum').rename(columns={columna_unica:"TOTAL"}).reset_index()
	
		pivot = pivot.merge(total, on=columna_total)
		pivot['Frecuencia'] = pivot[columna_unica] / pivot["TOTAL"]
			
	fig = px.bar(pivot, x=ejex, 
				 y="Frecuencia", color=color,
				 facet_row=fila, facet_col=columna, barmode="group",
				 color_discrete_sequence=px.colors.qualitative.Pastel,
				 text="Frecuencia",
				 facet_col_wrap=4)
	fig.for_each_yaxis(lambda yaxis:  yaxis.update(tickformat = ',.0%'))
	#fig.layout.yaxis.tickformat = ',.0%'
	fig.update_traces(textposition='outside', texttemplate='%{text:,.2%}')
	return fig 

def absolute_bar_chart(columna_unica=None, pivot=None, ejex=None, color=None, fila=None, columna=None):
	fig = px.bar(pivot, x=ejex, y=columna_unica,
		   color=color, facet_row=fila, 
		   facet_col=columna, barmode="group", 
		   color_discrete_sequence=px.colors.qualitative.Pastel,
		   text=columna_unica,
		   facet_col_wrap=4)
	fig.update_traces(textposition='outside', texttemplate='%{text}')
	fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), 
					  template = "simple_white")
	return fig


def bar_chart(columna_unica=None, pivot=None, ejex=None, color=None, fila=None, columna=None, indices=None):
	st.write(columna_unica)
	if st.checkbox("Visualizar frecuencia relativa"):
		columna_total = st.selectbox("Relativo respecto a: ", ["Total"]+indices)
		fig = relative_bar_chart(columna_total=columna_total,
								 columna_unica=columna_unica,
								 pivot=pivot, ejex=ejex, color=color, 
								 fila=fila, columna=columna, indices=indices)
	else:
		fig = absolute_bar_chart(columna_unica=columna_unica,
								 pivot=pivot, ejex=ejex, color=color, 
								 fila=fila, columna=columna)
	return fig

def box_chart(columna_unica=None, pivot=None, ejex=None, color=None, fila=None, columna=None, indices=None):
	fig = px.box(pivot, x=ejex, y=columna_unica,
		   color=color, facet_row=fila, 
		   facet_col=columna,
		   color_discrete_sequence=px.colors.qualitative.Pastel,
		   facet_col_wrap=4)
	return fig

def main():
	st.write("""# Visualizaciones""")

	#file = st.file_uploader('File uploader')
	file = "Datos_seguimiento_semanal_MinTIC.xlsx"
	columna_unica = 'ID de respuesta'
	col_preguntas = 7

	if file:
		datos = load_data(file)
		df = copy.deepcopy(datos)

		chart_type = st.radio("Tipo de visualización ",
							 ("Barras", "Dispersión", "Cajas"))

		pregunta, filtros_def, indices, lista_agrupadores = filtros(df, col_preguntas)
		ejex, color, columna, fila = filtros_def
		height = st.slider("Ajuste el tamaño vertical de la gráfica", 500,1000)
		
		df[pregunta] = df[pregunta].astype(str)
		pivot = pivot_data(df, indices, columna_unica)

		
		if chart_type == "Barras":
			fig = bar_chart(columna_unica=columna_unica,
							pivot=pivot, ejex=ejex, color=color, 
							fila=fila, columna=columna, indices=indices)
		elif chart_type == "Cajas":
			fig = box_chart(columna_unica=pregunta,
							pivot=df, ejex=ejex, color=color, 
							fila=fila, columna=columna, indices=indices)
			fig.update_yaxes(col=1, title=None)


		fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
		fig.update_layout(height=height)

		st.plotly_chart(fig, use_container_width = True, config= config)

if __name__=="__main__":
	main()