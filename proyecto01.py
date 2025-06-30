import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

st.set_page_config(layout="wide", page_title="Análisis de ANP Perú")

@st.cache_data
def load_data(file_path='anp_datos.csv'):
    try:
        df = pd.read_csv(file_path, sep=';')
        return df.iloc[0:94, :]
    except FileNotFoundError:
        st.error(f"Error: El archivo '{file_path}' no se encuentra. Asegúrate de que esté en el mismo directorio que tu script de Streamlit.")
        st.stop()
    except Exception as e:
        st.error(f"Error al cargar o procesar el archivo '{file_path}': {e}")
        st.stop()

df = load_data()

st.sidebar.title("Menú")
menu_selection = st.sidebar.radio(
    "Selecciona una sección:",
    [
        "Inicio",
        "% ANP por Departamento",
        "Cantidad de ANP por Departamento",
        "Contribución ANP",
        "Superficie ANP por Tipo",
        "Desempeño Departamental",
        "ANP por Tipo"
    ]
)

if menu_selection == "Inicio":
    st.title('Análisis de las Áreas Naturales Protegidas en el Perú')
    st.write('**Flavio Rabanal, Tomás del Castillo**')
    st.write('**Programación Avanzada 2025-I**')
    st.write('Este proyecto presenta un análisis cuantitativo de las Áreas Naturales Protegidas (ANP) en el Perú, desagregadas a nivel departamental. Utilizando una base de datos oficial del Servicio Nacional de Áreas Naturales Protegidas por el Estado (SERNANP), se construyeron tablas que permiten comparar la distribución espacial, la superficie protegida y la contribución de cada departamento tanto a nivel regional como nacional.')
    st.write('**Objetivo:**')
    st.write('Ofrecer una herramienta visual e informativa que facilite la comprensión de la cobertura actual de ANP, identifique patrones geográficos y resalte las brechas existentes en la protección ambiental del país.')
    st.image("https://www.peru.travel/Contenido/General/Imagen/es/152/1.1/Huascaran.jpg", use_container_width=True)


elif menu_selection == "% ANP por Departamento":
    st.header("Porcentaje de ANP por Departamento")
    st.write('Muestra el porcentaje del territorio departamental que está cubierto por Áreas Naturales Protegidas, lo que permite comparar la proporción de territorio protegido en cada región.')
    
    df_anp_area = df[["ANP_CATE", "ANP_NOMB", "DEPARTAMENTO1", "ANP_SULEG"]]
    df_anp_area_total = df_anp_area.groupby("DEPARTAMENTO1").sum()["ANP_SULEG"].sort_values().reset_index()
    
    df_anp_area_total["area_total_dep"] = [1570000, 466920, 4381480, 1423130, 7199900, 2549990, 3331754, 3589249, 4419723, 466920, 3924913, 3480159, 2531959, 3591481, 2132783, 3684885, 2089579, 7198650, 10241055, 5125331, 36885195, 8530054]
    
    df_anp_area_total["porcentaje_anp"] = (df_anp_area_total["ANP_SULEG"] / df_anp_area_total["area_total_dep"]) * 100
    st.dataframe(df_anp_area_total, use_container_width=True)

    fig01, ax01 = plt.subplots(figsize=(12, 6))
    ax01.bar(df_anp_area_total["DEPARTAMENTO1"], df_anp_area_total["porcentaje_anp"], color='skyblue')
    ax01.set_xlabel("Departamento")
    ax01.set_ylabel("Porcentaje de ANP (%)")
    ax01.set_title("Porcentaje de Área Natural Protegida (ANP) por Departamento")
    plt.xticks(rotation=90)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig01)
    plt.close(fig01)


