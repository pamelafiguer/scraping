import ssl, json, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import webbrowser

# Configuración SSL
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

def configurar_chrome():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    return options

def obtener_descripcion(url, service, chrome_options):
    descripcion_driver = None
    try:
        # Aumentar tiempo de espera
        descripcion_driver = webdriver.Chrome(service=service, options=chrome_options)
        descripcion_driver.set_page_load_timeout(30)
        descripcion_driver.get(url)
        time.sleep(3)
        
        wait = WebDriverWait(descripcion_driver, 10)
        description_elements = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, '.box_detail p, .box_detail li')))
        
        description_texts = []
        for element in description_elements:
            text = element.text.strip()
            if text and len(text) > 30:
                description_texts.append(text)
        
        return '\n'.join(description_texts) if description_texts else "Descripción no disponible"
    
    except Exception as e:
        print(f"Error al obtener descripción: {str(e)}")
        return "Descripción no disponible"
    finally:
        if descripcion_driver:
            try:
                descripcion_driver.quit()
            except:
                pass

def extraer_datos_trabajo(job, service, chrome_options, index):
    try:
        # Aumentar tiempo de espera inicial
        time.sleep(2)
        wait = WebDriverWait(job, 15)
        
        try:
            # Título y URL
            title_element = job.find_element(By.CSS_SELECTOR, 'h1.fs18 a, .js-o-link')
            title = title_element.text.strip()
            job_url = title_element.get_attribute('href').split('#')[0]
        except:
            title = "No disponible"
            job_url = ""
            
        try:
            # Empresa
            company_element = job.find_element(By.CSS_SELECTOR, 'fc_base t_ellipsis')
            company = company_element.text.strip()
        except:
            company = "No disponible"
            
        try:
            # Calificación 
            rating_element = job.find_element(By.CSS_SELECTOR, '.dFlex span')
            rating = rating_element.text.strip()
        except:
            rating = "No disponible"
            
        try:
            # Ubicación
            location_element = job.find_element(By.CSS_SELECTOR, 'p.fs16.fc_base span[itemprop="addressLocality"]')
            location = location_element.text.strip()
        except:
            location = "No disponible"

        # Modalidad y tiempo
        modality_salary = "No disponible"
        time_posted = "No disponible"
        
        try:
            info_elements = job.find_elements(By.CSS_SELECTOR, '.fs13, .tag-mobile')
            for element in info_elements:
                text = element.text.strip()
                if any(keyword in text.lower() for keyword in ["presencial", "remoto", "s/."]):
                    modality_salary = text
                elif any(keyword in text.lower() for keyword in ["hace", "ayer"]):
                    time_posted = text
        except:
            pass

        return {
            "id": index,
            "titulo": title,
            "empresa": company,
            "calificacion": rating,
            "ubicacion": location,
            "modalidad_sueldo": modality_salary,
            "tiempo_publicacion": time_posted,
            "url": job_url
        }
        
    except Exception as e:
        print(f"Error extrayendo datos de trabajo {index}: {str(e)}")
        return None
    


def main():
    url = 'https://pe.computrabajo.com/trabajo-de-programadores-java-en-lima'
    print("Iniciando búsqueda de trabajos...")
    
    chrome_options = configurar_chrome()
    service = Service(ChromeDriverManager().install())
    driver = None
    trabajos_lista = []

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        time.sleep(5)

        wait = WebDriverWait(driver, 15)
        jobs = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'box_offer')))

        if not jobs:
            print("No se encontraron ofertas de trabajo")
            return

        print(f"\nSe encontraron {len(jobs)} ofertas de trabajo")

        for index, job in enumerate(jobs, 1):
            trabajo_info = extraer_datos_trabajo(job, service, chrome_options, index)
            
            if trabajo_info:
                trabajos_lista.append(trabajo_info)
                
                print(f"\nOferta #{index}")
                print(f"Título: {trabajo_info['titulo']}")
                print(f"Empresa: {trabajo_info['empresa']}")
                print(f"Calificación: {trabajo_info['calificacion']}")
                print(f"Ubicación: {trabajo_info['ubicacion']}")
                print(f"Modalidad y sueldo: {trabajo_info['modalidad_sueldo']}")
                print(f"Tiempo de publicación: {trabajo_info['tiempo_publicacion']}")
                print(f"Descripción: {trabajo_info['descripcion'][:200]}...")
                print(f"URL: {trabajo_info['url']}")
                print("-" * 50)
        with open('trabajos.json', 'w', encoding='utf-8') as f:
            json.dump({"ofertas": trabajos_lista}, f, ensure_ascii=False, indent=2)
        print("\nDatos guardados en trabajos.json")
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

    except Exception as e:
        print(f"Error general: {e}")
    
    finally:
        if driver:
            driver.quit()
            print("\nNavegador cerrado")

if __name__ == "__main__":
    main()