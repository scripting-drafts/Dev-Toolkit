from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from subprocess import Popen, PIPE
from time import sleep
import requests
import re

msgWelcome = '''Benvingut al Port de Barcelona. Envia *ca* per continuar en català.
Bienvenido al Puerto de Barcelona. Envía *es* para continuar en español.
Welcome to the Port of Barcelona. Send *en* to continue in English.
Bienvenue au Port de Barcelona. Envoyer *fr* pour continuer en français.\n'''

msgInstrCa = '''Si us plau, indiqui el tipus d'incidència que vol reportar:
*abocament*, *objecte*, *animals*, *olors*, *soroll*, *pols*, *fum*, *altres*\n'''

msgInstrEs = '''Por favor, indique el tipo de incidencia que desea reportar:
*vertido*, *objeto*, *animales*, *olores*, *ruido*, *polvo*, *humo*, *otros*\n'''

msgInstrEn = '''Please, tell us the kind of incident you would like to report:
*spill*, *object*, *animals*, *smell*, *noise*, *dust*, *smoke*, *others*\n'''

msgInstrFr = '''Veuillez nous indiquer le type d'incident que vous souhaitez signaler:
*gaspillage*, *objet*, *animaux*, *odeur*, *bruit*, *poussière*, *fumée*, *autres*\n'''

vLangs = ["ca","es","en","fr"]
vInstr = [msgInstrCa,msgInstrEs,msgInstrEn,msgInstrFr]

msgIncAbCa = ["Especifiqui: *mar*, *dàrsena* o *calzada*\n"]
msgIncObCa = ["Especifiqui: *flotant* o *calzada*\n"]
msgIncAnCa = ["Especifiqui: *mar*, *calzada* o *aus mortes*\n"]
msgIncOlCa = ["Especifiqui: *mala olor* o *olor química*\n"]
msgIncSoCa = ["Especifiqui: *port*, *embarcació*\n"]
msgIncPoCa = ["Especifiqui: *port*, *soja*\n"]
msgIncFuCa = ["Especifiqui: *port*, *embarcació* o *altres*\n"]

msgIncAbEs = ["Especifique: *mar*, *dársena* o *calzada*\n"]
msgIncObEs = ["Especifique: *flotante* o *calzada*\n"]
msgIncAnEs = ["Especifique: *mar*, *calzada* o *aves muertas*\n"]
msgIncOlEs = ["Especifique: *mal olor* u *olor químico*\n"]
msgIncSoEs = ["Especifique: *puerto* o *embarcación*\n"]
msgIncPoEs = ["Especifique: *puerto* o *soja*\n"]
msgIncFuEs = ["Especifique: *puerto*, *embarcación* u *otros*\n"]

msgIncAbEn = ["Specify: *sea*, *dock* or *road*\n"]
msgIncObEn = ["Specify: *floating* or *road*\n"]
msgIncAnEn = ["Specify: *sea*, *road* or *dead birds*\n"]
msgIncOlEn = ["Specify: *bad smell* or *chemical smell*\n"]
msgIncSoEn = ["Specify: *harbour* or *ship*\n"]
msgIncPoEn = ["Specify: *harbour* or *soy*\n"]
msgIncFuEn = ["Specify: *harbour*, *ship* or *others*\n"]

msgIncAbFr = ["Spécifier: *mer*, *dock* or *chaussée*\n"]
msgIncObFr = ["Spécifier: *flottant* or *chaussée*\n"]
msgIncAnFr = ["Spécifier: *mer*, *chaussée* or *oiseaux morts*\n"]
msgIncOlFr = ["Spécifier: *mal odeur* or *odeur chimique*\n"]
msgIncSoFr = ["Spécifier: *port* or *bateau*\n"]
msgIncPoFr = ["Spécifier: *port* or *soja*\n"]
msgIncFuFr = ["Spécifier: *port*, *bateau* or *autres*\n"]

vIncidentsCa = ["abocament","objecte","animals","olors","soroll","pols","fum","altres"]
vIncidentsEs = ["vertido","objeto","animales","olores","ruido","polvo","humo","otros"]
vIncidentsEn = ["spill", "object", "animals", "smell", "noise", "dust", "smoke", "others"]
vIncidentsFr = ["gaspillage", "objet", "animaux", "odeur", "bruit", "poussière", "fumée", "autres"]
vIncidents = [vIncidentsCa,vIncidentsEs, vIncidentsEn, vIncidentsFr]

