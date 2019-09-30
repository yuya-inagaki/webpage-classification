# coding: utf-8

#--------------------------------------------------------------
#
#   Python3系で作成
#   idとclass名の取得・csvへの書き込み、該当idとclassの座標取得
#
#--------------------------------------------------------------

#use csv
import csv
import pandas as pd
#get screenshot
import os
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary #firefox使用のため
#read html
from bs4 import BeautifulSoup
import re
#OpenCV
import cv2

### 定数
CSV_INPUT_PATH = './input/webList-input.csv'
SCREEN_W = 1280
SCREEN_H = 900
SCREEN_H_REAL = 900
THRESHOLD_PICTORIAL = 0.7
THRESHOLD_TEXT = 0.3

# CSVの行数をカウントする関数
def count_row_csv(file_path):
    return sum(1 for line in open(file_path)) - 1

# htmlを取得する関数
def get_html(driver):
    soup = BeautifulSoup( driver.page_source, "html.parser")
    html = soup.prettify() #html成形
    f = open('./working/index.html', 'w') # 書き込みモードで開く
    f.write(html) # 引数の文字列をファイルに書き込む
    f.close() # ファイルを閉じる

# 画像の割合を計算する関数
def calc_pictorial_ratio(driver, screenshot):
    print("Getting position and size of //img")
    image_area = 0 # 画像存在領域の合計
    images = driver.find_elements_by_xpath('//img')
    print(images)
    for image in images:
        try: # 正常処理
            if str(image.is_displayed()) == "True": #表示されている時のみリストに挿入
                start_x = int(image.location['x'])
                start_y = int(image.location['y'])
                size_w = int(image.size['width'])
                size_h = int(image.size['height'])
                end_x = start_x + size_w
                end_y = start_y + size_h

                place_check = check_in_screen(start_x, start_y, end_x, end_y)
                if(place_check != 0):
                    start_x = place_check[0]
                    start_y = place_check[1]
                    end_x = place_check[2]
                    end_y = place_check[3]

                    print(str(start_x) + ' / ' + str(start_y) + ' / ' + str(size_w) + ' / ' + str(size_h))

                    print_rectangle(screenshot, start_x, start_y, end_x, end_y)
                    image_area += (end_x-start_x)*(end_y-start_y)

        except: # エラー処理
            print("Error(Can't find elements[img])")

    image_ratio = (image_area / (SCREEN_W * SCREEN_H_REAL))*100
    print(image_ratio)
    if image_ratio > 100:
        return 100
    else:
        return image_ratio

# 一つの画面内に入っているかどうかを判断する関数
def check_in_screen(start_x, start_y, end_x, end_y):
    if(0<start_x<SCREEN_W and 0<start_y<SCREEN_H_REAL and 0<end_x<SCREEN_W and 0<end_y<SCREEN_H_REAL):
        return (start_x, start_y, end_x, end_y)
    elif(SCREEN_W < start_x or SCREEN_H_REAL < start_y):
        return 0
    elif(SCREEN_W < end_x and SCREEN_H_REAL < end_y):
        return (start_x, start_y, SCREEN_W, SCREEN_H_REAL)
    elif(start_x < 0 and start_y < 0):
        return (0, 0, end_x, end_y)
    elif(start_x < 0):
        return (0, start_y, end_x, end_y)
    elif(start_y < 0):
        return (start_x, 0, end_x, end_y)  
    elif(SCREEN_W < end_x):
        return (start_x, start_y, SCREEN_W, end_y)
    elif(SCREEN_H_REAL < end_y):
        return (start_x, start_y, end_x, SCREEN_H_REAL)
    else:
        return 0


# 画像へ描写を行う関数
def print_rectangle(img, start_x, start_y, end_x, end_y):
    cv2.rectangle(img, (start_x, start_y) , (end_x, end_y), (0, 0, 255), 2)

# 画像サイズを縮小して返す関数
def resize_image(screenshot):
    height_resize = screenshot.shape[0] / (screenshot.shape[1] / SCREEN_W)
    SCREEN_H_REAL = height_resize
    size = (int(SCREEN_W), int(height_resize))
    return cv2.resize(screenshot, size)

# 分析全体をする関数
def analyze_page(driver, num, title, url):
    driver.get(url) # 検証ページをオープン
    get_html(driver) # htmlの取得
    driver.save_screenshot('./output/screenshot/'+ str(num) + '-' + title +'.png') # スクショ取得

    screenshot = cv2.imread('./output/screenshot/'+ str(num) + '-' + title +'.png', 1)
    screenshot = resize_image(screenshot)
    
    image_ratio = calc_pictorial_ratio(driver, screenshot) # 画像の割合を計算

    print('占有率: ' + str(image_ratio))

    # 画像占有率による分岐
    if(image_ratio>(THRESHOLD_PICTORIAL*100)):
        cv2.imwrite('./output/pictorial/'+ str(num) + '-' + title +'.png', screenshot ) #Save
    elif(image_ratio<(THRESHOLD_TEXT*100)):
        cv2.imwrite('./output/text/'+ str(num) + '-' + title +'.png', screenshot ) #Save
    else:
        cv2.imwrite('./output/mixed/'+ str(num) + '-' + title +'.png', screenshot ) #Save


# main
if __name__ == '__main__':
    # csvの読み込み
    tag_list_num = count_row_csv(CSV_INPUT_PATH)
    csv_web_list = pd.read_csv(CSV_INPUT_PATH)

    print('行数: ' + str(tag_list_num))

    binary = FirefoxBinary('/Applications/Firefox.app/Contents/MacOS/firefox')
    binary.add_command_line_options('-headless')
    driver = webdriver.Firefox(firefox_binary=binary)
    driver.set_window_size(SCREEN_W, SCREEN_H)


    for i in range(tag_list_num):
        print('解析対象' + str(i+1) + ': ' + str(csv_web_list.iat[i, 2]))
        analyze_page(driver ,i+1 , csv_web_list.iat[i, 1] , csv_web_list.iat[i, 2])

    # Close Web Browser
    driver.quit()
