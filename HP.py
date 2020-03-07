from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
import sys
import os
import pandas as pd
import time
from bs4 import BeautifulSoup
import re
# import math
import pickle
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import numpy as np
import datetime


def get_rid_of_EU_glupost(driver):
    try:
        EU_reqs_approval = driver.find_element_by_partial_link_text("Prihvati i zatvori")
        EU_reqs_approval.click()
    except:
        pass

def prepare_lists(lista):
    try:
        lista.remove("INFONA")
    except:
        pass
    lista = sorted(lista, key=len, reverse=True)
    return lista


def update_map(df, map):
    df['Web Model'] = df['Web Model'].astype(str)
    map['Model'] = map['Model'].astype(str)
    Manufacturers = [x.upper() for x in list(map['Manufacturer'].drop_duplicates(keep='first'))]
    Models = [x.upper() for x in list(map['Model'].drop_duplicates(keep='first'))]
    Memories = [x.upper() for x in list(map['Memory'].drop_duplicates(keep='first'))]
    Manufacturers, Models, Memories = prepare_lists(Manufacturers), prepare_lists(Models), prepare_lists(Memories)
    lists = [Manufacturers, Models, Memories]
    fields = ["Manufacturer", "Model", "Memory"]
    web_labels = df[['Web Model']]
    fresh_web_labels = pd.merge(web_labels, map, on=['Web Model'], how='left')
    fresh_web_labels = fresh_web_labels.loc[fresh_web_labels["Model"].isnull()].copy()
    fresh_web_labels.drop_duplicates(subset=['Manufacturer', 'Model', 'Memory', 'Web Model'], inplace=True)
    for n, row in fresh_web_labels.iterrows():
        web_label_u = str(row['Web Model']).upper()
        web_label = web_label_u.replace(" ", "")
        web_label = web_label.replace("-", "")
        for i, lista in enumerate(lists):
            success = False
            for element in lista:
                to_be_found = element.upper().replace(" ", "")
                if to_be_found.isdecimal():
                    pass
                else:
                    if to_be_found in web_label and not success:
                        row[fields[i]] = element
                        success = True
            if not success and lista != Memories:
                question = "I need help guessing the " + fields[i].upper() + " of the model above. Input it here please -> "
                print(web_label_u) #, n)
                row[fields[i]] = input(question).upper()
    fresh_web_labels.sort_values(by=['Manufacturer', 'Model', 'Memory', 'Web Model'], inplace=True)
    fresh_web_labels.drop_duplicates(subset=['Manufacturer', 'Model', 'Memory', 'Web Model'], inplace=True)
    fresh_web_labels.fillna("INFONA", inplace=True)
    result=pd.concat([map,fresh_web_labels])
    with pd.ExcelWriter("map.xlsx") as file:  # doctest: +SKIP
        result.to_excel(file, sheet_name='map', index=False)
    return result


def update_map_o(df, map):
    df['Web Model'] = df['Web Model'].astype(str)
    map.fillna("INFONA", inplace=True)
    map['Model'] = map['Model'].astype(str)
    Manufacturers = [x.upper() for x in list(map['Manufacturer'].drop_duplicates(keep='first'))]
    Models = [x.upper() for x in list(map['Model'].drop_duplicates(keep='first'))]
    Memories = [x.upper() for x in list(map['Memory'].drop_duplicates(keep='first'))]
    Manufacturers, Models, Memories = prepare_lists(Manufacturers), prepare_lists(Models), prepare_lists(Memories)
    lists = [Manufacturers, Models, Memories]
    fields = ["Manufacturer", "Model", "Memory"]
    extract = df[['Web Model']]
    fusion = pd.merge(extract, map, on=['Web Model'], how='left')
    fusion.drop_duplicates(subset=['Manufacturer', 'Model', 'Memory', 'Web Model'], inplace=True)
    for n, row in fusion.iterrows():
        web_label = str(row['Web Model'])
        long_model = web_label.replace(" ", "")
        long_model = long_model.replace("-", "")
        cadena = long_model.upper()
        for i, lista in enumerate(lists):
            success = False
            if row[fields[i]] == "INFONA":
                for element in lista:
                    to_be_found = element.upper().replace(" ", "")
                    to_be_found = to_be_found.replace(" ", "")
                    if to_be_found in cadena and not success:
                        row[fields[i]] = element
                        success = True
                if not success and lista != Memories:
                    question = "I need help guessing the " + fields[i] + " of the model above. Input it here please -> "
                    print(web_label, n)
                    row[fields[i]] = input(question).upper()
    fusion.sort_values(by=['Manufacturer', 'Model', 'Memory', 'Web Model'], inplace=True)
    fusion.drop_duplicates(subset=['Manufacturer', 'Model', 'Memory', 'Web Model'], inplace=True)
    with pd.ExcelWriter("map.xlsx") as file:  # doctest: +SKIP
        fusion.to_excel(file, sheet_name='map', index=False)
    return fusion


