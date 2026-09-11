import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Finance 105 - Fluxo Pro", page_icon="💰", layout="wide"
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
    # Dados iniciais de exemplo
    dados_iniciais = [
        [
            datetime.date(2026, 9, 1),
            "Receita",
            "Salário",
            "Empresa Principal",
            6500.00,
            "Conta Corrente",
        ],
        [
            datetime.date(2026, 9, 3),
            "Despesa",
            "Moradia",
            "Aluguel",
            1600.00,
            "Conta Corrente",
        ],
        [
            datetime.date(2026, 9, 5),
            "Despesa",
            "Alimentação",
            "Supermercado Mensal",
            600.50,
            "Cartão de Crédito",
        ],
    ]
    st.session_state.transacoes = pd.DataFrame(
        dados_iniciais, columns=st.session_state.transacoes.columns
    )

if "categorias" not in st.session_state:
    st.session_state.categorias = [
        "Salário",
        "Freelance",
        "Investimentos",
        "Moradia",
        "Alimentação",
        "Transporte",
        "Lazer",
        "Outros",
    ]

if "contas" not in st.session_state:
    st.session_state.contas = [
        "Conta Corrente",
        "Cartão de Crédito",
        "Dinheiro",
        "Poupança",
    ]

# --- MENU LATERAL ---
st.sidebar.title("🚀 Finance 105")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navegação",
    [
        "📊 Dashboard",
        "📝 Lançamentos",
        "📋 Cadastro (Form)",
        "🏷️ Gerenciar Categorias",
    ],
)

# --- ABA 1: DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("Visão Geral Executiva")
    st.markdown("Acompanhe seus indicadores e fluxo financeiro em tempo real.")

    df = st.session_state.transacoes

    if df.empty:
        st.warning(
            "Nenhuma transação cadastrada. Vá em 'Lançamentos' ou 'Cadastro"
            " (Form)' para adicionar."
        )
    else:
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
                st.info("Sem despesas para exibir.")

        with c2:
            st.subheader("Evolução por Data")
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

        st.subheader("Histórico Consolidado")
        st.dataframe(df, use_container_width=True)

# --- ABA 2: LANÇAMENTOS ---
elif menu == "📝 Lançamentos":
    st.title("Lançamento Rápido")
    st.markdown("Registre entradas e saídas de forma ágil.")

    with st.form("form_lancamento", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
            categoria = st.selectbox(
                "Categoria", st.session_state.categorias
            )
            descricao = st.text_input("Descrição")
        with col2:
            valor = st.number_input(
                "Valor (R$)", min_value=0.01, format="%.2f"
            )
            data = st.date_input("Data", datetime.date.today())
            conta = st.selectbox("Conta / Cartão", st.session_state.contas)

        enviar = st.form_submit_button("Salvar Lançamento")
        if enviar:
            nova_linha = pd.DataFrame(
                [[data, tipo, categoria, descricao, valor, conta]],
                columns=st.session_state.transacoes.columns,
            )
            st.session_state.transacoes = pd.concat(
                [st.session_state.transacoes, nova_linha], ignore_index=True
            )
            st.success("Lançamento salvo com sucesso!")

# --- ABA 3: CADASTRO (FORM) ---
elif menu == "📋 Cadastro (Form)":
    st.title("Tela de Cadastro Avançado")
    st.markdown(
        "Cadastre novas contas, fontes de receita ou parâmetros operacionais"
        " do sistema."
    )

    tab_cad1, tab_cad2 = st.tabs(["Nova Conta / Cartão", "Nova Categoria"])

    with tab_cad1:
        st.subheader("Adicionar Nova Conta ou Cartão")
        nova_conta = st.text_input("Nome da Conta ou Cartão (Ex: Nubank, Itaú)")
        if st.button("Cadastrar Conta"):
            if nova_conta and nova_conta not in st.session_state.contas:
                st.session_state.contas.append(nova_conta)
                st.success(
                    f"Conta '{nova_conta}' cadastrada com sucesso na lista de"
                    " opções!"
                )
            else:
                st.warning("Insira um nome válido ou que já não exista.")

    with tab_cad2:
        st.subheader("Adicionar Nova Categoria")
        nova_cat = st.text_input(
            "Nome da Categoria (Ex: Educação, Assinaturas)"
        )
        if st.button("Cadastrar Categoria"):
            if nova_cat and nova_cat not in st.session_state.categorias:
                st.session_state.categorias.append(nova_cat)
                st.success(f"Categoria '{nova_cat}' adicionada com sucesso!")
            else:
                st.warning("Insira uma categoria válida ou existente.")

# --- ABA 4: GERENCIAR CATEGORIAS ---
elif menu == "🏷️ Gerenciar Categorias":
    st.title("Painel de Categorias e Contas")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Categorias Cadastradas")
        for cat in st.session_state.categorias:
            st.write(f"- {cat}")
    with col2:
        st.subheader("Contas e Cartões Cadastrados")
        for c in st.session_state.contas:
            st.write(f"- {c}")
