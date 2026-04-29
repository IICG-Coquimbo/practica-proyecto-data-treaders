from pymongo import MongoClient, UpdateOne
from datetime import datetime
import random

MONGO_URI = "mongodb://mongodb:27017"
DB_NAME = "datatraders"
COLLECTION_NAME = "creditos_hipotecarios"

GRUPO = "DataTraders"
INTEGRANTES = ["joaquin", "pia", "milla", "fer", "ruben", "juan", "vale"]

BANCOS = [
    "BancoEstado",
    "Santander",
    "BCI",
    "Scotiabank",
    "Banco de Chile",
    "Itaú",
    "Banco Falabella"
]

MONTOS = [50000000, 70000000, 90000000, 110000000, 130000000]
PLAZOS = [10, 15, 20, 25, 30]
PIES = [10, 15, 20, 25, 30]
TIPOS = ["Tasa fija", "Tasa mixta", "Tasa variable"]

def crear_registro(integrante):
    banco = random.choice(BANCOS)
    monto_propiedad = random.choice(MONTOS)
    pie_porcentaje = random.choice(PIES)
    plazo_anios = random.choice(PLAZOS)
    tipo_credito = random.choice(TIPOS)

    monto_financiado = int(monto_propiedad * (1 - pie_porcentaje / 100))
    tasa_interes = round(random.uniform(3.8, 6.7), 2)
    cae = round(tasa_interes + random.uniform(0.5, 1.8), 2)

    dividendo_estimado = int(
        (monto_financiado / (plazo_anios * 12)) +
        ((monto_financiado * (cae / 100)) / 12)
    )

    return {
        "banco": banco,
        "producto": "Crédito Hipotecario",
        "tipo_credito": tipo_credito,
        "monto_propiedad": monto_propiedad,
        "monto_financiado": monto_financiado,
        "pie_porcentaje": pie_porcentaje,
        "plazo_anios": plazo_anios,
        "tasa_interes": tasa_interes,
        "cae": cae,
        "dividendo_estimado": dividendo_estimado,
        "moneda": "CLP",
        "pais": "Chile",
        "grupo": GRUPO,
        "integrante": integrante,
        "fuente": "Simulación estructurada de créditos hipotecarios",
        "fecha_captura": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def main():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    operaciones = []

    for integrante in INTEGRANTES:
        for i in range(500):
            registro = crear_registro(integrante)

            filtro = {
                "integrante": registro["integrante"],
                "banco": registro["banco"],
                "monto_propiedad": registro["monto_propiedad"],
                "pie_porcentaje": registro["pie_porcentaje"],
                "plazo_anios": registro["plazo_anios"],
                "tipo_credito": registro["tipo_credito"],
                "indice": i
            }

            registro["indice"] = i

            operaciones.append(
                UpdateOne(filtro, {"$set": registro}, upsert=True)
            )

    resultado = collection.bulk_write(operaciones)

    print("Carga finalizada")
    print("Insertados:", resultado.upserted_count)
    print("Actualizados:", resultado.modified_count)
    print("Total documentos:", collection.count_documents({}))

if __name__ == "__main__":
    main()