def numerize(decimal_text):
    pick_first = str(re.findall(r'[0-9\.,]+', decimal_text)[0])
    check_comma = pick_first.find(",")
    fuera_puntos = pick_first.replace(".", "")
    if check_comma:
        floatifying = fuera_puntos.replace(",", ".")
    answer = float(floatifying)
    return answer


def clickea(driver, Xpath):
    tries = 0
    while tries < 10:
        try:
            web_element = driver.find_element(By.XPATH, Xpath)
            tries = 10
        except:
            time.sleep(1)
            tries += 1
    web_element.click()


def refresh_SD():
    dfsd = pd.DataFrame(columns=['Company', 'Web Model', 'Upfront', 'Installment', 'Final HS price', 'MRC_total', 'Tariff Name','GB'])
    today_day, today_month, today_year = get_date()
    day, month, year = load_Co_log("Sancta_Domenica")
    if day == today_day and month == today_month and year == today_year:
        print("Sancta Domenica already updated today")
    else:
        driver = webdriver.Chrome()
        next_page_available = True
        driver.get("https://www.sancta-domenica.hr/komunikacije/mobiteli.html")
        time.sleep(4)
        for n in range(9):
            cross_address='/html/body/div['+str(n)+']/span/span'
            try:
                cross = driver.find_element(By.XPATH, cross_address)  # /html/body/div[4]/span/span
            except:
                pass
        cross.click()
        while next_page_available:
            soup = BeautifulSoup(driver.page_source, "lxml")
            all_divs = soup.findAll("div", "product-item-info")
            for item in all_divs:
                model = (item.find("a", "product-item-link").get_text())
                all_prices = item.findAll("span", "price")
                prices = []
                for n in range(len(all_prices)):
                    prices.append(numerize(all_prices[n].get_text()))
                price = min(prices)
                dfsd = dfsd.append({'Company': 'Sancta Domenica', 'Web Model': model, 'Upfront': price, 'Installment': 0,
                                    'Final HS price': price, 'MRC_total': 0, 'Tariff Name': 'SD', 'GB': 0},
                                   ignore_index=True)
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            try:
                next_page = driver.find_element_by_partial_link_text('Nastavi')
                next_page.click()
            except:
                next_page_available = False
        driver.quit()
        store_last_checkpoint(dfsd, "Sancta_Domenica")
        #dfsd.to_excel("SD.xlsx")
        print("SD Done")
        return dfsd

