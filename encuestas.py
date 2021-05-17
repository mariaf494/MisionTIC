import streamlit as st
import pandas as pd
import plotly.express as px
import copy
import numpy as np
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


def filtros_encuesta(datos, col_preguntas):

    # col_preguntas = int(st.number_input('Ingrese un número', 1,50,5))
    lista_filtros = []
    lista_preguntas = list(datos.iloc[:, col_preguntas:].columns)
    pregunta = st.selectbox("Seleccione la pregunta: ", lista_preguntas)
    lista_agrupadores = list(datos.iloc[:, 1:col_preguntas].columns)
    lista_grupos = datos.Grupo.unique()
    lista_grupos.sort()
    grupo = st.multiselect("Seleccione el grupo: ",  lista_grupos)
    lista_semanas = datos.Semana.unique()
    lista_semanas.sort()
    semanas = st.multiselect(
        "Seleccione la semana de interés: ",  lista_semanas)

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
    return pregunta, filtros_def, indices, grupo, semanas


def filtros_habilidades(datos, col_preguntas, grafica):
    # col_preguntas = int(st.number_input('Ingrese un número', 1,50,5))
    lista_filtros = []
    lista_preguntas = list(datos.iloc[:, col_preguntas:].columns)
    pregunta = st.selectbox("Seleccione la dimensión: ", lista_preguntas)
    lista_agrupadores = list(datos.iloc[:, 1:col_preguntas].columns)
    lista_grupos = datos.Grupo.unique()
    grupo = st.multiselect("Seleccione el grupo: ",  lista_grupos)

    if grafica == 'Histograma':
        lista_filtros.append(st.selectbox("Seleccione el eje x", [
                             "Dimensión"]))
    elif grafica == "Cajas" or grafica == "Barras":
        lista_filtros.append(st.selectbox(
            "Seleccione el eje x", lista_agrupadores))
    else:
        lista_filtros.append(st.selectbox("Seleccione el eje x", [
                             "Dimensión"] + lista_agrupadores))
    lista_filtros.append(st.selectbox("Dividir por color", [
        " "] + lista_agrupadores))
    lista_filtros.append(st.selectbox("Dividir por columna", [
        " "] + lista_agrupadores))
    lista_filtros.append(st.selectbox("Dividir por fila", [
        " "] + lista_agrupadores))

    filtros_def = [None if x == ' ' else x for x in lista_filtros]
    filtros_def = [pregunta if x == "Dimensión" else x for x in filtros_def]
    indices = list(set(filtros_def).difference([None]))
    return pregunta, filtros_def, indices, grupo


def filtros_docentes(datos, col_preguntas):
    # col_preguntas = int(st.number_input('Ingrese un número', 1,50,5))
    lista_filtros = []
    lista_preguntas = list(datos.iloc[:, col_preguntas:].columns)
    pregunta = st.selectbox("Seleccione la pregunta: ", lista_preguntas)
    lista_filtros.append(st.selectbox("Seleccione el eje x",
                                      ["Pregunta"]))
    lista_filtros.append(st.selectbox("Dividir por color", [
        " ", "Pregunta"]))
    lista_filtros.append(st.selectbox("Dividir por columna", [
        " ", "Pregunta"]))
    lista_filtros.append(st.selectbox("Dividir por fila", [
        " ", "Pregunta"]))

    filtros_def = [None if x == ' ' else x for x in lista_filtros]
    filtros_def = [pregunta if x == "Pregunta" else x for x in filtros_def]
    indices = list(set(filtros_def).difference([None]))
    return pregunta, filtros_def, indices


def pivot_data(datos, indices, columna_unica, aggfunc):
    return datos.pivot_table(index=indices, values=columna_unica, aggfunc=aggfunc).reset_index()


