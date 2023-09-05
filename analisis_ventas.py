import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Carga de datos en el Dataframe
df = pd.read_csv("ventas_divana.csv", sep=";")

### Exploración Inicial de los Datos ###

# Mostrar las primeras filas del DataFrame
print(df.head())

# Obtener información sobre las columnas y tipos de datos
print(df.info())

# Obtener estadísticas descriptivas de las columnas numéricas
print(df.describe())

### Identificación y Tratamiento de Datos Duplicados ###

# Identificar registros duplicados basados en la columna 'Número de orden'y el 'SKU'
duplicated_orders = df[df.duplicated(subset=['Número de orden', 'SKU'], keep=False)]
print(duplicated_orders.head())

# Eliminar registros duplicados
df = df.drop(duplicated_orders.index)

### Tratamiento de Datos Faltantes ###

# Verificar si hay datos faltantes en cada columna
print(df.isnull().sum())

# Reemplazar campos vacíos por "sin_información" en todo el DataFrame
df_filled = df.fillna("sin_información")

# Eliminar los registros llenados del DataFrame original
df = df.dropna()

# Guardar el DataFrame llenado en un archivo CSV
df_filled.to_csv('df_filled.csv', index=False)

# Verificar si hay datos faltantes en cada columna
print(df.isnull().sum())

### Ajuste de Tipos de Datos ### 

# Verificaremos los datos actuales de cada columna
print(df.dtypes)

# Convertir columna "Fecha de venta" al tipo datetime.
df['Fecha de venta'] = pd.to_datetime(df['Fecha de venta'], dayfirst=True)

# Reemplazar comas por puntos en las columnas especificadas
df[["Precio Facturable", "Envío"]] = df[["Precio Facturable", "Envío"]].astype(str)
df["Precio Facturable"] = df["Precio Facturable"].str.replace(',', '.')
df["Envío"] = df["Envío"].str.replace(',', '.')

# Convertir las columnas a tipo float
df[["Precio de venta", "Envío", "Precio Facturable"]] = df[["Precio de venta", "Envío", "Precio Facturable"]].astype(float)

### Parte II: Análisis Descriptivo y Visualización ###

### Cálculos de Métricas Clave ###

# Crear una nueva columna "Año-Mes" para agrupar por mes y año
df['Año-Mes'] = df['Fecha de venta'].dt.to_period('M')
print(df['Año-Mes'])

# Calcular las ventas promedio mensuales
ventas_totales_mensuales = df.groupby('Año-Mes')
print(ventas_totales_mensuales)

# Aplicar la función de agregación "sum()", a la columna "Precio Facturable", para conocer el total de ventas por cada mes de cada año.
ventas_totales_mensuales = df.groupby('Año-Mes')['Precio Facturable'].sum()
print(ventas_totales_mensuales)

# Convertiremos el resultado a la notación decimal, en vez de la notación cientifica, con '{:.2f}'.format y apply()
ventas_totales_mensuales = df.groupby('Año-Mes')['Precio Facturable'].sum()
print(ventas_totales_mensuales.apply('{:.0f}'.format))

# agrupar por Año-Mes, la cantidad de "Número de orden" con Groupby
cantidad_ordenes = df.groupby('Año-Mes')['Número de orden']
print(cantidad_ordenes)

# Aplicar la función de agregación ".nunique", para totalizar la cantidad de órdenes por "Año-Mes".
cantidad_ordenes = df.groupby('Año-Mes')['Número de orden'].nunique()
print(cantidad_ordenes)

# Calcular las ventas promedio por mes
ventas_promedio_mensuales = ventas_totales_mensuales / cantidad_ordenes
print(ventas_promedio_mensuales.apply('{:.2f}'.format))

# Simplificando los pasos: Los pasos anteriores los podemos ejecutar en uno solo, de la siguiente forma:
# Calcular las ventas promedio mensuales
# ventas_promedio_mensuales = (df.groupby('Año-Mes')['Precio Facturable'].sum()/df.groupby('Año-Mes')['Número de orden'].nunique()).apply('{:.2f}'.format)
# print(ventas_promedio_mensuales)

# Convertir "ventas_promedio" en un Dataframe para asignarle un nombre a la columna que contiene el cálculo del promedio de ventas por mes.
ventas_promedio_df = ventas_promedio_mensuales.reset_index()
ventas_promedio_df.columns = ['Año-Mes', 'Ventas Promedio']
print(ventas_promedio_df)

