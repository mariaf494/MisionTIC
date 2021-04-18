import streamlit as st
import pandas as pd
import plotly.express as px
import copy
from PIL import Image


st.set_page_config(layout="wide")

config = {'scrollZoom': True, 'displaylogo': False, 'responsive': True,
          'editable': True,
          'toImageButtonOptions': {
              'format': 'png',  # one of png, svg, jpeg, webp
              'filename': 'custom_image',
              'height': None,
              'width': None,
              'scale': 3  # Multiply title/legend/axis/canvas sizes by this factor
          }}


@st.cache
def load_data(file):
    return pd.read_excel(file)


def filtros(datos, col_preguntas):
    lista_filtros = []

    # col_preguntas = int(st.number_input('Ingrese un número', 1,50,5))
    lista_preguntas = list(datos.iloc[:, col_preguntas:].columns)
    lista_agrupadores = list(datos.iloc[:, 1:col_preguntas].columns)
    lista_grupos = datos.Grupo.unique()

    pregunta = st.selectbox("Seleccione la pregunta: ", lista_preguntas)
    grupo = st.multiselect("Seleccione el grupo: ",  lista_grupos)

    lista_filtros.append(st.selectbox("Seleccione el eje x", [
                         "Pregunta"] + lista_agrupadores))
    lista_filtros.append(st.selectbox("Dividir por color", [
                         " ", "Pregunta"] + lista_agrupadores))
    lista_filtros.append(st.selectbox("Dividir por columna", [
                         " ", "Pregunta"] + lista_agrupadores))
    lista_filtros.append(st.selectbox("Dividir por fila", [
                         " ", "Pregunta"] + lista_agrupadores))

    filtros_def = [None if x == ' ' else x for x in lista_filtros]
    filtros_def = [pregunta if x == "Pregunta" else x for x in filtros_def]
    indices = list(set(filtros_def).difference([None]))

    return pregunta, filtros_def, indices, lista_agrupadores, grupo


def pivot_data(datos, indices, columna_unica):
    return datos.pivot_table(index=indices,
                             values=columna_unica,
                             aggfunc="count").reset_index()


def relative_bar_chart(columna_total=None, columna_unica=None, pivot=None,
                       ejex=None, color=None, fila=None, columna=None, indices=None, category_orders=None):
    if columna_total == "Total":
        total = pivot[columna_unica].sum()
        pivot['Frecuencia'] = pivot[columna_unica] / total
    else:
        total = pivot.pivot_table(index=columna_total,
                                  values=columna_unica,
                                  aggfunc='sum').rename(columns={columna_unica: "TOTAL"}).reset_index()

        pivot = pivot.merge(total, on=columna_total)
        pivot['Frecuencia'] = pivot[columna_unica] / pivot["TOTAL"]

    fig = px.bar(pivot, x=ejex,
                 y="Frecuencia", color=color,
                 facet_row=fila, facet_col=columna, barmode="group",
                 color_discrete_sequence=px.colors.qualitative.Pastel,
                 text="Frecuencia",
                 facet_col_wrap=4,
                 category_orders=category_orders)
    fig.for_each_yaxis(lambda yaxis:  yaxis.update(tickformat=',.0%'))
    # fig.layout.yaxis.tickformat = ',.0%'
    fig.update_traces(textposition='outside', texttemplate='%{text:,.2%}')
    return fig


def absolute_bar_chart(columna_unica=None, pivot=None, ejex=None, color=None, fila=None, columna=None, category_orders=None, indices=None):
    fig = px.bar(pivot, x=ejex, y=columna_unica,
                 color=color, facet_row=fila,
                 facet_col=columna, barmode="group",
                 color_discrete_sequence=px.colors.qualitative.Pastel,
                 text=columna_unica,
                 facet_col_wrap=4,
                 category_orders=category_orders
                 )
    fig.update_traces(textposition='outside', texttemplate='%{text}')
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                      template="simple_white")
    return fig


def bar_chart(**kwargs):
    #st.write(kwargs['columna_unica'])
    if st.checkbox("Visualizar frecuencia relativa"):
        columna_total = st.selectbox(
            "Relativo respecto a: ", ["Total"]+kwargs["indices"])
        kwargs["columna_total"] = columna_total
        fig = relative_bar_chart(**kwargs)
    else:
        fig = absolute_bar_chart(**kwargs)
    return fig


