# Fuentes

Las tres tipografías están bajo **SIL Open Font License 1.1** y Devicon bajo **MIT**; ambas
permiten usarlas, incrustarlas y redistribuirlas siempre que la licencia viaje con ellas.
Por eso los `OFL-*.txt` y `MIT-Devicon.txt` están aquí.

| Fuente | Papel | Autoría |
|---|---|---|
| **Archivo Black** | Sin uso desde la cabecera mínima; se queda por si vuelve. | Omnibus-Type |
| **Space Grotesk** | El oficio en la cabecera. | Florian Karsten |
| **JetBrains Mono** | Etiquetas pequeñas y los nombres del stack. | JetBrains |
| **Devicon** | Los iconos del stack (fuente de iconos, `master` del 17/09/2026). | konpa y colaboradores |

`generate.py` no las enlaza: las **recorta** a los caracteres que cada pieza usa y las
incrusta en el SVG en base64. Por eso la cabecera pesa unos 7 KB y se ve igual
en cualquier máquina, tenga instalada la fuente o no.

Los iconos de Devicon y los nombres del stack no se incrustan como fuente: se convierten
a trazos (`<path>`), así que cada pieza del stack pesa unos 4 KB y no depende de nada.
