@echo off
SET REPO=C:\Users\ASUS\marketing_de_influencia
SET PYTHON=C:\Users\ASUS\AppData\Local\Programs\Python\Python313\python.exe

:: Tarea cada hora
schtasks /create /tn "InfluMetric_Hourly" /tr "%PYTHON% %REPO%\pipeline.py" /sc hourly /mo 1 /st 08:00 /f

:: Tarea al arrancar Windows
schtasks /create /tn "InfluMetric_Startup" /tr "%PYTHON% %REPO%\scheduler.py" /sc onstart /delay 0001:00 /f

echo Tareas creadas correctamente.
pause
