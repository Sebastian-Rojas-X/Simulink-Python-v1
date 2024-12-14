import matlab.engine
import matplotlib.pyplot as plt

# Iniciar la API de MATLAB
eng = matlab.engine.start_matlab()

# Establecer el directorio de trabajo de MATLAB a donde está el modelo de Simulink y el archivo .mat
eng.cd(r'C:\New Microred Simulink') 

# Cargar el modelo de Simulink
eng.load_system('SmallScaleMicroGrid')

# Valores para 'num_valor'
num_valores = [0, 14400, 28800, 43200, 57600, 72000] #Divición en N ventanas de tiempo (60x60x24)

# Inicializar listas para almacenar los datos
all_load_data = []
all_solar_data = []
all_batt_data = []
all_acum_data = []

last_acum = 0

# Ciclo para simular con diferentes valores
for num_valor in num_valores:
    print(f"****************************************")
    print(f"Simulando con num_valor = {num_valor}")
    
    # Ajustar los parámetros del tiempo de simulación
    start_time = str(0)     # Tiempo de inicio de la simulación
    stop_time = str(14400)  # Tiempo de fin de la simulación (en segundos)
    eng.set_param('SmallScaleMicroGrid', 'StartTime', start_time, nargout=0)
    eng.set_param('SmallScaleMicroGrid', 'StopTime', stop_time, nargout=0)

    # Cambiar el valor de una constante
    model_name = 'SmallScaleMicroGrid'          # Nombre del modelo

    constant_block = f'{model_name}/Constant3'  # Bloque específico
    eng.set_param(constant_block, 'Value', str(num_valor), nargout=0)

    constant_block2 = f'{model_name}/Constant5'  # Bloque específico
    eng.set_param(constant_block2, 'Value', str(last_acum), nargout=0)

    # Simular el modelo de Simulink
    eng.sim('SmallScaleMicroGrid', nargout=0)

    # Obtener los datos de salida
    load_data = eng.workspace['load_out']   
    load_data = [item2[0] for item2 in load_data]
    all_load_data.append(load_data)
    first_load = load_data[0]              
    print(f"Valor carga inicial: {first_load}")

    solar_data = eng.workspace['solar_out']   
    solar_data = [item3[0] for item3 in solar_data]
    all_solar_data.append(solar_data)
    first_solar = solar_data[0]              
    print(f"Valor solar inicial: {first_solar}")

    batt_data = eng.workspace['batt_out']   
    batt_data = [item3[0] for item3 in batt_data]
    all_batt_data.append(batt_data)
    first_batt = batt_data[0]              
    print(f"Valor bateria inicial: {first_batt}")

    acum_data = eng.workspace['acum_out']   
    acum_data = [item4[0] for item4 in acum_data]
    all_acum_data.append(acum_data)
    last_acum = acum_data[-1]              
    print(f"Valor acumulado inicial: {last_acum}")

# Guardar el modelo
eng.save_system('SmallScaleMicroGrid', nargout=0)

# Cerrar el sistema de Simulink
eng.close_system('SmallScaleMicroGrid', nargout=0)

# Finalizar el engine de MATLAB
eng.quit()

# Graficar los datos en ventanas separadas

# Gráfico para load_data
plt.figure()
for i, data in enumerate(all_load_data):
    plt.plot(data, label=f'num_valor = {num_valores[i]}')
plt.title('Datos de carga (load_out)')
plt.xlabel('Tiempo (muestras)')
plt.ylabel('Valor de carga')
plt.legend()
plt.grid(True)
plt.show(block=False)

# Gráfico para solar_data
plt.figure()
for i, data in enumerate(all_solar_data):
    plt.plot(data, label=f'num_valor = {num_valores[i]}')
plt.title('Datos solares (solar_out)')
plt.xlabel('Tiempo (muestras)')
plt.ylabel('Valor solar')
plt.legend()
plt.grid(True)
plt.show(block=False)

# Gráfico para batt_data
plt.figure()
for i, data in enumerate(all_batt_data):
    plt.plot(data, label=f'num_valor = {num_valores[i]}')
plt.title('Datos de batería (batt_out)')
plt.xlabel('Tiempo (muestras)')
plt.ylabel('Valor de la batería')
plt.legend()
plt.grid(True)
plt.show(block=False)

# Pausar para mantener las ventanas abiertas
#input("Presione Enter para cerrar los gráficos...")
plt.show()

#-------------------------------------------------------
# CODIGO ALGORITMO OPTIMIZACION

from pulp import LpProblem, LpVariable, LpBinary, LpMinimize, value

# Crear el modelo de optimización
model = LpProblem("Minimizar_costos_operativos", LpMinimize)

# Parámetros (ejemplo simple)
I_demand = 20   # Corriente demandada por la casa (A)
I_solar = 12    # Corriente generada por los paneles solares (A)
I_bat_max = 10  # Corriente máxima que puede entregar la batería (A)

C_grid = 0.5    # Costo de la corriente de la red (\$/A)
C_bat = 0.2     # Costo de la corriente de la batería (\$/A)

# Variables de decisión
I_grid = LpVariable("I_grid", lowBound=0, cat="Continuous")     # Corriente de la red (A)
I_bat = LpVariable("I_bat", lowBound=0, cat="Continuous")       # Corriente de la batería (A)
x = LpVariable("x", cat="Binary")                               # Variable binaria para uso de la batería

# Función objetivo: Minimizar costos operativos
model += C_grid * I_grid + C_bat * I_bat, "Costo_total"

# Restricciones
model += I_demand == I_solar + I_bat + I_grid, "Balance_corriente"  # Balance de corriente
model += I_bat <= x * I_bat_max, "Limite_corriente_bateria"         # Límite de corriente de la batería

# Resolver el modelo
model.solve()

# Resultados
print(f"Estado del modelo: {model.status}")
print(f"Corriente tomada de la red: {value(I_grid)} A")
print(f"Corriente suministrada por la batería: {value(I_bat)} A")
print(f"Uso de la batería (x): {int(value(x))}")
print(f"Costo total: {value(model.objective)} $")
#-------------------------------------------------------