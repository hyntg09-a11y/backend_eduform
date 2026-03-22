import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_eduform.settings')
django.setup()

import polars as pl
import xlsxwriter
from django.db import connection

cursor = connection.cursor()
tables = connection.introspection.table_names()

resumen = []
for table in tables:
    cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
    count = cursor.fetchone()[0]
    cols = connection.introspection.get_table_description(cursor, table)
    resumen.append({'Tabla': table, 'Columnas': len(cols), 'Registros': count})

hojas = {'Resumen': pl.DataFrame(resumen)}

for table in tables:
    cols = connection.introspection.get_table_description(cursor, table)
    hojas[table[:31]] = pl.DataFrame({
        'Campo': [c.name for c in cols],
        'Tipo': [str(c.type_code) for c in cols],
        'Nulo': [str(c.null_ok) for c in cols]
    })

with xlsxwriter.Workbook('documentacion_db.xlsx') as wb:
    for nombre, df in hojas.items():
        df.write_excel(workbook=wb, worksheet=nombre)

print('Listo: documentacion_db.xlsx')
