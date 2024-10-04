import os
import streamlit as st
from io import BytesIO
from replace import inserir_tabelas_word
from docx import Document
from sharepoint_code import SharePoint  # Classe SharePoint para baixar o template

st.set_page_config(layout="wide")

# Função para gerar o documento e retornar o conteúdo em memória
def gerar_documento():
    # Instância da classe SharePoint
    sp = SharePoint()

    # Nome do arquivo template no SharePoint
    template_name = 'Template_Proposta_Comercial.docx'

    # 1. Fazer o download do template do SharePoint
    template_path = sp.download_file(template_name)  # Agora baixamos o template e salvamos localmente em "/tmp"

    # Nome do arquivo de saída
    output_filename = f"Proposta Blutrafos nº BT {st.session_state['dados_iniciais']['bt']}-Rev{st.session_state['dados_iniciais']['rev']}.docx"
    
    # Dicionário de substituições
    replacements = {
        '{{CLIENTE}}': st.session_state['dados_iniciais'].get('cliente', ''),
        '{{NOMECLIENTE}}': st.session_state['dados_iniciais'].get('nomeCliente', ''),
        '{{FONE}}': st.session_state['dados_iniciais'].get('fone', ''),
        '{{EMAIL}}': st.session_state['dados_iniciais'].get('email', ''),
        '{{BT}}': st.session_state['dados_iniciais'].get('bt', ''),
        '{{OBRA}}': st.session_state['dados_iniciais'].get('obra', ''),
        '{{DIA}}': st.session_state['dados_iniciais'].get('dia', ''),
        '{{MES}}': st.session_state['dados_iniciais'].get('mes', ''),
        '{{ANO}}': st.session_state['dados_iniciais'].get('ano', ''),
        '{{REV}}': st.session_state['dados_iniciais'].get('rev', ''),
        '{{LOCAL}}': st.session_state['dados_iniciais'].get('local', '')
    }

    itens_configurados = st.session_state.get('itens_configurados', [])

    # Verifica se os dados necessários estão preenchidos
    if itens_configurados:
        # Criar o documento em memória (BytesIO)
        buffer = BytesIO()

        try:
            # Carrega o template do documento Word baixado do SharePoint
            doc = Document(template_path)  # Usando o caminho local temporário do arquivo

            # Chama a função para inserir as tabelas e substituir o conteúdo no documento
            doc = inserir_tabelas_word(doc, itens_configurados, '', replacements)  # Certifique-se de passar todos os argumentos corretamente
            doc.save(buffer)  # Salva o documento em memória
            
            buffer.seek(0)  # Move o ponteiro para o início do buffer
            return buffer, output_filename
        
        except Exception as e:
            st.error(f"Erro ao gerar o documento: {e}")
            return None, None
    else:
        st.error("Por favor, preencha todos os itens antes de gerar o documento.")
        return None, None