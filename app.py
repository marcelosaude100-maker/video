"""
Filtro do Saber - Gerador de Vídeos de 5 Segundos com IA.

Esta é uma aplicação Streamlit integrada à API do Replicate usando o modelo
Luma Dream Machine para gerar vídeos de 5 segundos de forma altamente robusta.
"""

import os
import streamlit as st
import replicate
from replicate.exceptions import ReplicateError

# ==========================================
# CONFIGURAÇÃO DA PÁGINA E UI/UX
# ==========================================
st.set_page_config(
    page_title="Filtro do Saber - Criador de Vídeos",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Customização CSS simples para um visual moderno e limpo
st.markdown("""
    <style>
    .main {
        background-color: #fafafa;
    }
    div.stButton > button:first-child {
        background-color: #FF4B4B;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
        height: 3em;
        border: none;
        transition: background-color 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #E03E3E;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# FUNÇÕES AUXILIARES / INTEGRAÇÃO DE API
# ==========================================
def get_api_token() -> str:
    """
    Recupera o token do Replicate de forma segura.
    Verifica primeiro no st.secrets e depois nas variáveis de ambiente.
    """
    if "REPLICATE_API_TOKEN" in st.secrets:
        return st.secrets["REPLICATE_API_TOKEN"]
    elif os.getenv("REPLICATE_API_TOKEN"):
        return os.getenv("REPLICATE_API_TOKEN")
    return ""

def generate_video_ia(prompt: str, aspect_ratio: str = "16:9") -> str:
    """
    Chama a API do Replicate usando o modelo Luma Dream Machine.
    Utiliza o método .run() para estabilidade de nível de produção.
    """
    token = get_api_token()
    if not token:
        raise ValueError(
            "Chave de API do Replicate não configurada. "
            "Por favor, configure o REPLICATE_API_TOKEN nos Secrets do Streamlit."
        )

    # Inicializa o cliente oficial do Replicate
    client = replicate.Client(api_token=token)

    # O método client.run gerencia internamente o polling, fila de espera
    # e tratamento de erros de forma muito mais segura que um loop while manual
    output = client.run(
        "luma/dream-machine",
        input={
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "loop": False
        }
    )

    # O retorno do modelo Luma Dream Machine é tipicamente a URL direta do vídeo
    if isinstance(output, list):
        return output[0]
    return str(output)

# ==========================================
# INTERFACE PRINCIPAL DO STREAMLIT
# ==========================================
def main():
    # Cabeçalho da aplicação
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🎬 Filtro do Saber</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.1em;'>Transforme suas ideias em vídeos cinematográficos de exatamente <b>5 segundos</b>!</p>", unsafe_allow_html=True)
    st.divider()

    # Campo de entrada do usuário
    user_prompt = st.text_area(
        "Descreva a cena que você quer criar:",
        placeholder="Ex: Um close-up dramático de uma ampulheta dourada escorrendo areia luminosa azul, estilo macro e cinematográfico.",
        max_chars=350,
        help="Seja descritivo! Adicione detalhes de estilo, câmera, iluminação e cores."
    )

    # Configurações expansíveis
    with st.expander("⚙️ Configurações do Vídeo"):
        st.write("⏱️ **Duração do vídeo:** 5 segundos *(Configuração padrão Filtro do Saber)*")
        aspect_ratio = st.selectbox(
            "Proporção de Tela (Aspect Ratio):",
            options=["16:9", "9:16", "1:1"],
            index=0,
            help="16:9 (YouTube), 9:16 (Shorts/Reels) ou 1:1 (Instagram)."
        )

    # Botão de ação principal
    if st.button("🚀 Gerar Vídeo de 5 Segundos"):
        if not user_prompt.strip():
            st.warning("⚠️ Por favor, digite uma descrição para o vídeo antes de continuar.")
            return

        try:
            # Exibe uma mensagem de processamento profissional e nativa
            with st.spinner("🎨 A IA do Luma Dream Machine está gerando seu vídeo de 5 segundos... Isso pode levar de 1 a 2 minutos dependendo da fila da API."):
                video_url = generate_video_ia(user_prompt, aspect_ratio)

            # Exibição de sucesso e renderização do vídeo
            st.success("🎉 Seu vídeo de 5 segundos foi gerado com sucesso!")
            st.video(video_url)

            # Botão de download direto do MP4 gerado
            st.download_button(
                label="📥 Baixar Vídeo MP4",
                data=video_url,
                file_name="filtro_do_saber_5s.mp4",
                mime="video/mp4",
                help="Clique para salvar o vídeo diretamente no seu dispositivo."
            )

        except ValueError as val_err:
            st.error(f"Configuração Pendente: {val_err}")
        except ReplicateError as rep_err:
            st.error(f"A API do Replicate retornou um erro: {rep_err}")
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    main()
