K = []      # Conjunto de estados
V = []      # Alfabeto
T = []      # Transições AFND
i = ""      # Estado inicial
F = []      # Estados finais
delta = {}  # Dicionário de transições AFND

def processar_afd(cadeia, estado_inicial, estados_finais, delta):
    estado_atual = estado_inicial

    for simbolo in cadeia:
        if (estado_atual, simbolo) in delta:
            estado_atual = delta[(estado_atual, simbolo)]
        else:
            return False

    return estado_atual in estados_finais

def converter_afnd(K, V, T, i, F, delta_afnd):
  
    def epsilon_closure(states):
        stack = list(states)
        closure = set(states)
        while stack:
            p = stack.pop()
            if (p, '') in delta_afnd:
                for q in delta_afnd[(p, '')]:
                    if q not in closure:
                        closure.add(q)
                        stack.append(q)
        return closure

    def move(states, simbolo):
        dest = set()
        for p in states:
            if (p, simbolo) in delta_afnd:
                dest.update(delta_afnd[(p, simbolo)])
        return dest

    inicial_afd = frozenset(epsilon_closure({i}))

    fila = [inicial_afd]
    visitados = set()
    novos_estados = []
    novos_finais = set()
    delta_afd = {} 

    while fila:
        conjunto_atual = fila.pop(0)
        if conjunto_atual in visitados:
            continue
        visitados.add(conjunto_atual)
        novos_estados.append(conjunto_atual)

        if any(s in F for s in conjunto_atual):
            novos_finais.add(conjunto_atual)

        for simbolo in V:
            if simbolo == '':
                continue

            dest = move(conjunto_atual, simbolo)
            if not dest:
                novo_conjunto = frozenset()
            else:
                novo_conjunto = frozenset(epsilon_closure(dest))

            if novo_conjunto not in delta_afd.values(): 
                pass

            delta_afd[(conjunto_atual, simbolo)] = novo_conjunto

            if novo_conjunto not in visitados and novo_conjunto not in fila:
                fila.append(novo_conjunto)

    nome = {}
    for idx, st in enumerate(novos_estados):
        nome[st] = f"q{idx}"

    if frozenset() in {v for v in delta_afd.values()} and frozenset() not in nome:
        nome[frozenset()] = f"q{len(nome)}"
        novos_estados.append(frozenset())

    K_afd = [nome[s] for s in novos_estados]
    i_afd = nome[inicial_afd]
    F_afd = [nome[s] for s in novos_finais]

    T_afd = []
    delta_afd_nomeado = {}
    for (orig, simbolo), dest in delta_afd.items():
        orig_nome = nome.get(orig, None)
        dest_nome = nome.get(dest, None)
        if orig_nome is None or dest_nome is None:
            continue
        T_afd.append((orig_nome, simbolo, dest_nome))
        delta_afd_nomeado[(orig_nome, simbolo)] = dest_nome

    return K_afd, V, T_afd, i_afd, F_afd, delta_afd_nomeado

estado_id = 0

def novo_estado():
    global estado_id
    e = f"q{estado_id}"
    estado_id += 1
    return e

def thompson(er):
    pilha = []
    operadores = []

    def aplica_operador(op):
        nonlocal pilha
        if op == "|":
            (i2, f2, d2) = pilha.pop()
            (i1, f1, d1) = pilha.pop()
            i = novo_estado()
            f = novo_estado()
            d = {**d1, **d2}

            d.setdefault((i, ''), set()).update({i1, i2})
            d.setdefault((f1, ''), set()).add(f)
            d.setdefault((f2, ''), set()).add(f)

            pilha.append((i, f, d))

        elif op == ".":
            (i2, f2, d2) = pilha.pop()
            (i1, f1, d1) = pilha.pop()
            d = {**d1, **d2}

            d.setdefault((f1, ''), set()).add(i2)
            pilha.append((i1, f2, d))

        elif op == "*":
            (i1, f1, d1) = pilha.pop()
            i = novo_estado()
            f = novo_estado()
            d = dict(d1)

            d.setdefault((i, ''), set()).update({i1, f})
            d.setdefault((f1, ''), set()).update({i1, f})

            pilha.append((i, f, d))

    def prioridade(op):
        if op == "*": return 3
        if op == ".": return 2
        if op == "|": return 1
        return 0

    er = inserir_concatenacao(er)

    i = 0
    while i < len(er):
        c = er[i]

        if c == "(":
            operadores.append(c)

        elif c == ")":
            while operadores and operadores[-1] != "(":
                aplica_operador(operadores.pop())
            operadores.pop()

        elif c in {"|", ".", "*"}:
            while operadores and prioridade(operadores[-1]) >= prioridade(c):
                aplica_operador(operadores.pop())
            operadores.append(c)

        else:
            s_in = novo_estado()
            s_out = novo_estado()
            d = {(s_in, c): {s_out}}
            pilha.append((s_in, s_out, d))

        i += 1

    while operadores:
        aplica_operador(operadores.pop())

    return pilha[0]

