import streamlit as st
import pandas as pd
from config_db import conectar_banco
from auth import verificar_acesso 

verificar_acesso()

def verificar_dados_iniciais():
    # Verifica se 'dados_iniciais' existe no st.session_state e se todos os campos necessários estão preenchidos
    dados_iniciais = st.session_state.get('dados_iniciais', {})
    
    # Lista de campos obrigatórios
    campos_obrigatorios = ['cliente', 'nomeCliente', 'fone', 'email', 'bt', 'obra', 'dia', 'mes', 'ano', 'rev', 'local']
    
    # Verifica se todos os campos obrigatórios estão presentes e não estão vazios
    for campo in campos_obrigatorios:
        if not dados_iniciais.get(campo):
            return False  # Se algum campo estiver vazio, retorna False
    
    return True  # Todos os campos estão preenchidos


def pagina_dados_iniciais():

    # Verificação dos dados iniciais antes de prosseguir
    if verificar_dados_iniciais():
        st.success("Todos os dados iniciais foram preenchidos corretamente.")
        
        # Continue com o restante da lógica da página, como a exibição de tabelas ou formulários adicionais
        # Aqui você pode incluir a lógica para os itens configurados
    else:
        st.error("Por favor, preencha todos os campos obrigatórios nos dados iniciais na Pag1 antes de continuar.")

    # Adicione aqui o restante da lógica da página

# Função para buscar os dados do banco de dados e armazenar em cache
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

# Função para calcular o preço total
def calcular_preco_total(preco_unit, quantidade):
    return preco_unit * quantidade

# Inicializando as chaves de session_state
if 'itens_configurados' not in st.session_state:
    st.session_state['itens_configurados'] = []

# Título da página
st.title('Configuração de Itens')
st.markdown("---")

# Busca dos dados (otimizado com cache)
df = buscar_dados()

# Variáveis fixas (não aparecem para o usuário)
lucro = st.number_input('Lucro (%):', min_value=0.0, max_value=100.0, step=0.1, value=5.0)   # Convertendo para decimal
icms = st.number_input('ICMS (%):', min_value=0.0, max_value=100.0, step=0.1, value=12.0)  # Convertendo para decimal
frete = st.number_input('Frete (%):', min_value=0.0, step=0.1, value=5.0)
comissao = st.number_input('Comissão (%):', min_value=0.0, step=0.1, value=5.0)
irpj_cssl = 2.28 / 100  # Valor fixo
tkxadmmkt = 3.7 / 100  # Valor fixo
mocusfixo = 20 / 100    # Valor fixo
pisconfins = 9.25 / 100 # Valor fixo
p_caixa_24 = 0.30       # 30% para classe 24kV
p_caixa_36 = 0.50       # 50% para classe 36kV
valor_ip_baixo = df['valor_ip_baixo'].iloc[0]
valor_ip_alto = df['valor_ip_alto'].iloc[0]
p_caixa = df['p_caixa'].iloc[0]
percentuais_k = {
    1: 0.0,     # k4
    4: 0.052,   # k6
    6: 0.0917,  # k8
    13: 0.2317, # k13
    20: 0.3359  # k20
}

# Calcular percentuais como a soma dos valores em decimal
percentuais = (lucro / 100) + (icms / 100) + (comissao / 100) + (frete / 100) + irpj_cssl + tkxadmmkt + mocusfixo + pisconfins

# Seleção da quantidade de itens
quantidade_itens = st.number_input('Quantidade de Itens:', min_value=1, step=1, value=len(st.session_state['itens_configurados']) or 1)

# Criar ou ajustar os itens configurados no session_state
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
        'Derivações': "13,8/13,2/12,6/12,0/11,4",
        'Fator K': 1,
        'IP': '00',
        'Perdas': None,
        'Preço Unitário': 0.0,
        'Preço Total': 0.0,
        'IPI': 0.0,
    })

# Remover itens se a quantidade for reduzida
while len(st.session_state['itens_configurados']) > quantidade_itens:
    st.session_state['itens_configurados'].pop()

# Lista de opções para IP
opcoes_ip = ['00', '21', '23', '54']

# Fator K
fator_k_opcoes = [1, 4, 6, 8, 13]

