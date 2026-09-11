import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Finanças Pro", page_icon="💰", layout="wide"
)

# Estilo CSS Customizado para um visual moderno
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
    }
    .metric-card {
        background-color: #1e222a;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Inicialização do Banco de Dados em Memória (Session State)
if "transacoes" not in st.session_state:
    st.session_state.transacoes = pd.DataFrame(
        columns=[
            "Data",
            "Tipo",
            "Categoria",
            "Descrição",
            "Valor",
            "Conta/Cartão",
        ]
    )
    # Dados de exemplo iniciais
    dados_iniciais = [
        [
            datetime.date(2026, 9, 1),
            "Receita",
            "Salário",
            "Empresa X",
            5500.00,
            "Conta Corrente",
        ],
        [
            datetime.date(2026, 9, 3),
            "Despesa",
            "Moradia",
            "Aluguel",
            1500.00,
            "Conta Corrente",
        ],
        [
            datetime.date(2026, 9, 5),
            "Despesa",
            "Alimentação",
            "Supermercado",
            450.50,
            "Cartão de Crédito",
        ],
        [
            datetime.date(2026, 9, 10),
            "Receita",
            "Freelance",
            "Projeto Web",
            1200.00,
            "Conta Corrente",
        ],
    ]
    st.session_state.transacoes = pd.DataFrame(
        dados_iniciais, columns=st.session_state.transacoes.columns
    )

# --- MENU LATERAL ---
st.sidebar.title("💰 Finanças Pro")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navegação",
    ["📊 Dashboard", "📝 Lançamentos", "🏷️ Categorias", "⚙️ Configurações"],
)

# --- ABA 1: DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("Visão Geral Financeira")
    st.markdown("Acompanhe seus principais indicadores em tempo real.")

    df = st.session_state.transacoes

    if df.empty:
        st.warning(
            "Nenhuma transação cadastrada ainda. Vá em 'Lançamentos' para"
            " adicionar."
        )
    else:
        # Filtros por Período / Mês
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            tipo_filtro = st.selectbox(
                "Filtrar por Tipo", ["Todos", "Receita", "Despesa"]
            )

        df_filtrado = df.copy()
        if tipo_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Tipo"] == tipo_filtro]

        # Métricas Principais
        total_receitas = df[df["Tipo"] == "Receita"]["Valor"].sum()
        total_despesas = df[df["Tipo"] == "Despesa"]["Valor"].sum()
        saldo_total = total_receitas - total_despesas

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="Receitas Totais", value=f"R$ {total_receitas:,.2f}"
            )
        with col2:
            st.metric(
                label="Despesas Totais", value=f"R$ {total_despesas:,.2f}"
            )
        with col3:
            st.metric(label="Saldo Líquido", value=f"R$ {saldo_total:,.2f}")

        st.markdown("---")

        # Gráficos
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("Despesas por Categoria")
            df_despesas = df[df["Tipo"] == "Despesa"]
            if not df_despesas.empty:
                fig_cat = px.pie(
                    df_despesas,
                    names="Categoria",
                    values="Valor",
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.RdBu,
                )
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("Sem despesas para exibir no gráfico.")

        with c2:
            st.subheader("Evolução / Transações por Data")
            if not df.empty:
                fig_bar = px.bar(
                    df,
                    x="Data",
                    y="Valor",
                    color="Tipo",
                    barmode="group",
                    color_discrete_map={
                        "Receita": "#2ecc71",
                        "Despesa": "#e74c3c",
                    },
                )
                st.plotly_chart(fig_bar, use_container_width=True)

        # Tabela Detalhada
        st.subheader("Histórico de Transações")
        st.dataframe(df_filtrado, use_container_width=True)

# --- ABA 2: LANÇAMENTOS ---
elif menu == "📝 Lançamentos":
    st.title("Novo Lançamento")
    st.markdown("Adicione novas receitas ou despesas ao seu fluxo.")

    with st.form("form_transacao", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
            categoria = st.selectbox(
                "Categoria",
                [
                    "Salário",
                    "Freelance",
                    "Investimentos",
                    "Moradia",
                    "Alimentação",
                    "Transporte",
                    "Lazer",
                    "Outros",
                ],
            )
            descricao = st.text_input("Descrição")

        with col2:
            valor = st.number_input(
                "Valor (R$)", min_value=0.01, format="%.2f"
            )
            data = st.date_input("Data", datetime.date.today())
            conta = st.selectbox(
                "Conta / Cartão",
                ["Conta Corrente", "Cartão de Crédito", "Dinheiro", "Poupança"],
            )

        enviar = st.form_submit_button("Salvar Transação")

        if enviar:
            nova_linha = pd.DataFrame(
                [[data, tipo, categoria, descricao, valor, conta]],
                columns=st.session_state.transacoes.columns,
            )
            st.session_state.transacoes = pd.concat(
                [st.session_state.transacoes, nova_linha], ignore_index=True
            )
            st.success("Transação cadastrada com sucesso!")

    st.markdown("---")
    st.subheader("Gerenciar Lançamentos Existentes")
    if not st.session_state.transacoes.empty:
        st.dataframe(
            st.session_state.transacoes, use_container_width=True
        )
        if st.button("Limpar Última Transação"):
            st.session_state.transacoes = (
                st.session_state.transacoes.iloc[:-1]
            )
            st.rerun()

# --- ABA 3: CATEGORIAS ---
elif menu == "🏷️ Categorias":
    st.title("Gerenciamento de Categorias")
    st.markdown("Visualize as categorias ativas no sistema.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Categorias de Receita")
        st.write("- Salário")
        st.write("- Freelance")
        st.write("- Investimentos")
        st.write("- Outros")

    with col2:
        st.subheader("Categorias de Despesa")
        st.write("- Moradia")
        st.write("- Alimentação")
        st.write("- Transporte")
        st.write("- Lazer")
        st.write("- Outros")

# --- ABA 4: CONFIGURAÇÕES ---
elif menu == "⚙️ Configurações":
    st.title("Configurações do Sistema")
    st.markdown("Gerencie dados e preferências do aplicativo.")

    if st.button("Resetar Todos os Dados (Zerar Sistema)"):
        st.session_state.transacoes = pd.DataFrame(
            columns=[
                "Data",
                "Tipo",
                "Categoria",
                "Descrição",
                "Valor",
                "Conta/Cartão",
            ]
        )
        st.success("Dados resetados com sucesso!")
        st.rerun()