def refresh_A1():
    dfA1 = pd.DataFrame(columns=['Company', 'Web Model', 'Upfront', 'Installment', 'Final HS price', 'MRC_total', 'Tariff Name','GB'])
    GB_included = {"Mobilna S+": 2,
                   "Mobilna M": 10,
                   "Mobilna L": 999999}
    MNP_MRCs = {"Mobilna S+": 119,
                "Mobilna M": 159,
                "Mobilna L": 239}
    today_day, today_month, today_year = get_date()
    day, month, year = load_Co_log("A1")
    if day == today_day and month == today_month and year == today_year:
        print("A1 already updated today")
    else:
        driver = webdriver.Chrome()
        driver.get("https://www.a1.hr/webshop/mobiteli-na-pretplatu#show=85")
        tariff_ids = ["TariffSiebel_1-5VHSYZ70", "TariffSiebel_1-5VHSYZ5V", "TariffSiebel_1-5VHSYZ65"]
        for tariff_id in tariff_ids:
            time.sleep(1)
            element = driver.find_element_by_id(tariff_id)  # TariffSiebel_1-5VHSYZ70")
            driver.execute_script("$(arguments[0]).click();", element)
            time.sleep(1)
            soup = BeautifulSoup(driver.page_source, "lxml")
            all_divs = soup.findAll("div", "Product")
            for item in all_divs:
                model = (item.find("p", "Product-title").get_text())
                upfront = numerize(item.find("p", "Product-priceNow").get_text())
                installment = numerize(item.find("p", "Product-priceFull").get_text())
                total_HS_price = upfront + 24 * installment
                tariff_name = (item.find("p", "Product-tariff js-product-tariff-name").get_text())
                mrc = MNP_MRCs[tariff_name]  # numerize(item.find("p", "Product-priceTariff").get_text())
                GB_inc = GB_included[tariff_name]
                dfA1 = dfA1.append({'Company': 'A1', 'Web Model': model, 'Upfront': upfront, 'Installment': installment,
                                    'Final HS price': total_HS_price,
                                    'MRC_total': mrc, 'Tariff Name': tariff_name, 'GB': GB_inc}, ignore_index=True)
        driver.quit()
        store_last_checkpoint(dfA1, "A1")
        #dfA1.to_excel("A1.xlsx")
        print("A1 Done")
        return dfA1

