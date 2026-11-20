import streamlit as st
import html
import re

st.markdown("""
<style>
    [data-testid="collapsedControl"], button[kind="header"] {
        display: none !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    section[data-testid="stSidebar"] {
        width: 75px !important;
        min-width: 75px !important;
        max-width: 75px !important;
        transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1), min-width 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        overflow-x: hidden !important;
    }
    section[data-testid="stSidebar"]:hover {
        width: 290px !important;
        min-width: 290px !important;
        max-width: 290px !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] span {
        visibility: hidden;
        opacity: 0;
        transition: visibility 0.2s, opacity 0.2s ease-in-out;
        white-space: nowrap !important;
    }
    section[data-testid="stSidebar"]:hover [data-testid="stSidebarNav"] span {
        visibility: visible;
        opacity: 1;
    }
    [data-testid="stSidebarNav"] ul li a {
        font-size: 15px !important;
        padding: 8px 12px !important;
    }
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Bibliografía", page_icon="📚", layout="wide")
st.title("Bibliografía")

st.markdown("""
<style>
    .ref {
        padding-left: 2.2rem;
        text-indent: -2.2rem;
        margin-bottom: 0.8rem;
        line-height: 1.55;
        font-size: 0.95rem;
    }
    .ref a {
        color: #7fb3ff;
        word-break: break-all;
    }
</style>
""", unsafe_allow_html=True)

st.caption("Referencias en formato APA, clasificadas por tipo de fuente y ordenadas alfabéticamente.")

def formato(ref: str) -> str:
    texto = html.escape(ref)
    texto = re.sub(r"(https?://[^\s<]+)", r'<a href="\1" target="_blank">\1</a>', texto)
    texto = re.sub(r"\*(.+?)\*", r"<i>\1</i>", texto)
    return texto

BIBLIOGRAFIA = {
    "Fuentes de datos": [
        "Haroon, S. (2023). *Airlines dataset* [Conjunto de datos]. Kaggle. https://www.kaggle.com/datasets/saadharoon27/airlines-dataset",
        "Internet Assigned Numbers Authority. (2017). *Time zone database* (Versión 2017b) [Conjunto de datos]. Public Technical Identifiers. https://www.iana.org/time-zones",
    ],
    "Métodos y herramientas": [
        "Kruskal, W. H., & Wallis, W. A. (1952). Use of ranks in one-criterion variance analysis. *Journal of the American Statistical Association, 47*(260), 583–621. https://doi.org/10.1080/01621459.1952.10483441",
        "Raasveldt, M., & Mühleisen, H. (2019). DuckDB: An embeddable analytical database. En *Proceedings of the 2019 International Conference on Management of Data* (pp. 1981–1984). Association for Computing Machinery. https://doi.org/10.1145/3299869.3320212",
    ],
    "Literatura sobre retrasos": [
        "Ball, M., Barnhart, C., Dresner, M., Hansen, M., Neels, K., Odoni, A., Peterson, E., Sherry, L., Trani, A., & Zou, B. (2010). *Total delay impact study: A comprehensive assessment of the costs and impacts of flight delay in the United States*. National Center of Excellence for Aviation Operations Research. https://rosap.ntl.bts.gov/view/dot/6234",
        "Beatty, R., Hsu, R., Berry, L., & Rome, J. (1999). Preliminary evaluation of flight delay propagation through an airline schedule. *Air Traffic Control Quarterly, 7*(4), 259–270.",
        "Lemay, X., & Bastin, F. (2025). *Prediction of airport on-time performance* (arXiv:2601.00875). arXiv. https://arxiv.org/abs/2601.00875",
        "Pyrgiotis, N., Malone, K. M., & Odoni, A. (2013). Modelling delay propagation within an airport network. *Transportation Research Part C: Emerging Technologies, 27*, 60–75.",
    ],
    "Trabajos de grado": [
        "Martínez Domenech, N. (2016). *Predicción y análisis de los retrasos en los vuelos: Estudio del aeropuerto de Arizona (E.E.U.U.)* [Proyecto de fin de grado, Universitat Autònoma de Barcelona]. Dipòsit Digital de Documents de la UAB. https://ddd.uab.cat/pub/tfg/2016/169883/MartinezDomenechNerea-TFGAa2015-16.pdf",
        "Monje Solá, R. (2015). *Análisis y predicción de los retrasos de vuelo: Estudio del aeropuerto de Seattle-Tacoma* [Proyecto de fin de grado, Universitat Autònoma de Barcelona]. Dipòsit Digital de Documents de la UAB. https://ddd.uab.cat/pub/tfg/2015/146885/MonjeSolaRaul-TFGAa2014-15.pdf",
    ],
    "Normativa y definiciones de puntualidad": [
        "Bureau of Transportation Statistics. (s. f.). *Understanding the reporting of causes of flight delays and cancellations*. U.S. Department of Transportation. https://www.bts.gov/topics/airlines-and-airports/understanding-reporting-causes-flight-delays-and-cancellations",
        "European Parliament & Council of the European Union. (2004). Regulation (EC) No 261/2004 of 11 February 2004 establishing common rules on compensation and assistance to passengers in the event of denied boarding and of cancellation or long delay of flights, and repealing Regulation (EEC) No 295/91. *Official Journal of the European Union, L 46*, 1–8. https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32004R0261",
        "International Air Transport Association. (2023). *Airport handling manual* (43.ª ed.). https://www.iata.org/en/publications/manuals/airport-handling-manual/",
        "OAG. (2023, 22 de mayo). *Defining late: On-time performance in the aviation industry*. https://oag.com/blog/defining-late-on-time-performance-in-the-aviation-industry",
        "Turu Logistics. (2023). *What is on-time performance (OTP) and why is it important?* https://turulojistik.com.tr/en/what-is-on-time-performance-otp-and-why-is-it-important/",
    ],
    "Gestión del tráfico aéreo y divulgación": [
        "Aircraft Owners and Pilots Association. (s. f.). *ABCs of aviation*. https://aopa.org/training-and-safety/active-pilots/safety-and-technique/operations/abcs-of-aviation",
        "Century Flight Peru. (2026, 20 de enero). ¿Qué es la gestión de tráfico aéreo (ATM) y por qué es crucial? *Blog Aviador*. https://centuryflightperu.com/blog-aviador/qu-es-la-gesti-n-de-tr-fico-a-reo-atm-y-por-qu-es-crucial",
        "O'Terror do Cumulonimbo. (2018, 18 de junio). Gestión del tráfico aéreo (ATM) de forma muy simplificada. *El vuelo de la Gran Avutarda*. https://greatbustardsflight.blogspot.com/2018/06/gestion-del-trafico-aereo-atm-de-forma.html",
    ],
}

total = sum(len(refs) for refs in BIBLIOGRAFIA.values())
st.caption(f"{total} referencias")

for categoria, referencias in BIBLIOGRAFIA.items():
    st.subheader(categoria)
    for ref in referencias:
        st.markdown(f'<div class="ref">{formato(ref)}</div>', unsafe_allow_html=True)