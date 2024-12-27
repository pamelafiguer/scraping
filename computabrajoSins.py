import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime, timedelta

class ComputrabajoScraper:
    def __init__(self):
        self.base_url = "https://pe.computrabajo.com/trabajo-de-programadores-java-en-lima"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def parse_fecha(self, fecha_texto):
        fecha_texto = fecha_texto.lower().strip()
        today = datetime.now()
        
        if "ayer" in fecha_texto:
            return (today - timedelta(days=1)).strftime("%Y-%m-%d")
        elif "hace" in fecha_texto:
            dias = int(''.join(filter(str.isdigit, fecha_texto)))
            return (today - timedelta(days=dias)).strftime("%Y-%m-%d")
        elif "más de 30 días" in fecha_texto:
            return (today - timedelta(days=30)).strftime("%Y-%m-%d")
        else:
            try:
                return datetime.strptime(fecha_texto, "%d de %B").replace(year=today.year).strftime("%Y-%m-%d")
            except:
                return fecha_texto

    def obtener_ofertas(self, paginas=3):
        todas_ofertas = []
        
        for pagina in range(1, paginas + 1):
            url = f"{self.base_url}?p={pagina}"
            
            try:
                response = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                trabajos = soup.find_all('article', class_='box_offer')
                
                for trabajo in trabajos:
                    oferta = {
                        'titulo': trabajo.find('h1', class_='fs18').get_text(strip=True) if trabajo.find('h1', class_='fs18') else "",
                        'empresa': trabajo.find('a', class_='fc_base').get_text(strip=True) if trabajo.find('a', class_='fc_base') else "",
                        'ubicacion': trabajo.find('p', class_='fs16').get_text(strip=True) if trabajo.find('p', class_='fs16') else "",
                        'descripcion': trabajo.find('p', class_='fw_b').get_text(strip=True) if trabajo.find('p', class_='fw_b') else "",
                        'salario': trabajo.find('p', class_='fs16 fc_base').get_text(strip=True) if trabajo.find('p', class_='fs16 fc_base') else "No especificado",
                        'fecha': trabajo.find('p', class_='fs13').get_text(strip=True) if trabajo.find('p', class_='fs13') else ""
                    }
                    
                    # Limpiar y formatear datos
                    oferta = {k: v.strip() for k, v in oferta.items() if v}
                    oferta['fecha'] = self.parse_fecha(oferta['fecha'])
                    todas_ofertas.append(oferta)
                
                time.sleep(2)  # Pausa entre solicitudes
                
            except Exception as e:
                print(f"Error en página {pagina}: {str(e)}")
                continue
        
        # Crear DataFrame y ordenar por fecha
        df = pd.DataFrame(todas_ofertas)
        df = df.sort_values('fecha', ascending=False)
        
        # Guardar en CSV con formato mejorado
        df.to_csv('ofertas_java_lima.csv', index=False, encoding='utf-8-sig')
        
        print(f"\nSe encontraron {len(todas_ofertas)} ofertas de trabajo")
        print("\nPrimeras 5 ofertas más recientes:")
        print(df.head().to_string())

if __name__ == "__main__":
    scraper = ComputrabajoScraper()
    scraper.obtener_ofertas()