elif menu_selection == "Cantidad de ANP por Departamento":
    st.header("Cantidad de ANP por Departamento")
    st.write('Presenta el número total de ANP registradas en cada departamento, ordenadas de mayor a menor. Sirve para observar dónde hay más diversidad de zonas protegidas.')
    
    df_anp_departamento = df[["ANP_NOMB", "DEPARTAMENTO1"]]
    df_num_anp_por_departamento = df_anp_departamento.groupby("DEPARTAMENTO1")["ANP_NOMB"].nunique().reset_index()
    df_num_anp_por_departamento.rename(columns={"ANP_NOMB": "Número de ANP"}, inplace=True)
    df_num_anp_por_departamento = df_num_anp_por_departamento.sort_values(by="Número de ANP", ascending=False)
    
    st.dataframe(df_num_anp_por_departamento.style.format({"Número de ANP": "{:.0f}"}), use_container_width=True)

    fig02, ax02 = plt.subplots(figsize=(12, 7))
    ax02.bar(df_num_anp_por_departamento["DEPARTAMENTO1"], df_num_anp_por_departamento["Número de ANP"], color='lightgreen')
    ax02.set_xlabel("Departamento", fontsize=12)
    ax02.set_ylabel("Número de Áreas Naturales Protegidas (ANP)", fontsize=12)
    ax02.set_title("Número Absoluto de ANP por Departamento", fontsize=14)
    plt.xticks(rotation=90, ha='right', fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig02)
    plt.close(fig02)


elif menu_selection == "Contribución ANP":
    st.header("Contribución Departamental y Nacional de cada ANP")
    st.write('Detalla cuánto aporta cada ANP a la superficie protegida de su propio departamento y al total nacional, resaltando la importancia relativa de cada área.')
    
    df_anp_contribucion = df[["ANP_NOMB", "DEPARTAMENTO1", "ANP_SULEG"]].copy()
    area_total_nacional_anp = df_anp_contribucion["ANP_SULEG"].sum()
    df_area_total_por_departamento = df_anp_contribucion.groupby("DEPARTAMENTO1")["ANP_SULEG"].sum().reset_index()
    df_area_total_por_departamento.rename(columns={"ANP_SULEG": "Area_Total_ANP_Departamento"}, inplace=True)

    df_anp_contribucion = pd.merge(df_anp_contribucion, df_area_total_por_departamento, on="DEPARTAMENTO1", how="left")

    df_anp_contribucion["Contribución Departamental (%)"] = (df_anp_contribucion["ANP_SULEG"] / df_anp_contribucion["Area_Total_ANP_Departamento"]) * 100
    df_anp_contribucion["Contribución Nacional (%)"] = (df_anp_contribucion["ANP_SULEG"] / area_total_nacional_anp) * 100

    df_resultado_contribucion = df_anp_contribucion[[
        "DEPARTAMENTO1",
        "ANP_NOMB",
        "ANP_SULEG",
        "Contribución Departamental (%)",
        "Contribución Nacional (%)"
    ]].sort_values(by=["DEPARTAMENTO1", "Contribución Departamental (%)"], ascending=[True, False])

    st.dataframe(df_resultado_contribucion.style.format({
        "ANP_SULEG": "{:,.2f} ha",
        "Contribución Departamental (%)": "{:.2f}%",
        "Contribución Nacional (%)": "{:.2f}%"
    }), use_container_width=True)


    df_anp_contribucion_sorted = df_anp_contribucion.sort_values(by=["DEPARTAMENTO1", "Contribución Departamental (%)"], ascending=[True, False])
    df_anp_mas_importante_por_dep = df_anp_contribucion_sorted.drop_duplicates(subset="DEPARTAMENTO1")
    df_anp_mas_importante_por_dep = df_anp_mas_importante_por_dep.sort_values(by="Contribución Departamental (%)", ascending=True)

    fig03, ax03 = plt.subplots(figsize=(14, 10))
    bars = ax03.barh(
        df_anp_mas_importante_por_dep["DEPARTAMENTO1"],
        df_anp_mas_importante_por_dep["Contribución Departamental (%)"],
        color='mediumseagreen'
    )

    ax03.set_xlabel("Contribución Departamental de la ANP Más Grande (%)", fontsize=12)
    ax03.set_ylabel("Departamento", fontsize=12)
    ax03.set_title("Contribución de la ANP Más Importante al Área Protegida de Cada Departamento", fontsize=14)
    plt.yticks(fontsize=10)

    for bar, anp_name in zip(bars, df_anp_mas_importante_por_dep["ANP_NOMB"]):
        width = bar.get_width()
        ypos = bar.get_y() + bar.get_height() / 2

        plt.text(
            width + 0.5,
            ypos,
            f"{round(width, 1)}%",
            ha='left',
            va='center',
            fontsize=9,
            color='black'
        )

        text_x_position = 0.5
        if width < 5:
            text_x_position = width / 2
        plt.text(
            text_x_position,
            ypos,
            anp_name,
            ha='left',
            va='center',
            fontsize=9,
            color='white',
            wrap=True
        )
    plt.xlim(0, df_anp_mas_importante_por_dep["Contribución Departamental (%)"].max() * 1.15)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    st.pyplot(fig03)
    plt.close(fig03)


