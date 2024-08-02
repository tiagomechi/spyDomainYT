from video_scraper.video_info import get_videos_data, get_video_info
from video_scraper.file_operations import save_to_file
from video_scraper.logger import logger
from video_scraper.utils import get_valid_option
from video_scraper.config import MAX_ATTEMPTS
import traceback
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.firefox import GeckoDriverManager

def main():
    dominio = input("Digite a URL do domínio: ")
    exibir_opcao = get_valid_option()

    nome_arquivo = None
    if exibir_opcao == '2':
        nome_arquivo = input("Digite o nome do arquivo a ser gerado: ")

    url = f'https://adstransparency.google.com/?origin=ata&region=BR&domain={dominio}&platform=YOUTUBE&format=VIDEO'
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))

    try:
        videos_data = get_videos_data(driver, url)
        video_metadata_list = []

        for video_data in videos_data:
            attempts = 0
            success = False
            while attempts < MAX_ATTEMPTS and not success:
                try:
                    video_metadata = get_video_info(video_data, driver)
                    if video_metadata:
                        video_metadata_list.append(video_metadata)
                        success = True
                except (TimeoutException, NoSuchElementException) as e:
                    attempts += 1
                    logger.error(f"Erro ao capturar dados do vídeo {video_data['youtube_url']}: Tentativa {attempts}/{MAX_ATTEMPTS}")
                    if attempts == MAX_ATTEMPTS:
                        logger.error(f"Falha ao capturar dados do vídeo {video_data['youtube_url']} após {MAX_ATTEMPTS} tentativas.")
        
        if exibir_opcao == '1':
            print(video_metadata_list)
        elif exibir_opcao == '2':
            save_to_file(video_metadata_list, nome_arquivo)
        else:
            print("Opção inválida.")
    except Exception as e:
        logger.critical(traceback.format_exc())
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
