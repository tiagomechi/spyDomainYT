from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
import time, traceback

def get_video_info(video_data, driver):
    url = video_data['youtube_url']
    img_src = video_data['img_src']
    
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(url)
    time.sleep(5)  # Ajuste o tempo de espera conforme necessário

    # Capturar as informações do vídeo
    try:
        title = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="title"]/*/yt-formatted-string'))).text

        channel_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'channel-name'))
        )
        a_element = channel_container.find_element(By.CSS_SELECTOR, 'a')
        channel_url = a_element.get_attribute('href')
        channel_name = a_element.text
        
        duration = driver.find_element(By.CSS_SELECTOR, 'span.ytp-time-duration').text
        description_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'description-inner'))
        )
        tooltip_element = description_container.find_element(By.ID, 'tooltip')
        driver.execute_script("arguments[0].classList.remove('hidden');", tooltip_element)
        WebDriverWait(driver, 10).until(
            EC.visibility_of(tooltip_element)
        )
        views_and_date = tooltip_element.text
        parts = views_and_date.split(' • ')

        # Extrair e processar o número de visualizações
        views_part = parts[0]
        views = views_part.split(' ')[0].replace('.', '')

        # Extrair e processar a data
        date_part = parts[1]
        # Converter a data para o formato dia/mês/ano
        date_obj = datetime.strptime(date_part, '%d de %b. de %Y')
        publish_date = date_obj.strftime('%d/%m/%Y')
        
        scripts = driver.find_elements(By.TAG_NAME, 'script')
        yt_initial_data = None
        for script in scripts:
            if 'var ytInitialData' in script.get_attribute('innerHTML'):
                yt_initial_data = script.get_attribute('innerHTML')
                break
        likes = None
        if yt_initial_data:
            # Usar regex para encontrar o número de likes no 'accessibilityText'
            match = re.search(r'\"accessibilityText\":\"Marque este vídeo como \\\"Gostei\\\" com mais ([\d.]+) pessoas\"', yt_initial_data)
            if match:
                likes = match.group(1).replace('.', '')  # Remover pontos e capturar o número
        else:
            likes = driver.find_element(By.CSS_SELECTOR, 'segmented-like-dislike-button-view-model .yt-spec-button-shape-next__button-text-content').text
            
        thumbnail_url = driver.find_element(By.CSS_SELECTOR, 'link[rel="image_src"]').get_attribute('href')
        
        current_video_url = driver.current_url
        video_id = current_video_url.split('v=')[1]
        shorts_url = f'https://www.youtube.com/shorts/{video_id}'
        driver.get(shorts_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        current_url = driver.current_url
        if current_url == shorts_url:
            shorts = shorts_url
        else:
            shorts = ''

        description_expander = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'description-inline-expander'))
        )
        description_expander.click()
        
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@aria-label="Mostrar transcrição"]'))
        ).click()
        
        transcript_segments = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'ytd-transcript-segment-renderer'))
        )
        transcript_text = ''
        for segment in transcript_segments:
            lines = segment.text.split('\n')
            if len(lines) > 1:
                transcript_text += lines[1] + " "

        video_info = {
            'title': title,
            'channel_name': channel_name,
            'channel_url': channel_url,
            'duration': duration,
            'views': views,
            'likes': likes,
            'thumbnail_url': thumbnail_url,
            'shorts': shorts,
            'transcript': transcript_text,
            'publish_date': publish_date,
            'video_url': url,
            'img_src': img_src
        }
        return video_info
    except Exception as e:
        print(f"Erro ao capturar informações do vídeo {url}: {e}")
        return None
    finally:
        # Fechar a aba atual e voltar para a aba original
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

# Defina o domínio desejado
dominio = 'eduqueseufilhote.com.br'  # Substitua pelo domínio desejado

# Crie a URL usando o domínio fornecido
url = f'https://adstransparency.google.com/?origin=ata&region=BR&domain={dominio}&platform=YOUTUBE&format=VIDEO'

# Configure o driver do Firefox
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))

try:
    # Acesse a URL
    driver.get(url)

    # Aguarde o carregamento da página (ajuste o tempo conforme necessário)
    time.sleep(5)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@aria-label="Filtro de formato do anúncio"]'))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@aria-label="Formato de Vídeo"]'))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.grid-expansion-button'))).click()
    elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'creative-preview'))
    )
    
    videos_data = []

    for element in elements:
        try:
            # Encontrar o elemento 'img' dentro do 'creative-preview'
            img_element = WebDriverWait(element, 10).until(EC.element_to_be_clickable((By.TAG_NAME, 'img')))
            # Capturar o valor do atributo 'src'
            img_src = img_element.get_attribute('src')
            # Dividir a URL usando '/' como delimitador e capturar a parte desejada
            video_id = img_src.split('/')[4]
            # Construir a URL completa do YouTube
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            # Adicionar os dados à lista
            videos_data.append({'img_src': img_src, 'youtube_url': youtube_url})
        except Exception as e:
            # Tratar caso o elemento 'img' não seja encontrado dentro de 'creative-preview'
            print(f"Erro: {e}")
    
    # Remover duplicatas sem retornar uma lista
    videos_data = list({v['youtube_url']: v for v in videos_data}.values())

    video_metadata_list = [] 
    # Iterar sobre os dados dos vídeos
    for video_data in videos_data:
        video_metadata = get_video_info(video_data, driver)
        if video_metadata:  # Adicionar apenas se não for None
            video_metadata_list.append(video_metadata)
    print(video_metadata_list)
except Exception as e:
    print(traceback.format_exc())
    print(e)
finally:
    # Feche o navegador
    driver.quit()






#copiar informações de depuração
#pesquisar por addebug_videoId
#depois inspecionar pagina de video no adstransparency
#https://adstransparency.google.com/advertiser/AR16046923194329726977/creative/CR05689536476862218241?origin=ata&region=BR&platform=YOUTUBE
#tentar localisar o id do video para detectar um padrão...
#Padrão detectado
#<img id="fletch-render-9429781484028111962_preview_c703921757516_v3_480_360_" src="https://i.ytimg.com/vi/cryHqpB2JFA/hqdefault.jpg" width="480" height="360">
#cryHqpB2JFA é o ID do video
#https://www.youtube.com/watch?v=cryHqpB2JFA
# proximos passos:
# capturar as seguintes infos:
# - Título Vídeo
# - Título do Canal
# - Duração do Vídeo
# - Quantidade de Views
# - Quantidade de Likes
# - Link da thumbnail
# - Indicação se é um YouTube Shorts ou não
# - Transcrição do vídeo
# - Data de publicação
# - Link do Vídeo