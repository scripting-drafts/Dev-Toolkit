from selenium import webdriver

file = open("./country_codes_list.txt", "+w")

driver = webdriver.Firefox()
driver.implicitly_wait(20)
driver.get("https://en.wikipedia.org/wiki/List_of_country_calling_codes")

codes = []

for x in range(1, 281):
    country = driver.find_element_by_css_selector('table.wikitable:nth-child(45) > tbody:nth-child(2) > tr:nth-child(' + str(x) + ') > td:nth-child(1)').text
    code = driver.find_element_by_css_selector('table.wikitable:nth-child(45) > tbody:nth-child(2) > tr:nth-child(' + str(x) + ') > td:nth-child(2)').text
    codes.append([code, country])

codes.sort()
for code in codes:
    file.write("<x:String>" + code[0] + " " + code[1] + "</x:String>" + "\n")

file.close()
driver.quit()