def box_chart(columna_unica=None, pivot=None, ejex=None, color=None, fila=None, columna=None, indices=None):
    fig = px.box(pivot, x=ejex, y=columna_unica,
                 color=color, facet_row=fila,
                 facet_col=columna,
                 color_discrete_sequence=px.colors.qualitative.Pastel,
                 facet_col_wrap=4)
    return fig


def write_init():
    """Used to write the page in the app.py file"""
    with st.spinner("Cargando Home ..."):
        st.write('# Visualización de datos - MINTIC')
        st.write(
            """
            ## Visualizaciones interactivas. 

            Esta página contiene visualizaciones interactivas del proceso de seguimiento semanal a los estudiantes que están participando del proyecto Misión TIC 2022 y reciben su formación en la Universidad del Norte.

            """
        )
        image = Image.open('Pagina_Interna.jpg')

        st.image(image, caption='')

def main():
    

    # file = st.file_uploader('File uploader')

    file = "Misión_TIC_prueba.xlsx"
    columna_unica = 'ID de respuesta'
    col_preguntas = 4

    st.sidebar.title("Misión TIC")
    pag = st.sidebar.radio("Página: ", ["Inicio", "Encuestas"])

    if pag == "Encuestas":
        st.write("""# Visualizaciones""")
        if file:
            datos = load_data(file)
            df = copy.deepcopy(datos)
            chart_type = st.radio("Tipo de visualización ",
                                  ("Barras", "Cajas"))
            pregunta, filtros_def, indices, lista_agrupadores, grupo = filtros(
                df, col_preguntas)
        ejex, color, columna, fila = filtros_def
        height = st.slider("Ajuste el tamaño vertical de la gráfica", 500, 1000)

        ## YA TENEMOS QUE MODIFICAR LOS ORDENES AQUÍ
        satisfaction = ["Nada satisfecho", "Un poco satisfecho", "Neutra", "Muy satisfecho", "Totalmente satisfecho", "No puedo asistir"]
        yes_no = ["Sí", "No"]
        dificultad = ["Muy bajo", "Bajo", "Intermedio", "Alto", "Muy alto"]
        dudas = ["Sobre la metodología " , "Compresión de las temáticas", "Asociado a los retos", "Instrucciones recibidas"]
        tema = ["Manejo del tiempo" , "Plan de vida" , "Manejo del estrés y la ansiedad", "Estrategias para trabajar en grupo", "Establecimiento y cumplimiento de objetivos"]
        tiempo = ["1 hora" , "2 horas" , "3 horas", "4 horas", "5 horas", "Más de 5 horas"]

        df[pregunta] = df[pregunta].astype(str)

        answers = set(df[pregunta])

        if len(set(satisfaction).intersection(answers)) >= len(answers):
        	cat_order = satisfaction
        elif  len(set(yes_no).intersection(answers)) >= len(answers):
        	cat_order = yes_no
        elif len(set(dificultad).intersection(answers)) >= len(answers):
        	cat_order = dificultad
        elif len(set(dudas).intersection(answers)) >= len(answers):
        	cat_order = dudas
        elif len(set(tema).intersection(answers)) >= len(answers):
          cat_order = tema
        elif len(set(tiempo).intersection(answers)) >= len(answers):
          cat_order = tiempo
        else:
          cat_order = list(answers)

        category_orders = {pregunta: cat_order,
                           "GENERO": ["F", "M"]}

        if grupo != []:
          df = df.loc[df.Grupo.isin(grupo)]

        pivot = pivot_data(df, indices, columna_unica)

        if chart_type == "Barras":
          argumentos = {"columna_unica":columna_unica,
                        "pivot":pivot, "ejex":ejex, "color":color,
                        "fila":fila, "columna":columna, "indices":indices,
                        "category_orders":category_orders}
          fig = bar_chart(**argumentos)

        elif chart_type == "Cajas":
          fig = box_chart(columna_unica=pregunta,
                          pivot=df, ejex=ejex, color=color,
                          fila=fila, columna=columna, indices=indices)
          fig.update_yaxes(col=1, title=None)

        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig.update_layout(height=height)
        st.plotly_chart(fig, use_container_width=True, config=config)

    else:
      write_init()

if __name__ == "__main__":
    main()
