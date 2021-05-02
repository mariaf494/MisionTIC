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


def load_data(file):
    return pd.read_excel(file)


def filtros_generales(pregunta, datos, col_preguntas):
    lista_filtros = []
    lista_agrupadores = list(datos.iloc[:, 1:col_preguntas].columns)
    lista_grupos = datos.Grupo.unique()
    grupo = st.multiselect("Seleccione el grupo: ",  lista_grupos)

    lista_filtros.append(st.selectbox("Seleccione el eje x",
                                      ["Pregunta"] + lista_agrupadores))
    lista_filtros.append(st.selectbox("Dividir por color", [
        " ", "Pregunta"] + lista_agrupadores))
    lista_filtros.append(st.selectbox("Dividir por columna", [
        " ", "Pregunta"] + lista_agrupadores))
    lista_filtros.append(st.selectbox("Dividir por fila", [
        " ", "Pregunta"] + lista_agrupadores))

    filtros_def = [None if x == ' ' else x for x in lista_filtros]
    filtros_def = [pregunta if x == "Pregunta" else x for x in filtros_def]
    indices = list(set(filtros_def).difference([None]))
    return filtros_def, indices, lista_agrupadores, grupo


def filtros_encuesta(datos, col_preguntas):

    # col_preguntas = int(st.number_input('Ingrese un número', 1,50,5))
    lista_filtros = []
    lista_preguntas = list(datos.iloc[:, col_preguntas:].columns)
    pregunta = st.selectbox("Seleccione la pregunta: ", lista_preguntas)
    lista_agrupadores = list(datos.iloc[:, 1:col_preguntas].columns)
    lista_grupos = datos.Grupo.unique()
    grupo = st.multiselect("Seleccione el grupo: ",  lista_grupos)

    lista_filtros.append(st.selectbox("Seleccione el eje x",
                                      ["Pregunta"] + lista_agrupadores))
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


def filtros_habilidades(datos, col_preguntas, grafica):
    # col_preguntas = int(st.number_input('Ingrese un número', 1,50,5))
    lista_filtros = []
    lista_preguntas = list(datos.iloc[:, col_preguntas:].columns)
    pregunta = st.selectbox("Seleccione la dimensión: ", lista_preguntas)
    lista_agrupadores = list(datos.iloc[:, 1:col_preguntas].columns)
    lista_grupos = datos.Grupo.unique()
    grupo = st.multiselect("Seleccione el grupo: ",  lista_grupos)

    if grafica == 'Barras':
        lista_filtros.append(st.selectbox("Seleccione el eje y",
                                          ["Dimensión"] + lista_agrupadores))
    lista_filtros.append(st.selectbox("Seleccione el eje x",
                                      ["Dimensión"] + lista_agrupadores))
    lista_filtros.append(st.selectbox("Dividir por color", [
        " ", "Dimensión"] + lista_agrupadores))
    lista_filtros.append(st.selectbox("Dividir por columna", [
        " ", "Dimensión"] + lista_agrupadores))
    lista_filtros.append(st.selectbox("Dividir por fila", [
        " ", "Dimensión"] + lista_agrupadores))

    filtros_def = [None if x == ' ' else x for x in lista_filtros]
    filtros_def = [pregunta if x == "Dimensión" else x for x in filtros_def]
    indices = list(set(filtros_def).difference([None]))
    return pregunta, filtros_def, indices, lista_agrupadores, grupo


def pivot_data(datos, indices, columna_unica):
    return datos.pivot_table(index=indices, values=columna_unica, aggfunc="count").reset_index()


