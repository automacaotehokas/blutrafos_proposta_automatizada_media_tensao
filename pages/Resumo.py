import streamlit as st
from io import BytesIO
from datetime import datetime
from replace import inserir_tabelas_word  # Certifique-se de importar a função correta do replace.py
from docx import Document  # Certifique-se de ter o módulo 'python-docx' instalado

st.set_page_config(layout="wide") 

# Função para gerar o documento e retornar o conteúdo em memória
def gerar_documento():
    # Caminho para o template
    template_path = "Template_Proposta_Comercial.docx"
    
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
            # Carrega o template do documento Word
            doc = Document(template_path)

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

# Página 3 para gerar o documento
def pagina_gerar_documento():
    st.title("Resumo")

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

    # Mostrando as informações configuradas na Pag2
    st.subheader("Itens")
    
    # Referenciando o resumo_df armazenado na Pag2
    resumo_df = st.session_state.get('resumo_df', None)
    if resumo_df is not None:
        st.table(resumo_df)  # Exibe a tabela de itens configurados
    else:
        st.write("Nenhum item configurado.")

    # Verificar se todos os dados obrigatórios estão preenchidos
    dados_completos = verificar_dados_completos()

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
