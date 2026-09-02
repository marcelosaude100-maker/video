"""
Filtro do Saber - Gerador de Vídeos de 5 Segundos com IA.

Esta é uma aplicação Streamlit integrada à API do Replicate usando o modelo
Luma Dream Machine para gerar vídeos de 5 segundos baseados em prompts de texto.
"""

import os
import time
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
    .video-title {
        text-align: center;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
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
    O modelo luma/dream-machine gera vídeos nativos de exatamente 5 segundos.
    """
    token = get_api_token()
    if not token:
        raise ValueError(
            "Chave de API do Replicate não configurada. "
            "Por favor, configure o REPLICATE_API_TOKEN nos Secrets."
        )

    # Inicializa o cliente do Replicate de forma explícita para evitar falhas de contexto
    client = replicate.Client(api_token=token)

    # Iniciando a predição de forma assíncrona para podermos monitorar o status em tempo real
    # e oferecer a melhor experiência ao usuário (UX)
    prediction = client.predictions.create(
        model="luma/dream-machine",
        input={
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "loop": False
        }
    )

    # Polling de progresso inteligente com tratamento de timeout (limite de 180 segundos)
    start_time = time.time()
    timeout = 180  # 3 minutos
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    while prediction.status not in ["succeeded", "failed", "canceled"]:
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout:
            # Cancela a predição na API do Replicate caso estoure o timeout
            try:
                prediction.cancel()
            except Exception:
                pass
            raise TimeoutError("O servidor da API demorou mais que o esperado para gerar o vídeo.")

        # Atualiza a interface com o status real do processamento
        status = prediction.status
        if status == "starting":
            progress_bar.progress(10)
            status_text.info("⌛ Alocando servidores de IA para o seu vídeo...")
        elif status == "processing":
            progress_bar.progress(50)
            status_text.info(f"🎨 Gerando os quadros do vídeo... (Tempo decorrido: {int(elapsed_time)}s)")
        
        time.sleep(4)  # Intervalo seguro para não sobrecarregar requisições à API
        prediction.reload()

    # Tratamento final com base no resultado do processamento
    if prediction.status == "succeeded":
        progress_bar.progress(100)
        status_text.empty()
        # O output do luma/dream-machine é uma string URL direta do vídeo gerado
        return prediction.output
    elif prediction.status == "failed":
        raise ReplicateError(f"A geração de vídeo falhou. Erro da API: {prediction.error}")
    else:
        raise ReplicateError("A geração foi cancelada inesperadamente.")

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
        help="Seja descritivo! Adicione palavras sobre o estilo, iluminação e cores para obter os melhores resultados."
    )

    # Configurações avançadas expansíveis (mantendo a interface limpa)
    with st.expander("⚙️ Configurações do Vídeo"):
        st.write("⏱️ **Duração do vídeo:** 5 segundos *(Bloqueado pelo sistema do Filtro do Saber)*")
        aspect_ratio = st.selectbox(
            "Proporção de Tela (Aspect Ratio):",
            options=["16:9", "9:16", "1:1"],
            index=0,
            help="16:9 é ideal para o YouTube tradicional, enquanto 9:16 é perfeito para Shorts e TikTok."
        )

    # Botão de ação principal
    if st.button("🚀 Gerar Vídeo de 5 Segundos"):
        if not user_prompt.strip():
            st.warning("⚠️ Por favor, digite uma descrição para o vídeo antes de continuar.")
            return

        try:
            # Container de status de carregamento
            with st.container():
                st.subheader("Gerando sua criação cinematográfica...")
                video_url = generate_video_ia(user_prompt, aspect_ratio)

            # Exibição de sucesso e renderização do vídeo
            st.success("🎉 Seu vídeo de 5 segundos foi gerado com sucesso!")
            
            # Elemento do vídeo na página
            st.video(video_url)

            # Botão de download do arquivo gerado
            st.download_button(
                label="📥 Baixar Vídeo MP4",
                data=video_url,
                file_name="filtro_do_saber_5s.mp4",
                mime="video/mp4",
                help="Clique para salvar o vídeo diretamente no seu dispositivo."
            )

        except ValueError as val_err:
            st.error(f"Configuração Necessária: {val_err}")
        except TimeoutError as timeout_err:
            st.error(f"Erro de Tempo Limite: {timeout_err} Tente novamente em alguns instantes.")
        except ReplicateError as rep_err:
            st.error(f"Erro na Plataforma de IA: {rep_err}")
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    main()