def relative_bar_chart(columna_total=None, columna_unica=None, pivot=None, ejex=None, color=None, fila=None, columna=None, indices=None, category_orders=None, range_y=None, range_x=None, label=""):
    if columna_total == "Total":
        total = pivot[columna_unica].sum()
        pivot['Frecuencia'] = pivot[columna_unica] / total
    else:
        total = pivot.pivot_table(index=columna_total, values=columna_unica, aggfunc='sum').rename(
            columns={columna_unica: "TOTAL"}).reset_index()
        pivot = pivot.merge(total, on=columna_total)
        pivot['Frecuencia'] = pivot[columna_unica] / pivot["TOTAL"]
    fig = px.bar(pivot, x=ejex, y="Frecuencia", color=color, facet_row=fila, facet_col=columna, barmode="group",
                 color_discrete_sequence=px.colors.qualitative.Pastel, text="Frecuencia", facet_col_wrap=4, category_orders=category_orders, range_y=range_y, labels={"Frecuenca": label})
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom",
                                  y=1.02, xanchor="right", x=1), xaxis={'type': 'category', 'range': range_x}, template="simple_white")
    return fig


def absolute_bar_chart(columna_unica=None, pivot=None, ejex=None, color=None, fila=None, columna=None, category_orders=None, indices=None, range_y=None, range_x=None, label=""):
    fig = px.bar(pivot, x=ejex, y=columna_unica, color=color, facet_row=fila, facet_col=columna, barmode="group",
                 color_discrete_sequence=px.colors.qualitative.Pastel, text=columna_unica, facet_col_wrap=4, category_orders=category_orders,
                 labels={columna_unica: label}, range_y=range_y, title=ejex)
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom",
                                  y=1.02, xanchor="right", x=1), xaxis={'type': 'category', 'range': range_x}, template="simple_white")
    return fig


def bar_chart(**kwargs):
    # st.write(kwargs['columna_unica'])
    if kwargs['relativo']:
        relativo_yesno = st.checkbox("Visualizar frecuencia relativa")
    else:
        relativo_yesno = False

    kwargs.pop('relativo')
    if relativo_yesno:
        columna_total = st.selectbox("Relativo respecto a: ", [
            "Total"]+kwargs["indices"])
        kwargs["columna_total"] = columna_total
        kwargs['range_y'] = (0, 1)
        kwargs['label'] = 'Frecuencia relativa'
        fig = relative_bar_chart(**kwargs)
        fig.for_each_yaxis(lambda yaxis:  yaxis.update(tickformat=',.0%'))
        fig.layout.yaxis.tickformat = ',.0%'
        fig.update_traces(textposition='outside', texttemplate='%{text:,.2%}')
    else:
        fig = absolute_bar_chart(**kwargs)
        fig.update_traces(textposition='outside',
                          texttemplate='%{text}')
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