# Calcular los productos más vendidos
productos_mas_vendidos = df.groupby('SKU')['Cantidad'].sum().sort_values(ascending=False).head(10)
print(productos_mas_vendidos)

# Calcular el valor promedio de la cesta de compras
valor_promedio_cesta = df.groupby('Número de orden')['Precio Facturable'].sum().mean()
print(valor_promedio_cesta)

# Calcular la retención de clientes por mes
clientes_retencion = df.groupby('Año-Mes')['Número de orden'].nunique()

# Calculamos el cambio porcentual entre los valores de órdenes únicas en meses sucesivos
clientes_retencion = (clientes_retencion.pct_change().fillna(0) * 100).apply('{:.2f}'.format)
clientes_retencion = clientes_retencion.astype(float)
print(clientes_retencion)

# Agrega la columna 'Día de la semana', que agrega el nombre del día de la semana, correspondiente a la fecha
df['Día de la semana'] = df['Fecha de venta'].dt.day_name()
# Calcular las tendencias de ventas por día de la semana
tendencias_dia_semana = df.groupby('Día de la semana')['Precio Facturable'].mean().sort_values(ascending=False)
print(tendencias_dia_semana)

### Creación de archivo PDF, donde generaremos el informe ejecutivo ###

# asignamos un nombre al archivo PDF
pdf_filename = 'Informe_Ejecutivo.pdf'
# Se crea el archivo en tamaño “letter”
c = canvas.Canvas(pdf_filename, pagesize=letter)

# Agregar título e introducción al archivo PDF
c.drawString(180, 700, 'Informe Ejecutivo: Análisis de Ventas')
c.drawString(20, 670, 'En este informe, presentamos los resultados del análisis de ventas de la empresa')
c.drawString(20, 650, 'Divana. Se realizaron diversos análisis exploratorios y visualizaciones para obtener')
c.drawString(20, 630, 'insights clave sobre las ventas y la retención de clientes.')

# Agregar logo o una imagen

# Se ingresa la ruta de nuestra imagen
image_path = 'logo.jpg'
# Se definen las coordenadas de la imagen en la hoja del PDF y su tamaño.
c.drawImage(image_path, 460, 650, width=110, height=100)

### Visualizaciones con Matplotlib ###

# Gráfico de Ventas Promedio Mensuales

ventas_promedio_mensuales = ventas_promedio_mensuales.astype(float)

plt.figure(figsize=(10,6))
ventas_promedio_mensuales.plot(kind='bar', color='skyblue')
plt.title('Ventas Promedio Mensuales')
plt.xlabel('Año-Mes')
plt.ylabel('Monto Ventas Promedio')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('ventas_promedio_mensuales.png')
plt.show()
c.drawImage('ventas_promedio_mensuales.png', 20, 196, width=580, height=400)

# Gráfico de Productos Más Vendidos

c.showPage()
plt.figure(figsize=(10,6))
productos_mas_vendidos.plot(kind='area', x= 'SKU', y='Cantidad', color='skyblue')
plt.title('Productos más vendidos')
plt.xlabel('SKU')
plt.ylabel('Cantidad vendida')
plt.xticks(range(10), productos_mas_vendidos.index, rotation=45)
plt.tight_layout()
plt.savefig('Productos Más Vendidos.png')
plt.show()
c.drawImage('Productos Más Vendidos.png', 20, 396, width=580, height=376)

# Gráfico de Ingresos Totales por Mes

plt.figure(figsize=(10,6))
ventas_totales_mensuales.plot(kind='line', marker='o', color='skyblue')
plt.title('Ingresos mensuales')
xlabel = 'Año-Mes'
ylabel = 'Precio Facturable'
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('Ingresos mensuales.png')
plt.show()
c.drawImage('Ingresos mensuales.png', 20, 10, width=580, height=376)

# Gráfico de Retención de Clientes

c.showPage()
plt.figure(figsize=(10,6))
clientes_retencion.plot(kind='barh', color='skyblue')
plt.title('Retención de Clientes')
plt.xlabel('Año-Mes')
plt.ylabel('Porcentaje de retención')
plt.xticks(rotation=45)
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('Retención de Clientes.png')
plt.show()
c.drawImage('Retención de Clientes.png', 20, 396, width=580, height=376)

# Gráfico de Tendencias de Ventas por Día de la Semana