def refresh_T2():
    dfT2 = pd.DataFrame(columns=['Company', 'Web Model', 'Upfront', 'Installment', 'Final HS price', 'MRC_total', 'Tariff Name','GB'])
    paginas, count = 0, 0
    menus = ['//*[@id="tariffsSummaryRow"]/table/tbody/tr/td[2]/p/span',
             '//*[@id="dataPackagesSummaryRow"]/table/tbody/tr/td[2]/p/span',
             '//*[@id="bindPeriodsSummaryRow"]/table/tbody/tr/td[2]/p']  # Tariffs, GBs, MCDs
    tariffs = ['//*[@id="frmData"]/div[4]/main/section/div[1]/section[2]/div[2]/div[2]/div[2]/div[1]/div[2]/p',
               '//*[@id="frmData"]/div[4]/main/section/div[1]/section[2]/div[2]/div[2]/div[2]/div[3]/div[2]/p']  # Raspali, Cisto Tristo
    GBs = ['//*[@id="frmData"]/div[4]/main/section/div[1]/section[2]/div[2]/div[3]/div[2]/div[4]/div[2]/p',
           '//*[@id="frmData"]/div[4]/main/section/div[1]/section[2]/div[2]/div[3]/div[2]/div[3]/div[2]/p',
           '//*[@id="frmData"]/div[4]/main/section/div[1]/section[2]/div[2]/div[3]/div[2]/div[2]/div[2]/p',
           '//*[@id="frmData"]/div[4]/main/section/div[1]/section[2]/div[2]/div[3]/div[2]/div[1]/div[2]/p']
    MCDs = ['//*[@id="frmData"]/div[4]/main/section/div[1]/section[2]/div[2]/div[4]/div[2]/div[1]/div[2]/p',
            '//*[@id="frmData"]/div[4]/main/section/div[1]/section[2]/div[2]/div[4]/div[2]/div[2]/div[2]/p',
            '//*[@id="frmData"]/div[4]/main/section/div[1]/section[2]/div[2]/div[4]/div[2]/div[2]/div[2]/p']
    GB_included = {"JEDAN I POL GB": 1.5,
                   "PET GB": 5,
                   "DESET GB": 10,
                   "BEZBROJ GB": 999999}
    today_day, today_month, today_year = get_date()
    day, month, year = load_Co_log("T2")
    if day == today_day and month == today_month and year == today_year:
        print("Tele2 already updated today")
    else:
        driver = webdriver.Chrome()
        next_page_available = True
        driver.get("https://www.tele2.hr/privatni-korisnici/mobiteli/uz-pretplatu/")
        while next_page_available:
            get_rid_of_EU_glupost(driver)
            phones_in_page = driver.find_elements_by_class_name("t2-device-col-var-img")
            for n, phone in enumerate(phones_in_page):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                refreshed_phones_in_page = driver.find_elements_by_class_name("t2-device-col-var-img")
                time.sleep(1)
                try:
                    refreshed_phones_in_page[n].click()
                except:
                    driver.get("https://www.tele2.hr/privatni-korisnici/mobiteli/uz-pretplatu/")
                    for veces in range(paginas):
                        next_page = driver.find_element_by_partial_link_text("Sljede")
                        next_page.click()
                    refreshed_phones_in_page = driver.find_elements_by_class_name("t2-device-col-var-img")
                    refreshed_phones_in_page[n].click()
                # collecting info from detailed page
                # for MCD in range(len(MCDs)):
                #     menuclick = True
                #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                clickea(driver, menus[0])
                for tariff in range(len(tariffs)):
                    clickea(driver, tariffs[tariff])
                # for GB in range(len(GBs)):
                #     if tariff == 1 and GB == 3:
                #         pass
                #     else:
                # clickea(driver, menuclick, menus[1], GBs[GB])
                    modelo = driver.find_element(By.XPATH, '//*[@id="deviceListSummary"]/table/tbody/tr/td[2]/p').text
                    upfront = numerize(driver.find_element(By.XPATH, '//*[@id="summarySpecsMainContainer"]/table/tbody/tr/td[3]/span[1]').text)
                    installment = numerize(driver.find_element(By.XPATH, '//*[@id="deviceListSummary"]/table/tbody/tr/td[3]/span[1]').text)
                    mrc1 = numerize(driver.find_element(By.XPATH, '//*[@id="tariffsSummaryRow"]/table/tbody/tr/td[3]/span[1]').text)
                    mrc2 = numerize(driver.find_element(By.XPATH, '//*[@id="dataPackagesSummaryRow"]/table/tbody/tr/td[3]/span[1]').text)
                    mrc = mrc1+mrc2
                    try:
                        web_discount = numerize(driver.find_element(By.XPATH,'//*[@id="posSavingsMainContainer"]/table/tbody/tr/td[3]/span[1]').text)
                    except:
                        web_discount = 0    ##### MAKE SURE IT TAKES UPFRONT AND MAKE SURE IT TAKES THIS PRICE INSTEAD OF INSTALLEMENT IF AVAILABLE AND HARD CODE A1
                    tariff_name = driver.find_element(By.XPATH, '//*[@id="tariffsSummaryRow"]/table/tbody/tr/td[2]/p/span').text
                    GB_web_name = driver.find_element(By.XPATH, '//*[@id="dataPackagesSummaryRow"]/table/tbody/tr/td[2]/p/span').text
                    GB_inc = GB_included[GB_web_name]
                    total_HS_price = upfront + 24 * installment + web_discount
                    ## Back.engeneering to make numbers match (considering irrelevant upfront and installment)
                    installment = total_HS_price/24
                    upfront = 0
                    dfT2 = dfT2.append(
                        {'Company': 'Tele2', 'Web Model': modelo, 'Upfront': upfront,'Installment': installment,
                         'Final HS price': total_HS_price,
                         'MRC_total': mrc,
                         'Tariff Name': tariff_name,'GB': GB_inc},
                        ignore_index=True)  # ,"Contract_type": contract_type,'Movement':movement_name
                print(".", end='')
                count += 1
                print(count, end='')
                driver.execute_script("window.history.go(-1)")
                get_rid_of_EU_glupost(driver)
                time.sleep(1)
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                next_page = driver.find_element_by_partial_link_text("Sljede")
                next_page.click()
                paginas += 1
            except:
                next_page_available = False
        driver.quit()
        store_last_checkpoint(dfT2, "T2")
        #dfT2.to_excel("T2.xlsx")
        print()
        print("T2 Done")
        return dfT2


