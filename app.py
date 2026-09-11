elif aba == "Cadastro (Form)":
    st.subheader("📝 Novo Registro (Formulário de Cadastro)")
    st.markdown("Preencha os campos abaixo para registrar receitas, despesas ou transferências com suporte a parcelamento e criação dinâmica de categorias e cartões.")

    # 1. Tipo e Status do Lançamento
    col_a, col_b = st.columns(2)
    with col_a:
        tipo = st.selectbox("Tipo", ["Despesa", "Receita", "Transferência"])
    with col_b:
        status = st.selectbox("Status / Fase", ["Budget", "Efetivado"])
        
    descricao = st.text_input("Descrição", placeholder="Ex: Supermercado, Aluguel, Salário...")
    
    # 2. Gerenciamento de Categorias Dinâmicas
    if "categorias" not in st.session_state:
        st.session_state.categorias = ["Food", "Transporte", "Moradia", "Lazer", "Transferência", "Outros"]

    lista_cat_opcao = st.session_state.categorias + ["+ Incluir Nova Categoria..."]
    cat_escolhida = st.selectbox("Categoria", lista_cat_opcao)
    categoria_final = cat_escolhida
    
    if cat_escolhida == "+ Incluir Nova Categoria...":
        nova_cat_digitada = st.text_input("Digite o nome da nova categoria:")
        if nova_cat_digitada.strip() != "":
            categoria_final = nova_cat_digitada.strip()

    # 3. Contas e Cartões
    contas_base = ["Cash husband", "Nubank"]
    if "cartoes" in st.session_state and not st.session_state.cartoes.empty:
        contas_base.extend(st.session_state.cartoes["Nome"].tolist())

    conta_final = ""
    conta_destino_final = ""
    cartao_selecionado_row = None

    if tipo == "Transferência":
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            conta_saida_escolhida = st.selectbox("Conta Saída (Origem)", contas_base + ["+ Incluir Novo Cartão/Conta..."])
            conta_final = conta_saida_escolhida
            if conta_saida_escolhida == "+ Incluir Novo Cartão/Conta...":
                novo_c_digitado = st.text_input("Digite o nome da Conta Saída:")
                if novo_c_digitado.strip() != "":
                    conta_final = novo_c_digitado.strip()
                    novo_c_df = pd.DataFrame([{"Nome": conta_final, "Fechamento": 10, "Limite": 1000.0, "Vencimento": 17}])
                    st.session_state.cartoes = pd.concat([st.session_state.cartoes, novo_c_df], ignore_index=True)
                    st.session_state.cartoes.to_csv(ARQUIVO_CARTOES, index=False)
        with col_t2:
            conta_destino_escolhida = st.selectbox("Conta Destino", contas_base + ["+ Incluir Novo Cartão/Conta..."])
            conta_destino_final = conta_destino_escolhida
            if conta_destino_escolhida == "+ Incluir Novo Cartão/Conta...":
                novo_d_digitado = st.text_input("Digite o nome da Conta Destino:")
                if novo_d_digitado.strip() != "":
                    conta_destino_final = novo_d_digitado.strip()
                    novo_d_df = pd.DataFrame([{"Nome": conta_destino_final, "Fechamento": 10, "Limite": 1000.0, "Vencimento": 17}])
                    st.session_state.cartoes = pd.concat([st.session_state.cartoes, novo_d_df], ignore_index=True)
                    st.session_state.cartoes.to_csv(ARQUIVO_CARTOES, index=False)
        categoria_final = "Transferência"
    else:
        conta_escolhida = st.selectbox("Account (Conta / Cartão)", contas_base + ["+ Incluir Novo Cartão/Conta..."])
        conta_final = conta_escolhida
        
        if "cartoes" in st.session_state and not st.session_state.cartoes.empty and conta_final in st.session_state.cartoes["Nome"].values:
            cartao_selecionado_row = st.session_state.cartoes[st.session_state.cartoes["Nome"] == conta_final].iloc[0]

        if conta_escolhida == "+ Incluir Novo Cartão/Conta...":
            novo_c_digitado = st.text_input("Digite o nome do novo Cartão / Conta:")
            if novo_c_digitado.strip() != "":
                conta_final = novo_c_digitado.strip()
                novo_c_df = pd.DataFrame([{"Nome": conta_final, "Fechamento": 10, "Limite": 1000.0, "Vencimento": 17}])
                st.session_state.cartoes = pd.concat([st.session_state.cartoes, novo_c_df], ignore_index=True)
                st.session_state.cartoes.to_csv(ARQUIVO_CARTOES, index=False)
                cartao_selecionado_row = novo_c_df.iloc[0]

    # 4. Valores, Datas e Parcelamento
    valor_total = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")
    data_compra = st.date_input("Data da Compra", value=datetime.today())
    
    parcelas = st.number_input("Installments (Parcelas)", min_value=1, max_value=48, value=1)
    frequencia = st.selectbox("Frequência", ["Mensal", "Quinzenal", "Anual", "Única"])
    modo_valor = st.selectbox("Modo de Valor", ["Dividir Total", "Replicar Integral"])
    
    # 5. Botão de Salvamento e Lógica de Parcelas
    if st.button("Salvar Lançamento", type="primary"):
        if not descricao.strip():
            st.error("⚠️ Por favor, preencha a descrição do lançamento.")
        elif valor_total <= 0:
            st.error("⚠️ O valor deve ser maior que zero.")
        else:
            # Adicionar nova categoria à lista global se ela for nova
            if cat_escolhida == "+ Incluir Nova Categoria..." and categoria_final not in st.session_state.categorias:
                st.session_state.categorias.append(categoria_final)
                pd.DataFrame({"Categoria": st.session_state.categorias}).to_csv(ARQUIVO_CATEGORIAS, index=False)

            novos_registros = []
            
            # Cálculo dos valores por parcela/frequência
            for i in range(1, int(parcelas) + 1):
                if modo_valor == "Dividir Total":
                    valor_parcela = valor_total / parcelas
                else:
                    valor_parcela = valor_total

                # Incremento de data baseado na frequência
                if frequencia == "Mensal":
                    data_atual_loop = data_compra + relativedelta(months=i-1)
                elif frequencia == "Quinzenal":
                    data_atual_loop = data_compra + relativedelta(weeks=2*(i-1))
                elif frequencia == "Anual":
                    data_atual_loop = data_compra + relativedelta(years=i-1)
                else:
                    data_atual_loop = data_compra

                parcela_str = f"{i}/{int(parcelas)}" if parcelas > 1 else "Única"
                desc_final = f"{descricao} ({parcela_str})" if parcelas > 1 else descricao

                novo_registro = {
                    "Tipo": tipo,
                    "Status": status,
                    "Descricao": desc_final,
                    "Categoria": categoria_final,
                    "Conta": conta_final,
                    "ContaDestino": conta_destino_final if tipo == "Transferência" else "",
                    "Valor": round(valor_parcela, 2),
                    "Data": data_atual_loop.strftime("%Y-%m-%d"),
                    "Parcela": parcela_str
                }
                novos_registros.append(novo_registro)

            # Inserir no DataFrame geral do Session State
            df_novo = pd.DataFrame(novos_registros)
            st.session_state.lancamentos = pd.concat([st.session_state.lancamentos, df_novo], ignore_index=True)
            
            # Salvar no arquivo CSV de lançamentos
            st.session_state.lancamentos.to_csv(ARQUIVO_LANCAMENTOS, index=False)
            
            st.success(f"✅ {len(novos_registros)} lançamento(s) cadastrado(s) com sucesso!")
            st.balloons()
