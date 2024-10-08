import os
import streamlit as st
from msal import ConfidentialClientApplication, SerializableTokenCache

CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
TENANT_ID = os.getenv('AZURE_TENANT_ID')
CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_URI = "http://localhost:8501"  # Ajuste conforme o seu ambiente
SCOPES = ["User.Read"]

def init_app():
    return ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )

def autenticar_usuario():
    app = init_app()
    token_cache = SerializableTokenCache()
    accounts = app.get_accounts()

    # Tenta autenticar de forma silenciosa se o usuário já estiver logado no navegador
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            email = result['id_token_claims']['preferred_username']
            return email

    # Se a autenticação silenciosa falhar, redirecionar para a página de login
    auth_url = app.get_authorization_request_url(
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    st.markdown(f"[Clique aqui para entrar]({auth_url})")
    return None