def get_date():
    dt = datetime.datetime.today()
    day = dt.day
    month = dt.month
    year = dt.year
    return day, month, year


def store_last_checkpoint(df, company):
    day, month, year = get_date()
    name = "./LastCheckPoint_" + company + ".pkl"
    with open(name, 'wb') as f:
        pickle.dump([day, month, year, df], f)


def load_Co_log(co):
    name = "./LastCheckPoint_" + co + ".pkl"
    with open(name, 'rb') as f:
        day, month, year, df = pickle.load(f)
    return day, month, year


def load_log():
    # day, month, year = get_date()
    dfs = [1, 2, 3]
    for i, co in enumerate(["Sancta_Domenica", "A1", "T2"]):
        name = "./LastCheckPoint_" + co + ".pkl"
        with open(name, 'rb') as f:
            day, month, year, dfs[i] = pickle.load(f)
    df = pd.concat([dfs[0], dfs[1], dfs[2]])
    return df


def save_and_show_in_excel(name, df):  #### Storage
    workbook_not_saved = True
    #path = "Recommended/" + name
    while workbook_not_saved:
        try:
            with pd.ExcelWriter(name) as file:  # doctest: +SKIP
                df.to_excel(file, sheet_name='All', index=False)
            os.startfile(name)
            workbook_not_saved = False
            print("There you go!")
        except:
            input("Please close the Recommended prices.xlsx file so changes can be saved. Then press ENTER.")


