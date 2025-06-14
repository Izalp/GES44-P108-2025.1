from decimal import Decimal, getcontext

def mg1_non_preemptive_priority_metrics(arrival_rates, service_times, service_variances):
    """
    Calcula métricas para M/G/1 com prioridade não-preemptiva baseada em SPT (versão corrigida).

    Parâmetros:
    - arrival_rates: lista de taxas de chegada (λ) para cada classe
    - service_times: lista de tempos médios de serviço (E[S]) em horas
    - service_variances: lista de variâncias dos tempos de serviço (Var[S]) em horas²

    Retorna:
    - dicionário com métricas por classe no formato Classe 1, Classe 2, etc.
    """
    getcontext().prec = 10

    n = len(arrival_rates)
    if not (len(service_times) == len(service_variances) == n):
        return {"Erro": "Listas de entrada devem ter o mesmo comprimento."}

    # Convertendo para Decimal
    arrival_rates = [Decimal(str(l)) for l in arrival_rates]
    service_times = [Decimal(str(s)) for s in service_times]
    service_variances = [Decimal(str(v)) for v in service_variances]

    # Ordenar por menor tempo de serviço (SPT)
    classes = sorted(
        [(i, arrival_rates[i], service_times[i], service_variances[i]) for i in range(n)],
        key=lambda x: x[2]  # menor E[S] tem mais prioridade
    )

    arrival_rates = [c[1] for c in classes]
    service_times = [c[2] for c in classes]
    service_variances = [c[3] for c in classes]
    original_indices = [c[0] for c in classes]

    utilizacoes = [arrival_rates[i] * service_times[i] for i in range(n)]
    rho_total = sum(utilizacoes)

    if rho_total >= 1:
        return {"Erro": "Sistema instável: soma das utilizações ≥ 1."}

    # E[S²] = Var[S] + (E[S])²
    ES2 = [service_variances[i] + service_times[i] ** 2 for i in range(n)]

    results = {}
    for i in range(n):
        # Soma das utilizações até a classe i-1
        rho_i_minus_1 = sum(utilizacoes[j] for j in range(i))
        # Soma das utilizações até a classe i
        rho_i = sum(utilizacoes[j] for j in range(i + 1))

        numerator = sum(arrival_rates[j] * ES2[j] for j in range(n))
        if i == 0:
        # Classe com maior prioridade (i=0)
            denominator = 2 * (1 - rho_i)
        else:
            denominator = 2 * (1 - rho_i_minus_1) * (1 - rho_i)

        Wq = numerator / denominator

        W = Wq + service_times[i]
        L = arrival_rates[i] * W
        Lq =  L - arrival_rates[i] * service_times[i]

        class_name = f"Classe {original_indices[i] + 1}"  # volta ao índice original
        results[class_name] = {
            "Taxa de Chegada (λ)": round(arrival_rates[i], 5),
            "Tempo Médio de Serviço (E[S])": round(service_times[i], 5),
            "Variância do Serviço (Var[S])": round(service_variances[i], 7),
            "Taxa de Ocupação (ρ)": round(utilizacoes[i], 5),
            "Número Médio no Sistema (L)": round(L, 5),
            "Número Médio na Fila (Lq)": round(Lq, 5),
            "Tempo Médio no Sistema (W)": round(W, 5),
            "Tempo Médio na Fila (Wq)": round(Wq, 5)
        }

    return results
