import requests
import pandas as pd
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

def get_from_excel():
    try:
        df = pd.read_excel('cnpjserro.xlsx')
        
        if 'CNPJ' not in df.columns:
            print("Coluna '[CNPJ]' não encontrada.")
            return

        cnpjs = df['CNPJ'].dropna().astype(str).str.zfill(8).tolist()
        
        resultados = []
        delay_segundos = 5.5
        #limite_consultas = 10  # Limite de 10 consultas

        for i, cnpj in enumerate(cnpjs):  # Limita a 10 primeiros CNPJs
            resultado = consulta_cnpj_base(cnpj)
            print(resultado)
            resultados.append(resultado)
            time.sleep(delay_segundos)
        
        df_resultado = pd.DataFrame(resultados)
        df_resultado.to_excel('erros.xlsx', index=False)
        print("Consulta finalizada! Resultados salvos em 'resultado_cnpjs.xlsx'.")

    except FileNotFoundError:
        print("Arquivo 'cnpjserro.xlsx' não encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

    #print(df)

get_from_excel()
