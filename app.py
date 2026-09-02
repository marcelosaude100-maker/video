"""
Filtro do Saber - Gerador de Vídeos de 5 Segundos com IA.

Esta é uma versão ultra-robusta com limpeza defensiva de credenciais e
painel de diagnóstico para resolução de problemas de autenticação (401).
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

# Customização CSS
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
# FUNÇÃO DEFENSIVA DE TRATAMENTO DE TOKEN
# ==========================================
def get_clean_api_token() -> str:
    """
    Recupera o token do Replicate de forma extremamente segura.
    Aplica limpeza defensiva para remover aspas, espaços e quebras de linha acidentais.
    """
    token = ""
    
    # 1. Tenta recuperar dos Secrets do Streamlit
    if "REPLICATE_API_TOKEN" in st.secrets:
        token = st.secrets["REPLICATE_API_TOKEN"]
    # 2. Tenta recuperar das variáveis de ambiente globais
    elif os.getenv("REPLICATE_API_TOKEN"):
        token = os.getenv("REPLICATE_API_TOKEN")

    if token:
        # Remove espaços em branco e quebras de linha nas pontas
        token = token.strip()
        
        # Remove aspas duplas ou simples que o usuário possa ter incluído acidentalmente dentro do valor
        if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
            token = token[1:-1].strip()
            
    return token

def generate_video_ia(prompt: str, aspect_ratio: str = "16:9") -> str:
    """
    Chama a API do Replicate configurando o ambiente de forma explícita.
    """
    token = get_clean_api_token()
    if not token:
        raise ValueError(
            "Chave de API do Replicate não configurada. "
            "Por favor, insira o seu REPLICATE_API_TOKEN nos Secrets do Streamlit."
        )

    # Injeta o token tratado diretamente no ambiente do sistema para garantir compatibilidade total
    os.environ["REPLICATE_API_TOKEN"] = token
    
    # Inicializa o cliente apontando diretamente para o token limpo
    client = replicate.Client(api_token=token)

    output = client.run(
        "luma/dream-machine",
        input={
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "loop": False
        }
    )

    if isinstance(output, list):
        return output
    return str(output)

# ==========================================
# INTERFACE PRINCIPAL DO STREAMLIT
# ==========================================
def main():
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🎬 Filtro do Saber</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.1em;'>Transforme suas ideias em vídeos cinematográficos de exatamente <b>5 segundos</b>!</p>", unsafe_allow_html=True)
    st.divider()

    # Campo de entrada do usuário
    user_prompt = st.text_area(
        "Descreva a cena que você quer criar:",
        placeholder="Ex: Um close-up dramático de uma ampulheta dourada escorrendo areia luminosa azul, estilo macro e cinematográfico.",
        max_chars=350
    )

    # Configurações expansíveis
    with st.expander("⚙️ Configurações do Vídeo"):
        st.write("⏱️ **Duração do vídeo:** 5 segundos *(Padrão Filtro do Saber)*")
        aspect_ratio = st.selectbox(
            "Proporção de Tela (Aspect Ratio):",
            options=["16:9", "9:16", "1:1"],
            index=0
        )

    # Botão de geração
    if st.button("🚀 Gerar Vídeo de 5 Segundos"):
        if not user_prompt.strip():
            st.warning("⚠️ Por favor, digite uma descrição para o vídeo antes de continuar.")
            return

        try:
            with st.spinner("🎨 A IA do Luma Dream Machine está gerando seu vídeo... Isso pode levar de 1 a 2 minutos dependendo da fila da API."):
                video_url = generate_video_ia(user_prompt, aspect_ratio)

            st.success("🎉 Seu vídeo de 5 segundos foi gerado com sucesso!")
            st.video(video_url)

            st.download_button(
                label="📥 Baixar Vídeo MP4",
                data=video_url,
                file_name="filtro_do_saber_5s.mp4",
                mime="video/mp4"
            )

        except ValueError as val_err:
            st.error(f"Configuração Pendente: {val_err}")
        except ReplicateError as rep_err:
            st.error(f"A API do Replicate retornou um erro: {rep_err}")
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")

    # ==========================================
    # PAINEL DE DIAGNÓSTICO (O SEU ALIADO AGORA)
    # ==========================================
    st.write("---")
    with st.expander("🔍 Painel de Diagnóstico de Autenticação (Filtro do Saber)"):
        st.subheader("Informações do Token de API")
        
        # Recuperamos o token bruto (sem limpeza) e o tratado para comparar
        raw_token = ""
        if "REPLICATE_API_TOKEN" in st.secrets:
            raw_token = st.secrets["REPLICATE_API_TOKEN"]
            
        clean_token = get_clean_api_token()
        
        if not raw_token:
            st.error("❌ O Streamlit Secrets está VAZIO ou não encontrou o nome 'REPLICATE_API_TOKEN'.")
            st.info("💡 Certifique-se de que salvou a linha exatamente como: REPLICATE_API_TOKEN = 'sua_chave'")
        else:
            st.success("✅ Um token foi detectado pelo sistema do Streamlit!")
            
            # Mostramos apenas dados seguros para não expor sua chave na tela
            st.write(f"• **Comprimento original do texto:** {len(raw_token)} caracteres")
            st.write(f"• **Comprimento após limpeza automática:** {len(clean_token)} caracteres")
            
            # Exibição mascarada segura (mostra apenas o início e o fim para conferência)
            if len(clean_token) > 8:
                st.info(f"🔑 **Formato limpo detectado:** `{clean_token[:5]}...{clean_token[-4:]}`")
            
            # Alertas inteligentes de formatação
            if raw_token.startswith('"') or raw_token.endswith('"') or raw_token.startswith("'") or raw_token.endswith("'"):
                st.warning("⚠️ **Alerta:** Seu segredo continha aspas extras no texto. Nossa limpeza automática removeu isso para você agora!")
                
            if "r8_" not in clean_token:
                st.error("⚠️ **Erro de Formato:** Os tokens do Replicate geralmente começam com o prefixo 'r8_'. O seu token atual não possui esse padrão. Verifique se copiou o código correto na plataforma.")

if __name__ == "__main__":
    main()