def relative_bar_chart(columna_total=None, columna_unica=None, pivot=None, ejex=None, color=None, fila=None, columna=None, indices=None, category_orders=None):
    if columna_total == "Total":
        total = pivot[columna_unica].sum()
        pivot['Frecuencia'] = pivot[columna_unica] / total
    else:
        total = pivot.pivot_table(index=columna_total, values=columna_unica, aggfunc='sum').rename(
            columns={columna_unica: "TOTAL"}).reset_index()
        pivot = pivot.merge(total, on=columna_total)
        pivot['Frecuencia'] = pivot[columna_unica] / pivot["TOTAL"]
    fig = px.bar(pivot, x=ejex, y="Frecuencia", color=color, facet_row=fila, facet_col=columna, barmode="group",
                 color_discrete_sequence=px.colors.qualitative.Pastel, text="Frecuencia", facet_col_wrap=4, category_orders=category_orders, range_y=(0, 1))
    fig.for_each_yaxis(lambda yaxis:  yaxis.update(tickformat=',.0%'))
    # fig.layout.yaxis.tickformat = ',.0%'
    fig.update_traces(textposition='outside', texttemplate='%{text:,.2%}')
    return fig


def absolute_bar_chart(columna_unica=None, pivot=None, ejex=None, color=None, fila=None, columna=None, category_orders=None, indices=None):
    fig = px.bar(pivot, x=ejex, y=columna_unica, color=color, facet_row=fila, facet_col=columna, barmode="group",
                 color_discrete_sequence=px.colors.qualitative.Pastel, text=columna_unica, facet_col_wrap=4, category_orders=category_orders)
    fig.update_traces(textposition='outside', texttemplate='%{text}')
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom",
                                  y=1.02, xanchor="right", x=1), template="simple_white")
    return fig


def bar_chart(**kwargs):
    # st.write(kwargs['columna_unica'])
    if st.checkbox("Visualizar frecuencia relativa"):
        columna_total = st.selectbox("Relativo respecto a: ", [
                                     "Total"]+kwargs["indices"])
        kwargs["columna_total"] = columna_total
        fig = relative_bar_chart(**kwargs)
    else:
        fig = absolute_bar_chart(**kwargs)
    return fig


def relative_hist_chart(columna_total=None, columna_unica=None, pivot=None, ejex=None, color=None, fila=None, columna=None, indices=None, category_orders=None):
    if columna_total == "Total":
        total = pivot[columna_unica].sum()
        pivot['Frecuencia'] = pivot[columna_unica] / total
    else:
        total = pivot.pivot_table(index=columna_total, values=columna_unica, aggfunc='sum').rename(
            columns={columna_unica: "TOTAL"}).reset_index()
        pivot = pivot.merge(total, on=columna_total)
        pivot['Frecuencia'] = pivot[columna_unica] / pivot["TOTAL"]
    fig = px.histogram(pivot, x=ejex, y="Frecuencia", color=color, facet_row=fila, facet_col=columna, barmode="group", cumulative=False,
                       color_discrete_sequence=px.colors.qualitative.Set2, facet_col_wrap=4, category_orders=category_orders, nbins=30, range_y=(0, 1))
    fig.for_each_yaxis(lambda yaxis:  yaxis.update(tickformat=',.0%'))
    fig.layout.yaxis.tickformat = ',.0%'
	#fig.update_traces(textposition='outside', texttemplate='%{text:,.2%}')
    return fig


def absolute_hist_chart(columna_unica=None, pivot=None, ejex=None, color=None, fila=None, columna=None, category_orders=None, indices=None):

    #tipo = st.radio("", ["group"])
    fig = px.histogram(pivot, x=ejex, color=color, facet_row=fila, facet_col=columna,  barmode="group", cumulative=False,
                       color_discrete_sequence=px.colors.qualitative.Set2, facet_col_wrap=4, category_orders=category_orders, nbins=30)

    fig.update_layout(legend=dict(orientation="h", yanchor="bottom",
                                  y=1.02, xanchor="right", x=1), template="simple_white")
    # fig.update_traces(overwrite=True, marker={"opacity": 0.5})
    return fig


def hist_chart(**kwargs):
    # st.write(kwargs['columna_unica'])
    if st.checkbox("Visualizar frecuencia relativa"):
        columna_total = st.selectbox("Relativo respecto a: ", [
                                     "Total"]+kwargs["indices"])
        kwargs["columna_total"] = columna_total
        fig = relative_hist_chart(**kwargs)
        fig.update_yaxes(col=1, title=None)
    else:
        fig = absolute_hist_chart(**kwargs)
        fig.update_yaxes(col=1, title=None)
    return fig