def pag_encuestas(col_preguntas, columna_unica, file):
    st.write("""# Visualizaciones""")
    if file:
        datos = load_data(file)
        df = copy.deepcopy(datos)
        chart_type = st.radio(
            "Tipo de visualización ", ("Barras", "Cajas"))
        pregunta, filtros_def, indices, grupo, semana = filtros_encuesta(
            df, col_preguntas)
        ejex, color, columna, fila = filtros_def
        height = st.slider(
            "Ajuste el tamaño vertical de la gráfica", 500, 1000)

        # YA TENEMOS QUE MODIFICAR LOS ORDENES AQUÍ
        satisfaction = ["Nada satisfecho", "Poco satisfecho", "Neutra",
                        "Muy satisfecho", "Totalmente satisfecho", "No puedo asistir/ No lo he usado"]
        yes_no = ["Sí", "No"]
        dificultad = ["No tuvo dificultades", "Muy bajo",
                      "Bajo", "Intermedio", "Alto", "Muy alto"]
        dudas = ["No tuvo dificultades", "Sobre la metodología", "Comprensión de las temáticas",
                 "Asociado a los retos", "Instrucciones recibidas"]
        tema = ["Manejo del tiempo", "Plan de vida", "Manejo del estrés y la ansiedad",
                "Estrategias para trabajar en grupo", "Establecimiento y cumplimiento de objetivos"]
        tiempo = ["1 hora", "2 horas", "3 horas",
                  "4 horas", "5 horas", "Más de 5 horas"]
        semana = ["Ciclo1-Sem1", "Ciclo1-Sem2", "Ciclo1-Sem3", "Ciclo1-Sem4"]
        df[pregunta] = df[pregunta].astype(str)

        answers = set(df[pregunta])
        # st.write(answers)
        # st.write((set(dudas).intersection(answers)))

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

        category_orders = {pregunta: cat_order,
                           "GENERO": ["F", "M", "Nb", "Otro"], "Grupo": [str(x) for x in range(1, 92)], "Semana": ["Ciclo1-Sem1", "Ciclo1-Sem2", "Ciclo1-Sem3", "Ciclo1-Sem4"]}

        if semana != []:
            df = df.loc[df.Semana.isin(semana)]
        if grupo != []:
            df = df.loc[df.Grupo.isin(grupo)]
        df["Grupo"] = df["Grupo"].astype(str)
        if len(df) == 0:
            st.warning(
                "El / los grupos seleccionados no tienen datos para mostrar")
        elif (fila == "Grupo" or columna == "Grupo") and (len(df.Grupo.unique()) > 10):
            st.warning(
                "Por favor use los filtros para seleccionar menos grupos")
        else:
            if chart_type == "Barras":
                pivot = pivot_data(df, indices, columna_unica, 'count')
                argumentos = {"relativo": True, "columna_unica": columna_unica, "pivot": pivot, "ejex": ejex, "color": color,
                              "fila": fila, "columna": columna, "indices": indices, "category_orders": category_orders, "label": "Cuenta", "range_x": (-1, len(cat_order)+1)}
                fig = bar_chart(**argumentos)

            elif chart_type == "Cajas":
                fig = box_chart(columna_unica=pregunta, pivot=df, ejex=ejex,
                                color=color, fila=fila, columna=columna, indices=indices)
            fig.update_yaxes(col=1, title=None)
            fig.update_xaxes(row=1, title=None)

            fig.for_each_annotation(
                lambda a: a.update(text=a.text.split("=")[-1]))
            fig.update_layout(height=height)
            st.plotly_chart(fig, use_container_width=True, config=config)


def pag_habilidades(col_preguntas, columna_unica, file):

    st.write("""# Visualizaciones""")
    if file:
        fig = None
        datos = load_data(file)
        df = copy.deepcopy(datos)
        chart_type = st.radio(
            "Tipo de visualización ", ("Histograma", "Cajas", "Barras"))
        pregunta, filtros_def, indices, grupo = filtros_habilidades(
            df, col_preguntas, chart_type)

        ejex, color, columna, fila = filtros_def

        height = st.slider(
            "Ajuste el tamaño vertical de la gráfica", 500, 1000)

        df[pregunta] = df[pregunta].astype(float)

        category_orders = {"GENERO": ["F", "M", "Nb", "Otros"]}

        if grupo != []:
            df = df.loc[df.Grupo.isin(grupo)]
        df["Grupo"] = df["Grupo"].astype(str)
        if len(df) == 0:
            st.warning(
                "El / los grupos seleccionados no tienen datos para mostrar")
        elif (fila == "Grupo" or columna == "Grupo") and (len(df.Grupo.unique()) > 10):
            st.warning(
                "Por favor use los filtros para seleccionar menos grupos")
        else:
            if chart_type == "Histograma":
                counts, bin_edges = np.histogram(
                    df[pregunta], bins=30, density=False)
                hist_df = pd.DataFrame(
                    {"Puntaje en "+pregunta: bin_edges[:-1], "Cuenta": counts})
                histogram_df = pd.merge_asof(df.sort_values(
                    pregunta), hist_df, left_on=pregunta, right_on="Puntaje en "+pregunta)
                indices.remove(pregunta)
                indices.append("Puntaje en "+pregunta)
                pivot = pivot_data(histogram_df, indices,
                                   columna_unica, "count")
                argumentos = {"relativo": True, "columna_unica": columna_unica, "pivot": pivot, "ejex": "Puntaje en "+pregunta, "color": color,
                              "fila": fila, "columna": columna, "indices": indices, "category_orders": category_orders, "label": "Cuenta"}
                fig = bar_chart(**argumentos)
            elif chart_type == "Cajas":
                fig = box_chart(columna_unica=pregunta, pivot=df, ejex=ejex,
                                color=color, fila=fila, columna=columna, indices=indices)
                fig.update_yaxes(col=1, title=None)
            elif chart_type == "Barras":
                pivot = pivot_data(df, indices, pregunta, "mean")
                argumentos = {"relativo": False, "columna_unica": pregunta, "pivot": pivot, "ejex": ejex, "color": color,
                              "fila": fila, "columna": columna, "indices": indices, "category_orders": category_orders, "range_y": (0, 100), "label": "Puntaje promedio"}
                fig = bar_chart(**argumentos)
                # fig.layout.yaxis.tickformat = ',.0%'
                fig.update_traces(textposition='outside',
                                  texttemplate='%{text:.2f}')

            elif chart_type == 'Dispersión':
                fig = px.scatter(
                    df, y=pregunta, x='Interes en la programación')
            if fig is not None:
                # fig.update_yaxes(col=1, title=None)
                fig.update_xaxes(row=1, title=None)
                fig.for_each_annotation(
                    lambda a: a.update(text=a.text.split("=")[-1]))
                fig.update_layout(height=height)
                st.plotly_chart(fig, use_container_width=True, config=config)
                st.markdown("Nota: los puntajes obtenidos por los participantes en la evaluación de sus conocimientos en programación han sido estandarizados en una escala de puntuaciones de 0 a 100, donde la media de los datos es 50 y la desviación estándar es 10")


