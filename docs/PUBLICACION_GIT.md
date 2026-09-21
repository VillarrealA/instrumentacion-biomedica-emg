# Publicación de la entrega en Git

## 1. Preparar la carpeta del equipo

1. Descomprimir el repositorio.
2. Copiar únicamente resúmenes, métricas y figuras derivadas a
   `resultados/equipoXX/`.
3. Completar `informes/equipoXX.md`.
4. Colocar en `figuras/` sólo las figuras finales de la entrega.
5. Incluir el esquema, los cálculos y la tabla de validación del acoplador.
6. Confirmar que `datos/crudos/` y las series temporales procesadas no contienen
   archivos rastreados por Git.

Para comprobarlo:

```bash
git status
```

Si aparece un CSV con todas las muestras de una persona, no debe agregarse al
repositorio. Los archivos `*_procesada.csv` de los equipos están excluidos por
el `.gitignore` incluido.

## 2. Crear el repositorio local

```bash
git init
git add .
git commit -m "Entrega inicial de la práctica EMG"
git branch -M main
```

## 3. Crear un repositorio remoto

Crear en GitHub o GitLab un repositorio privado llamado, por ejemplo:

```text
instrumentacion-biomedica-emg-equipo01
```

No solicitar que el servicio agregue otro README, licencia o `.gitignore`, pues
ya están incluidos.

## 4. Enlazar y publicar

Reemplazar la dirección por la correspondiente al equipo:

```bash
git remote add origin https://github.com/USUARIO/instrumentacion-biomedica-emg-equipo01.git
git push -u origin main
```

## 5. Actualizaciones

```bash
git add resultados figuras informes docs
git commit -m "Agrega análisis y discusión de las estaciones"
git push
```

## Lista de revisión

- [ ] El README identifica el equipo mediante un código, no mediante datos personales.
- [ ] El informe registra equipo, colocación, separación, muestreo y filtros.
- [ ] Se incluyen diseño, valores, ganancia y validación del acoplador.
- [ ] Todas las ventanas analizadas incluyen tiempo inicial y final.
- [ ] Las figuras muestran unidades y condiciones.
- [ ] Los resultados distinguen actividad eléctrica de fuerza mecánica.
- [ ] El repositorio no contiene datos crudos, series muestra por muestra ni
      identificadores personales.
- [ ] Otro equipo puede ejecutar el programa con un CSV del mismo formato.

## Historial sugerido

En lugar de un solo commit final, conviene conservar un historial breve:

```text
1. Estructura inicial y protocolo
2. Resultados de Vernier
3. Diseño y validación del acoplador
4. Resultados de Arduino
5. Comparación con PhysioNet
6. Discusión y revisión final
```
