# Sistema de Nómina CIPA

Proyecto de la Unidad Tres. La aplicación permite registrar empleados de distintos tipos y calcular sus pagos con Python. También tiene una versión web para consultar el personal y los reportes.

## Requisitos

- Python 3.10 o una versión posterior.
- Tkinter, incluido normalmente con Python.
- Node.js para ejecutar las pruebas de la parte web.

No se necesitan paquetes externos para ejecutar la aplicación de escritorio.

## Ejecutar la aplicación

Desde la carpeta del proyecto:

```bash
python gui.py
```

Para ver un ejemplo en la terminal:

```bash
python main.py
```

Para ejecutar las pruebas de Python:

```bash
python -m unittest discover -v
```

## Tipos de empleado

- **Asalariado:** recibe un salario fijo. El ejercicio contempla un aumento del 10 % cuando supera los cinco años de antigüedad.
- **Por horas:** cobra según las horas trabajadas. Las horas que pasan de 40 se pagan a una tarifa de 1,5 veces la normal.
- **Por comisión:** recibe un salario base y una comisión sobre las ventas. Si las ventas superan los $20.000.000, se agrega un 3 % sobre las ventas.
- **Temporal:** recibe un salario fijo durante el tiempo indicado en el contrato.

## Deducciones y beneficios

El cálculo descuenta el 4 % de seguridad social y pensión, además de la ARL configurada. Los empleados asalariados y por comisión tienen un bono de alimentación de $1.000.000, pagado por la empresa y mostrado por separado. Para empleados por horas, el fondo de ahorro del 2 % aplica cuando llevan más de un año y aceptan el aporte.

Estos porcentajes y condiciones corresponden a los supuestos del ejercicio. No deben tomarse como una liquidación laboral oficial.

## Interfaz web

Ejecuta el siguiente comando para abrir el sistema en el navegador:

```bash
./abrir_sistema_web.sh
```

El script inicia un servidor local y abre la página principal. La web tiene cuatro páginas:

- `index.html`: resumen general.
- `empleados.html`: registro, búsqueda, edición y eliminación de empleados.
- `nomina.html`: cálculo y detalle de los pagos.
- `reportes.html`: resumen y exportación a CSV.

Los archivos `app.js` y `app.css` contienen la lógica y los estilos que comparten las páginas. Los registros de la versión web se guardan en el almacenamiento del navegador; no se sincronizan con la aplicación de escritorio ni con otros dispositivos.

La aplicación de escritorio guarda los datos en `payroll/employees_data.json` al registrar el primer empleado. Ese archivo es local y no se incluye en Git.

## Archivos principales

```text
sistema_nomina_cipa/
├── gui.py
├── main.py
├── payroll/
│   ├── employees.py
│   └── payroll_service.py
├── tests/
│   ├── test_payroll.py
│   └── test_web_logic.js
├── index.html
├── empleados.html
├── nomina.html
├── reportes.html
├── app.css
├── app.js
└── abrir_sistema_web.sh
```

Las clases de empleados contienen las reglas de cada tipo de pago. `PayrollService` reúne los cálculos de nómina y `PayrollConfig` permite configurar los porcentajes usados por el servicio.

## Comprobar los cambios

```bash
python -m unittest discover -v
node --check app.js
node tests/test_web_logic.js
bash -n abrir_sistema_web.sh
git diff --check
```

Las pruebas comprueban los cálculos y algunos casos de la lógica web. Conviene abrir la aplicación y probar también el registro, la edición, la eliminación, los reportes y la exportación antes de entregarla.
