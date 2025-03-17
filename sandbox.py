import requests
import time

def calcular_dv(cnpj_parcial):
    def calcular_digito(cnpj, pesos):
        soma = sum(int(cnpj[i]) * pesos[i] for i in range(len(pesos)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    cnpj_base = cnpj_parcial + "0001"
    pesos_dv1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    dv1 = calcular_digito(cnpj_base, pesos_dv1)

    pesos_dv2 = [6] + pesos_dv1
    dv2 = calcular_digito(cnpj_base + str(dv1), pesos_dv2)

    return cnpj_base + str(dv1) + str(dv2)

def consulta_cnpj_base(cnpj_base):
    cnpj_completo = calcular_dv(cnpj_base)
    print(cnpj_completo)
    url = f"https://api.cnpjs.dev/v1/{cnpj_completo}"

    try:
        response = requests.get(url)

        if response.status_code != 200:
            return {"Erro": f"Status {response.status_code}: {response.text}"}

        resp = response.json()

        if "status" in resp and resp["status"] == "ERROR":
            return {"Erro": resp.get("message", "Erro desconhecido")}

        return {
            "CNPJ": resp.get("cnpj", "Não disponível"),
            "Razão Social": resp.get("razao_social", "Não disponível"),
        }

    except requests.exceptions.RequestException as e:
        return {"Erro": f"Erro de conexão: {e}"}

def consultar_lista_cnpjs(cnpjs):
    try:
        resultados = []
        delay_segundos = 5.5

        for cnpj in cnpjs:
            resultado = consulta_cnpj_base(cnpj)
            
            # Verifica erro 429 e tenta novamente após o delay
            if "429 Too Many Requests" in str(resultado):
                print("Recebido erro 429. Aguardando para tentar novamente...")
                time.sleep(delay_segundos)
                resultado = consulta_cnpj_base(cnpj)

            print(resultado)
            resultados.append(resultado)
            time.sleep(delay_segundos)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Exemplo de lista de CNPJs (8 primeiros dígitos)
cnpjs_exemplo = [""]

consultar_lista_cnpjs(cnpjs_exemplo)
