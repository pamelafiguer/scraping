import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configuración de Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ejecutar en modo headless (sin interfaz gráfica)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--enable-unsafe-webgl")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")

# URL de la página de LinkedIn
url = "https://www.linkedin.com/jobs/search/?currentJobId=4102767425&keywords=programador%20php&origin=BLENDED_SEARCH_RESULT_NAVIGATION_SEE_ALL&originToLandingJobPostings=4102767425%2C4102764750%2C4015046639"

# Iniciar el navegador
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Acceder a la página
    driver.get(url)
    time.sleep(5)  # Esperar a que la página cargue completamente

    # Extraer los elementos de las ofertas de empleo
    jobs = driver.find_elements(By.CSS_SELECTOR, '.job-card-container__link')

    for job in jobs:
        try:
            # Extraer el título de la oferta
            title_element = job.find_element(By.CSS_SELECTOR, 'h3.job-card-list__title')
            title = title_element.text.strip() if title_element else "No disponible"

            # Extraer el nombre de la empresa
            company_element = job.find_element(By.CSS_SELECTOR, 'h4.job-card-container__company-name')
            company = company_element.text.strip() if company_element else "No disponible"

            # Extraer la ubicación
            location_element = job.find_element(By.CSS_SELECTOR, 'span.job-card-container__metadata-item')
            location = location_element.text.strip() if location_element else "No disponible"

            # Imprimir los detalles de la oferta
            print(f"Título: {title}\nEmpresa: {company}\nUbicación: {location}\n{'-' * 40}")

        except Exception as e:
            print(f"Error al extraer los detalles de la oferta: {e}")

        # Agregar un retraso aleatorio entre 1 y 3 segundos
        time.sleep(1)

except Exception as e:
    print(f"Ocurrió un error: {e}")

finally:
    # Cerrar el navegador
    driver.quit()