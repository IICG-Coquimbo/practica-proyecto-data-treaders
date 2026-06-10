import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient
import certifi

# 1. Configuración de la interfaz web corporativa de DataTraders
st.set_page_config(page_title="Dashboard DataTraders - Hito 2", layout="wide")
st.title("🏛️ Cuadro de Mando Integral · Control de KPIs Hipotecarios")
st.markdown("### **Métricas Organizacionales — Grupo DataTraders (UCN 2026)**")
st.markdown("---")

# 2. Credenciales de conexión extraídas de sus notebooks
USUARIO  = "joaquinserey_db_user"
PASSWORD = "joaquin3001"
HOST     = "datatreaders.xake49k.mongodb.net"
DB       = "HipotecarioChile"

URI = f"mongodb+srv://{USUARIO}:{PASSWORD}@{HOST}/{DB}?retryWrites=true&w=majority&appName=DataTraders"

@st.cache_data
def cargar_datos_desde_atlas():
    client = MongoClient(URI, tlsCAFile=certifi.where())
    db = client[DB]
    
    # Descargamos las colecciones reales de sus hitos
    df_proc = pd.DataFrame(list(db["processed_data"].find({}, {"_id": 0})))
    df_clus = pd.DataFrame(list(db["clustered_data"].find({}, {"_id": 0})))
    
    # Contadores operacionales en tiempo real
    total_raw = db["datos_hipotecarios"].count_documents({})
    total_processed = len(df_proc)
    
    client.close()
    
    # Unimos de forma segura las variables del EDA con las etiquetas de K-Means
    if not df_clus.empty and not df_proc.empty:
        df_proc["cae"] = pd.to_numeric(df_proc["cae"], errors="coerce")
        df_clus["cae"] = pd.to_numeric(df_clus["cae"], errors="coerce")
        df_proc["banco"] = df_proc["banco"].astype(str)
        df_clus["banco"] = df_clus["banco"].astype(str)
        df_proc["date"] = df_proc["date"].astype(str)
        df_clus["date"] = df_clus["date"].astype(str)
        
        # Cruce por llaves financieras compuestas
        df_final = pd.merge(df_proc, df_clus, on=["cae", "banco", "date"], how="left")
    else:
        df_final = df_proc
        df_final["cluster_nombre"] = "Riesgo no asignado"
        
    # Limpieza menor por si quedaron nulos en el mapeo del cluster
    df_final["cluster_nombre"] = df_final["cluster_nombre"].fillna("Riesgo Medio")
    return df_final, total_raw, total_processed

# Carga en vivo
df, total_original, total_procesados = cargar_datos_desde_atlas()

# 3. Estructura de navegación por Niveles Organizacionales (Rúbrica)
tab_est, tab_tac, tab_op = st.tabs([
    "🎯 Nivel Estratégico (CEO)", 
    "📈 Nivel Táctico (Gerente)", 
    "⚙️ Nivel Operacional (Supervisor)"
])

# ==========================================
# PESTAÑA 1: NIVEL ESTRATÉGICO
# ==========================================
with tab_est:
    st.header("Análisis de Decisiones Estratégicas del Mercado")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔹 KPI: CAE Promedio por Banco")
        st.caption("Objetivo: Comparar el costo promedio de los créditos entre bancos para apoyar decisiones estratégicas.")
        
        bancos_data = df.groupby("banco")["cae"].mean().sort_values(ascending=False)
        
        # Usamos su paleta dinámica exacta (Naranjo el máximo, azul el mínimo)
        colores_b = ["#D85A30" if v == bancos_data.max() 
                     else "#1B3A6B" if v == bancos_data.min() 
                     else "#6B8EBF" for v in bancos_data.values]
                     
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(bancos_data.index, bancos_data.values, color=colores_b, edgecolor="white")
        ax.set_ylabel("CAE Promedio (%)")
        plt.xticks(rotation=30, ha="right")
        sns.despine(left=True)
        st.pyplot(fig)
        
    with col2:
        st.subheader("🔹 KPI: Variación del CAE en el Tiempo")
        st.caption("Objetivo: Identificar períodos donde el CAE aumenta o disminuye para analizar tendencias.")
        
        # Lógica temporal exacta de su gráfico 2
        df_tiempo = df[df["date"].notna()].copy()
        df_tiempo["periodo"] = pd.to_datetime(df_tiempo["date"]).dt.to_period("M").astype(str)
        bancos_reales = [b for b in ["BancoEstado", "Santander", "BCI", "Scotiabank", "Itaú"] if b in df_tiempo["banco"].unique()]
        
        if bancos_reales:
            evol = df_tiempo[df_tiempo["banco"].isin(bancos_reales)].groupby(["periodo", "banco"])["cae"].mean().reset_index()
            
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            # Su paleta de colores del notebook
            colores_lineas = {"BancoEstado": "#1B3A6B", "Santander": "#D85A30", "BCI": "#085041"}
            
            for b in bancos_reales:
                sub = evol[evol["banco"] == b]
                ax2.plot(sub["periodo"], sub["cae"], label=b, marker="o", linewidth=2, color=colores_lineas.get(b, "#CCCCCC"))
            
            ax2.set_ylabel("CAE (%)")
            plt.xticks(rotation=45, ha="right")
            ax2.legend(title="Bancos")
            sns.despine(left=True)
            st.pyplot(fig2)
        else:
            st.info("No se encontraron registros temporales suficientes para graficar la evolución.")

