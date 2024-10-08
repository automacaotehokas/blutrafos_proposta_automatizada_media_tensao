import os
import streamlit as st
from msal import ConfidentialClientApplication

# Configuração da página inicial
st.set_page_config(page_title="Proposta Automatizada - Média Tensão", layout="wide")

# Configurações de autenticação
CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
TENANT_ID = os.getenv('AZURE_TENANT_ID')
CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_URI = "http://localhost:8501"  # Ajuste conforme o seu ambiente
SCOPES = ["User.Read"]
EMAILS_PERMITIDOS = ["waleska@blutrafos.com.br",
"leandro@blutrafos.com.br",
"gabrielle.pinto@blutrafos.com.br",
"vilson@blutrafos.com.br",
"jaqueline.santos@blutrafos.com.br",
"marlon@blutrafos.com.br",
"daiana.raimundi@blutrafos.com.br",
"alexandre@blutrafos.com.br"]

def init_app():
    return ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )

def autenticar_usuario():
    app = init_app()
    accounts = app.get_accounts()

    # Tenta autenticar de forma silenciosa se o usuário já estiver logado no navegador
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            email = result['id_token_claims']['preferred_username']
            if email in EMAILS_PERMITIDOS:
                return True
            else:
                st.error("Você não tem permissão para acessar este aplicativo.")
                return False

    # Se a autenticação silenciosa falhar, redirecionar para a página de login
    auth_url = app.get_authorization_request_url(
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    st.markdown(f"[Clique aqui para entrar]({auth_url})")
    return False

# Verifica se o usuário está autenticado e autorizado
if not autenticar_usuario():
    st.stop()  # Para a execução do código se o usuário não estiver autorizado

# Conteúdo principal da página após a autenticação
# Adicionando a imagem do logo
st.image("image1png.png", width=100)

# Título da página
st.title("Proposta Automatizada - Média Tensão")
st.markdown("---")

# Descrição justificada da página
st.markdown(
    """
    <style>
    .justified-text {
        text-align: justify;
    }
    </style>
    <div class="justified-text">
        Bem-vindo à Proposta Automatizada de Média Tensão da Blutrafos. Este sistema foi desenvolvido para 
        facilitar o processo de criação de propostas comerciais personalizadas. Com ele, é possível configurar 
        itens técnicos, calcular preços e gerar documentos profissionais de maneira automatizada, otimizando 
        tempo e garantindo precisão nas informações fornecidas aos nossos clientes.
        <br><br>
        Nosso objetivo é proporcionar uma solução eficiente, rápida e segura, integrando todas as etapas do 
        processo de criação de propostas em um único lugar, com a capacidade de armazenar e gerenciar dados de 
        forma centralizada através da integração com o SharePoint.
    </div>
    """, 
    unsafe_allow_html=True
)
