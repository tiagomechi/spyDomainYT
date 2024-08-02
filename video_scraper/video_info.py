import re
from numpy import RAISE
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .utils import parse_date
import time

def get_video_title(driver):
    """Obtém o título do vídeo."""
    title_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="title"]/*/yt-formatted-string'))
    )
    return title_element.text

def get_channel_info(driver):
    """Obtém as informações do canal."""
    channel_container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'channel-name'))
    )
    a_element = channel_container.find_element(By.CSS_SELECTOR, 'a')
    channel_url = a_element.get_attribute('href')
    channel_name = a_element.text
    return channel_name, channel_url

def get_video_duration(driver):
    """Obtém a duração do vídeo."""
    duration_element = driver.find_element(By.CSS_SELECTOR, 'span.ytp-time-duration')
    return duration_element.text

def get_views_and_publish_date(driver):
    """Obtém o número de visualizações e a data de publicação do vídeo."""
    description_container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'description-inner'))
    )
    tooltip_element = description_container.find_element(By.ID, 'tooltip')
    driver.execute_script("arguments[0].classList.remove('hidden');", tooltip_element)
    WebDriverWait(driver, 10).until(EC.visibility_of(tooltip_element))
    views_and_date = tooltip_element.text
    parts = views_and_date.split(' • ')

    views = parts[0].split(' ')[0].replace('.', '')
    date_part = parts[1]
    publish_date = parse_date(date_part)

    return views, publish_date

def get_likes(driver):
    """Obtém o número de likes do vídeo."""
    scripts = driver.find_elements(By.TAG_NAME, 'script')
    yt_initial_data = None
    for script in scripts:
        if 'var ytInitialData' in script.get_attribute('innerHTML'):
            yt_initial_data = script.get_attribute('innerHTML')
            break

    if yt_initial_data:
        match = re.search(r'\"accessibilityText\":\"Marque este vídeo como \\\"Gostei\\\" com mais ([\d.]+) pessoas\"', yt_initial_data)
        if match:
            return match.group(1).replace('.', '')  # Remover pontos e capturar o número
    else:
        likes_element = driver.find_element(By.CSS_SELECTOR, 'segmented-like-dislike-button-view-model .yt-spec-button-shape-next__button-text-content')
        return likes_element.text

def get_thumbnail_url(driver):
    """Obtém a URL da thumbnail do vídeo."""
    thumbnail_element = driver.find_element(By.CSS_SELECTOR, 'link[rel="image_src"]')
    return thumbnail_element.get_attribute('href')

def is_shorts_video(driver, video_id):
    """Verifica se o vídeo é um Shorts e retorna a URL do Shorts se for, caso contrário retorna uma string vazia."""
    shorts_url = f'https://www.youtube.com/shorts/{video_id}'
    driver.get(shorts_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    if driver.current_url == shorts_url:
        return shorts_url
    else:
        return ''


def get_transcript(driver):
    """Obtém a transcrição do vídeo."""
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'description-inline-expander'))
    ).click()
    
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

    return transcript_text.strip()

def get_video_info(video_data, driver):
    """Captura todas as informações do vídeo."""
    url = video_data['youtube_url']
    img_src = video_data['img_src']
    
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(url)
    time.sleep(5)  # Ajuste o tempo de espera conforme necessário

    try:
        title = get_video_title(driver)
        channel_name, channel_url = get_channel_info(driver)
        duration = get_video_duration(driver)
        views, publish_date = get_views_and_publish_date(driver)
        likes = get_likes(driver)
        thumbnail_url = get_thumbnail_url(driver)
        current_video_url = driver.current_url
        video_id = current_video_url.split('v=')[1]
        transcript = get_transcript(driver)
        shorts = is_shorts_video(driver, video_id)

        video_info = {
            'title': title,
            'channel_name': channel_name,
            'channel_url': channel_url,
            'duration': duration,
            'views': views,
            'likes': likes,
            'thumbnail_url': thumbnail_url,
            'shorts': shorts,
            'transcript': transcript,
            'publish_date': publish_date,
            'video_url': url,
            'img_src': img_src
        }
        return video_info
    except Exception as e:
        print(f"Erro ao capturar informações do vídeo {url}: {e}")
        raise TypeError(e)
    finally:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

def get_videos_data(driver, url):
    """Obtém os dados dos vídeos da página especificada."""
    driver.get(url)
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
            img_element = WebDriverWait(element, 10).until(EC.element_to_be_clickable((By.TAG_NAME, 'img')))
            img_src = img_element.get_attribute('src')
            video_id = img_src.split('/')[4]
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            videos_data.append({'img_src': img_src, 'youtube_url': youtube_url})
        except Exception as e:
            print(f"Erro: {e}")
    
    return list({v['youtube_url']: v for v in videos_data}.values())
