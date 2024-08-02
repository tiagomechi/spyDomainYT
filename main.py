from video_scraper.video_info import get_videos_data, get_video_info
from video_scraper.file_operations import save_to_file
import traceback
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

def main():
    dominio = input("Digite a URL do domínio: ")
    exibir_opcao = input("Digite a opção da sua preferência de exibição:\n[1] Print no console.\n[2] Prefiro gerar um arquivo.\n")

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
            while attempts < 5 and not success:
                try:
                    video_metadata = get_video_info(video_data, driver)
                    if video_metadata:
                        video_metadata_list.append(video_metadata)
                        success = True
                except Exception as e:
                    attempts += 1
                    print(f"Erro ao capturar dados do vídeo {video_data['youtube_url']}: Tentativa {attempts}/5")
                    if attempts == 5:
                        print(f"Falha ao capturar dados do vídeo {video_data['youtube_url']} após 5 tentativas.")
        
        if exibir_opcao == '1':
            print(video_metadata_list)
        elif exibir_opcao == '2':
            save_to_file(video_metadata_list, nome_arquivo)
        else:
            print("Opção inválida.")
    except Exception as e:
        print(traceback.format_exc())
        print(e)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