# Exibição e ajustes dos itens
for item in range(len(st.session_state['itens_configurados'])):
    st.subheader(f"Item {item + 1}")

    # Modificando a lista de descrições para incluir uma opção em branco no início
    descricao_opcoes = [""] + df['descricao'].unique().tolist()

    # Seleção da descrição
    descricao_key = f'descricao_{item}'
    descricao_escolhida = st.selectbox(
        f'Digite ou Selecione a Descrição do Item {item + 1}:',
        descricao_opcoes,
        key=descricao_key,
        index=0 if st.session_state['itens_configurados'][item]['Descrição'] == "" else descricao_opcoes.index(st.session_state['itens_configurados'][item]['Descrição'])
    )

    # Atribuindo o ID do item selecionado
    if descricao_escolhida:
        id_item = df[df['descricao'] == descricao_escolhida]['id'].values[0]
        st.session_state['itens_configurados'][item]['ID'] = id_item
        st.session_state['itens_configurados'][item]['Descrição'] = descricao_escolhida

        # Preenchendo os detalhes a partir da descrição selecionada
        detalhes_item = df[df['descricao'] == descricao_escolhida].iloc[0]  # Definição da variável detalhes_item
        st.session_state['itens_configurados'][item]['Potência'] = detalhes_item['potencia']
        st.session_state['itens_configurados'][item]['Perdas'] = detalhes_item['perdas']
        st.session_state['itens_configurados'][item]['classe_tensao'] = detalhes_item['classe_tensao']  # Adicione esta linha

        # Variáveis para o cálculo
        preco_base = detalhes_item['preco']
        p_trafo = detalhes_item['p_trafo']

        # Calculando o Preço Unitário sem ajustes
        preco_unitario = preco_base / (1 - p_trafo - percentuais)
    else:
        preco_unitario = 0.0  # Resetar o preço unitário caso a descrição não seja escolhida

    # Campos de entrada
    tensao_primaria = st.text_input(f'Tensão Primária do Item {item + 1}:', key=f'tensao_primaria_{item}', value=st.session_state['itens_configurados'][item]['Tensão Primária'],placeholder="Digite apenas o valor sem unidade")
    tensao_secundaria = st.text_input(f'Tensão Secundária do Item {item + 1}:', key=f'tensao_secundaria_{item}', value=st.session_state['itens_configurados'][item]['Tensão Secundária'],placeholder="Digite apenas o valor sem unidade")
    derivacoes = st.text_input(f'Derivações do Item {item + 1}:', key=f'derivacoes_{item}', value=st.session_state['itens_configurados'][item]['Derivações'],placeholder="Digite apenas o valor sem unidade")

    # Salvar valores no session_state
    st.session_state['itens_configurados'][item]['Tensão Primária'] = tensao_primaria
    st.session_state['itens_configurados'][item]['Tensão Secundária'] = tensao_secundaria
    st.session_state['itens_configurados'][item]['Derivações'] = derivacoes

    # Campo de IP
    ip_escolhido = st.selectbox(
        f'Selecione o IP do Item {item + 1}:',
        opcoes_ip,
        key=f'ip_{item}',
        index=opcoes_ip.index(st.session_state['itens_configurados'][item]['IP'])
    )
    st.session_state['itens_configurados'][item]['IP'] = ip_escolhido

    # Campo de Fator K
    fator_k_escolhido = st.selectbox(
        f'Selecione o Fator K do Item {item + 1}:',
        fator_k_opcoes,
        key=f'fator_k_{item}',
        index=fator_k_opcoes.index(st.session_state['itens_configurados'][item]['Fator K'])
    )
    st.session_state['itens_configurados'][item]['Fator K'] = fator_k_escolhido

    # Ajustar o preço unitário de acordo com o Fator K escolhido
    if fator_k_escolhido in percentuais_k:
        ajuste_percentual = percentuais_k[fator_k_escolhido]
        preco_unitario *= (1 + ajuste_percentual)  # Ajustando o preço unitário

    # Calcular adicional_ip
    if ip_escolhido == '00':
        adicional_ip = 0.0
    else:
        if int(ip_escolhido) < 54:
            adicional_ip = valor_ip_baixo / (1 - percentuais - p_caixa)
        else:  # ip_escolhido >= 54
            adicional_ip = valor_ip_alto / (1 - percentuais - p_caixa)

        # Ajustar adicional_ip com base na classe de tensão
        classe_tensao = detalhes_item['classe_tensao']  # Captura a classe de tensão
        percentual_adicionado = 0  # Inicializa a variável para o percentual

        if classe_tensao == "24 kV":
            percentual_adicionado = p_caixa_24 * adicional_ip  # 30% do adicional_ip
        elif classe_tensao == "36 kV":
            percentual_adicionado = p_caixa_36 * adicional_ip  # 50% do adicional_ip

        adicional_ip += percentual_adicionado  # Adiciona o percentual ao valor total

        # Somar adicional_ip ao preco_unitario
        preco_unitario += adicional_ip

    # Salvar o preço unitário ajustado no session_state
    st.session_state['itens_configurados'][item]['Preço Unitário'] = preco_unitario


    # Quantidade de cada item
    quantidade = st.number_input(
        f'Quantidade para o Item {item + 1}:',
        min_value=1,
        value=st.session_state['itens_configurados'][item]['Quantidade'],
        step=1,
        key=f'qtd_{item}'
    )
    st.session_state['itens_configurados'][item]['Quantidade'] = quantidade
    ipi = st.number_input(f'IPI do Item {item + 1} (%):', min_value=0.0, step=0.1, value=0.0, key=f'ipi_{item}')
    st.session_state['itens_configurados'][item]['IPI'] = ipi  # Armazena o valor de IPI

    # Calculando o Preço Total
    preco_total = calcular_preco_total(preco_unitario, quantidade)
    st.session_state['itens_configurados'][item]['Preço Total'] = preco_total

    st.markdown("---")

# Mostrar a tabela de resumo
st.subheader("Resumo dos Itens Selecionados")
resumo_df = pd.DataFrame(st.session_state['itens_configurados'])

# Ajustar a exibição para mostrar Potência Formatada e Tensão Primária / Secundária
resumo_df['Potência'] = resumo_df['Potência'].apply(lambda x: f"{x:,.0f} kVA" if x is not None else "")
resumo_df['Tensões'] = resumo_df['Tensão Primária'] + "kV" + " / " + resumo_df['Tensão Secundária'] + " V"
resumo_df = resumo_df[['Item', 'Quantidade', 'Potência', 'Tensões', 'Perdas', 'Fator K', 'IP', 'Preço Unitário', 'Preço Total']]

# Exibir a tabela ajustada
st.table(resumo_df)

# Armazenar o resumo_df no session_state para ser acessado na Pag3
st.session_state['resumo_df'] = resumo_df  # Isso garante que o resumo_df seja acessível na Pag3

st.markdown("---")

# Soma do preço total
total_fornecimento = resumo_df['Preço Total'].sum()
st.subheader(f"Valor Total do Fornecimento: R$ {total_fornecimento:,.2f}")