elif menu_selection == "Superficie ANP por Tipo":
    st.header("Superficie Total de ANP por Tipo de Área")
    st.write('Agrupa las ANP según su categoría (Parques Nacionales, Santuarios, Reservas, entre otros) y muestra cuántas hay y cuánta superficie representan en total.')
    
    df_summary_by_type = df.groupby("ANP_CATE").agg(
        Numero_ANP=('ANP_NOMB', 'nunique'),
        Superficie_Total_ha=('ANP_SULEG', 'sum')
    ).reset_index()

    df_summary_by_type.rename(columns={
        "ANP_CATE": "Tipo de ANP",
        "Numero_ANP": "Cantidad",
        "Superficie_Total_ha": "Superficie Total (ha)"
    }, inplace=True)

    df_summary_by_type = df_summary_by_type.sort_values(by="Superficie Total (ha)", ascending=False)

    st.dataframe(df_summary_by_type.style.format({
        "Cantidad": "{:.0f}",
        "Superficie Total (ha)": "{:,.2f} ha"
    }), use_container_width=True)

    df_summary_by_type = df_summary_by_type.sort_values(by="Superficie Total (ha)", ascending=False)

    fig04, ax04 = plt.subplots(figsize=(12, 7))
    bars = ax04.bar(
        df_summary_by_type["Tipo de ANP"],
        df_summary_by_type["Superficie Total (ha)"],
        color='darkgreen'
    )

    ax04.set_xlabel("Tipo de Área Natural Protegida", fontsize=12)
    ax04.set_ylabel("Superficie Total (ha)", fontsize=12)
    ax04.set_title("Superficie Total de ANP por Tipo de Área", fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    
    formatter = mticker.FormatStrFormatter('%1.0f')
    plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width()/2,
            yval + (plt.gca().get_ylim()[1] * 0.01),
            f"{yval:,.0f}",
            ha='center',
            va='bottom',
            fontsize=9,
            color='black'
        )
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig04)
    plt.close(fig04)


elif menu_selection == "Desempeño Departamental":
    st.header("Desempeño Departamental en Protección Ambiental")
    st.write('Compara el porcentaje de ANP de cada departamento con el promedio nacional y muestra la diferencia, indicando qué regiones superan o están por debajo de ese estándar.')
    
    df_anp_area_t5 = df[["ANP_NOMB", "DEPARTAMENTO1", "ANP_SULEG"]]
    df_departamento_summary = df_anp_area_t5.groupby("DEPARTAMENTO1").sum()["ANP_SULEG"].reset_index()
    
    df_departamento_summary["Area_Total_Departamento_ha"] = [
        1570000, 2089579, 466920, 4381480, 1423130, 7199900, 2549990, 3331754,
        3589249, 4419723, 466920, 3924913, 3480159, 2531959, 3591481, 2132783,
        3684885, 2089579, 7198650, 10241055, 5125331, 36885195, 8530054
    ]

    df_departamento_summary["Porcentaje de ANP del Departamento"] = \
        (df_departamento_summary["ANP_SULEG"] / df_departamento_summary["Area_Total_Departamento_ha"]) * 100

    porcentaje_anp_nacional_promedio = df_departamento_summary["Porcentaje de ANP del Departamento"].mean()

    df_departamento_summary["Porcentaje de ANP Nacional Promedio"] = porcentaje_anp_nacional_promedio
    df_departamento_summary["Diferencia con Promedio Nacional"] = \
        df_departamento_summary["Porcentaje de ANP del Departamento"] - porcentaje_anp_nacional_promedio

    df_final_table = df_departamento_summary[[
        "DEPARTAMENTO1",
        "Porcentaje de ANP del Departamento",
        "Porcentaje de ANP Nacional Promedio",
        "Diferencia con Promedio Nacional"
    ]].copy()

    df_final_table.rename(columns={
        "DEPARTAMENTO1": "Departamento"
    }, inplace=True)

    df_final_table = df_final_table.sort_values(by="Diferencia con Promedio Nacional", ascending=False)
    st.dataframe(df_final_table.style.format({
        "Porcentaje de ANP del Departamento": "{:.2f}%",
        "Porcentaje de ANP Nacional Promedio": "{:.2f}%",
        "Diferencia con Promedio Nacional": "{:+.2f}%"
    }), use_container_width=True)


    df_chart_data = df_departamento_summary.sort_values(by="Diferencia con Promedio Nacional", ascending=False)
    fig05, ax05 = plt.subplots(figsize=(14, 8))

    colors = ['green' if x >= 0 else 'red' for x in df_chart_data["Diferencia con Promedio Nacional"]]

    bars = ax05.bar(
        df_chart_data["DEPARTAMENTO1"],
        df_chart_data["Diferencia con Promedio Nacional"],
        color=colors
    )

    ax05.set_xlabel("Departamento", fontsize=12)
    ax05.set_ylabel("Diferencia con Promedio Nacional (%)", fontsize=12)
    ax05.set_title("Desviación del Porcentaje de ANP Departamental Respecto al Promedio Nacional", fontsize=14)

    plt.xticks(rotation=60, ha='right', fontsize=10)

    plt.axhline(0, color='gray', linestyle='--', linewidth=0.8)

    for bar in bars:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width()/2,
            yval + (plt.gca().get_ylim()[1] * 0.01) if yval >= 0 else yval - (plt.gca().get_ylim()[1] * 0.02),
            f"{yval:+.2f}%",
            ha='center',
            va='bottom' if yval >= 0 else 'top',
            fontsize=9,
            color='black'
        )
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig05)
    plt.close(fig05)