def pag_docentes(col_preguntas, columna_unica, file):
    st.write("""# Visualizaciones Interactivas""")
    if file:
        datos = load_data(file)
        df = copy.deepcopy(datos)
        chart_type = st.radio(
            "Tipo de visualización ", ("Barras", "Cajas"))
        pregunta, filtros_def, indices = filtros_docentes(
            df, col_preguntas)
        ejex, color, columna, fila = filtros_def
        height_d = st.slider(
            "Ajuste el tamaño vertical de la gráfica", 500, 1000)

        Si_No = ["Sí", "No"]
        Num = [str(x) for x in range(1, 11)]
        try:
            df[pregunta] = df[pregunta].fillna(
                '0').astype(int).astype(str).replace("0", "")
        except:
            df[pregunta] = df[pregunta].astype(str)

        answers = set(df[pregunta])

        if len(set(Si_No).intersection(answers)) >= len(answers):
            cat_order = Si_No
        elif len(set(Num).intersection(answers)) >= 2:
            cat_order = Num
        else:
            cat_order = list(answers)

        category_orders = {pregunta: cat_order,
                           "GENERO": ["F", "M", "Nb", "Otro"], "Grupo": [str(x) for x in range(1, 92)]}

        if chart_type == "Barras":
            pivot = pivot_data(df, indices, columna_unica, 'count')

            #st.write("holi", len(cat_order))
            argumentos = {"relativo": True, "columna_unica": columna_unica, "pivot": pivot, "ejex": ejex, "color": color,
                          "fila": fila, "columna": columna, "indices": indices, "category_orders": category_orders, "label": "Cuenta", "range_x": (-1, len(cat_order)+1)}
            fig = bar_chart(**argumentos)

        elif chart_type == "Cajas":
            fig = box_chart(columna_unica=pregunta, pivot=df, ejex=ejex,
                            color=color, fila=fila, columna=columna, indices=indices)
            fig.update_yaxes(col=1, title=None)
            fig.update_xaxes(row=1, title=None)

        fig.for_each_annotation(
            lambda a: a.update(text=a.text.split("=")[-1]))
        fig.update_layout(height=height_d)
        st.plotly_chart(fig, use_container_width=True, config=config)


def main():
    columna_unica = 'ID de respuesta'

    st.sidebar.title("Misión TIC")
    pag = st.sidebar.radio(
        "Página: ", ["Inicio", "Encuesta estudiantes", "Encuesta docentes", "Habilidades en programación"])
    if pag == "Encuesta estudiantes":
        pag_encuestas(4, columna_unica, "Misión_TIC_3.xlsx")

    elif pag == "Encuesta docentes":
        pag_docentes(2, columna_unica, "Docentes_sem1.xlsx")

    elif pag == "Habilidades en programación":
        pag_habilidades(3, columna_unica,
                        "Datos_Pre_Misión_TIC.xlsx")

    else:
        write_init()


if __name__ == "__main__":
    main()
