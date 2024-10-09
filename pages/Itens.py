import streamlit as st
import pandas as pd
from config_db import conectar_banco
from auth import verificar_acesso 

verificar_acesso()

def verificar_dados_iniciais():
    dados_iniciais = st.session_state.get('dados_iniciais', {})
    campos_obrigatorios = ['cliente', 'nomeCliente', 'fone', 'email', 'bt',  'dia', 'mes', 'ano', 'rev', 'local']
    for campo in campos_obrigatorios:
        if not dados_iniciais.get(campo):
            return False
    return True

def pagina_dados_iniciais():
    if verificar_dados_iniciais():
        st.success("Todos os dados iniciais foram preenchidos corretamente.")
    else:
        st.error("Por favor, preencha todos os campos obrigatórios nos dados iniciais na Pag1 antes de continuar.")

@st.cache_data
def buscar_dados():
    conn = conectar_banco()
    query = """
        SELECT id, descricao, potencia, classe_tensao, perdas, preco, p_trafo, valor_ip_baixo, valor_ip_alto, p_caixa
        FROM custos_media_tensao
        ORDER BY descricao ASC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def calcular_preco_total(preco_unit, quantidade):
    return preco_unit * quantidade

# Inicializando as variáveis no session_state
if 'itens_configurados' not in st.session_state:
    st.session_state['itens_configurados'] = []

if 'frete' not in st.session_state:
    st.session_state['frete'] = 5.0
if 'icms' not in st.session_state:
    st.session_state['icms'] = 12.0
if 'lucro' not in st.session_state:
    st.session_state['lucro'] = 5.0
if 'comissao' not in st.session_state:
    st.session_state['comissao'] = 5.0

# Título da página
st.title('Configuração de Itens')
st.markdown("---")

df = buscar_dados()

st.session_state['lucro'] = st.number_input('Lucro (%):', min_value=0.0, max_value=100.0, step=0.1, value=st.session_state['lucro'])
st.session_state['icms'] = st.number_input('ICMS (%):', min_value=0.0, max_value=100.0, step=0.1, value=st.session_state['icms'])
st.session_state['frete'] = st.number_input('Frete (%):', min_value=0.0, step=0.1, value=st.session_state['frete'])
st.session_state['comissao'] = st.number_input('Comissão (%):', min_value=0.0, step=0.1, value=st.session_state['comissao'])

irpj_cssl = 2.28 / 100
tkxadmmkt = 3.7 / 100
mocusfixo = 20 / 100
pisconfins = 9.25 / 100
p_caixa_24 = 0.30
p_caixa_36 = 0.50
valor_ip_baixo = df['valor_ip_baixo'].iloc[0]
valor_ip_alto = df['valor_ip_alto'].iloc[0]
p_caixa = df['p_caixa'].iloc[0]
percentuais_k = {
    1: 0.0,
    4: 0.052,
    6: 0.0917,
    13: 0.2317,
    20: 0.3359
}

percentuais = (st.session_state['lucro'] / 100) + (st.session_state['icms'] / 100) + \
              (st.session_state['comissao'] / 100) + (st.session_state['frete'] / 100) + \
              irpj_cssl + tkxadmmkt + mocusfixo + pisconfins

quantidade_itens = st.number_input('Quantidade de Itens:', min_value=1, step=1, value=len(st.session_state['itens_configurados']) or 1)

while len(st.session_state['itens_configurados']) < quantidade_itens:
    item_index = len(st.session_state['itens_configurados'])
    st.session_state['itens_configurados'].append({
        'ID': None,
        'Item': item_index + 1,
        'Quantidade': 1,
        'Descrição': "",
        'Potência': None,
        'Tensão Primária': None,
        'Tensão Secundária': None,
        'Derivações': "",
        'Fator K': 1,
        'IP': '00',
        'Perdas': None,
        'Preço Unitário': 0.0,
        'Preço Total': 0.0,
        'IPI': 0.0,
    })

while len(st.session_state['itens_configurados']) > quantidade_itens:
    st.session_state['itens_configurados'].pop()

opcoes_ip = ['00', '21', '23', '54']
fator_k_opcoes = [1, 4, 6, 8, 13]

for item in range(len(st.session_state['itens_configurados'])):
    st.subheader(f"Item {item + 1}")

    descricao_opcoes = [""] + df['descricao'].unique().tolist()
    descricao_key = f'descricao_{item}'
    descricao_escolhida = st.selectbox(
        f'Digite ou Selecione a Descrição do Item {item + 1}:',
        descricao_opcoes,
        key=descricao_key,
        index=0 if st.session_state['itens_configurados'][item]['Descrição'] == "" else descricao_opcoes.index(st.session_state['itens_configurados'][item]['Descrição'])
    )

    if descricao_escolhida:
        id_item = df[df['descricao'] == descricao_escolhida]['id'].values[0]
        st.session_state['itens_configurados'][item]['ID'] = id_item
        st.session_state['itens_configurados'][item]['Descrição'] = descricao_escolhida

        detalhes_item = df[df['descricao'] == descricao_escolhida].iloc[0]
        st.session_state['itens_configurados'][item]['Potência'] = detalhes_item['potencia']
        st.session_state['itens_configurados'][item]['Perdas'] = detalhes_item['perdas']
        st.session_state['itens_configurados'][item]['classe_tensao'] = detalhes_item['classe_tensao']

        # Configurando valores padrão com base na classe de tensão
        if detalhes_item['classe_tensao'] == "15 kV":
            tensao_primaria_default = "13.8"
            tensao_secundaria_default = "380"
            derivacoes_default = "13,8/13,2/12,6/12,0/11,4"
        elif detalhes_item['classe_tensao'] == "24 kV":
            tensao_primaria_default = "23.1"
            tensao_secundaria_default = "380"
            derivacoes_default = "23,1/22,0/20,9"
        elif detalhes_item['classe_tensao'] == "36 kV":
            tensao_primaria_default = "34.5"
            tensao_secundaria_default = "380"
            derivacoes_default = "+/- 2x2,5%"
        else:
            tensao_primaria_default = ""
            tensao_secundaria_default = ""
            derivacoes_default = ""

        # Se os valores estiverem vazios, define os padrões
        if not st.session_state['itens_configurados'][item]['Tensão Primária']:
            st.session_state['itens_configurados'][item]['Tensão Primária'] = tensao_primaria_default
        if not st.session_state['itens_configurados'][item]['Tensão Secundária']:
            st.session_state['itens_configurados'][item]['Tensão Secundária'] = tensao_secundaria_default
        if not st.session_state['itens_configurados'][item]['Derivações']:
            st.session_state['itens_configurados'][item]['Derivações'] = derivacoes_default

        preco_base = detalhes_item['preco']
        p_trafo = detalhes_item['p_trafo']

        preco_unitario = preco_base / (1 - p_trafo - percentuais)
    else:
        preco_unitario = 0.0

    tensao_primaria = st.text_input(f'Tensão Primária do Item {item + 1}:', key=f'tensao_primaria_{item}', value=st.session_state['itens_configurados'][item]['Tensão Primária'])
    tensao_secundaria = st.text_input(f'Tensão Secundária do Item {item + 1}:', key=f'tensao_secundaria_{item}', value=st.session_state['itens_configurados'][item]['Tensão Secundária'])
    derivacoes = st.text_input(f'Derivações do Item {item + 1}:', key=f'derivacoes_{item}', value=st.session_state['itens_configurados'][item]['Derivações'])

    st.session_state['itens_configurados'][item]['Tensão Primária'] = tensao_primaria
    st.session_state['itens_configurados'][item]['Tensão Secundária'] = tensao_secundaria
    st.session_state['itens_configurados'][item]['Derivações'] = derivacoes

    ip_escolhido = st.selectbox(
        f'Selecione o IP do Item {item + 1}:',
        opcoes_ip,
        key=f'ip_{item}',
        index=opcoes_ip.index(st.session_state['itens_configurados'][item]['IP'])
    )
    st.session_state['itens_configurados'][item]['IP'] = ip_escolhido

    fator_k_escolhido = st.selectbox(
        f'Selecione o Fator K do Item {item + 1}:',
        fator_k_opcoes,
        key=f'fator_k_{item}',
        index=fator_k_opcoes.index(st.session_state['itens_configurados'][item]['Fator K'])
    )
    st.session_state['itens_configurados'][item]['Fator K'] = fator_k_escolhido

    if fator_k_escolhido in percentuais_k:
        ajuste_percentual = percentuais_k[fator_k_escolhido]
        preco_unitario *= (1 + ajuste_percentual)

    if ip_escolhido == '00':
        adicional_ip = 0.0
    else:
        if int(ip_escolhido) < 54:
            adicional_ip = valor_ip_baixo / (1 - percentuais - p_caixa)
        else:
            adicional_ip = valor_ip_alto / (1 - percentuais - p_caixa)

        classe_tensao = detalhes_item['classe_tensao']
        percentual_adicionado = 0

        if classe_tensao == "24 kV":
            percentual_adicionado = p_caixa_24 * adicional_ip
        elif classe_tensao == "36 kV":
            percentual_adicionado = p_caixa_36 * adicional_ip

        adicional_ip += percentual_adicionado
        preco_unitario += adicional_ip

    st.session_state['itens_configurados'][item]['Preço Unitário'] = preco_unitario

    quantidade = st.number_input(
        f'Quantidade para o Item {item + 1}:',
        min_value=1,
        value=st.session_state['itens_configurados'][item]['Quantidade'],
        step=1,
        key=f'qtd_{item}'
    )
    st.session_state['itens_configurados'][item]['Quantidade'] = quantidade
    ipi = st.number_input(f'IPI do Item {item + 1} (%):', min_value=0.0, step=0.1, value=0.0, key=f'ipi_{item}')
    st.session_state['itens_configurados'][item]['IPI'] = ipi

    preco_total = calcular_preco_total(preco_unitario, quantidade)
    st.session_state['itens_configurados'][item]['Preço Total'] = preco_total

    st.markdown("---")

st.subheader("Resumo dos Itens Selecionados")
resumo_df = pd.DataFrame(st.session_state['itens_configurados'])

resumo_df['Potência'] = resumo_df['Potência'].apply(lambda x: f"{x:,.0f} kVA" if x is not None else "")
resumo_df['Tensões'] = resumo_df['Tensão Primária'] + "kV" + " / " + resumo_df['Tensão Secundária'] + " V"
resumo_df = resumo_df[['Item', 'Quantidade', 'Potência', 'Tensões', 'Perdas', 'Fator K', 'IP', 'Preço Unitário', 'Preço Total']]

st.table(resumo_df)

st.session_state['resumo_df'] = resumo_df

st.markdown("---")

total_fornecimento = resumo_df['Preço Total'].sum()
st.subheader(f"Valor Total do Fornecimento: R$ {total_fornecimento:,.2f}")
