import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import math

@st.fragment(run_every="6s")
def mostrar_tablero_vuelos(df: pd.DataFrame, filas_por_pagina: int = 5):
    if df.empty:
        st.info("No hay vuelos para mostrar con los filtros seleccionados.")
        return

    if "pagina_fids" not in st.session_state:
        st.session_state.pagina_fids = 0

    if st.session_state.get("total_vuelos_previo") != len(df):
        st.session_state.pagina_fids = 0
        st.session_state.total_vuelos_previo = len(df)

    total_paginas = max(1, math.ceil(len(df) / filas_por_pagina))
    inicio = (st.session_state.pagina_fids % total_paginas) * filas_por_pagina
    fin = inicio + filas_por_pagina
    df_pagina = df.iloc[inicio:fin].copy()

    pagina_actual = (st.session_state.pagina_fids % total_paginas) + 1
    st.session_state.pagina_fids += 1

    for col in ["hora", "vuelo", "destino", "puerta", "estado"]:
        df_pagina[col] = df_pagina[col].astype(str).str.upper()

    vuelos_json = df_pagina[["hora", "vuelo", "destino", "puerta", "estado"]].to_json(orient="records")

    html_fids = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
      body {{
        background-color: transparent;
        color: #f4d03f;
        font-family: 'Share Tech Mono', monospace;
        margin: 0;
        padding: 0;
      }}
      .header-bar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #1a1a1a;
        padding: 10px 18px;
        border: 3px solid #333;
        border-bottom: none;
        border-radius: 6px 6px 0 0;
        color: #fff;
        font-size: 18px;
      }}
      .clock-box {{
        color: #2ecc71;
        background: #0d0d0d;
        padding: 4px 10px;
        border-radius: 4px;
        border: 1px solid #333;
        font-size: 18px;
        letter-spacing: 2px;
      }}
      .board {{
        width: 100%;
        border-collapse: collapse;
        background: #1a1a1a;
        border: 3px solid #333;
        border-radius: 0 0 6px 6px;
      }}
      .board th {{
        background: #222;
        color: #aaa;
        text-align: left;
        padding: 10px 15px;
        font-size: 15px;
        letter-spacing: 2px;
        border-bottom: 2px solid #444;
      }}
      .board td {{
        padding: 10px 15px;
        font-size: 20px;
        border-bottom: 1px solid #2a2a2a;
        letter-spacing: 1.5px;
      }}
      .flap {{
        display: inline-block;
        background: #0d0d0d;
        padding: 2px 5px;
        margin: 0 1px;
        border-radius: 3px;
        border-bottom: 1px solid #333;
      }}
      .status-EMBARCANDO, .status-A-TIEMPO, .status-EN-HORA {{ color: #2ecc71; font-weight: bold; }}
      .status-RETRASADO, .status-DEMORADO {{ color: #e67e22; font-weight: bold; }}
      .status-CANCELADO {{ color: #e74c3c; font-weight: bold; }}
    </style>
    </head>
    <body>
    <div class="header-bar">
      <span>✈ MONITOR DE OPERACIONES / FLIGHT BOARD</span>
      <span style="color:#aaa; font-size:15px;">PÁGINA {pagina_actual} DE {total_paginas}</span>
      <span class="clock-box" id="live-clock">--:--:--</span>
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
      function updateClock() {{
        const now = new Date();
        const h = String(now.getHours()).padStart(2, '0');
        const m = String(now.getMinutes()).padStart(2, '0');
        const s = String(now.getSeconds()).padStart(2, '0');
        document.getElementById('live-clock').textContent = `${{h}}:${{m}}:${{s}}`;
      }}
      setInterval(updateClock, 1000);
      updateClock();

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
    alto_calculado = 115 + (len(df_pagina) * 48)
    components.html(html_fids, height=alto_calculado)