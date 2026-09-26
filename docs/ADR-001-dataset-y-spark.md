# ADR-001: Dataset y justificación de Spark

**Estado:** Aceptado
**Fecha:** 2026-09-17

## Contexto

La plataforma necesita datos de riesgo crediticio con dos características:
volumen suficiente para justificar procesamiento distribuido, y una estructura
relacional que permita construir features de comportamiento a partir de varias
tablas satélite.

Restricciones: el proyecto corre sobre Databricks Free Edition, con cuota diaria
limitada y cómputo exclusivamente serverless.

## Decisión

Se usa el dataset Home Credit Default Risk (Kaggle) y se procesa con Spark.

El dataset tiene siete tablas: una de solicitudes y seis de comportamiento
crediticio histórico. El volumen total ronda los 2,6 GB, concentrado en las
tablas satélite: `installments_payments` (706 MB), `credit_card_balance`
(414 MB), `previous_application` (395 MB), `POS_CASH_balance` (383 MB) y
`bureau_balance` (366 MB), frente a `application_train` (162 MB).

## Alternativas consideradas

**Freddie Mac Single-Family Loan-Level Dataset.** Mayor volumen y desempeño
mensual real por crédito, lo que permitiría cosechas verdaderas. Se descartó
por el costo de rediseñar el plan ya elaborado sobre Home Credit.

**Datos sintéticos.** Control total sobre la licencia, pero se pierde realismo
y valor demostrativo.

**Procesamiento con pandas.** `application_train` cabe en memoria, pero las
tablas de comportamiento, que son el centro del feature engineering, no. Usar
pandas obligaría a procesarlas por fragmentos manualmente.

## Consecuencias

**A favor:**
- Las agregaciones sobre las tablas satélite justifican Spark de forma genuina.
- Es un dataset conocido, con un benchmark público que permite comparar
  resultados contra participantes reales.

**En contra:**
- Las reglas de la competencia restringen el uso de los datos a los fines de
  la competencia y prohíben su redistribución. Los CSV se excluyen del
  repositorio mediante `.gitignore`, y el proyecto participa con late
  submissions para alinear el uso con esa restricción.
- El dataset no contiene fechas absolutas: el tiempo es relativo a la fecha de
  solicitud de cada cliente. Esto impide construir cosechas por mes calendario,
  y el análisis de maduración (F8) debe usar tiempo relativo. La limitación se
  documenta de forma explícita en lugar de disimularse.
- Las etiquetas ya vienen definidas, así que no se ejercita la definición del
  target ni la ventana de observación, que en un caso real es una decisión de
  negocio relevante.