vIncCa = [msgIncAbCa, msgIncObCa, msgIncAnCa, msgIncOlCa, msgIncSoCa, msgIncPoCa, msgIncFuCa]
vIncEs = [msgIncAbEs, msgIncObEs, msgIncAnEs, msgIncOlEs, msgIncSoEs, msgIncPoEs, msgIncFuEs]
vIncEn = [msgIncAbEn, msgIncObEn, msgIncAnEn, msgIncOlEn, msgIncSoEn, msgIncPoEn, msgIncFuEn]
vIncFr = [msgIncAbFr, msgIncObFr, msgIncAnFr, msgIncOlFr, msgIncSoFr, msgIncPoFr, msgIncFuFr]
vInc = [vIncCa, vIncEs, vIncEn, vIncFr]

vIncDetailCa = ["mar", "dàrsena", "calzada", "flotant", "aus mortes", "mala olor", "olor química", "port", "embarcació", "soja", "altres"]
vIncDetailEs = ["mar", "dársena", "calzada", "flotante", "aves muertas", "mal olor", "olor químico", "puerto", "embarcación", "soja", "otros"]
vIncDetailEn = ["sea", "dock", "road", "floating", "dead birds", "bad smell", "chemical smell", "harbour", "ship", "soy", "others"]
vIncDetailFr = ["mer", "dock", "chaussée", "flottant", "oiseaux morts", "mal odeur", "odeur chimique", "port", "bateau", "soja", "autres"]
vIncDetail = [vIncDetailCa, vIncDetailEs, vIncDetailEn, vIncDetailFr]

picReqCA = "Si us plau, envïi una foto de la incidència\n"
picReqES = "Por favor, envíe una foto de la incidencia\n"
picReqEN = "Please, send a picture of the incident\n"
picReqFR = "S'il vous plaît, prenez une photo de l'incident\n"

picReq = [picReqCA, picReqES, picReqEN, picReqFR]

proCA = "Processant...\n"
proES = "Procesando...\n"
proEN = "Processing...\n"
proFR = "En traitement...\n"

pro = [proCA, proES, proEN, proFR]

locMSGCA = "Si us plau, comparteixi la seva localització\n"
locMSGES = "Por favor, comparta su localización\n"
locMSGEN = "Please, share your location\n"
locMSGFR = "S'il vous plaît, partager votre emplacement\n"
locMSG = [locMSGCA, locMSGES, locMSGEN, locMSGFR]

endMSGCA = "Gràcies\n"
endMSGES = "Gracias\n"
endMSGEN = "Thank you\n"
endMSGFR = "Mersi\n"
End = [endMSGCA, endMSGES, endMSGEN, endMSGFR]

reString = re.compile('(\d+\.\d+)')
data = {}
end = {}
user_queue = []
x = 0

profile = webdriver.FirefoxProfile()
profile.set_preference("dom.webnotifications.enabled", False)
profile.set_preference("dom.push.enabled", False)
profile.set_preference("dom.webdriver.enabled", False)
profile.set_preference('useAutomationExtension', False)
profile.set_preference('privacy.trackingprotection.enabled', True)
# profile.set_preference("browser.cache.disk.enable", False)
# profile.set_preference("browser.cache.memory.enable", False)
# profile.set_preference("browser.cache.offline.enable", False)
# profile.set_preference("network.http.use-cache", False)
profile.update_preferences()

driver = webdriver.Firefox(profile)
driver.implicitly_wait(10)
driver.get('https://web.whatsapp.com')

# CSS SELECTORS
unread_class = '._31gEB'
user_id_class = '.DP7CM > ._3ko75._5h6Y_._3Whw5'
text_box_class = '._2FVVk._2UL8j > ._3FRCZ.copyable-text.selectable-text'
message_class = '._3Whw5.selectable-text.invisible-space.copyable-text'
message_context_class = '.eRacY'
bot_message_class = '._2oWZe._2HWXK'
image_context_class = '._2kLly > ._39rvu'
pic_class = '._2kLly > ._8Yseo._3W6yC._3Whw5'
location_class = '._2geuz'
user_boxes_class = '._3ko75._5h6Y_._3Whw5'
delete_button_class = '.Ut_N0.n-CQr'
delete_class = '._2LPYs.S7_rT.FV2Qy'

