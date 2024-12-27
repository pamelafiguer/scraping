from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json
import webbrowser


MODALIDADES_PERMITIDAS = ['Presencial', 'Híbrido', 'Remoto']
def obtener_detalles(url, driver):
    try:
        print(f"Obteniendo detalles de: {url}")  # Debug
        driver_detalles = webdriver.Chrome()
        driver_detalles.get(url)
        
        # Aumentar tiempo de espera
        time.sleep(5)
        
        # Espera explícita para los detalles
        WebDriverWait(driver_detalles, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sc-jqsdoX"))
        )
        
        html_detalles = driver_detalles.page_source
        soup_detalles = BeautifulSoup(html_detalles, 'html.parser')
        
        # Buscar el contenedor de detalles con selector más flexible
        detalles_container = soup_detalles.find('div', class_=lambda x: x and 'sc-jqsdoX' in x)
        
        if detalles_container:
            # Obtener todos los párrafos
            parrafos = detalles_container.find_all(['p', 'li'])
            
            # Concatenar texto
            texto_detalles = '\n'.join([p.text.strip() for p in parrafos if p.text.strip()])
            
            return texto_detalles if texto_detalles else "No disponible"
        
        return "No disponible"
        
    except Exception as e:
        print(f"Error detallado al obtener detalles: {str(e)}")
        return "No disponible"
    finally:
        try:
            driver_detalles.quit()
        except:
            pass


def configurar_driver():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    return webdriver.Chrome(options=chrome_options)

trabajos_lista = []

try:
    driver = configurar_driver()
    url = "https://www.bumeran.com.pe/empleos-busqueda-python.html?recientes=true"
    driver.get(url)
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "sc-jBoNkH"))
    )
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    Datos = soup.find_all('div', class_=lambda x: x and 'sc-jBoNkH' in x)
    
    for index, item in enumerate(Datos, 1):
        try:
            trabajo_info = {
                "id": index,
                "titulo": "No disponible",
                "empresa": "No disponible",
                "ubicacion": "No disponible",
                "modalidad": "No disponible",
                "tiempo_publicacion": "No disponible",
                "calificacion": "No disponible",
                "url": "No disponible"
            }
            
            
            titulo = item.find('span', class_=lambda x: x and 'sc-hfLElm jPHYOC' in x)
            if titulo:
                trabajo_info["titulo"] = titulo.text.strip()

            
            empresa = item.find('span', class_=lambda x: x and 'sc-jFpLkX' in x)
            if empresa:
                trabajo_info["empresa"] = empresa.text.strip()
            

            elementos = item.find_all('span', class_='sc-gkfylT gFZkwW')

            if len(elementos) >= 2:  
              if elementos[0]:
                trabajo_info["ubicacion"] = elementos[0].text.strip()
    
              if elementos[1]:
                 modalidad_texto = elementos[1].text.strip()
                 if any(m.lower() in modalidad_texto.lower() for m in MODALIDADES_PERMITIDAS):
                    for m in MODALIDADES_PERMITIDAS:
                        if m.lower() in modalidad_texto.lower():
                           trabajo_info["modalidad"] = m
                           break
                 else:
                   trabajo_info["modalidad"] = "No especificada"
            calificacion = item.find('div', class_=lambda x: x and 'sc-juQqkt' in x)
            if calificacion:
                calif_texto = calificacion.get_text().strip()
                if calif_texto.replace('.','',1).isdigit():
                    trabajo_info["calificacion"] = calif_texto
            
            tiempo = item.find('div', class_=lambda x: x and 'sc-izUgoq' in x)
            if tiempo:
                trabajo_info["tiempo_publicacion"] = tiempo.text.strip()
            
            
            url_element = item.find('a', class_=lambda x: x and 'sc-fPbjcq iognrJ' in x)
            if url_element and url_element.get('href'):
              base_url = "https://www.bumeran.com.pe"
              url_path = url_element['href']
              if not url_path.startswith('http'):
                  trabajo_info["url"] = base_url + url_path
              else:
                 trabajo_info["url"] = url_path
            
              if trabajo_info["url"] != "No disponible":
                 trabajo_info["detalles"] = obtener_detalles(trabajo_info["url"], driver)

            trabajos_lista.append(trabajo_info)
            
            print(f"\nOferta #{index}")
            print(f"Título: {trabajo_info['titulo']}")
            print(f"Empresa: {trabajo_info['empresa']}")
            print(f"Ubicación: {trabajo_info['ubicacion']}")
            print(f"Modalidad: {trabajo_info['modalidad']}")
            print(f"Calificación: {trabajo_info['calificacion']}")
            print(f"Detalles: {trabajo_info['Detalles']}")
            print(f"Tiempo: {trabajo_info['tiempo_publicacion']}")
            print(f"URL: {trabajo_info['url']}")
            print("-" * 50)
            
        except Exception as e:
            print(f"Error procesando oferta {index}: {str(e)}")
            continue
    
    with open('trabajos_bumeran.json', 'w', encoding='utf-8') as f:
        json.dump({"ofertas": trabajos_lista}, f, ensure_ascii=False, indent=2)
    print(f"\nSe encontraron {len(trabajos_lista)} ofertas")
    print("Datos guardados en trabajos_bumeran.json")
    
    while trabajos_lista:
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
            break

except Exception as e:
    print(f"Error general: {str(e)}")

finally:
    driver.quit()
    print("\nNavegador cerrado")