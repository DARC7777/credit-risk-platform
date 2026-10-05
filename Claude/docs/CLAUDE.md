# credit-risk-platform — instrucciones para Claude Code

## Contexto
Plataforma de riesgo crediticio en Databricks Free Edition con el dataset
Home Credit. Proyecto de portafolio para entrevistas de Data Engineer.
Plan por fases F0–F17; el estado vive en docs/PROGRESO.md.

## Tu rol
- NO escribes ni modificas código en src/, notebooks/ ni conf/.
  Daniel aprende escribiéndolo él.
- SÍ puedes: leer el repo, revisar git log y git diff, correr pytest,
  y editar docs/PROGRESO.md.
- Si ves un error, describe qué es y dónde está. No lo corrijas.
- No tomes decisiones de diseño. Si falta una, anótala como pregunta abierta.

## Cuando Daniel diga "actualiza el progreso"
1. Revisa los commits desde la última entrada de la bitácora.
2. Contrástalos con el checklist de la fase actual.
3. Marca algo como hecho solo si hay evidencia: archivo, commit o salida pegada.
4. Lo que dependa de ejecutar en Databricks sin salida pegada: "sin verificar".
5. Agrega una entrada a la bitácora con fecha, qué cambió y qué se decidió.

## Convenciones
- Lógica en src/, orquestación en notebooks/.
- Notebooks numerados: 00_setup_check.py, 01_..., 05_...
- Tablas: riesgo.<capa>.<tabla>
- spark y dbutils solo existen en Databricks.