while True:
    try:
        unread = driver.find_elements_by_css_selector(unread_class)
        if len(unread):
            element = unread[-1]
            ActionChains(driver).move_to_element_with_offset(element, 0, -20).click().perform()
            ActionChains(driver).move_to_element_with_offset(element, 0, -20).click().perform()
            ActionChains(driver).move_to_element_with_offset(element, 0, -20).click().perform()
    except Exception:
        pass
    try:
        user_id = driver.find_element_by_css_selector(user_id_class).text.replace('+', '00').replace(' ', '')

        if user_id not in user_queue:
            user_queue.append(user_id)

        if user_queue[0] not in [*data]:
            text_box = driver.find_element_by_css_selector(text_box_class)
            text_box.send_keys(msgWelcome)
            data[user_queue[0]] = ['init']
            user_queue.remove(user_queue[0])
    except Exception:
        pass
    try:
        cnt = 10
        user_id = driver.find_element_by_css_selector(user_id_class).text.replace('+', '00').replace(' ', '')

        if user_id not in user_queue:
            user_queue.append(user_id)

        while len(data[user_queue[0]]) == 1:
            message = driver.find_elements_by_css_selector(message_class)[-1]
            try:
                message_context = driver.find_elements_by_css_selector(message_context_class)[-1]
                bot_message = message_context.find_element_by_css_selector(bot_message_class)
            except Exception:
                bot_message = ''

            if message.text.lower() in vLangs and bot_message == '':
                data[user_queue[0]].append(vLangs[vLangs.index(message.text.lower())])
                text_box = driver.find_element_by_css_selector(text_box_class)
                text_box.send_keys(vInstr[vLangs.index(data[user_queue[0]][1])])
                user_queue.remove(user_queue[0])
                sleep(1)
                break
            sleep(1)
            cnt -= 1
            if not cnt:
                user_queue.remove(user_queue[0])

        while len(data[user_queue[0]]) == 2:
            message = driver.find_elements_by_css_selector(message_class)[-1]
            try:
                message_context = driver.find_elements_by_css_selector(message_context_class)[-1]
                bot_message = message_context.find_element_by_css_selector(bot_message_class)
            except Exception:
                bot_message = ''

            if message.text.lower() in vIncidents[vLangs.index(data[user_queue[0]][1])] and bot_message == '':
                if message.text.lower() == vIncidents[vLangs.index(data[user_queue[0]][1])][7]:
                    inc_type = vIncidents[1][vIncidents[vLangs.index(data[user_queue[0]][1])].index(message.text.lower())]
                    text_box = driver.find_element_by_css_selector(text_box_class)
                    text_box.send_keys(picReq[vLangs.index(data[user_queue[0]][1])])
                    data[user_queue[0]].append(inc_type)
                    data[user_queue[0]].append(inc_type)
                    user_queue.remove(user_queue[0])
                    sleep(1)
                    break
                else:
                    inc = vIncidents[vLangs.index(data[user_queue[0]][1])].index(message.text.lower())
                    inc_type = vIncidents[1][vIncidents[vLangs.index(data[user_queue[0]][1])].index(message.text.lower())]
                    text_box = driver.find_element_by_css_selector(text_box_class)
                    text_box.send_keys(vInc[vLangs.index(data[user_queue[0]][1])][inc])
                    data[user_queue[0]].append(inc_type)
                    user_queue.remove(user_queue[0])
                    sleep(1)
                    break
            sleep(1)
            cnt -= 1
            if not cnt:
                user_queue.remove(user_queue[0])

        while len(data[user_queue[0]]) == 3:
            message = driver.find_elements_by_css_selector(message_class)[-1]
            try:
                message_context = driver.find_elements_by_css_selector(message_context_class)[-1]
                bot_message = message_context.find_element_by_css_selector(bot_message_class)
            except Exception:
                bot_message = ''

            if message.text.lower() in vIncDetail[vLangs.index(data[user_queue[0]][1])] and bot_message == '':
                inc_detail = vIncDetail[1][vIncDetail[vLangs.index(data[user_queue[0]][1])].index(message.text.lower())]
                text_box = driver.find_element_by_css_selector(text_box_class)
                text_box.send_keys(picReq[vLangs.index(data[user_queue[0]][1])])
                data[user_queue[0]].append(inc_detail)
                user_queue.remove(user_queue[0])
                sleep(1)
                break
            sleep(1)
            cnt -= 1
            if not cnt:
                user_queue.remove(user_queue[0])

        while len(data[user_queue[0]]) == 4:
            try:
                image_context = driver.find_elements_by_css_selector(image_context_class)[-1]
                image_context.click()
                sleep(3)
                pic = driver.find_element_by_css_selector(pic_class)
                data[user_queue[0]][0] = str('{:>016d}'.format(x))
                screenshot = pic.screenshot(data[user_queue[0]][0] + '.png')
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                text_box = driver.find_element_by_css_selector(text_box_class)
                text_box.send_keys(pro[vLangs.index(data[user_queue[0]][1])])
                upload = Popen('drive push -quiet ' + data[user_queue[0]][0] + '.png', stdin=None, stderr=None, shell=True).communicate()
                publish = Popen('drive pub ' + data[user_queue[0]][0] + '.png', stdin=None, stderr=None, stdout=PIPE, shell=True).communicate()
                parts = str(publish).split('id=')
                pub_id = str(parts[1]).split('\\n')
                public_id = pub_id[0]
                data[user_queue[0]].append('https://drive.google.com/file/d/' + public_id + '/preview')
                text_box.send_keys(locMSG[vLangs.index(data[user_queue[0]][1])])
                x += 1
                user_queue.remove(user_queue[0])
                sleep(1)
                break
            except Exception:
                pass
            sleep(1)
            cnt -= 1
            if not cnt:
                user_queue.remove(user_queue[0])

        while len(data[user_queue[0]]) == 5:
            try:
                location = driver.find_element_by_css_selector(location_class)
                locationURL = location.get_attribute('href')
                coordinates = re.findall(reString, locationURL)
                data[user_queue[0]].append(coordinates[0])
                data[user_queue[0]].append(coordinates[1])
                data[user_queue[0]].append(locationURL)
                try:
                    response = requests.post('http://127.0.0.1:8000/input/' + user_queue[0] + '/', headers={ 'content-Type': 'application/json'}, data= '{"id":"' + data[user_queue[0]][0] + '", "inc_type":"' + data[user_queue[0]][2] + '", "inc_detail":"' + data[user_queue[0]][3] + '", "lat":"' + data[user_queue[0]][5] + '", "lon":"' + data[user_queue[0]][6] + '", "url":"' + data[user_queue[0]][7] + '", "pic":"' + data[user_queue[0]][4] + '", "is_active":"True"}')
                except response.status_code == '400' or response.status_code == '422':
                    data[user_queue[0]].append(response.status_code)
                    requests.post('http://127.0.0.1:8000/invalid_input/' + user_queue[0] + '/', headers={ 'content-Type': 'application/json'}, data='{"id":"' + data[user_queue[0]][0] + '", "data":"' + data[user_queue[0]] + '"}')
                except Exception as e:
                    print(e)
                    pass
                text_box = driver.find_element_by_css_selector(text_box_class)
                text_box.send_keys(End[vLangs.index(data[user_queue[0]][1])])
                end[user_queue[0]] = True
                user_queue.remove(user_queue[0])
                sleep(1)
                break
            except Exception:
                pass
            sleep(1)
            cnt -= 1
            if not cnt:
                user_queue.remove(user_queue[0])

        if end[user_queue[0]]:
            user_boxes = driver.find_elements_by_css_selector(user_boxes_class)
            user_delete = [user_box for user_box in user_boxes if user_box.text.replace('+', '00').replace(' ', '') == user_queue[0]]
            ActionChains(driver).context_click(user_delete[0]).perform()
            delete_button = driver.find_elements_by_css_selector(delete_button_class)[2]
            delete_button.click()
            delete = driver.find_element_by_css_selector(delete_class)
            delete.click()
            del data[user_queue[0]]
            user_queue.remove(user_queue[0])
            sleep(3)

        if len(end[user_queue[0]]):
            del end[user_queue[0]]
    except Exception:
        pass
