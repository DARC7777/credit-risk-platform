# ADR-002: Arquitectura de capas y organización del código

**Estado:** Aceptado
**Fecha:** 2026-09-17

## Contexto

El proyecto ingiere siete tablas de origen con calidad desconocida y debe
servir a varios consumidores distintos: entrenamiento de modelos, scoring
batch, tableros y un copiloto de IA. Además, uno de los requisitos del
proyecto es poder reconstruir cualquier resultado desde cero.

Eso exige separar los datos tal como llegaron de los datos ya validados, y
separar la lógica de transformación de su ejecución.

## Decisión

Arquitectura medallion sobre un catálogo propio `riesgo` en Unity Catalog,
con cinco esquemas: `bronze` (datos crudos), `silver` (datos validados),
`gold` (features y tablas de consumo), `ml` (artefactos de modelado y
monitoreo) y `ai` (objetos del copiloto).

El volume de aterrizaje `home_credit_raw` vive en el esquema `bronze`. Los
archivos crudos son el activo más sensible de la plataforma, así que se alojan
en la capa más restringida, junto a las tablas Bronze que se derivan de ellos
y comparten sus permisos.

La lógica de transformación vive en módulos Python bajo `src/`. Los notebooks
importan esos módulos y solo orquestan la secuencia de pasos.

## Alternativas consideradas

**Una sola tabla limpia, sin capas.** Mezclar ingesta y limpieza en un único
paso obliga a volver a la fuente original ante cualquier error, y elimina la
posibilidad de distinguir qué llegó mal del origen y qué se dañó en la
transformación.

**Toda la lógica en notebooks.** El código dentro de un notebook no se puede
importar, así que no se puede probar con pytest ni reutilizar desde otro
proceso. La misma transformación terminaría duplicada en el notebook de
entrenamiento, el de scoring y el del copiloto, y un error corregido en uno
seguiría vivo en los demás.

## Consecuencias

**A favor:**
- Cada capa deja una tabla intermedia consultable, así que ante un resultado
  incorrecto se puede identificar en qué paso se produjo el error sin
  reprocesar desde el origen.
- Silver y Gold se pueden reconstruir sin volver a descargar los datos.
- Los permisos se asignan por esquema, de modo que un consumidor de Gold no
  necesita acceso a los datos crudos.
- La lógica en `src/` se prueba con tests unitarios y se reutiliza desde
  notebooks, jobs y el copiloto sin duplicarse.

**En contra:**
- Los mismos registros se almacenan tres veces, una por capa, con el costo de
  almacenamiento que eso implica.
- Cada capa es un paso de cómputo adicional, y en Free Edition el cómputo se
  paga en cuota diaria.
- Un dato tarda más en estar disponible en Gold que si se escribiera
  directamente desde el origen.