def inserir_concatenacao(er):
    r = ""
    for i in range(len(er) - 1):
        a, b = er[i], er[i + 1]
        r += a
        if a not in "(|" and b not in "|)*)":
            r += "."
    return r + er[-1]

def expressao_regular_para_afd(K, V, T, i, F, delta):

    er = input("Digite a expressão regular: ")

    inicio, fim, delta_er = thompson(er)

    K = list({inicio, fim} | {s for (s, _) in delta_er.keys()} | {t for ds in delta_er.values() for t in ds})
    V = sorted(list({s for (_, s) in delta_er.keys() if s != ''}))
    T = []
    delta = {}

    for (orig, simb), dests in delta_er.items():
        for d in dests:
            T.append((orig, simb, d))
            delta.setdefault((orig, simb), set()).add(d)

    i = inicio
    F = [fim]

    return K, V, T, i, F, delta

while True:
    escolha = input(
        "Digite:\n"
        "[0] Digitar manualmente AFND\n"
        "[1] Teste automático de AFND\n"
        "[2] Digitar manualmente Expressão Regular\n"
        "[3] Teste automático de Expressão Regular\n"
    )

    if escolha == "0":
        K = input("Estados (ex: q0 q1 q2): ").split()
        V = input("Alfabeto (ex: a b): ").split()

        while True:
            i = input("Estado inicial: ")
            F = input("Estados finais separados por espaço: ").split()
            if i in K and all(f in K for f in F):
                break
            print("Erro: estados inválidos.")

        print("\nDigite transições no formato:")
        print("origem símbolo destino1 destino2 ...")
        print("Digite 'fim' para encerrar\n")

        T = []
        delta = {}

        while True:
            entrada = input("Transição: ")
            if entrada == "fim":
                break

            partes = entrada.split()
            origem = partes[0]
            simbolo = partes[1]
            destinos = partes[2:]

            T.append((origem, simbolo, *destinos))
            delta.setdefault((origem, simbolo), set()).update(destinos)
        break

    elif escolha == "1":
        K = ["q0", "q1", "q2"]
        V = ["a", "b", "c"]
        i = "q0"
        F = ["q2"]

        T = [
            ("q0", "a", "q0", "q1"),
            ("q0", "b", "q1"),
            ("q0", "c", "q2"),
            ("q1", "a", "q0"),
            ("q1", "b", "q0", "q2"),
            ("q1", "c", "q0"),
            ("q2", "a", "q1"),
            ("q2", "b", "q0", "q1"),
            ("q2", "c", "q2"),
        ]

        for origem, simb, *destinos in T:
            delta.setdefault((origem, simb), set()).update(destinos)
        break

    elif escolha == "2":
        K, V, T, i, F, delta = expressao_regular_para_afd(K, V, T, i, F, delta)
        break

    elif escolha == "3":
        print("\n===== Teste automático para Expressão Regular =====")

        er = "(a|b)*abb"
        print("Expressão Regular usada:", er)

        inicio, fim, delta_er = thompson(er)

        K = list({inicio, fim} | {s for (s, _) in delta_er.keys()} | {t for ds in delta_er.values() for t in ds})
        V = sorted(list({s for (_, s) in delta_er.keys() if s != ''}))
        T = []
        delta = {}

        for (orig, simb), dests in delta_er.items():
            for d in dests:
                T.append((orig, simb, d))
                delta.setdefault((orig, simb), set()).add(d)

        i = inicio
        F = [fim]

        print("AFND criado a partir da ER!\n")
        break

    else:
        print("Escolha inválida.\n")


print("\n===== AFND INFORMADO =====")
print("Estados:", K)
print("Alfabeto:", V)
print("Inicial:", i)
print("Finais:", F)
print("Transições:", T)

K, V, T, i, F, delta = converter_afnd(K, V, T, i, F, delta)

print("\n===== AFD GERADO =====")
print("Estados:", K)
print("Alfabeto:", V)
print("Inicial:", i)
print("Finais:", F)
print("Transições:", T)

while True:
    cadeia = input("\nDigite a cadeia para testar ('sair' para encerrar): ")

    if cadeia == "sair":
        break

    if processar_afd(cadeia, i, F, delta):
        print("Cadeia aceita!")
    else:
        print("Cadeia rejeitada!")