def recommend_prices(model_list, df, GB_ranges):
    poly = PolynomialFeatures(degree=3)
    FLAT = 999999
    DISCOUNT_HS_PREMIUM = .97
    MRC_PREMIUM = 1.04
    df["Memory"].fillna('INFONA', inplace=True)
    df["GB"].fillna(0, inplace=True)
    df.GB = df.GB.astype(int)
    df_to_return = pd.DataFrame(columns=['Manufacturer', 'Model', 'Memory',
                                         'Company', 'PRP/Mkt Price', 'Tariff Name', 'GB', 'MRC_total',
                                         'Final HS price',
                                         'TCO', 'Ideal MRC', 'Ideal HS price', 'Ideal TCO'])

    for index, row in model_list.iterrows():
        manufacturer, model, memory = row.Manufacturer, row.Model, row.Memory
        recommended_HS_price_for_PRP = 999999
        looking_for_PRP = df.loc[(df['Manufacturer'] == row['Manufacturer'])
                                 & (df['Model'] == row['Model']) & (df['Memory'] == row['Memory'])
                                 & (df['Company'] == "Sancta Domenica")]
        if len(looking_for_PRP) > 0:
            recommended_HS_price_for_PRP = looking_for_PRP.iloc[0]["Final HS price"]
        subset = df.loc[(df['Manufacturer'] == row['Manufacturer'])
                        & (df['Model'] == row['Model']) & (df['Memory'] == row['Memory'])
                        & (df['Company'] == "A1") & (df['GB'] > 0) & (df['GB'] < FLAT)].copy()
        A1_is_selling=False
        if len(subset) > 0:
            #A1_is_selling=True
            X_raw, y = np.array(subset['GB']).reshape(-1, 1), np.array(subset['Final HS price']).reshape(-1, 1)
            X = poly.fit_transform(X_raw)
            X2_raw, y2 = np.array(subset['GB']).reshape(-1, 1), np.array(subset['MRC_total']).reshape(-1, 1)
            X2 = poly.fit_transform(X2_raw)
            HS_price_prediction = LinearRegression().fit(X, y)
            MRC_prediction = LinearRegression().fit(X2, y2)

            # FOR FLAT
            row_for_flat = df.loc[(df['Manufacturer'] == row['Manufacturer'])
                                  & (df['Model'] == row['Model']) & (df['Memory'] == row['Memory'])
                                  & (df['Company'] == "A1") & (df['GB'] == FLAT)].copy()

            GB_ranges_to_explore = GB_ranges.loc[(GB_ranges['Tariff Name'] != "PRP")]
            for indice, fila in GB_ranges_to_explore.iterrows():
                MRC = fila['Current MRC']
                #if A1_is_selling:
                intGB_raw = np.array(int(fila.GB)).reshape(1, -1)
                intGB = poly.fit_transform(intGB_raw)
                if intGB_raw == FLAT:
                    recommended_HS_price = max(int(row_for_flat.iloc[0]["Final HS price"] * DISCOUNT_HS_PREMIUM), 0)
                    recommended_MRC = int(row_for_flat.iloc[0]["MRC_total"] * MRC_PREMIUM)
                else:
                    recommended_HS_price = max(int(HS_price_prediction.predict(intGB) * DISCOUNT_HS_PREMIUM), 0)
                    recommended_MRC = int(MRC_prediction.predict(intGB) * MRC_PREMIUM)
            # else:
            #     recommended_HS_price = 0
            #     recommended_MRC = MRC
                gap_HS_price = recommended_MRC - MRC
                if gap_HS_price > 0:
                    corrected_HS_price = recommended_HS_price + gap_HS_price * 24
                else:
                    corrected_HS_price = recommended_HS_price
                if recommended_HS_price_for_PRP != 999999:
                    corrected_HS_price = min(corrected_HS_price, recommended_HS_price_for_PRP)
                else:
                    zero_shaped = np.array(0).reshape(1, -1)
                    zero=poly.fit_transform(zero_shaped)
                    recommended_HS_price_for_PRP=max(int(HS_price_prediction.predict(zero) * DISCOUNT_HS_PREMIUM), 0)
                    corrected_HS_price=recommended_HS_price_for_PRP
                df_to_return = df_to_return.append({'Manufacturer': manufacturer,
                                                    'Model': model,
                                                    'Memory': memory,
                                                    'Final HS price': corrected_HS_price,
                                                    'MRC_total': MRC,
                                                    'Company': "T",
                                                    'PRP/Mkt Price': recommended_HS_price_for_PRP,
                                                    'Tariff Name': fila['Tariff Name'],
                                                    'GB': int(fila.GB),
                                                    'TCO': corrected_HS_price + 24 * MRC,
                                                    'Ideal MRC': recommended_MRC,
                                                    'Ideal HS price': recommended_HS_price,
                                                    'Ideal TCO': recommended_MRC * 24 + recommended_HS_price},
                                                   ignore_index=True)
    return df_to_return


def recommend_prices_for_PRP(df):
    df_to_return = pd.DataFrame(columns=['Manufacturer', 'Model', 'Memory',
                                         'Company', 'PRP/Mkt Price', 'Tariff Name', 'GB', 'MRC_total',
                                         'Final HS price',
                                         'TCO', 'Ideal MRC', 'Ideal HS price', 'Ideal TCO'])

    subset = df.loc[(df['Company'] == "Sancta Domenica")].copy()
    subset.drop_duplicates(subset=['Manufacturer', 'Model', 'Memory'], inplace=True)
    for index, row in subset.iterrows():
        recommended_HS_price_for_PRP = row["Final HS price"]
        df_to_return = df_to_return.append({'Manufacturer': row.Manufacturer,
                                            'Model': row["Model"],
                                            'Memory': row.Memory,
                                            'Final HS price': recommended_HS_price_for_PRP,
                                            'MRC_total': 0,
                                            'Company': "T",
                                            'PRP/Mkt Price': recommended_HS_price_for_PRP,
                                            'Tariff Name': 'PRP',
                                            'GB': 0,
                                            'TCO': recommended_HS_price_for_PRP,
                                            'Ideal MRC': 0,
                                            'Ideal HS price': recommended_HS_price_for_PRP,
                                            'Ideal TCO': recommended_HS_price_for_PRP}, ignore_index=True)
    return df_to_return


