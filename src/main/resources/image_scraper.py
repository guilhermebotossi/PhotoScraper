try:
    import requests
    import urllib.request
    from bs4 import BeautifulSoup 
    import json
    import re
    import time
    import os
    from datetime import datetime
    import sys
    from random import randrange
    import hashlib
    from urllib.parse import urljoin, urlparse
    import cv2
except:
    print("Não foram instaladas todas as dependencias necessarias ao script. Favor executar o \"setup.bat\" novamente.")
    input("Press Enter to continue...")
    sys.exit()

booking_pattern = "highres_url: '(https:\\/\\/.*\\.jpg)'"
booking_regex = re.compile(booking_pattern)
tripadvisor_pattern = "https:\\/\\/media-cdn\\.tripadvisor\\.com\\/media\\/photo-\\w/[\\w|\\/|-]+.jpg"
tripadvisor_regex = re.compile(tripadvisor_pattern)
target_width = 2880
target_height = 1920

def read_all_lines_from_file(basePath):
    path = os.path.join(basePath, "url.txt")
    if not os.path.exists(path):
        print("O arquivo \"url.txt\", não esta definido na mesma pasta do script")
        sys.exit(0)
    x = open(path).read().splitlines()
    print("Foram identificadas " + str(len(x)) + " url's no arquivo de configuração.\n")
    return x

def retrieve_image_list_from_url(url, hotel_name):
    request = requests.get(url) 
    image_list=[]
    if("booking" in url):
        image_list = retrieve_image_list_from_booking(request)
    if("tripadvisor" in url):
        image_list = retrieve_image_list_from_tripadvisor(request)        
    print("Foram encontradas " + str(len(image_list))  + " imagens do hotel " + hotel_name)
    return image_list

def retrieve_image_list_from_booking(request):
    soup = BeautifulSoup(request.content, 'html5lib') 
    scripts = soup.find_all('script')
    content = None
    for script in scripts:
        tag_text = script.text
        if(tag_text.find('hotelPhotos') != -1):
            content = tag_text 
            break
    return booking_regex.findall(content)

def retrieve_image_list_from_tripadvisor(request) :
    soup = BeautifulSoup(request.content, 'html5lib') 
    scripts = soup.find_all('script')
    content = None
    for script in scripts:
        tag_text = script.text
        if(tag_text.find('albums') != -1):
            content = tag_text
            break
    return list(dict.fromkeys(tripadvisor_regex.findall(content)))


def create_destination_folder_if_does_not_exist(basePath, hotel_name):
    folder_name = hotel_name + "_" + str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    folder_path = os.path.join(basePath, folder_name)
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    return folder_path

def download_images_to_folder(image_list, folder_path):
    num = 1
    for image in image_list:
        image_name = os.path.basename(image)
        print("\t* Fazendo download da imagem " + str(num) + " de " + str(len(image_list)) )
        imagePath = os.path.join(folder_path, image_name)
        urllib.request.urlretrieve(image,imagePath)
        resizeImage(imagePath, folder_path)
        num+=1

def execute_thread_sleep_if_necessary(isNeeded):
    if(isNeeded):
        seconds_wait_between_requests = randrange(30)
        print("\nAguardando " + str(seconds_wait_between_requests) + " segundos para nova busca\n")
        time.sleep(seconds_wait_between_requests)

def add_url_to_history(basePath, url, status):
    folder = os.path.join(basePath, "history")
    if not os.path.exists(folder):
       os.mkdir(folder)
    path = os.path.join(folder, "history_"+str(datetime.now().strftime('%Y-%m-%d'))+".txt")
    line = url + "_" + status +"_" + str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    open(path, "a").write("\n" + line  + "_" + generate_hash(line))

def generate_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()

def printSummary(total, done, errors, noImages, totalOfImages):
    print("\n\n====================Resumo====================")
    print("Total de Url's: " + str(total))
    print("Download's finalizados com sucesso: " + str(done))
    print("Numero de imagens baixadas: " + str(totalOfImages))
    print("Download's com erro: " + str(errors))
    print("Url's sem imagens encontradas: " + str(noImages))
    print("==============================================\n\n")

def resizeImage(image, hotelFolderPath) :
    resizedFolder = os.path.join(hotelFolderPath, "resized")
    if not os.path.exists(resizedFolder):
        os.mkdir(resizedFolder)

    img = cv2.imread(image, cv2.IMREAD_UNCHANGED)
    imageName = os.path.basename(image)
    dim = (target_width, target_height)
    print("Executando resize da imagem " + str(imageName) + " para as dimensões Width : " + str(target_width) + " e Height : " + str(target_height))
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    imagePath = os.path.join(resizedFolder, "resized_" + imageName)
    cv2.imwrite(imagePath, resized)


def init():
    basePath = sys.path[0]
    done = 0
    errors = 0
    noImages = 0
    totalOfImages = 0

    urls = read_all_lines_from_file(basePath)
    number_of_urls = len(urls)
    current = 1
    for url in urls :
        url = urljoin(url, urlparse(url).path)
        hotel_name = os.path.basename(url).replace(".html", "")
        add_url_to_history(basePath, url, "STARTED")
        print("[" + str(current) + " de " + str(number_of_urls) + "] Iniciando busca das imagens do hotel : " + hotel_name)
        try:
            image_list = retrieve_image_list_from_url(url, hotel_name)
            
            if(len(image_list) == 0):
                print("Não foram encontradas imagens para o hotel " + hotel_name)
                add_url_to_history(basePath, url, "NO_IMAGES_FOUND")
                noImages += 1
            else:
                folder_path = create_destination_folder_if_does_not_exist(basePath, hotel_name)
                download_images_to_folder(image_list, folder_path)
                add_url_to_history(basePath, url, "DONE")
                totalOfImages += len(image_list)
                done += 1
        except: 
            add_url_to_history(basePath, url, "ERROR")
            print("Erro ao baixar imagens")
            errors += 1
        execute_thread_sleep_if_necessary(current != number_of_urls)
        current += 1
    printSummary(number_of_urls, done, errors, noImages, totalOfImages)
    
try:
    init()
finally:
    input("Press Enter to continue...")    


