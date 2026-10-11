# Upgrade de arrakis a Ubuntu 26.04.1 LTS — impacto en `aibot`

Fecha: 2026-10-10/11. Documento general: `/opt/servicios_locales/upgrade_2604/README.md`.

## Qué cambió

Ubuntu 26.04 sustituye Python 3.12 por **Python 3.14** (`python3.12` ya no existe). El venv de este
proyecto apuntaba a `/usr/bin/python3.12` y dejó de funcionar con el upgrade. **No hubo cambios de código.**

## Venv reconstruido

| | |
|---|---|
| Ruta | `/opt/aibot/venv` (misma ruta, mismo dueño y permisos) |
| Python | 3.12.3 -> **3.14** |
| Paquetes instalados | 52 |
| Versiones distintas al manifiesto 3.12 | lxml(6.1.3) psycopg2-binary(2.9.13) pydantic_core(2.50.0) |
| Venv anterior (se conserva unos días) | `/opt/aibot/venv.py312` |
| Manifiesto previo | `/opt/servicios_locales/upgrade_2604/manifests/venvs/opt_aibot_venv.req` |
| Log | `/opt/servicios_locales/upgrade_2604/venv_logs/opt_aibot_venv.log` |
| Script | `/opt/servicios_locales/upgrade_2604/rebuild_venv.sh` |

## Uso del venv

`aibot.service` (actualmente `disabled`).

## Verificación

Sin servicio activo. 3 paquetes sin wheel para la versión fijada en 3.14 se instalaron en la versión más cercana compatible (ver tabla).

## Rehacer el venv desde cero

```bash
/opt/servicios_locales/upgrade_2604/rebuild_venv.sh /opt/aibot/venv \
  /opt/servicios_locales/upgrade_2604/manifests/venvs/opt_aibot_venv.req
```