# ==========================================
# PESTAÑA 2: NIVEL TÁCTICO
# ==========================================
with tab_tac:
    st.header("Modelos Predictivos y Control de Desviaciones")
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("🔹 KPI: Tasa de Alza del CAE por Clúster")
        st.caption("Objetivo: Evaluar qué segmento presenta mayor probabilidad de aumento de tasas (Variable Y).")
        
        # Calculamos la probabilidad real de la variable Y ('sube_cae') según el clúster de K-Means
        df_cluster_plot = df.groupby("cluster_nombre")["sube_cae"].mean().reset_index()
        df_cluster_plot["sube_cae"] *= 100 # Convertir a porcentaje
        
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        # Paleta de su K-Means (Azul, Verde, Rojo)
        paleta_kmeans = {"Riesgo Bajo": "#1B3A6B", "Riesgo Medio": "#085041", "Riesgo Alto": "#C0392B"}
        
        sns.barplot(data=df_cluster_plot, x="cluster_nombre", y="sube_cae", palette=paleta_kmeans, order=["Riesgo Bajo", "Riesgo Medio", "Riesgo Alto"], ax=ax3)
        ax3.set_ylabel("% Probabilidad de Alza el Próximo Mes")
        ax3.set_xlabel("Clúster K-Means")
        sns.despine(left=True)
        st.pyplot(fig3)
        
    with col4:
        st.subheader("🔹 KPI: Desviación del CAE respecto al Promedio del Banco")
        st.caption("Objetivo: Detectar créditos fuera de rango (más costosos o convenientes).")
        
        fig4, ax4 = plt.subplots(figsize=(6, 4))
        # Boxplot de su ingeniería de variables
        sns.boxplot(data=df, x="banco", y="desviacion_vs_banco", palette="vlag", ax=ax4)
        ax4.axhline(y=0, color="red", linestyle="--", alpha=0.6, label="Media del Banco")
        ax4.set_ylabel("Desviación (Puntos Porcentuales)")
        plt.xticks(rotation=25, ha="right")
        ax4.legend()
        sns.despine(left=True)
        st.pyplot(fig4)

# ==========================================
# PESTAÑA 3: NIVEL OPERACIONAL
# ==========================================
with tab_op:
    st.header("Métricas de Control de Ingesta y Calidad de Datos")
    st.caption("Frecuencia: Por carga de datos | Objetivo: Controlar que el proceso de limpieza mantenga una base confiable.")
    
    # Cálculo real de la depuración que hicieron en el notebook del EDA
    eliminados_cant = total_original - total_procesados
    porcentaje_eliminados = (eliminados_cant / total_original) * 100 if total_original > 0 else 0
    
    # Tarjetas operacionales dinámicas conectadas a Mongo
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="📥 Registros Iniciales en Bruto (raw_data)", value=f"{total_original} filas")
    with c2:
        st.metric(label="✅ KPI: Registros Procesados Correctamente", value=f"{total_procesados} filas", delta="Calidad Certificada")
    with c3:
        st.metric(label="🗑️ KPI: Porcentaje de Registros Eliminados", value=f"{porcentaje_eliminados:.2f}%", delta="Outliers + Duplicados", delta_color="inverse")
        
    st.markdown("---")
    st.subheader("📋 Vista de Auditoría de Datos de Entrada para Modelos (`processed_data`)")
    st.dataframe(df[['extractor', 'banco', 'region', 'monto', 'cae', 'cuota_estimada', 'desviacion_vs_banco', 'cluster_nombre', 'sube_cae']].head(15), hide_index=True)