def Rogue_two_output():
    refresh = ""
    print("RogueTwo was developped by Diego Perez-Tenessa de Block and is part "
          "of Diego's Industrial Biz and Magic Portfolio.")
    print("All rights reserved.")
    df_map = pd.read_excel("map.xlsx", sheet_name="map")
    df_dashboard = pd.read_excel("Dashboard.xlsx", sheet_name="SA or FMC offers")
    #df_modifications = df_dashboard.loc[(df_dashboard['Carrier'] != "T")].copy()

    while refresh not in ["y", "n"]:
        refresh = input("Refresh info from web (y/n)? ").lower()
        if refresh == "y":
            dfa = refresh_SD()
            dfb = refresh_A1()
            dfc = refresh_T2()
            dff = pd.concat([dfa, dfb, dfc])
            print("All Done!")
        if refresh == "n":
            dff = load_log()
    # store_last_checkpoint(dff)

    dff.sort_values(by=['Company', "Web Model", "Upfront", "Installment", "MRC_total", "Tariff Name",
                        "GB", "Final HS price"], inplace=True)
    dff.drop_duplicates(subset=["Company","Web Model","Upfront", "Installment", "MRC_total", "Tariff Name",
                                "GB","Final HS price"], keep='last', inplace=True)
    updated_map = update_map(dff, df_map)
    print('Building recommendations...')
    df_all = pd.merge(dff, updated_map, on=['Web Model'], how='left')
    df_all.sort_values(by=['Company', 'Manufacturer', 'Model', 'Memory', 'Tariff Name','GB','Final HS price'], inplace=True)
    df_all.drop_duplicates(subset=['Company', 'Manufacturer', 'Model', 'Memory', 'Tariff Name','GB'], keep="last",
                           inplace=True)
    #df_all_modifications = pd.merge(df_all, df_modifications, on=['Tariff Name'], how='left')
    #df_all_modifications['MRC_total'] = df_all_modifications['MRC'] + df_all_modifications['Additional Price']
    df_all['TCO'] = df_all['Final HS price'] + df_all['MRC_total'] * 24
    df_all['Ideal MRC'], df_all['Ideal HS price'], df_all['Ideal TCO'],df_all['PRP/Mkt Price'] = [0, 0, 0, 0]
    df_all.sort_values(
        by=['Manufacturer', 'Model', 'Memory', 'TCO', 'Final HS price', 'Company', 'Tariff Name', 'GB','MRC_total'],
        inplace=True)
    df_final = df_all[['Manufacturer', 'Model', 'Memory',
                                     'Company', 'PRP/Mkt Price', 'Tariff Name', 'GB', 'MRC_total',
                                     'Final HS price',
                                     'TCO', 'Ideal MRC', 'Ideal HS price', 'Ideal TCO']]

    ###RECOMMENDING
    model_list = df_final.copy()
    model_list = model_list[['Manufacturer', 'Model', 'Memory']]
    model_list["Memory"].fillna("INFONA", inplace=True)
    model_list.drop_duplicates(subset=['Manufacturer', 'Model', 'Memory'], inplace=True)
    GB_ranges = df_dashboard.loc[(df_dashboard['Carrier'] == "T")].copy()
    df_recommended_prices = recommend_prices(model_list, df_all, GB_ranges)
    df_prices_PRP = recommend_prices_for_PRP(df_all)
    df_concat = pd.concat([df_final, df_recommended_prices, df_prices_PRP])
    df_concat.drop_duplicates(subset=["Manufacturer","Model","Memory","Tariff Name","GB"], keep='first', inplace=True)
    return df_concat


if __name__ == '__main__':
    output = Rogue_two_output()
    #day, month, year = get_date()
    file_name = 'Recommended prices.xlsx' #_'+str(year)+str(month)+str(day)+'.xlsx'
    save_and_show_in_excel(file_name, output)