def box_chart(columna_unica=None, pivot=None, ejex=None, color=None, fila=None, columna=None, indices=None):
    fig = px.box(pivot, x=ejex, y=columna_unica, color=color, facet_row=fila, facet_col=columna,
                 color_discrete_sequence=px.colors.qualitative.Pastel, facet_col_wrap=4)
    return fig


def write_init():
    # Used to write the page in the app.py file
    with st.spinner("Cargando Home ..."):
        st.write('# Visualización de datos - MINTIC')
        st.write(
            """
    # Visualizaciones interactivas.

    Esta página contiene visualizaciones interactivas del proceso de seguimiento semanal a los estudiantes que están participando del proyecto Misión TIC 2022 y reciben su formación en la Universidad del Norte.

    """
        )
        image = Image.open('Pagina_Interna.jpg')

        st.image(image, caption='')


def main():
    columna_unica = 'ID de respuesta'
    col_preguntas = 4

    st.sidebar.title("Misión TIC")
    pag = st.sidebar.radio(
        "Página: ", ["Inicio", "Encuesta", "Habilidades en programación"])
    if pag == "Encuesta":
        file = "Ciclo1_semana1_plataforma.xlsx"
        st.write("""# Visualizaciones""")
        if file:
            datos = load_data(file)
            df = copy.deepcopy(datos)
            chart_type = st.radio(
                "Tipo de visualización ", ("Barras", "Cajas"))
            pregunta, filtros_def, indices, lista_agrupadores, grupo = filtros_encuesta(
                df, col_preguntas)
            ejex, color, columna, fila = filtros_def
            height = st.slider(
                "Ajuste el tamaño vertical de la gráfica", 500, 1000)

            # YA TENEMOS QUE MODIFICAR LOS ORDENES AQUÍ
            satisfaction = ["Nada satisfecho", "Un poco satisfecho", "Neutra",
                            "Muy satisfecho", "Totalmente satisfecho", "No puedo asistir"]
            yes_no = ["Sí", "No"]
            dificultad = ["No responde", "Muy bajo",
                          "Bajo", "Intermedio", "Alto", "Muy alto"]
            dudas = ["Sobre la metodología", "Compresión de las temáticas",
                     "Asociado a los retos", "Instrucciones recibidas"]
            dificultad = ["Muy bajo", "Bajo", "Intermedio", "Alto", "Muy alto"]
            dudas = ["Sobre la metodología ", "Compresión de las temáticas",
                     "Asociado a los retos", "Instrucciones recibidas"]
            tema = ["Manejo del tiempo", "Plan de vida", "Manejo del estrés y la ansiedad",
                    "Estrategias para trabajar en grupo", "Establecimiento y cumplimiento de objetivos"]
            tiempo = ["1 hora", "2 horas", "3 horas",
                      "4 horas", "5 horas", "Más de 5 horas"]

            df[pregunta] = df[pregunta].astype(str)

            answers = set(df[pregunta])

            if len(set(satisfaction).intersection(answers)) >= len(answers):
                cat_order = satisfaction
            elif len(set(yes_no).intersection(answers)) >= len(answers):
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

            category_orders = {pregunta: cat_order, "GENERO": ["F", "M" , "Nb", "Otros"]}

            if grupo != []:
                df = df.loc[df.Grupo.isin(grupo)]

            pivot = pivot_data(df, indices, columna_unica)

            if chart_type == "Barras":
                argumentos = {"columna_unica": columna_unica, "pivot": pivot, "ejex": ejex, "color": color,
                              "fila": fila, "columna": columna, "indices": indices, "category_orders": category_orders}
                fig = bar_chart(**argumentos)

            elif chart_type == "Cajas":
                fig = box_chart(columna_unica=pregunta, pivot=df, ejex=ejex,
                                color=color, fila=fila, columna=columna, indices=indices)
                fig.update_yaxes(col=1, title=None)

            fig.for_each_annotation(
                lambda a: a.update(text=a.text.split("=")[-1]))
            fig.update_layout(height=height)
            st.plotly_chart(fig, use_container_width=True, config=config)
    elif pag == "Habilidades en programación":
        file = "Datos_nuevos_prueba1.xlsx"
        st.write("""# Visualizaciones""")
        if file:
            fig = None
            datos = load_data(file)
            df = copy.deepcopy(datos)
            chart_type = st.radio(
                "Tipo de visualización ", ("Histograma", "Cajas"))
            pregunta, filtros_def, indices, lista_agrupadores, grupo = filtros_habilidades(
                df, col_preguntas, chart_type)
            if chart_type == 'Barras':
                ejey, ejex, color, columna, fila = filtros_def
            else:
                ejex, color, columna, fila = filtros_def
            height = st.slider(
                "Ajuste el tamaño vertical de la gráfica", 500, 1000)

            # YA TENEMOS QUE MODIFICAR LOS ORDENES AQUÍ
            satisfaction = ["Nada satisfecho", "Un poco satisfecho", "Neutra",
                            "Muy satisfecho", "Totalmente satisfecho", "No puedo asistir/ No lo he usado"]
            yes_no = ["Sí", "No"]
            dificultad = ["No tuvo dificultades", "Muy bajo",
                          "Bajo", "Intermedio", "Alto", "Muy alto"]
            dudas = ["Sobre la metodología", "Compresión de las temáticas",
                     "Asociado a los retos", "Instrucciones recibidas" , "No tuvo dificultades"]
            dificultad = ["Muy bajo", "Bajo", "Intermedio", "Alto", "Muy alto"]
            dudas = ["Sobre la metodología ", "Compresión de las temáticas",
                     "Asociado a los retos", "Instrucciones recibidas"]
            tema = ["Manejo del tiempo", "Plan de vida", "Manejo del estrés y la ansiedad",
                    "Estrategias para trabajar en grupo", "Establecimiento y cumplimiento de objetivos"]
            tiempo = ["1 hora", "2 horas", "3 horas",
                      "4 horas", "5 horas", "Más de 5 horas"]

            df[pregunta] = df[pregunta].astype(float)

            answers = set(df[pregunta])

            if len(set(satisfaction).intersection(answers)) >= len(answers):
                cat_order = satisfaction
            elif len(set(yes_no).intersection(answers)) >= len(answers):
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

            category_orders = {pregunta: cat_order, "GENERO": ["F", "M"]}

            if grupo != []:
                df = df.loc[df.Grupo.isin(grupo)]

            pivot = pivot_data(df, indices, columna_unica)

            if chart_type == "Histograma":
                argumentos = {"columna_unica": columna_unica, "pivot": df, "ejex": ejex, "color": color,
                              "fila": fila, "columna": columna, "indices": indices, "category_orders": category_orders}
                fig = hist_chart(**argumentos)
            elif chart_type == "Cajas":
                if ejex == pregunta:
                    st.warning(
                        'Seleccione un eje X diferente para ver la grafica')
                else:
                    fig = box_chart(columna_unica=pregunta, pivot=df, ejex=ejex,
                                    color=color, fila=fila, columna=columna, indices=indices)
                    fig.update_yaxes(col=1, title=None)
            elif chart_type == "Barras":
                argumentos = {"ejey": ejey, "columna_unica": columna_unica, "pivot": pivot, "ejex": ejex, "color": color,
                              "fila": fila, "columna": columna, "indices": indices, "category_orders": category_orders}
                fig = bar_chart(**argumentos)

            elif chart_type == 'Dispersión':
                fig = px.scatter(
                    df, y=pregunta, x='Interes en la programación')
            if fig is not None:
                fig.for_each_annotation(
                    lambda a: a.update(text=a.text.split("=")[-1]))
                fig.update_layout(height=height)
                st.plotly_chart(fig, use_container_width=True, config=config)
                st.markdown("Nota: los puntajes obtenidos por los participantes en la evaluación de sus conocimientos en programación han sido estandarizados en una escala de puntuaciones de 0 a 100, donde la media de los datos es 50 y la desviación estándar es 10")
    else:
        write_init()


if __name__ == "__main__":
    main()
