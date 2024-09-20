from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException, StaleElementReferenceException, ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
import time
import datetime
import csv
import itertools
import re


concept = input('What are you looking for?:\n')

barris = ['Barceloneta','Barri Gòtic', 'El Raval', 'Sant Pere', 'Santa Caterina', 'La Ribera',
'Antiga Esquerra de l\'Eixample', 'Nova Esquerra de l\'Eixample', 'Dreta de l\'Eixample',
'Fort Pienc', 'Sagrada Família', 'Sant Antoni', 'La Bordeta', 'La Font de la Guatlla',
'Hostafrancs', 'La Marina de Port', 'La Marina de Prat Vermell', 'El Poblesec', 'Sants',
'Sants-Badal', 'Montjuïc', 'Zona Franca', 'Port', 'Les Corts', 'La Maternitat i Sant Ramon',
'Pedralbes', 'El Putget i Farró', 'Sarrià', 'Sant Gervasi - La Bonanova', 'Sant Gervasi - Galvany',
'Les Tres Torres', 'Vallvidrera', 'Tibidabo', 'Les Planes', 'Vila de Gràcia', 'Camp d\'en Grassot i Gràcia Nova',
'La Salut', 'Barri del Coll', 'Vallcarca i els Penitents', 'El baix Guinardó', 'El Guinardó',
'Can Baró', 'El Carmel', 'La Font d\'en Fargues', 'Horta', 'La Clota', 'Montbau', 'Sant Genís dels Agudells',
'La Teixonera', 'La Vall d\'Hebron', 'Can Peguera', 'Canyelles', 'Ciutat Meridiana', 'La Guineueta',
'Porta', 'Prosperitat', 'Les Roquetes', 'Torre Baró', 'Trinitat Nova', 'El Turó de la Peira',
'Vallbona', 'Verdum', 'Vilapicina', 'La Torre Llobeta', 'Baró de Viver', 'Bon Pastor', 'El Congrés i els Indians',
'Navas', 'Sant Andreu de Palomar', 'La Sagrera', 'Trinitat Vella', 'El Besòs i el Maresme', 'El Clot',
'El Camp de l\'Arpa del Clot', 'Diagonal Mar i el Front Marítim del Poblenou', 'El Parc i la llacuna del Poblenou',
'El Poblenou', 'Provençals del Poblenou', 'Sant Martí de Provençals', 'La Verneda', 'La Pau', 'Vila Olímpica del Poblenou']

startDate = datetime.date.today()
start = time.strftime("%H:%M:%S")
path = './' + str(startDate) + '_' + start + '_' + 'barcelona-' + concept + '.csv'
searchLevel = 1
locationList = []
locationSet = ()
reCode = re.compile('(-?\d+\.\d+?),(-?\d+\.\d+)')

data = {
    'name':[],
    'address':[],
    'rate':[],
    'comments':[],
    'type':[],
    'lat':[],
    'lon':[],
    'errors':[]
}

class mapsSearch:
    def setDriver(self):
        driver = webdriver.Firefox()
        driver.implicitly_wait(10)
        driver.get('https://www.google.com/maps/')
        driver.fullscreen_window()

        self.driver = driver

    def getDriver(self):
        return self.driver

    def zoomSearch(self):
        try:
            zoomIn = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'widget-zoom-in')))
            self.driver.find_element_by_id('widget-zoom-in').click()
            time.sleep(3) #6
            searchThisArea = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'widget-search-this-area-inner')))
            self.driver.find_element_by_class_name('widget-search-this-area-inner').click()
            time.sleep(3) #6
        except TimeoutException:
            print('zoomSearch:TimeoutException')
            pass
        except ElementNotInteractableException:
            print('zoomSearch:ElementNotInteractableException | Skipping neighbourhood')
            pass

def unique_everseen(iterable, key=None):
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in filterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element

####################################### INITIALIZE
ms = mapsSearch()
ms.setDriver()
time.sleep(3)
try:
    ms.getDriver().switch_to.frame(ms.getDriver().find_element_by_css_selector('.widget-consent-frame'))
    ms.getDriver().find_element_by_css_selector('#introAgreeButton > span:nth-child(3) > span:nth-child(1)').click()
    ms.getDriver().switch_to.default_content()
