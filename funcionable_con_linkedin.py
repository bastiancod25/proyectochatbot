# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import time
import re
import random
import json
import os
from datetime import datetime
import hashlib
from google.cloud import storage # <--- LIBRERÍA NECESARIA PARA LA NUBE

# --- CONFIGURACIÓN DE CLOUD STORAGE ---
# ¡IMPORTANTE! Reemplaza 'historial_practicas' con el nombre exacto de tu Bucket
BUCKET_NAME = "historial_practicas"
BLOB_NAME = "ofertas_publicadas.json"

# CONFIGURACIÓN JWT PARA PRACTICE (se mantiene igual)
JWT_CONFIG = {
    'login_url': 'http://practicas.fi.ubiobio.cl/index.php/wp-json/jwt-auth/v1/token',
    'posts_url': 'http://practicas.fi.ubiobio.cl/index.php/wp-json/wp/v2/practice',
    'validate_url': 'http://practicas.fi.ubiobio.cl/index.php/wp-json/jwt-auth/v1/token/validate',
    'media_url': 'http://practicas.fi.ubiobio.cl/index.php/wp-json/wp/v2/media',
    'username': 'darkazz123',
    'password': 'RfFroY3E55qd6Dxdcq$R1$qR'
}

# URL de la búsqueda en LinkedIn y Headers (se mantienen igual)
url = "https://www.linkedin.com/jobs/search/?f_JT=I&f_TPR=r2592000&geoId=104621616&keywords=practica&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true&sortBy=DD&spellCorrectionEnabled=true"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image:apng,*/*;q=0.8',
    'Connection': 'keep-alive',
}

# Lista de palabras clave y carreras (se mantienen igual)
PALABRAS_CLAVE_PRACTICA = ['práctica profesional', 'practicante', 'internship', 'pasantía', 'estudiante en práctica', 'alumnos en práctica']

CARRERAS_ALIAS = {
    'Ingeniería Civil Industrial': ['ingenieria civil industrial', 'ing. civil industrial', 'ing civil industrial', 'ingeniero civil industrial', 'civil industrial'],
    'Ingeniería Ejecucion en Mecánica': ['ingenieria ejecucion mecanica', 'ing. ejecucion mecanica', 'ing ejecucion mecanica', 'ingeniero ejecucion mecanico', 'ejecucion mecanica'],
    'Ingeniería Civil Eléctrica': ['ingenieria civil electrica', 'ing. civil electrica', 'ing civil electrica', 'ingeniero civil electrico', 'civil electrico', 'civil electrica'],
    'Ingeniería Civil en Automatización': ['ingenieria civil en automatizacion', 'ing. civil en automatizacion', 'ingeniero civil en automatizacion', 'civil en automatizacion'],
    'Ingeniería Civil Química': ['ingenieria civil quimica', 'ing. civil quimica', 'ing civil quimica', 'ingeniero civil quimico', 'civil quimico', 'civil quimica'],
    'Ingeniería Civil': ['ingenieria civil', 'ing. civil', 'ing civil', 'ingeniero civil']
}

# --------------------------------------------------------------------------
# --- FUNCIONES ADAPTADAS PARA CLOUD STORAGE ---
# --------------------------------------------------------------------------

def cargar_ofertas_publicadas():
    """Carga ofertas ya publicadas desde Google Cloud Storage"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(BLOB_NAME)
    
    try:
        # Descarga el contenido del archivo JSON
        content = blob.download_as_text(encoding='utf-8')
        print(f"📁 DEBUG Historial cargado de Cloud Storage ({len(content)} bytes)")
        return json.loads(content)
    except Exception as e:
        # Si el archivo no existe (error 404), retorna una lista vacía. Esto es normal la primera vez.
        print(f"⚠️ No se pudo cargar el historial (puede que el archivo no exista o haya error de permisos). Error: {e}")
        return []

def guardar_ofertas_publicadas(ofertas_publicadas):
    """Guarda ofertas publicadas en Google Cloud Storage"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(BLOB_NAME)
    
    try:
        # Sube el contenido actualizado
        blob.upload_from_string(
            data=json.dumps(ofertas_publicadas, ensure_ascii=False, indent=2),
            content_type='application/json'
        )
        print(f"✅ Historial actualizado en Cloud Storage: {BLOB_NAME}")
    except Exception as e:
        print(f"❌ Error al guardar en Cloud Storage: {e}. Revisa permisos IAM.")


# --------------------------------------------------------------------------
# --- FUNCIONES RESTANTES (se mantienen casi igual) ---
# --------------------------------------------------------------------------

def generar_hash_oferta(oferta):
    """Genera un hash simple basado en el título y la empresa"""
    base_string = f"{oferta['titulo'].lower()}_{oferta['empresa'].lower()}"
    hash_generado = hashlib.md5(base_string.encode()).hexdigest()
    # print(f"🔍 DEBUG Hash generado: {hash_generado} para '{oferta['titulo']}' - '{oferta['empresa']}'")
    return hash_generado

def limpiar_texto(texto):
    """Limpia el texto de caracteres especiales y normaliza"""
    if not texto: return ""
    texto = texto.lower()
    texto = texto.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    texto = texto.replace('ñ', 'n')
    texto = re.sub(r'[.,]', '', texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()

def limpiar_descripcion(descripcion):
    """Limpia la descripción eliminando 'Show more', 'Show less', etc."""
    if not descripcion: return ""
    patrones_eliminar = [ r'show more\s*show less', r'show more', r'show less', r'ver más\s*ver menos', r'ver más', r'ver menos' ]
    descripcion_limpia = descripcion
    for patron in patrones_eliminar:
        descripcion_limpia = re.sub(patron, '', descripcion_limpia, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', descripcion_limpia).strip()

def identificar_carreras_por_alias(titulo, descripcion, carreras_alias_dict):
    """Identifica carreras presentes en el título o descripción"""
    texto_busqueda = limpiar_texto(titulo + " " + descripcion)
    es_practica = any(keyword in texto_busqueda for keyword in PALABRAS_CLAVE_PRACTICA)
    if not es_practica: return []
    carreras_encontradas = set()
    for carrera_oficial, aliases in carreras_alias_dict.items():
        for alias in aliases:
            if alias in texto_busqueda:
                carreras_encontradas.add(carrera_oficial)
                break
    return sorted(list(carreras_encontradas))

def obtener_html(url, headers):
    """Obtiene el HTML de la página"""
    try:
        session = requests.Session()
        session.headers.update(headers)
        response = session.get(url, timeout=15)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"❌ Error obteniendo HTML: {e}")
        return None

def extraer_ofertas(html):
    """Extrae las ofertas del HTML"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        job_listings = soup.find_all('div', class_='base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card')
        return job_listings
    except:
        return []

def extraer_descripcion_completa(job_soup):
    """Extrae la descripción completa y la limpia"""
    selectores = ['.jobs-description__content', '#job-details', '.jobs-box__html-content', '.description__text--rich']
    for selector in selectores:
        elemento = job_soup.select_one(selector)
        if elemento:
            descripcion_raw = elemento.get_text(separator=' ', strip=True)
            return limpiar_descripcion(descripcion_raw)
    return "No se pudo extraer la descripción."

def extraer_area_de_descripcion(descripcion):
    """Intenta extraer el área de trabajo de la descripción"""
    areas_comunes = [
        'tecnología', 'marketing', 'ventas', 'recursos humanos', 'finanzas',
        'operaciones', 'logística', 'administración', 'ingeniería', 'desarrollo',
        'sistemas', 'informática', 'contabilidad', 'legal', 'comunicaciones'
    ]
    descripcion_lower = descripcion.lower()
    for area in areas_comunes:
        if area in descripcion_lower:
            return area.title()
    return "No especificada"

def extraer_modalidad_de_descripcion(descripcion):
    """Intenta extraer la modalidad de trabajo de la descripción"""
    modalidades = {
        'remoto': ['remoto', 'remote', 'teletrabajo', 'home office'],
        'presencial': ['presencial', 'oficina', 'in-site'],
        'híbrido': ['híbrido', 'hybrid', 'mixto']
    }
    descripcion_lower = descripcion.lower()
    for modalidad, keywords in modalidades.items():
        if any(keyword in descripcion_lower for keyword in keywords):
            return modalidad.title()
    return "No especificada"

def extraer_detalles_oferta(job_listing, carreras_alias_dict, session):
    """Extrae los detalles específicos para WordPress"""
    try:
        # Extracción de campos
        title_element = job_listing.find('h3', class_='base-search-card__title')
        titulo = title_element.text.strip() if title_element else ''
        company_element = job_listing.find('h4', class_='base-search-card__subtitle')
        empresa = company_element.text.strip() if company_element else ''
        location_element = job_listing.find('span', class_='job-search-card__location')
        ubicacion = location_element.text.strip() if location_element else ''
        date_element = job_listing.find('time', class_='job-search-card__listdate')
        fecha_publicacion = date_element['datetime'] if date_element else ''
        link_element = job_listing.find('a', class_='base-card__full-link')
        link = link_element['href'] if link_element else ''
        imagen_empresa = ''
        img_element = job_listing.find('img', class_='artdeco-entity-image')
        if not img_element: img_element = job_listing.find('img', class_='base-card__image')
        if img_element: imagen_empresa = img_element.get('data-delayed-url') or img_element.get('src', '')

        # Extracción de descripción
        descripcion = ''
        if link:
            try:
                job_response = session.get(link, timeout=15)
                if job_response.status_code == 200:
                    job_soup = BeautifulSoup(job_response.content, 'html.parser')
                    descripcion = extraer_descripcion_completa(job_soup)
                time.sleep(random.uniform(2, 4))
            except:
                descripcion = "No se pudo extraer la descripción."

        carreras_relacionadas = identificar_carreras_por_alias(titulo, descripcion, carreras_alias_dict)

        if carreras_relacionadas:
            area = extraer_area_de_descripcion(descripcion)
            modalidad = extraer_modalidad_de_descripcion(descripcion)
            fecha_actual = datetime.now()
            inicio_postulacion = fecha_actual.strftime('%d/%m/%Y')

            return {
                'fecha_publicacion': fecha_publicacion,
                'titulo': titulo,
                'empresa': empresa,
                'reseña_empresa': "Empresa con presencia en el mercado que ofrece oportunidades de crecimiento profesional.",
                'carreras_relacionadas': carreras_relacionadas,
                'descripcion': descripcion,
                'area': area,
                'beneficios': "Experiencia profesional, desarrollo de habilidades, networking, posible contratación posterior",
                'modalidad': modalidad,
                'ubicacion': ubicacion,
                'inicio_postulacion': inicio_postulacion,
                'cierre_postulacion': "Se desconoce fecha cierre",
                'correo_electronico': "Consultar en la oferta original",
                'link': link,
                'observacion': "Postulación a través de LinkedIn. Revisar requisitos específicos en la oferta original.",
                'imagen_empresa': imagen_empresa
            }
        return None
    except Exception as e:
        print(f"❌ Error extrayendo detalles de oferta: {e}")
        return None

def obtener_token_jwt():
    """Obtiene token JWT para autenticación"""
    credentials = {
        "username": JWT_CONFIG['username'],
        "password": JWT_CONFIG['password']
    }
    try:
        response = requests.post(JWT_CONFIG['login_url'], json=credentials, timeout=10)
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Token JWT obtenido exitosamente")
            return token_data['token']
        else:
            print(f"❌ Error obteniendo token: {response.status_code}")
            return None
    except:
        print(f"❌ Error de conexión obteniendo token")
        return None

def validar_token_jwt(token):
    """Valida si el token JWT sigue siendo válido"""
    headers = { 'Authorization': f'Bearer {token}' }
    try:
        response = requests.post(JWT_CONFIG['validate_url'], headers=headers, timeout=10)
        return response.status_code == 200
    except:
        return False

def subir_imagen_como_featured_media(token, imagen_url, nombre_empresa):
    """Sube una imagen y la devuelve como ID para featured_media"""
    try:
        if not imagen_url: return 0
        print(f"📤 Subiendo imagen para {nombre_empresa}...")
        img_response = requests.get(imagen_url, timeout=15)
        if img_response.status_code != 200:
            print(f"❌ No se pudo descargar la imagen")
            return 0
        files = {
            'file': (f"{nombre_empresa.replace(' ', '_')}.jpg", img_response.content, 'image/jpeg')
        }
        headers = { 'Authorization': f'Bearer {token}' }
        response = requests.post(
            JWT_CONFIG['media_url'],
            files=files,
            headers=headers,
            timeout=30
        )
        if response.status_code == 201:
            media_info = response.json()
            print(f"✅ Imagen subida exitosamente (ID: {media_info['id']})")
            return media_info['id']
        else:
            print(f"⚠️ No se pudo subir imagen: {response.status_code}")
            return 0
    except Exception as e:
        print(f"⚠️ Error subiendo imagen: {e}")
        return 0

def publicar_practica_wordpress_jwt(token, oferta_data):
    """Publica práctica con imagen destacada"""
    try:
        featured_media_id = 0
        if oferta_data.get('imagen_empresa'):
            featured_media_id = subir_imagen_como_featured_media(token, oferta_data['imagen_empresa'], oferta_data['empresa'])

        carreras_texto = ', '.join(oferta_data['carreras_relacionadas'])
        excerpt_personalizado = f"Práctica profesional en {oferta_data['empresa']} - {oferta_data['ubicacion']}\nCarrera(s): {carreras_texto}"

        contenido_html = f"""
        <table class="table table-striped table-responsive">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Detalle</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>Empresa</td><td>{oferta_data['empresa']}</td></tr>
                <tr><td>Reseña empresa</td><td>{oferta_data['reseña_empresa']}</td></tr>
                <tr><td>Carrera(s)</td><td>{', '.join(oferta_data['carreras_relacionadas'])}</td></tr>
                <tr><td>Descripción/Funciones</td><td>{oferta_data['descripcion']}</td></tr>
                <tr><td>Área</td><td>{oferta_data['area']}</td></tr>
                <tr><td>Beneficios</td><td>{oferta_data['beneficios']}</td></tr>
                <tr><td>Modalidad</td><td>{oferta_data['modalidad']}</td></tr>
                <tr><td>Ubicación</td><td>{oferta_data['ubicacion']}</td></tr>
                <tr><td>Inicio postulación</td><td>{oferta_data['inicio_postulacion']}</td></tr>
                <tr><td>Cierre postulación</td><td>{oferta_data['cierre_postulacion']}</td></tr>
                <tr><td>Correo electrónico</td><td>{oferta_data['correo_electronico']}</td></tr>
                <tr><td>Link Postulación</td><td><a href="{oferta_data['link']}" target="_blank" rel="noopener">Postular aquí</a></td></tr>
                <tr><td>Observación de la postulación</td><td>{oferta_data['observacion']}</td></tr>
            </tbody>
        </table>
        """
        post_data = {
            "title": oferta_data['titulo'],
            "content": contenido_html,
            "status": "publish",
            "excerpt": excerpt_personalizado,
            "featured_media": featured_media_id,
            "categories": [1]
        }
        headers = { 'Content-Type': 'application/json', 'Authorization': f'Bearer {token}' }
        response = requests.post(JWT_CONFIG['posts_url'], json=post_data, headers=headers, timeout=30)
        if response.status_code == 201:
            post_info = response.json()
            print(f"✅ Publicado: {oferta_data['titulo']} (ID: {post_info['id']})")
            return post_info['id']
        else:
            print(f"❌ Error JWT: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error al publicar: {e}")
        return None

def verificar_duplicado_publicado(nueva_oferta, ofertas_publicadas):
    """Verifica si una oferta ya fue publicada anteriormente usando hash"""
    if not nueva_oferta or not ofertas_publicadas: return False
    hash_nueva_oferta = generar_hash_oferta(nueva_oferta)
    # print(f"🔍 DEBUG Verificando duplicado para hash: {hash_nueva_oferta}") # Desactivado para evitar logs masivos
    for i, oferta_pub in enumerate(ofertas_publicadas):
        hash_publicado = oferta_pub.get('hash') or generar_hash_oferta(oferta_pub)
        if hash_publicado == hash_nueva_oferta:
            print(f"🔄 DEBUG ¡DUPLICADO ENCONTRADO! Hash coincide: {hash_nueva_oferta}. Título: {oferta_pub.get('titulo', 'N/A')}")
            return True
    # print(f"✅ DEBUG No se encontró duplicado para: {hash_nueva_oferta}") # Desactivado para evitar logs masivos
    return False

def verificar_duplicado_en_jobs(nueva_oferta, jobs_existentes):
    """Verifica si una oferta ya existe en la lista de trabajos actual usando hash"""
    if not nueva_oferta or not jobs_existentes: return False
    hash_nueva_oferta = generar_hash_oferta(nueva_oferta)
    # print(f"🔍 DEBUG Verificando duplicado en sesión para hash: {hash_nueva_oferta}") # Desactivado para evitar logs masivos
    for i, job in enumerate(jobs_existentes):
        hash_existente = generar_hash_oferta(job)
        if hash_existente == hash_nueva_oferta:
            print(f"🔄 DEBUG ¡DUPLICADO EN SESIÓN! Hash coincide: {hash_nueva_oferta}")
            return True
    # print(f"✅ DEBUG No se encontró duplicado en sesión para: {hash_nueva_oferta}") # Desactivado para evitar logs masivos
    return False

# --------------------------------------------------------------------------
# --- FUNCIÓN PRINCIPAL ADAPTADA PARA CLOUD FUNCTIONS (ENTRY POINT) ---
# --------------------------------------------------------------------------

def main(request=None): # <--- CAMBIO CLAVE: ACEPTAR EL ARGUMENTO DE CLOUD FUNCTIONS
    """
    Función principal llamada por Cloud Scheduler o una solicitud HTTP.
    Realiza scraping, filtra, y publica en WordPress, guardando el historial en Cloud Storage.
    """
    print("🚀 Iniciando proceso automatizado LinkedIn → WordPress en Cloud Functions...")

    # Obtener token JWT
    token = obtener_token_jwt()
    if not token:
        print("❌ Proceso detenido: No se pudo obtener token JWT.")
        return "Error: No se pudo obtener token JWT", 500

    # Cargar ofertas ya publicadas desde Cloud Storage
    ofertas_publicadas = cargar_ofertas_publicadas()
    print(f"📚 Cargadas {len(ofertas_publicadas)} ofertas previamente publicadas desde Cloud Storage")

    # Scraping de LinkedIn
    html = obtener_html(url, headers)
    if not html:
        print("❌ Proceso detenido: No se pudo obtener el HTML de LinkedIn.")
        return "Error: No se pudo obtener el HTML de LinkedIn", 500

    job_listings = extraer_ofertas(html)
    if not job_listings:
        print("❌ No se encontraron ofertas de trabajo.")
        return "Éxito: No se encontraron ofertas nuevas", 200

    print(f"🔍 Encontradas {len(job_listings)} ofertas en LinkedIn")

    jobs_wordpress = []
    jobs_procesados_session = []
    session = requests.Session()
    session.headers.update(headers)

    # Extraer detalles de cada oferta y filtrar duplicados en la sesión
    for i, job_listing in enumerate(job_listings, 1):
        # print(f"\n{'='*60}")
        # print(f"Procesando oferta {i}/{len(job_listings)}") # Desactivado para reducir logs en CF

        job = extraer_detalles_oferta(job_listing, CARRERAS_ALIAS, session)
        if job:
            if not verificar_duplicado_en_jobs(job, jobs_procesados_session):
                jobs_wordpress.append(job)
                jobs_procesados_session.append(job)
                # print(f"  ✅ Oferta agregada: {job['titulo']}") # Desactivado
        
    if not jobs_wordpress:
        print("❌ No se encontraron ofertas relevantes para publicar.")
        return "Éxito: No se encontraron ofertas relevantes para publicar", 200

    print(f"\n📋 {len(jobs_wordpress)} ofertas únicas encontradas para el proceso de publicación")

    # Publicar en WordPress usando JWT
    publicadas = 0
    duplicadas = 0
    errores = 0
    nuevas_ofertas_publicadas = []

    for oferta in jobs_wordpress:
        # Verificar duplicados con ofertas previamente publicadas usando hash
        if verificar_duplicado_publicado(oferta, ofertas_publicadas):
            duplicadas += 1
            # print(f"  🔄 Ya publicada anteriormente: {oferta['titulo']}") # Desactivado
            continue

        # Validar y renovar token si es necesario
        if not validar_token_jwt(token):
            print("⚠️ Token expirado, obteniendo nuevo token...")
            token = obtener_token_jwt()
            if not token:
                print("❌ Proceso detenido: No se pudo renovar el token.")
                break

        # Publicar
        print(f"📤 Publicando: {oferta['titulo']}")
        post_id = publicar_practica_wordpress_jwt(token, oferta)

        if post_id:
            hash_oferta = generar_hash_oferta(oferta)
            nuevas_ofertas_publicadas.append({
                'hash': hash_oferta,
                'titulo': oferta['titulo'],
                'empresa': oferta['empresa'],
                'fecha_publicacion': oferta['fecha_publicacion'],
                'fecha_procesamiento': datetime.now().isoformat(),
                'post_id': post_id
            })
            publicadas += 1
        else:
            errores += 1
            print(f"  ❌ Error publicando: {oferta['titulo']}")

        time.sleep(random.uniform(2, 4)) # Pausa entre publicaciones

    # Actualizar y guardar lista completa en Cloud Storage
    ofertas_publicadas.extend(nuevas_ofertas_publicadas)
    guardar_ofertas_publicadas(ofertas_publicadas)

    # Resumen final
    resumen = (
        f"📊 RESUMEN FINAL:\n"
        f"--------------------------------------------------\n"
        f" 🆕 Publicadas: {publicadas}\n"
        f" 🔄 Duplicadas (Historial/Sesión): {duplicadas}\n"
        f" ❌ Errores: {errores}\n"
        f" 💾 Total en Historial: {len(ofertas_publicadas)}\n"
        f"--------------------------------------------------"
    )
    print(resumen)
    return resumen, 200

# El bloque if __name__ == "__main__": se ELIMINA para el despliegue en Cloud Functions.
# La función 'main' es llamada directamente por el servicio de GCP.