elif menu_selection == "ANP por Tipo":
    st.header("ANP por Tipo")
    st.write("Selecciona un tipo de ANP para filtrar la tabla y el gráfico de cantidad por departamento.")

    anp_types_interactive = df['ANP_CATE'].unique().tolist()
    anp_types_interactive.sort()
    dropdown_options_interactive = ["Todos los tipos"] + anp_types_interactive

    selected_type_interactive = st.selectbox(
        'Tipo de ANP (Sección Interactiva):',
        dropdown_options_interactive,
        index=0,
        key='interactive_anp_selector',
        help="Selecciona el tipo de Área Natural Protegida para filtrar los datos en esta sección interactiva."
    )

    if selected_type_interactive == "Todos los tipos":
        df_filtered_interactive = df
        titulo_tabla_interactive = "Todos los tipos de ANP"
        titulo_grafico_interactive = "Cantidad de ANP por Departamento (Todos los tipos)"
    else:
        df_filtered_interactive = df[df['ANP_CATE'] == selected_type_interactive]
        titulo_tabla_interactive = f"ANP de tipo: '{selected_type_interactive}'"
        titulo_grafico_interactive = f"Cantidad de ANP por Departamento para '{selected_type_interactive}'"

    if not df_filtered_interactive.empty:
        df_counts_table_interactive = df_filtered_interactive.groupby('DEPARTAMENTO1').size().reset_index(name='Cantidad de ANP')
        df_counts_table_interactive.rename(columns={'DEPARTAMENTO1': 'Departamento'}, inplace=True)
        df_counts_table_interactive = df_counts_table_interactive.sort_values(by='Cantidad de ANP', ascending=False)
        df_counts_table_interactive = df_counts_table_interactive.reset_index(drop=True)

        st.subheader(titulo_tabla_interactive)
        st.dataframe(df_counts_table_interactive, use_container_width=True)

        st.subheader(titulo_grafico_interactive)
        chart_interactive = alt.Chart(df_counts_table_interactive).mark_bar().encode(
            x=alt.X('Cantidad de ANP', title='Cantidad de ANP'),
            y=alt.Y('Departamento', sort='-x', title='Departamento'),
            tooltip=['Departamento', 'Cantidad de ANP']
        ).properties(
            title=titulo_grafico_interactive
        ).interactive()

        st.altair_chart(chart_interactive, use_container_width=True)

    else:
        st.warning("No hay datos para el tipo de ANP seleccionado en la sección interactiva.")


st.write('---')
st.write('**Bibliografía:**')
st.write('Áreas Naturales Protegidas (ANP) de Administración Nacional definitiva | Plataforma Nacional de Datos Abiertos. (s. f.). https://www.datosabiertos.gob.pe/dataset/%C3%A1reas-naturales-protegidas-anp-de-administraci%C3%B3n-nacional-definitiva')