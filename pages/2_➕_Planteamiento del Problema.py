import streamlit as st

st.set_page_config(page_title="Planteamiento del Problema", page_icon="➕", layout="wide")
##############################################################################################
### PLANTEAMIENTO DEL PROBLEMA ###
st.title("Planteamiento del Problema")
st.markdown(""" 
planteamiento del problema
""", unsafe_allow_html=True)
##############################################################################################

##############################################################################################
### JUSTIFICACION ###
st.subheader("1.1 Justificacion")
st.markdown("""
la Justificacion
""", unsafe_allow_html=True)
##############################################################################################

##############################################################################################
### OBJETIVOS ###
st.subheader("1.2 Objetivos")
st.markdown("""
los Objetivos
""", unsafe_allow_html=True)

with st.expander("1.2.1 Objetivos generales", expanded=True):
    st.markdown("""
     Objetivos generales
    """, unsafe_allow_html=True)

with st.expander("1.2.2 Objetivos específicos", expanded=False):
    st.markdown("""
     Objetivos específicos
    """, unsafe_allow_html=True)
##############################################################################################

##############################################################################################
### VARIABLES ###
st.subheader("1.3 Variables de estudio")
st.markdown("""
variables de estudio
""", unsafe_allow_html=True)
##############################################################################################