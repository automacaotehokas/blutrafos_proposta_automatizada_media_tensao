import os
import streamlit as st
from io import BytesIO
from replace import inserir_tabelas_word
from docx import Document
from sharepoint_code import SharePoint  # Classe SharePoint para baixar o template
from auth import verificar_acesso 

verificar_acesso()
st.set_page_config(layout="wide")

# Função para baixar o template uma vez e reutilizá-lo
def get_template_file():
    # Verifica se o template já foi baixado
    local_template_path = "/tmp/Template_Proposta_Comercial.docx"
    
    if not os.path.exists(local_template_path):
        # Se o template não foi baixado, faz o download do SharePoint
        sp = SharePoint()
        template_name = 'Template_Proposta_Comercial.docx'
        local_template_path = sp.download_file(template_name)
    
    return local_template_path

# Função para gerar o documento e retornar o conteúdo em memória
def gerar_documento():
    # Pegar o template (baixar se ainda não baixado)
    template_path = get_template_file()

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

    # Garantir que os itens configurados estejam no st.session_state
    itens_configurados = st.session_state.get('itens_configurados', [])

    if not itens_configurados:
        st.error("Por favor, preencha todos os itens antes de gerar o documento.")
        return None, None

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

# Função para verificar se os dados estão completos
def verificar_dados_completos():
    dados_iniciais = st.session_state.get('dados_iniciais', {})
    itens_configurados = st.session_state.get('itens_configurados', [])

    # Lista de campos obrigatórios em dados_iniciais
    campos_obrigatorios = ['cliente', 'nomeCliente', 'fone', 'email', 'bt', 'obra', 'dia', 'mes', 'ano', 'rev', 'local']
    
    # Verifica se algum campo obrigatório está vazio
    for campo in campos_obrigatorios:
        if not dados_iniciais.get(campo):
            return False

    # Verifica se os itens estão configurados
    if not itens_configurados:
        return False

    return True  # Tudo preenchido corretamente

# Página para gerar o documento
def pagina_gerar_documento():
    st.title("Resumo")
    st.markdown("---")

    # Verifica se os dados da Pag1 estão preenchidos
    if 'dados_iniciais' not in st.session_state:
        st.error("Por favor, preencha os dados na Pag1 antes de gerar o documento.")
        return  # Saia da função se os dados não estiverem presentes

    # Resumo da Pag1 como uma ficha
    st.subheader("Dados Iniciais")
    st.write("**Cliente:**", st.session_state['dados_iniciais'].get('cliente', ''))
    st.write("**Nome do Cliente:**", st.session_state['dados_iniciais'].get('nomeCliente', ''))
    st.write("**Telefone:**", st.session_state['dados_iniciais'].get('fone', ''))
    st.write("**Email:**", st.session_state['dados_iniciais'].get('email', ''))
    st.write("**BT:**", st.session_state['dados_iniciais'].get('bt', ''))
    st.write("**Obra:**", st.session_state['dados_iniciais'].get('obra', ''))
    st.write("**Data:**", f"{st.session_state['dados_iniciais'].get('dia', '')}/{st.session_state['dados_iniciais'].get('mes', '')}/{st.session_state['dados_iniciais'].get('ano', '')}")
    st.write("**Revisão:**", st.session_state['dados_iniciais'].get('rev', ''))
    st.write("**Local:**", st.session_state['dados_iniciais'].get('local', ''))

    st.markdown("---")

    # Mostrando as informações configuradas na Pag2
    st.subheader("Itens Configurados")
    
    # Referenciando o resumo_df armazenado na Pag2
    resumo_df = st.session_state.get('resumo_df', None)
    if resumo_df is not None:
        st.table(resumo_df)  # Exibe a tabela de itens configurados
    else:
        st.write("Nenhum item configurado.")

    # Verificar se todos os dados obrigatórios estão preenchidos
    dados_completos = verificar_dados_completos()
    st.write("O botão abaixo estará disponível após o preenchimento de todos os dados anteriores")

    # Gerar e baixar o documento em um único botão
    if st.button('Confirmar', disabled=not dados_completos):
        if dados_completos:
            buffer, output_filename = gerar_documento()
            if buffer:
                # Oferecer o download diretamente após a geração
                st.download_button(
                    label="Clique para Baixar o Documento",
                    data=buffer,
                    file_name=output_filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            else:
                st.error("Erro ao gerar o documento.")
        else:
            st.error("Por favor, preencha todos os campos obrigatórios antes de gerar o documento.")

# Chama a função da Pag3
pagina_gerar_documento()
