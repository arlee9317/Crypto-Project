from coinbase.rest import RESTClient
from json import dumps
import APIKeys
import EmailInfo
import Stocks
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import time
import threading
import smtplib
from email.mime.text import MIMEText

#delcare variables
dict = []
TimeArray=[0,5,10,15,20,25,30]
FirstScanDone = True
FinishedScan = False
Minutes = 5 #how long you want the timer to trigger crypto info
PercPriceDif = 1.2 # % change for Crypto Price
PercVolDif = 3.3 # % change for Crypto Volume

# API keys to access coinbase
api_key = APIKeys.APIKey 
api_secret = APIKeys.APISecret
client = RESTClient(api_key=api_key, api_secret=api_secret)

#create array of Crypto Currencies using only USD
CryptoArray = np.array(Stocks.Stocklist)

#--------------------------------  declaring functions -------------------------------

# Sending email function
def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())

# Caculations from data gotten from Coinbase
def calc():
    #CalcDone = False #flag to initialize as false at beginning of function
    if dict[i]["Price"][1] or dict[i]["Volume"][1] != 0:
        #Price/Volume change for 5 minutes
        DeltaPrice5 = round((dict[i]["Price"][0] - dict[i]["Price"][1]) / dict[i]["Price"][1] * 100, 2)
        DeltaVol5 = round((dict[i]["Volume"][0] - dict[i]["Volume"][1]) / dict[i]["Volume"][1] * 100, 2)
    else:
        DeltaPrice5 = 0.0
        DeltaVol5 = 0.0
      
    if dict[i]["Price"][2] or dict[i]["Volume"][2] != 0:
        #Price/Volume change for 10 minutes
        DeltaPrice10 = round((dict[i]["Price"][0] - dict[i]["Price"][2]) / dict[i]["Price"][2] * 100, 2)
        DeltaVol10 = round((dict[i]["Volume"][0] - dict[i]["Volume"][2]) / dict[i]["Volume"][2] * 100, 2)
    else:
        DeltaPrice10 = 0.0
        DeltaVol10 = 0.0

    if dict[i]["Price"][3] or dict[i]["Volume"][3] != 0:
        #Price/Volume change for 15 minutes
        DeltaPrice15 = round((dict[i]["Price"][0] - dict[i]["Price"][3]) / dict[i]["Price"][3] * 100, 2)
        DeltaVol15 = round((dict[i]["Volume"][0] - dict[i]["Volume"][3]) / dict[i]["Volume"][3] * 100, 2)
    else:
        DeltaPrice15 = 0.0
        DeltaVol15 = 0.0

    if dict[i]["Price"][4] or dict[i]["Volume"][4] != 0:
        #Price/Volume change for 20 minutes
        DeltaPrice20 = round((dict[i]["Price"][0] - dict[i]["Price"][4]) / dict[i]["Price"][4] * 100, 2)
        DeltaVol20 = round((dict[i]["Volume"][0] - dict[i]["Volume"][4]) / dict[i]["Volume"][4] * 100, 2)
    else:
        DeltaPrice20 = 0.0
        DeltaVol20 = 0.0

    if dict[i]["Price"][5] and dict[i]["Volume"][5] != 0:
        #Price/Volume change for 25 minutes
        DeltaPrice25 = round((dict[i]["Price"][0] - dict[i]["Price"][5]) / dict[i]["Price"][5] * 100, 2)
        DeltaVol25 = round((dict[i]["Volume"][0] - dict[i]["Volume"][5]) / dict[i]["Volume"][5] * 100, 2)
    else:
        DeltaPrice25 = 0.0
        DeltaVol25 = 0.0

    if dict[i]["Price"][6] and dict[i]["Volume"][6] != 0:
        #Price/Volume change for 30 minutes
        DeltaPrice30 = round((dict[i]["Price"][0] - dict[i]["Price"][6]) / dict[i]["Price"][6] * 100, 2)
        DeltaVol30 = round((dict[i]["Volume"][0] - dict[i]["Volume"][6]) / dict[i]["Volume"][6] * 100, 2)
    else:
        DeltaPrice30 = 0.0
        DeltaVol30 = 0.0
    
    #Regression analysis for Price
    X_axis = np.array(TimeArray).reshape((-1, 1))
    X_Poly = PolynomialFeatures(degree=2, include_bias=False)
    X_PolyVal = X_Poly.fit_transform(X_axis)

    Y_axisP = np.array(dict[i]["Price"])
    ModelPrice = LinearRegression()
    ModelPrice.fit(X_PolyVal, Y_axisP)

    #Regression analysis for Volume
    Y_axisV = np.array(dict[i]["Volume"])
    ModelVol = LinearRegression()
    ModelVol.fit(X_PolyVal, Y_axisV)

    #print(f"Slope Price:{ModelPrice.coef_}, Slope Volume: {ModelVol.coef_}")
    # if any price is greater than threshold send data to email
    if (DeltaPrice5 or DeltaPrice10 or DeltaPrice15 or DeltaPrice20 or DeltaPrice25 or DeltaPrice30) >= PercPriceDif:
        subject = f"{dict[i]["CryptoName"]+ " is trending"}"
        body = f"D1 Price: {DeltaPrice5}%, Volume: {DeltaVol5}%\n D2 Price: {DeltaPrice10}%, Volume: {DeltaVol10}%\n D3 Price: {DeltaPrice15}%, Volume: {DeltaVol15}%\n D4 Price: {DeltaPrice20}%, Volume: {DeltaVol20}%\n D5 Price: {DeltaPrice25}%, Volume: {DeltaVol25}%\n D6 Price: {DeltaPrice30}%, Volume: {DeltaVol30}%\n Slope Price: {ModelPrice.coef_}, Slope Volume: {ModelVol.coef_}\n"
        sender = EmailInfo.Sender
        recipients = EmailInfo.Recipients
        password = EmailInfo.Password
        print("Email Sent------------------------")
        send_email(subject, body, sender, recipients, password)

#----------------------------------------- Main Code --------------------------------------

while True:
    Start = time.perf_counter()
    
    for i in range(len(CryptoArray)):
        
        product = client.get_product(f"{CryptoArray[i]}-USD") #Getting Crypto info from Coinbase
        if FinishedScan == False:
            Crypto_id = str(product['product_id']) #getting the name of the Crypto currency
            Crypto_Info = {'CryptoName' : Crypto_id, 'Price': [0, 0, 0, 0, 0, 0, 0], 'Volume': [0, 0, 0, 0, 0, 0, 0]} #adding info into a dictionary
            dict.append(Crypto_Info) #adding dictionary to a list
        print(f'{dict[i]["CryptoName"]}')
        # choosing which items I want from Crpto Data
        CryptoPrice = float(product['price']) # convert string from json into float
        dict[i]["Price"].insert(0,CryptoPrice)
        dict[i]["Price"].pop(7)

        CryptoVol = float(product['volume_24h']) # convert string from json into float
        dict[i]["Volume"].insert(0, CryptoVol)
        dict[i]["Volume"].pop(7)

        t1 = threading.Thread(target=calc)
        t1.start()
        time.sleep(0.8)
        # After gone through entire Crypto list turn this bit on 
        if i == (len(CryptoArray) - 1):
            FinishedScan = True
        t1.join()    
    finish = time.perf_counter()
    print(f'Finished in {round(finish-Start, 2)} second(s)')
    time.sleep(75)  
    #calc() # calling calc function