import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import math

st.set_page_config(layout="wide")
st.title("Panel de Salidas - Aeropuerto")

# 1. Datos de ejemplo (10 vuelos para que veas la rotación en 2 páginas)
df_vuelos = pd.DataFrame([
    {"hora": "08:30", "vuelo": "IB 6674", "destino": "MADRID",       "puerta": "A12", "estado": "EN HORA"},
    {"hora": "09:15", "vuelo": "AV 011",  "destino": "BOGOTA",       "puerta": "B04", "estado": "EMBARCANDO"},
    {"hora": "10:00", "vuelo": "CM 224",  "destino": "PANAMA",       "puerta": "C01", "estado": "RETRASADO"},
    {"hora": "11:45", "vuelo": "LA 501",  "destino": "SANTIAGO",     "puerta": "A08", "estado": "EN HORA"},
    {"hora": "12:20", "vuelo": "AA 908",  "destino": "MIAMI",        "puerta": "D15", "estado": "CANCELADO"},
    {"hora": "13:10", "vuelo": "AF 428",  "destino": "PARIS",        "puerta": "E02", "estado": "EN HORA"},
    {"hora": "14:05", "vuelo": "LH 534",  "destino": "FRANKFURT",    "puerta": "E09", "estado": "EN HORA"},
    {"hora": "15:30", "vuelo": "DL 148",  "destino": "ATLANTA",      "puerta": "D03", "estado": "EMBARCANDO"},
    {"hora": "16:40", "vuelo": "UX 072",  "destino": "MADRID",       "puerta": "A04", "estado": "RETRASADO"},
    {"hora": "18:00", "vuelo": "KL 741",  "destino": "AMSTERDAM",    "puerta": "E11", "estado": "EN HORA"},
])

# 2. Fragmento que se ejecuta cada 6 segundos sin recargar toda la página
@st.fragment(run_every="6s")
def tablero_aeropuerto(df, filas_por_pagina=5):
    if "pagina_fids" not in st.session_state:
        st.session_state.pagina_fids = 0

    total_paginas = max(1, math.ceil(len(df) / filas_por_pagina))
    inicio = (st.session_state.pagina_fids % total_paginas) * filas_por_pagina
    fin = inicio + filas_por_pagina
    df_pagina = df.iloc[inicio:fin]

    pagina_actual = (st.session_state.pagina_fids % total_paginas) + 1
    st.session_state.pagina_fids += 1

    vuelos_json = df_pagina.to_json(orient="records")

    html_fids = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

      body {{
        background-color: #111;
        color: #f4d03f;
        font-family: 'Share Tech Mono', monospace;
        margin: 0;
        padding: 15px;
      }}

      .header-bar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #1a1a1a;
        padding: 10px 18px;
        border: 3px solid #333;
        border-bottom: none;
        color: #fff;
        font-size: 20px;
      }}

      .board {{
        width: 100%;
        border-collapse: collapse;
        background: #1a1a1a;
        box-shadow: 0 10px 30px rgba(0,0,0,0.8);
        border: 3px solid #333;
      }}

      .board th {{
        background: #222;
        color: #aaa;
        text-align: left;
        padding: 12px 15px;
        font-size: 16px;
        letter-spacing: 2px;
        border-bottom: 2px solid #444;
      }}

      .board td {{
        padding: 12px 15px;
        font-size: 22px;
        border-bottom: 1px solid #2a2a2a;
        letter-spacing: 1.5px;
      }}

      .flap {{
        display: inline-block;
        background: #0d0d0d;
        padding: 2px 6px;
        margin: 0 1px;
        border-radius: 3px;
        border-bottom: 1px solid #333;
        box-shadow: inset 0 -1px 0 rgba(255,255,255,0.1);
      }}

      .status-EMBARCANDO {{ color: #2ecc71; font-weight: bold; animation: blink 1.2s infinite; }}
      .status-RETRASADO  {{ color: #e67e22; }}
      .status-CANCELADO  {{ color: #e74c3c; }}
      .status-EN-HORA    {{ color: #f4d03f; }}

      @keyframes blink {{
        50% {{ opacity: 0.4; }}
      }}
    </style>
    </head>
    <body>

    <div class="header-bar">
      <span>✈ SALIDAS / DEPARTURES</span>
      <span style="color:#aaa; font-size:16px;">PÁGINA {pagina_actual} DE {total_paginas}</span>
    </div>

    <table class="board">
      <thead>
        <tr>
          <th>HORA</th>
          <th>VUELO</th>
          <th>DESTINO</th>
          <th>PUERTA</th>
          <th>ESTADO</th>
        </tr>
      </thead>
      <tbody id="fids-body"></tbody>
    </table>

    <script>
      const vuelos = {vuelos_json};
      const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:- ";

      function wrapFlaps(text) {{
        return text.toString().split('').map(c => `<span class="flap">${{c === ' ' ? '&nbsp;' : c}}</span>`).join('');
      }}

      const tbody = document.getElementById('fids-body');
      vuelos.forEach((v) => {{
        const tr = document.createElement('tr');
        const statusClass = 'status-' + v.estado.replace(/\\s+/g, '-');
        tr.innerHTML = `
          <td class="cell" data-target="${{v.hora}}"></td>
          <td class="cell" data-target="${{v.vuelo}}"></td>
          <td class="cell" data-target="${{v.destino}}"></td>
          <td class="cell" data-target="${{v.puerta}}"></td>
          <td class="cell ${{statusClass}}" data-target="${{v.estado}}"></td>
        `;
        tbody.appendChild(tr);
      }});

      document.querySelectorAll('.cell').forEach((cell) => {{
        const target = cell.getAttribute('data-target');
        let iterations = 0;
        const interval = setInterval(() => {{
          const scrambled = target.split('').map((char, idx) => {{
            if (idx < iterations) return char;
            return chars[Math.floor(Math.random() * chars.length)];
          }}).join('');
          cell.innerHTML = wrapFlaps(scrambled);
          if (iterations >= target.length) clearInterval(interval);
          iterations += 1 / 2;
        }}, 35);
      }});
    </script>
    </body>
    </html>
    """
    components.html(html_fids, height=390)

# Llamas a la función pasándole tus datos
tablero_aeropuerto(df_vuelos, filas_por_pagina=5)