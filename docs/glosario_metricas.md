# Glosario de Metricas — Olist E-Commerce Analytics

Todos los valores monetarios estan expresados en Reales brasilenhos (BRL). El conjunto de datos
abarca de septiembre de 2016 a agosto de 2018, con aproximadamente 99.441 ordenes y 96.096
clientes unicos.

---

## ingresos

**Definicion:** Suma de los precios de los items de cada orden, excluyendo el flete. Representa
el valor de venta neto recibido por los vendedores antes de descontar costos de envio.

**Logica SQL:**
```sql
SUM(price)
-- proveniente de olist_order_items_dataset,
-- agregado por orden en serving.mart_ordenes_enriquecidas
```

**Columna en el mart:** `serving.mart_ordenes_enriquecidas.ingresos` (numeric, BRL)

---

## flete

**Definicion:** Costo total de envio cobrado al cliente por todos los items de una orden.

**Logica SQL:**
```sql
SUM(freight_value)
-- proveniente de olist_order_items_dataset, agregado por orden
```

**Columna en el mart:** `serving.mart_ordenes_enriquecidas.flete` (numeric, BRL)

---

## ordenes

**Definicion:** Cantidad de ordenes distintas realizadas, identificadas por su identificador
unico de orden.

**Logica SQL:**
```sql
COUNT(DISTINCT id_orden)
```

**Columna en el mart:** `serving.mart_ordenes_enriquecidas.id_orden` (text, clave primaria de
la tabla de hechos)

---

## ticket promedio

**Definicion:** Ingreso promedio por orden; mide el tamano tipico del carrito de compra en BRL.

**Logica SQL:**
```sql
SUM(ingresos) / COUNT(DISTINCT id_orden)
```

**Derivado de columnas del mart:** `ingresos` / `id_orden`

---

## dias de entrega

**Definicion:** Numero de dias calendario entre la fecha de compra y la fecha real de entrega
al cliente.

**Logica SQL:**
```sql
DATE_PART('day', order_delivered_customer_date - order_purchase_timestamp)
```

**Columna en el mart:** `serving.mart_ordenes_enriquecidas.dias_entrega` (integer, nullable;
NULL para ordenes no entregadas)

---

## tasa a tiempo

**Definicion:** Proporcion de ordenes entregadas que llegaron en la fecha estimada o antes;
se expresa como porcentaje.

**Logica SQL:**
```sql
AVG(a_tiempo)
-- a_tiempo es un indicador 0/1:
--   1 si order_delivered_customer_date <= order_estimated_delivery_date
--   0 en caso contrario
-- NULL para ordenes no entregadas (excluidas automaticamente por AVG)
```

**Columna en el mart:** `serving.mart_ordenes_enriquecidas.a_tiempo` (integer 0/1, nullable)

---

## puntaje promedio de resena

**Definicion:** Calificacion promedio de satisfaccion del cliente por orden, en una escala de
1 (peor) a 5 (mejor).

**Logica SQL:**
```sql
AVG(review_score)
-- proveniente de olist_order_reviews_dataset;
-- se promedia por orden cuando existen multiples resenas
```

**Columna en el mart:** `serving.mart_ordenes_enriquecidas.puntaje_promedio` (numeric 1-5,
nullable; NULL cuando no se envio ninguna resena)

---

## tasa de clientes recurrentes

**Definicion:** Proporcion de clientes unicos que realizaron mas de una orden durante el periodo
de analisis; mide la fidelizacion de clientes.

**Logica SQL:**
```sql
COUNT(DISTINCT id_cliente_unico) FILTER (WHERE cantidad_ordenes > 1)
/ COUNT(DISTINCT id_cliente_unico)

-- donde cantidad_ordenes = COUNT(id_orden) por id_cliente_unico
```

**Columna en el mart:** `serving.mart_ordenes_enriquecidas.id_cliente_unico` (text); el conteo
de ordenes por cliente se calcula en tiempo de consulta.

---

## cuotas promedio

**Definicion:** Numero promedio de cuotas de pago elegidas por los clientes; refleja el uso del
sistema de "parcelamento" (pago en cuotas) caracteristico del mercado brasileno.

**Logica SQL:**
```sql
AVG(payment_installments)
-- proveniente de olist_order_payments_dataset, una fila por metodo de pago
```

**Columna en el mart:** `serving.mart_ordenes_enriquecidas.cuotas` (integer)

---

## Contexto adicional

| Metrica | Granularidad | Nulabilidad |
|---|---|---|
| ingresos | por orden | nunca nulo |
| flete | por orden | nunca nulo |
| ordenes | por orden | nunca nulo |
| ticket promedio | derivado | nunca nulo |
| dias de entrega | por orden entregada | nulo para no entregadas |
| tasa a tiempo | por orden entregada | nulo para no entregadas |
| puntaje promedio de resena | por orden con resena | nulo sin resena |
| tasa de clientes recurrentes | sobre todos los clientes | nunca nulo |
| cuotas promedio | por orden | nunca nulo |
