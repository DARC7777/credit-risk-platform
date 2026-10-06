## Actualización 2026-10-03 · Llave de Bronze con `_row_hash`

### Contexto
Con la llave natural sola, el `MERGE` ignoraba cualquier registro cuya llave ya existiera en Bronze. Si la fuente enviaba un crédito corregido, por ejemplo el mismo `SK_ID_BUREAU` con otro saldo, la corrección se perdía sin aviso. Bronze debe guardar el registro de los cambios, no solo la primera versión que llegó.

### Decisión
La llave de Bronze pasa a ser la llave natural más `_row_hash`.

`_row_hash` es una huella del contenido de todas las columnas del contrato: si cambia una sola columna, cambia el hash. Así, el `MERGE` distingue dos casos:

| Llega | Llave natural | `_row_hash` | Resultado |
|---|---|---|---|
| La misma fila otra vez | igual | igual | Se ignora: la carga sigue siendo idempotente |
| La fila corregida | igual | distinto | Se inserta como versión nueva |

`installments_payments` es la excepción: su llave ya era solo `_row_hash`, porque la tabla no tiene llave natural (los pagos parciales repiten las mismas columnas de identificación). A esa tabla no se le agrega el hash por segunda vez.

### Consecuencias
**Positivas**
- Ninguna corrección de la fuente se pierde: Bronze conserva la historia completa de cada registro.
- La idempotencia se mantiene: recargar el mismo archivo no duplica filas.

**Negativas**
- En Bronze deja de cumplirse "una fila por llave natural": un registro corregido tiene varias versiones.
- La verificación de F1 compara filas contra llaves naturales distintas; cuando lleguen correcciones dará ✗ y habrá que ajustarla para contar llaves de Bronze.
- Bronze crece con cada corrección.
- Guardar versiones choca con la purga por derecho al olvido: borrar a un cliente exige borrar todas sus versiones (se resuelve en F4c).

**Trabajo que pasa a Silver (F2)**
- Silver se queda con la versión vigente de cada llave natural, la más reciente según `_ingested_at`.

### Evidencia
Recarga completa del 2026-10-05, ocho tablas, un lote cada una:

```
pos_cash_balance          csv= 10,001,358 bronze= 10,001,358 llaves= 10,001,358 lotes=1  ✓
application_test          csv=     48,744 bronze=     48,744 llaves=     48,744 lotes=1  ✓
application_train         csv=    307,511 bronze=    307,511 llaves=    307,511 lotes=1  ✓
bureau                    csv=  1,716,428 bronze=  1,716,428 llaves=  1,716,428 lotes=1  ✓
bureau_balance            csv= 27,299,925 bronze= 27,299,925 llaves= 27,299,925 lotes=1  ✓
credit_card_balance       csv=  3,840,312 bronze=  3,840,312 llaves=  3,840,312 lotes=1  ✓
installments_payments     csv= 13,605,401 bronze= 13,605,401 llaves= 13,605,401 lotes=1  ✓
previous_application      csv=  1,670,214 bronze=  1,670,214 llaves=  1,670,214 lotes=1  ✓
```