import streamlit as st
from datetime import datetime

st.set_page_config(layout="wide")

def aplicar_mascara_telefone():
    telefone = ''.join(filter(str.isdigit, st.session_state['fone_raw']))  # Remove todos os caracteres que não são dígitos
    if len(telefone) == 11:
        telefone_formatado = f"({telefone[:2]}) 9 {telefone[2:7]}-{telefone[7:]}"
    elif len(telefone) == 10:
        telefone_formatado = f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
    else:
        telefone_formatado = telefone
    st.session_state['dados_iniciais']['fone'] = telefone_formatado

def configurar_informacoes():
    st.title('Dados Iniciais')
    st.markdown("---")
    
    # Campo para a data da proposta
    data_hoje = datetime.today()
    data_selecionada = st.date_input('Data da Proposta:', value=data_hoje)

    # Mapeando o número do mês para o nome em português
    meses_pt = [
        "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", 
        "Junho", "Julho", "Agosto", "Setembro", "Outubro", 
        "Novembro", "Dezembro"
    ]
    
    # Criação de duas colunas, cada uma ocupando 50% do espaço
    col1, col2 = st.columns(2)

    if 'dados_iniciais' not in st.session_state:
        st.session_state['dados_iniciais'] = {}
    
    with col1:
        st.session_state['dados_iniciais'].update({
            'dia': data_selecionada.strftime('%d'),
            'mes': meses_pt[data_selecionada.month],
            'ano': data_selecionada.strftime('%Y'),
            'bt': st.text_input('Nº BT:', st.session_state['dados_iniciais'].get('bt', ''), autocomplete='off'),
            'rev': st.text_input('Rev:', st.session_state['dados_iniciais'].get('rev', ''), autocomplete='off'),
            'cliente': st.text_input('Cliente:', st.session_state['dados_iniciais'].get('cliente', ''), autocomplete='off',placeholder='Digite o nome da empresa'),
            'obra': st.text_input('Obra:', st.session_state['dados_iniciais'].get('obra', ''), autocomplete='off'),
           
            

            
        })

    with col2:
        # Captura o valor original do telefone para aplicação da máscara
        st.session_state['dados_iniciais'].update({
             'nomeCliente': st.text_input('Nome do Contato:', st.session_state['dados_iniciais'].get('nomeCliente', ''), autocomplete='off',placeholder='Digite o nome do contato dentro da empresa'),
            'email': st.text_input('E-mail do Contato:', st.session_state['dados_iniciais'].get('email', ''), autocomplete='off'),
            'local': st.text_input('Local de Entrega: ', st.session_state['dados_iniciais'].get('local', ''), autocomplete='off',placeholder='Digite o local da entrega neste formato: Cidade/Estado')
        })
        st.text_input(
            'Telefone do Contato:', 
            value=st.session_state['dados_iniciais'].get('fone', ''), 
            max_chars=15, 
            autocomplete='off', 
            key='fone_raw', 
            on_change=aplicar_mascara_telefone,placeholder="Digite sem formação, exemplo: 47999998888"
        )
        

# Chamada para configurar as informações na interface
configurar_informacoes()