plt.figure(figsize=(10,6))
tendencias_dia_semana.plot(kind='line', marker='o', color='skyblue')
plt.title('Tendencias de Ventas por Día de la Semana')
plt.xlabel('Día de la Semana')
plt.ylabel('Ventas Promedio')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('Tendencias de Ventas por Día de la Semana.png')
plt.show()
c.drawImage('Tendencias de Ventas por Día de la Semana.png', 20, 10, width=580, height=376)

### Análisis RFM (Recencia, Frecuencia y Monto)###

# Cálculo de la fecha más reciente
fecha_reciente = df['Fecha de venta'].max()
print(fecha_reciente)

# Crear un nuevo DataFrame con los valores RFM

rfm_df = df.groupby('RUT').agg({
    'Fecha de venta': lambda x: (fecha_reciente - x.max()).days,
    'Número de orden': 'count',
    'Precio Facturable': 'sum'
    })
rfm_df['Precio Facturable'] = rfm_df['Precio Facturable'].apply('{:.0f}'.format)
print(rfm_df)

# Renombrar las columnas para RFM
rfm_df.rename(columns={
    'Fecha de venta': 'Recencia',
    'Número de orden': 'Frecuencia',
    'Precio Facturable': 'Monto'
}, inplace=True)

# Cambiar el tipo de datos del dataframe, a integer (int)
rfm_df = rfm_df.astype(int)

# Imprimir los primeros 10 registros
print(rfm_df.head(10))

### Segmentación RFM ###

### Funciones ###
"""Se crean las siguiente funciones para asignar valores de Recencia, Frecuencia y Monto"""
# Función asignar_recencia
def asignar_recencia(r):
  if r <= 30:
    return 4
  elif r <= 60:
    return 3
  elif r <= 90:
    return 2
  else:
    return 1

# Función asignar_frecuencia
def asignar_frecuencia(f):
  if f <= 1:
    return 1
  elif f <= 2:
    return 2
  elif f <= 3:
    return 3
  else:
    return 4

# Función asignar_monto
def asignar_monto(m):
  if m <= 50000:
    return 1
  elif m <= 100000:
    return 2
  elif m <= 150000:
    return 3
  else:
    return 4

# Aplicar las funciones a las columnas RFM

rfm_df['Recencia'] = rfm_df['Recencia'].apply(asignar_recencia)
rfm_df['Frecuencia'] = rfm_df['Frecuencia'].apply(asignar_frecuencia)
rfm_df['Monto'] = rfm_df['Monto'].apply(asignar_monto)

# Mostrar los primeros registros del DataFrame RFM con valores segmentados
print(rfm_df.head(10))

### Análisis de Segmentos RFM ###

# Calcular el RFM combinado para cada cliente
rfm_df['RFM'] = rfm_df['Recencia'] * 100 + rfm_df['Frecuencia'] * 10 + rfm_df['Monto']

# ordenar los registros de Mayor a Menor
rfm_df = rfm_df.sort_values('RFM', ascending=False)

# Mostrar los primeros registros del DataFrame RFM con valores RFM combinados
print(rfm_df.head(10))

# Visualizar la distribución de los segmentos RFM y guardarlos en documento PDF
c.showPage()
plt.figure(figsize=(10,6))
rfm_df['RFM'].plot(kind='hist', color= 'skyblue')
plt.title('Distribución de Segmentos RFM')
plt.xlabel('Segmento RFM')
plt.ylabel('Frecuencia')
plt.tight_layout()
plt.savefig('Distribución de Segmentos RFM.png')
plt.show()
c.drawImage('Distribución de Segmentos RFM.png', 20, 396, width=580, height=376)

### Parte IV: Recomendaciones Estratégicas. ###

# Generar recomendaciones estratégicas basadas en los resultados del análisis
# Recomendación para segmentos de alto valor:
if rfm_df['RFM'].max() >= 400:
  c.drawString(20, 380, 'Para nuestros clientes de alto valor (segmentos con RFM alto), recomendamos implementar programas de')
  c.drawString(20, 360, 'lealtad personalizados y ofertas exclusivas para fortalecer su retención y fomentar compras repetidas.')

# Recomendación para segmentos de bajo valor:
if rfm_df['RFM'].min() <= 200:
  c.drawString(20, 330, 'Para los segmentos de bajo valor (RFM bajo), sugerimos lanzar campañas de reactivación con descuentos')
  c.drawString(20, 310, 'especiales y contenido relevante para reenganchar a estos clientes.')

# Guardar el PDF generado
c.save()