except Exception:
    pass

####################################### LOCATE PLACES
for barri in tqdm(barris):
    try:
        ms.getDriver().find_element_by_id('searchboxinput').send_keys(Keys.CONTROL + 'a')
        ms.getDriver().find_element_by_id('searchboxinput').send_keys(barri + ' barcelona' + Keys.RETURN)
    except ElementNotInteractableException:
        ms.getDriver().get('https://www.google.com/maps/')
        ms.getDriver().find_element_by_id('searchboxinput').send_keys(barri + ' barcelona' + Keys.RETURN)
    time.sleep(6)
    try:
        ms.getDriver().find_element_by_id('searchboxinput').send_keys(Keys.CONTROL + 'a')
        ms.getDriver().find_element_by_id('searchboxinput').send_keys(concept + Keys.RETURN)
    except ElementNotInteractableException:
        time.sleep(4)
        ms.getDriver().find_element_by_id('searchboxinput').send_keys(Keys.CONTROL + 'a')
        ms.getDriver().find_element_by_id('searchboxinput').send_keys(concept + Keys.RETURN)
    time.sleep(4)
    ms.zoomSearch()
    searchLevel = 1
    while searchLevel <= 6:
        try:
            sectionResultsRAW = WebDriverWait(ms.getDriver(), 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.section-result-title')))
            sectionResultsLocationRAW = WebDriverWait(ms.getDriver(), 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.section-result-location')))
        except TimeoutException:
            break
        else:
            for (sectionResult, sectionResultLocation) in itertools.zip_longest(sectionResultsRAW, sectionResultsLocationRAW, fillvalue =''):
                locationList.append([sectionResult.text, sectionResultLocation.text])
        ms.zoomSearch()
        try:
            emptyList = ms.getDriver().find_element_by_css_selector('.section-no-result-title')
        except NoSuchElementException:
            pass
        else:
            break
        searchLevel += 1

################################## FILTER DUPLICATES
locationSet = list(unique_everseen(locationList, key=frozenset))

################################## EXTRACT DATA
for (sectionResult, sectionResultLocation) in tqdm(locationSet):
    try:
        ms.getDriver().find_element_by_id('searchboxinput').send_keys(Keys.CONTROL + 'a')
    except ElementNotInteractableException:
        ms.getDriver().get('https://www.google.com/maps/')
    finally:
        ms.getDriver().find_element_by_id('searchboxinput').send_keys(sectionResult + " " + sectionResultLocation + Keys.RETURN)
    time.sleep(4)
    try:
        try:
            newTitle = WebDriverWait(ms.getDriver(), 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.section-hero-header-title-title')))
            cleanNewTitle = newTitle.text
        except Exception:
            newTitle = WebDriverWait(ms.getDriver(), 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.section-hero-header-title-title.GLOBAL__gm2-headline-5')))
            cleanNewTitle = newTitle.text
        try:
            newLocation = WebDriverWait(ms.getDriver(), 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.section-info-text')))
            cleanNewLocation = newLocation.text
        except Exception:
            newLocation = WebDriverWait(ms.getDriver(), 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ugiz4pqJLAG__primary-text.gm2-body-2')))
            cleanNewLocation = newLocation.text
    except TimeoutException:
        try:
            click = WebDriverWait(ms.getDriver(), 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.section-result-title')))
            ms.getDriver().find_element_by_css_selector('.section-result').click()
            time.sleep(4)
            try:
                try:
                    newTitle = WebDriverWait(ms.getDriver(), 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.section-hero-header-title-title')))
                    cleanNewTitle = newTitle.text
                except Exception:
                    newTitle = WebDriverWait(ms.getDriver(), 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.section-hero-header-title-title.GLOBAL__gm2-headline-5')))
                    cleanNewTitle = newTitle.text
                try:
                    newLocation = WebDriverWait(ms.getDriver(), 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.section-info-text')))
                    cleanNewLocation = newLocation.text
                except Exception:
                    newLocation = WebDriverWait(ms.getDriver(), 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ugiz4pqJLAG__primary-text.gm2-body-2')))
                    cleanNewLocation = newLocation.text
            except TimeoutException:
                print('#TimeoutException: Something is wrong')
                pass
            else:
                try:
                    starsRate = WebDriverWait(ms.getDriver(), 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.section-star-display')))
                    cleanStarsRate = float((starsRate.text).replace(',','.'))
                except TimeoutException:
                    cleanStarsRate = ''
                    pass
                try:
                    commentsNum = WebDriverWait(ms.getDriver(), 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.section-rating-term-list > span:nth-child(1) > span:nth-child(2) > span:nth-child(1) > button:nth-child(1)')))
                    subCommentsNum = re.sub('[()]', '', str(commentsNum.text))
                    cleanCommentsNum = int(subCommentsNum.replace('.', ''))
                except TimeoutException:
                    cleanCommentsNum = ''
                    pass
                try:
                    try:
                        placeType = WebDriverWait(ms.getDriver(), 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.section-rating > div:nth-child(2) > span:nth-child(1) > span:nth-child(1) > button:nth-child(1)')))
                        cleanPlaceType = placeType.text
                    except Exception:
                        placeType = WebDriverWait(ms.getDriver(), 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.GLOBAL__gm2-body-2:nth-child(2) > span:nth-child(1) > span:nth-child(1) > button:nth-child(1)')))
                        cleanPlaceType = placeType.text
                except TimeoutException:
                    cleanPlaceType = ''
                    pass
                try:
                    url = ms.getDriver().current_url
                    geoCode = re.findall(reCode, url)
                    lat, lon = geoCode[0][0], geoCode[0][1]
                    data['errors'].append('')
                except Exception as e:
                    error = e
                    data['errors'].append(error)
                    lat, lon = '', ''

        except TimeoutException:
            print('2 TimeoutException in click')
            pass
        except ElementClickInterceptedException:
            print('2 ElementClickInterceptedException')
            pass
    else:
        try:
            starsRate = WebDriverWait(ms.getDriver(), 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.section-star-display')))
            cleanStarsRate = float((starsRate.text).replace(',','.'))
        except TimeoutException:
            cleanStarsRate = ''
            pass
        try:
            commentsNum = WebDriverWait(ms.getDriver(), 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.section-rating-term-list > span:nth-child(1) > span:nth-child(2) > span:nth-child(1) > button:nth-child(1)')))
            subCommentsNum = re.sub('[()]', '', str(commentsNum.text))
            cleanCommentsNum = int(subCommentsNum.replace('.', ''))
        except TimeoutException:
            cleanCommentsNum = ''
            pass
        try:
            try:
                placeType = WebDriverWait(ms.getDriver(), 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.section-rating > div:nth-child(2) > span:nth-child(1) > span:nth-child(1) > button:nth-child(1)')))
                cleanPlaceType = placeType.text
            except Exception:
                placeType = WebDriverWait(ms.getDriver(), 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.GLOBAL__gm2-body-2:nth-child(2) > span:nth-child(1) > span:nth-child(1) > button:nth-child(1)')))
                cleanPlaceType = placeType.text
        except TimeoutException:
            cleanPlaceType = ''
            pass
        try:
            url = ms.getDriver().current_url
            geoCode = re.findall(reCode, url)
            lat, lon = geoCode[0][0], geoCode[0][1]
            data['errors'].append('')
        except Exception as e:
            error = e
            data['errors'].append(error)
            lat, lon = '', ''
    finally:
        data['name'].append(cleanNewTitle)
        data['address'].append(cleanNewLocation)
        data['rate'].append(cleanStarsRate)
        data['comments'].append(cleanCommentsNum)
        data['type'].append(cleanPlaceType)
        data['lat'].append(lat)
        data['lon'].append(lon)
ms.getDriver().quit()

################################## WRITE DATA
with open(path, 'w', encoding='utf_8_sig') as f:
    writer = csv.writer(f, dialect='excel', delimiter=';')
    writer.writerow(data.keys())
    writer.writerows(zip(*data.values()))

endDate = datetime.date.today()
end = time.strftime("%H:%M:%S")

print('Time elapsed:\n' + str(startDate) + ' ' + start + '\n' + str(endDate) + ' ' + end)
