from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import json
import webbrowser

def obtener_detalles(url, driver):
    try:
        driver_detalles = webdriver.Chrome()  # Crear nuevo driver para no interferir
        driver_detalles.get(url)
        time.sleep(2)
        
        html_detalles = driver_detalles.page_source
        soup_detalles = BeautifulSoup(html_detalles, 'html.parser')
        
        # Aquí agregarás el selector específico cuando lo encuentres
        detalles = soup_detalles.find('p', class_='mbB')
        
        driver_detalles.quit()
        if detalles:
            return detalles.text.strip()
        return "No disponible"
    except Exception as e:
        print(f"Error al obtener detalles: {str(e)}")
        return "No disponible"


trabajos_lista = []

# Configurar el driver
driver = webdriver.Chrome()
url = "https://www.bumeran.com.pe/en-lima/empleos-busqueda-programador-en-java.html"
driver.get(url)

# Esperar a que la página cargue
time.sleep(3)

# Obtener el HTML
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# Encontrar todos los trabajos
Datos = soup.find_all('div', class_='sc-kAPOMq gIDpXV sc-jBoNkH qkxdS')
# Extraer datos con manejo de errores
for index, item in enumerate(Datos, 1):
    try:
        trabajo_info = {
            "id": index,
            "titulo": "No disponible",
            "empresa": "No disponible",
            "calificacion": "No disponible",
            "ubicacion": "No disponible",
            "modalidad": "No disponible",
            "tiempo_publicacion": "No disponible",
            "url": ""
        }
        
        # calificación
        calificacion = item.find('p', class_='dIB fs16 fc_base mt5')      
        if calificacion and calificacion.find('span', class_='fwB'):
            trabajo_info["calificacion"] = calificacion.find('span').text.strip()
  
                # Título y URL
        titulo = item.find('h2', class_='fs18 fwB')
        if titulo and titulo.find('a'):
            trabajo_info["titulo"] = titulo.find('a').text.strip()
            # Asegurarse que la URL sea absoluta
            url_relativa = titulo.find('a')['href']
            trabajo_info["url"] = f"https://pe.computrabajo.com{url_relativa}" if not url_relativa.startswith('http') else url_relativa
            detalles = obtener_detalles(trabajo_info["url"], driver)
            trabajo_info["Detalles"] = detalles

        # Ubicación
        ubicacion = item.find('p', class_='fs16 fc_base mt5')
        if ubicacion and ubicacion.find('span', class_='mr10'):
            trabajo_info["ubicacion"] = ubicacion.find('span', class_='mr10').text.strip()
        
        # Empresa
        empresa = item.find('span', class_='sc-jFpLkX coQDdI')
        if empresa and empresa.find('h3'):
            trabajo_info["empresa"] = empresa.find('a').text.strip()
        
        # Modalidad
        modalidad = item.find('div', class_='fs13 mt15')
        if modalidad and modalidad.find('span', class_='dIB mr10'):
            trabajo_info["modalidad"] = modalidad.find('span').text.strip()
            
        # Tiempo de publicidad
        tiempo = item.find('p', class_='fs13 fc_aux mt15')
        if tiempo:
            trabajo_info["tiempo_publicacion"] = tiempo.text.strip()
        
       
        trabajos_lista.append(trabajo_info)
        
        # Imprimir información
        print(f"\nOferta #{index}")
        print(f"Título: {trabajo_info['titulo']}")
        print(f"Empresa: {trabajo_info['empresa']}")
        print(f"Calificación: {trabajo_info['calificacion']}")
        print(f"Ubicación: {trabajo_info['ubicacion']}")
        print(f"Modalidad: {trabajo_info['modalidad']}")
        print(f"Detalles: {trabajo_info['Detalles']}")
        print(f"Tiempo de publicación: {trabajo_info['tiempo_publicacion']}")
        print(f"URL: {trabajo_info['url']}")
        print("-" * 50)

    except Exception as e:
        print(f"Error al procesar item {index}: {str(e)}")
        continue

# Guardar en JSON
with open('trabajos.json', 'w', encoding='utf-8') as f:
    json.dump({"ofertas": trabajos_lista}, f, ensure_ascii=False, indent=2)
print("\nDatos guardados en trabajos.json")

# Interacción con usuario para abrir URLs
while True:
    try:
        seleccion = input(f"\nIngrese número de oferta (1-{len(trabajos_lista)}) o 'q' para salir: ")
        if seleccion.lower() == 'q':
            break
        
        indice = int(seleccion) - 1
        if 0 <= indice < len(trabajos_lista):
            print(f"\nAbriendo oferta: {trabajos_lista[indice]['titulo']}")
            webbrowser.open(trabajos_lista[indice]['url'])
        else:
            print("Número de oferta inválido")
    except ValueError:
        print("Por favor ingrese un número válido")
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario")
        break

# Cerrar el driver
driver.quit()
print("\nNavegador cerrado")