import os
import streamlit as st
from msal import ConfidentialClientApplication

# Configuração da página inicial - deve ser a primeira chamada
st.set_page_config(page_title="Proposta Automatizada - Média Tensão", layout="centered", initial_sidebar_state="collapsed")

# Função para exibir ou ocultar a barra lateral com base no estado de autenticação
def exibir_barra_lateral(exibir):
    if not exibir:
        st.markdown(
            """
            <style>
            /* Esconde a seta da barra lateral e a barra lateral */
            [data-testid="stSidebar"], [data-testid="collapsedControl"] {
                display: none;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
            /* Mostra a barra lateral completamente expandida */
            [data-testid="stSidebar"] {
                display: block;
                visibility: visible;
            }
            /* Esconde a seta para recolher a barra lateral */
            [data-testid="collapsedControl"] {
                display: none;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

# Configurações de autenticação
CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
TENANT_ID = os.getenv('AZURE_TENANT_ID')
CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_URI = "https://blutrafoscomercialmediatensao.streamlit.app"
SCOPES = ["User.Read"]

# Lê a variável de ambiente e converte para uma lista de e-mails permitidos
EMAILS_PERMITIDOS = os.getenv('EMAILS_PERMITIDOS', '').split(',')

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
                # Mostrar mensagem de erro e interromper a execução se o usuário não tiver permissão
                st.error("Você não tem permissão para acessar este aplicativo.")
                st.stop()

    # Verifica se há um código de autorização na URL após o redirecionamento
    query_params = st.experimental_get_query_params()
    if "code" in query_params:
        code = query_params["code"][0]  # Obtém o código de autorização da URL
        result = app.acquire_token_by_authorization_code(
            code=code,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        
        if "access_token" in result:
            email = result['id_token_claims']['preferred_username']
            if email in EMAILS_PERMITIDOS:
                st.experimental_set_query_params()  # Limpa o código da URL após a autenticação
                return True
            else:
                # Mostrar mensagem de erro e interromper a execução se o usuário não tiver permissão
                st.error("Você não tem permissão para acessar este aplicativo.")
                st.stop()
        else:
            st.error("Falha na autenticação. Por favor, tente novamente.")
            st.stop()

    # Se o usuário não estiver autenticado, redirecionar para a página de login
    auth_url = app.get_authorization_request_url(
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    st.markdown(f"[Clique aqui para entrar]({auth_url})")
    st.stop()  # Para a execução do código até que o usuário esteja autenticado

def verificar_acesso():
    if not autenticar_usuario():
        st.stop()  # Para a execução do código se o usuário não estiver autorizado

# Chama a verificação de acesso no início do código
verificar_acesso()

# Após a autenticação, exibe a barra lateral completamente expandida
exibir_barra_lateral(True)

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
        Bem-vindo à Proposta Automatizada de Média Tensão. Este sistema foi desenvolvido para 
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
