import yaml
from pathlib import Path

RUTA = Path("conf/data_contracts_draft.yaml")

LLAVES = {
    "application_train":     ["SK_ID_CURR"],
    "application_test":      ["SK_ID_CURR"],
    "bureau":                ["SK_ID_BUREAU"],
    "bureau_balance":        ["SK_ID_BUREAU", "MONTHS_BALANCE"],
    "previous_application":  ["SK_ID_PREV"],
    "pos_cash_balance":      ["SK_ID_PREV", "MONTHS_BALANCE"],
    "credit_card_balance":   ["SK_ID_PREV", "MONTHS_BALANCE"],
    "installments_payments": ["_row_hash"],
}

contrato = yaml.safe_load(RUTA.read_text(encoding="utf-8"))

for tabla, llave in LLAVES.items():
    info = contrato["tablas"][tabla]
    info["llave"] = llave
    for col in info["columnas"]:
        if col["nombre"] in llave:
            col["nulable"] = False

texto = yaml.safe_dump(contrato, sort_keys=False, allow_unicode=True)

encabezado = "  installments_payments:\n    archivo: installments_payments.csv\n"
comentario = (
    "    # Sin ID de transacción en la fuente: pagos parciales repiten\n"
    "    # crédito+versión+cuota+fecha (770 casos). Sin filas idénticas,\n"
    "    # así que se usa un hash de todas las columnas como llave técnica.\n"
)
texto = texto.replace(encabezado, encabezado + comentario)

RUTA.write_text(texto, encoding="utf-8")

for tabla, info in contrato["tablas"].items():
    print(f"{tabla:25s} {info['llave']}")