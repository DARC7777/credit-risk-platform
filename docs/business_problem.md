# El problema de negocio

## La decisión

Una entidad de crédito de consumo recibe solicitudes de financiación y debe
decidir, antes de desembolsar, si aprueba cada una. La decisión se toma con la
información disponible en el momento de la solicitud: los datos declarados por
el solicitante y su historial crediticio previo, tanto interno como reportado
por burós externos.

Es una decisión anticipada y de alto volumen. No se analiza un crédito ya
otorgado; se estima el comportamiento futuro de alguien sobre quien solo se
tiene información pasada.

## Los dos errores y lo que cuestan

La decisión puede fallar de dos formas, y no cuestan lo mismo.

**Aprobar a quien no paga.** Se pierde el saldo no recuperado del capital
prestado, más los costos de cobranza y provisión. Es una pérdida directa,
visible en los estados financieros y atribuible a la operación de crédito.

**Rechazar a quien sí habría pagado.** Se pierde el margen financiero que ese
crédito habría generado durante su vida. Es un costo de oportunidad: no
aparece en ningún estado financiero, porque nadie contabiliza al cliente que
no se ganó.

En crédito de consumo, el primer error suele costar varias veces más que el
segundo: se pierde el capital completo frente a un margen porcentual. Esa
asimetría es la que determina dónde se ubica el umbral de aprobación, y por
eso el umbral es una decisión de negocio, no una elección estadística.

De ahí se desprende el criterio central del proyecto: **el objetivo no es
maximizar la exactitud del modelo, sino minimizar la pérdida esperada de la
cartera.** Un modelo más exacto con un umbral mal elegido puede costar más
dinero que un modelo menos exacto bien calibrado.

## Por qué el problema es difícil

**El evento es poco frecuente.** La gran mayoría de los créditos se paga. Los
casos de incumplimiento son una minoría, lo que dificulta aprender a
distinguirlos y hace que métricas como la exactitud global resulten engañosas.

**La etiqueta llega tarde.** Si el incumplimiento se define como mora superior
a noventa días, el resultado real de un crédito otorgado hoy no se conoce
hasta dentro de doce meses o más. Esto significa que el desempeño del modelo
no se puede medir con la métrica relevante en el momento en que se necesita, y
obliga a monitorear con indicadores indirectos mientras tanto.

**Solo se observa a los aprobados.** El comportamiento de pago únicamente
existe para las solicitudes que fueron aprobadas. De las rechazadas nunca se
sabe si habrían pagado, así que cada modelo se entrena sobre una población
filtrada por las decisiones del modelo anterior. Este sesgo de selección se
acumula con el tiempo y es una limitación estructural del dominio.

## Qué debe entregar la plataforma

1. Una estimación de la probabilidad de incumplimiento para cada solicitud.
2. Un umbral de decisión justificado en unidades monetarias, no en métricas
   estadísticas, con análisis de sensibilidad frente a los supuestos de costo.
3. Una explicación comprensible de cada decisión, en lenguaje de negocio, que
   permita sustentar un rechazo ante el solicitante y ante el regulador.
4. Evidencia continua de que el sistema sigue funcionando: estabilidad de la
   población, del score y del desempeño observado por cosecha.
5. Continuidad de la operación ante fallas: si una fuente de datos no está
   disponible, la originación debe degradarse, no detenerse.

## El dataset como sustituto

El proyecto usa el dataset Home Credit Default Risk, que corresponde a
operaciones reales de crédito de consumo. Permite ejercitar el problema
completo: construcción de variables de comportamiento a partir de historial
crediticio, decisión bajo costos asimétricos, explicabilidad y monitoreo.

Tiene dos limitaciones que se declaran de forma explícita. Primera: las fechas
son relativas a cada solicitud, no absolutas, de modo que no es posible
construir cosechas por mes calendario y el análisis de maduración debe usar
tiempo relativo. Segunda: la definición del incumplimiento viene dada, así que
no se ejercita la decisión de negocio de definir el evento y su ventana de
observación, que en un caso real es una discusión con áreas de riesgo y
cobranza.

Los supuestos de costo utilizados en el análisis de umbral son
parametrizables y se documentan junto con su sensibilidad, precisamente porque
no provienen de la cartera real de ninguna entidad.