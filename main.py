import streamlit as st
import requests
import os
from dotenv import load_dotenv
from prompt import gerar_prompt

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

st.set_page_config(page_title="Mentor PBL", page_icon="🧠")

# Sessão inicial
if 'perguntas' not in st.session_state:
    st.session_state.perguntas = []
if 'fase' not in st.session_state:
    st.session_state.fase = 'inicio'
if 'ultima_input' not in st.session_state:
    st.session_state.ultima_input = ""

st.markdown("""
    <h1 style='text-align: center; color: #328E6E;'>🧠 Mentor PBL</h1>
    <p style='text-align: center;'>Um facilitador com IA para estimular o pensamento crítico através de perguntas orientadoras.</p>
""", unsafe_allow_html=True)

st.divider()

if st.session_state.fase == 'inicio':
    with st.container():
        st.subheader("1️⃣ Descreva sua dúvida, ideia ou hipótese inicial")
        user_input = st.text_area("", key="input_inicial", height=150)

        if st.button("🎯 Pedir ajuda"):
            if not user_input.strip():
                st.warning("Por favor, escreva algo.")
            else:
                with st.spinner("Gerando orientação..."):
                    prompt = gerar_prompt(user_input)
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    response = requests.post(GEMINI_URL, json=payload)

                    if response.status_code == 200:
                        output = response.json()
                        try:
                            content = output['candidates'][0]['content']['parts'][0]['text']
                            st.session_state.perguntas.append(content)
                            st.session_state.fase = 'esperando_resposta'
                            st.session_state.ultima_input = user_input
                            st.experimental_rerun()
                        except Exception:
                            st.error("Erro ao interpretar resposta do Gemini.")
                    else:
                        st.error(f"Erro na API do Gemini: {response.status_code}")

elif st.session_state.fase == 'esperando_resposta':
    st.subheader("2️⃣ Reflexão orientada")
    st.markdown("""
        <div style='background-color: #ffe6e6; padding: 1rem; border-radius: 10px;'>
            <h4 style='color: #328E6E;'>🤔 Pergunta provocativa gerada:</h4>
            <p>{}</p>
        </div>
    """.format(st.session_state.perguntas[-1].replace("\n", "<br>")), unsafe_allow_html=True)

    resposta = st.text_area("💬 Responda a pergunta acima ou reflita sobre ela:", height=150)

    if st.button("➡️ Continuar investigando"):
        if not resposta.strip():
            st.warning("Por favor, escreva sua reflexão para continuar.")
        else:
            with st.spinner("Gerando novas perguntas..."):
                novo_prompt = gerar_prompt(resposta)
                payload = {"contents": [{"parts": [{"text": novo_prompt}]}]}
                response = requests.post(GEMINI_URL, json=payload)

                if response.status_code == 200:
                    output = response.json()
                    try:
                        content = output['candidates'][0]['content']['parts'][0]['text']
                        st.session_state.perguntas.append(content)
                        st.session_state.ultima_input = resposta
                        st.experimental_rerun()
                    except Exception:
                        st.error("Erro ao interpretar resposta do Gemini.")
                else:
                    st.error(f"Erro na API do Gemini: {response.status_code}")

st.divider()
if st.button("🔄 Reiniciar conversa"):
    st.session_state.fase = 'inicio'
    st.session_state.perguntas = []
    st.session_state.ultima_input = ""
    st.experimental_rerun()
