import pandas as pd
import geopandas as gpd

import folium
from datetime import datetime
from folium import Choropleth
from IPython.display import IFrame

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from PIL import Image
import glob

import cv2
import os

pd.options.display.max_columns = None
pd.options.display.max_rows = None

prov = gpd.read_file('./prov.shp')
prov = prov.drop(['NAME_0', 'KODE'], axis=1)
prov = prov.set_index('NAME_1')
prov = prov.sort_index(ascending=True)

daily_covid = pd.read_excel('./covid_harian.xlsx')
daily_covid = pd.DataFrame(daily_covid)
daily_covid = daily_covid.rename(columns={'Unnamed: 0': 'Tanggal', 'Aceh': 'Aceh', 'Bali': 'Bali',
                                          'Babel': 'Bangka Belitung', 'Banten': 'Banten', 'Bengkulu': 'Bengkulu',
                                          'Gorontalo': 'Gorontalo', 'Jabar': 'Jawa Barat', 'Jakarta': 'Jakarta Raya',
                                          'Jambi': 'Jambi', 'Jateng': 'Jawa Tengah', 'Jatim': 'Jawa Timur',
                                          'Kalbar': 'Kalimantan Barat', 'Kalsel': 'Kalimantan Selatan',
                                          'Kaltara': 'Kalimantan Utara', 'Kalteng': 'Kalimantan Tengah',
                                          'Kaltim': 'Kalimantan Timur', 'Kep Riau': 'Kepulauan Riau',
                                          'Lampung': 'Lampung', 'Maluku': 'Maluku', 'Malut': 'Maluku Utara',
                                          'NTB': 'Nusa Tenggara Barat', 'NTT': 'Nusa Tenggara Timur',
                                          'Papbar': 'Papua Barat', 'Papua': 'Papua', 'Riau': 'Riau',
                                          'Sulbar': 'Sulawesi Barat', 'Sulsel': 'Sulawesi Selatan',
                                          'Sulteng': 'Sulawesi Tengah', 'Sultra': 'Sulawesi Tenggara',
                                          'Sulut': 'Sulawesi Utara', 'Sumbar': 'Sumatera Barat',
                                          'Sumsel': 'Sumatera Selatan', 'Sumut': 'Sumatera Utara', 'DIY': 'Yogyakarta'})
daily_covid.to_csv('daily_covid_t')
daily_covid['Tanggal'] = daily_covid['Tanggal'].astype(str)
daily_covid_fix = daily_covid.set_index(daily_covid['Tanggal'])
daily_covid_fix = daily_covid_fix.drop(['Tanggal'], axis=1)
daily_covid_fix = daily_covid_fix.T
daily_covid_fix = daily_covid_fix.sort_index(ascending=True)

df = prov.merge(daily_covid_fix, left_index=True, right_index=True, how='inner')
df.to_csv('merged_data')

list_of_days = daily_covid['Tanggal'][518:521]


def embed_map(the_map, filename):
    the_map.save(filename)
    return IFrame(filename, width='100%', height='500px')


for day in list_of_days:
    df_geo = df.copy()

    map1 = folium.Map(tiles=None, zoom_control=False)

    choropleth = Choropleth(geo_data=df_geo.__geo_interface__,
                            data=df_geo[day]/1000,
                            key_on='feature.id',
                            bins=[0, 50, 100, 250, 500, 750, 1000],
                            threshold_scale=[0, 50, 100, 250, 500, 750, 1000],
                            fill_color='Dark2',
                            fill_opacity=0.75,
                            line_color='white',
                            line_weight=0.25,
                            line_opacity=0.75,
                            legend_name='Total Case (1:1000)').add_to(map1)

    map1.fit_bounds([[12.728487, 101.419820], [-13.729686, 136.219106]])

    date = pd.to_datetime(day)
    date = datetime.strftime(date, '%d %B %Y')

    title_html = f'''<h3 align="center" style="font-size:25px">
                        <b>{date}</b></h3>
                     '''
    map1.get_root().html.add_child(folium.Element(title_html))

    embed_map(map1, f'./html_maps/{day}_Covid.html')


chrome_options = Options()
chrome_options.add_argument("enable-automation")
chrome_options.add_argument('--disable-notifications')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('start-maximized')
chrome_options.add_argument("--disable-gpu")


for day in list_of_days:
    tmpurl = f'D:/Project/covid_visualization/html_maps/{day}_Covid.html'
    browser = webdriver.Chrome(executable_path=r'C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe',
                               options=chrome_options)
    time.sleep(5)
    browser.get(tmpurl)
    time.sleep(20)
    browser.save_screenshot(f'./maps/{day}_Covid.png')
    browser.close()
    browser.quit()


def png_to_gif(path_to_images, save_file_path, duration=500):
    frames = []

    images = glob.glob(f'{path_to_images}')

    for i in sorted(images):
        im = Image.open(i)
        im = im.resize((1980, 1020), Image.ANTIALIAS)
        frames.append(im.copy())

    frames[0].save(f'{save_file_path}', format='GIF', append_images=frames[1:], save_all=True,
                   duration=duration, loop=0)


png_to_gif(path_to_images='./maps/*.png',
           save_file_path='./plots/Covid_Choropleth.gif',
           duration=500)


image_folder = 'maps'
video_name = 'covid.avi'

images_ = [img for img in os.listdir(image_folder) if img.endswith(".png")]
frame = cv2.imread(os.path.join(image_folder, images_[0]))
height, width, layers = frame.shape
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
video = cv2.VideoWriter(video_name, fourcc, 4, (width, height))

for image in images_:
    video.write(cv2.imread(os.path.join(image_folder, image)))

cv2.destroyAllWindows()
video.release()
