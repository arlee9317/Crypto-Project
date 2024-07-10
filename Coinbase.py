from coinbase.rest import RESTClient
from json import dumps
import APIKeys
import EmailInfo
import Stocks
import numpy as np
import time
import threading
import smtplib
from email.mime.text import MIMEText

#delcare variables
dict = []
FirstScan = True #flag to get the program running initially
IdScanDone = False
Minutes = 5 #how long you want the timer to trigger crypto info
PercPriceDif = 3.3 # % change for Crypto Price
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
def calc(calcdict):

   print("Calc started")
   for j in range(len(calcdict)):
      
      if calcdict[j]["Price"][1] or calcdict[j]["Volume"][1] != 0:
        #Price/Volume change for 5 minutes
        DeltaPrice5 = round((calcdict[j]["Price"][0] - calcdict[j]["Price"][1]) / calcdict[j]["Price"][1] * 100, 2)
        DeltaVol5 = round((calcdict[j]["Volume"][0] - calcdict[j]["Volume"][1]) / calcdict[j]["Volume"][1] * 100, 2)
      else:
        DeltaPrice5 = 0.0
        DeltaVol5 = 0.0
      
      if calcdict[j]["Price"][2] or calcdict[j]["Volume"][2] != 0:
        #Price/Volume change for 10 minutes
        DeltaPrice10 = round((calcdict[j]["Price"][0] - calcdict[j]["Price"][2]) / calcdict[j]["Price"][2] * 100, 2)
        DeltaVol10 = round((calcdict[j]["Volume"][0] - calcdict[j]["Volume"][2]) / calcdict[j]["Volume"][2] * 100, 2)
      else:
        DeltaPrice10 = 0.0
        DeltaVol10 = 0.0

      if calcdict[j]["Price"][3] or calcdict[j]["Volume"][3] != 0:
        #Price/Volume change for 15 minutes
        DeltaPrice15 = round((calcdict[j]["Price"][0] - calcdict[j]["Price"][3]) / calcdict[j]["Price"][3] * 100, 2)
        DeltaVol15 = round((calcdict[j]["Volume"][0] - calcdict[j]["Volume"][3]) / calcdict[j]["Volume"][3] * 100, 2)
      else:
        DeltaPrice15 = 0.0
        DeltaVol15 = 0.0

      if calcdict[j]["Price"][4] or calcdict[j]["Volume"][4] != 0:
        #Price/Volume change for 20 minutes
        DeltaPrice20 = round((calcdict[j]["Price"][0] - calcdict[j]["Price"][4]) / calcdict[j]["Price"][4] * 100, 2)
        DeltaVol20 = round((calcdict[j]["Volume"][0] - calcdict[j]["Volume"][4]) / calcdict[j]["Volume"][4] * 100, 2)
      else:
        DeltaPrice20 = 0.0
        DeltaVol20 = 0.0

      if calcdict[j]["Price"][5] and calcdict[j]["Volume"][5] != 0:
        #Price/Volume change for 25 minutes
        DeltaPrice25 = round((calcdict[j]["Price"][0] - calcdict[j]["Price"][5]) / calcdict[j]["Price"][5] * 100, 2)
        DeltaVol25 = round((calcdict[j]["Volume"][0] - calcdict[j]["Volume"][5]) / calcdict[j]["Volume"][5] * 100, 2)
      else:
        DeltaPrice25 = 0.0
        DeltaVol25 = 0.0

      if calcdict[j]["Price"][6] and calcdict[j]["Volume"][6] != 0:
        #Price/Volume change for 30 minutes
        DeltaPrice30 = round((calcdict[j]["Price"][0] - calcdict[j]["Price"][6]) / calcdict[j]["Price"][6] * 100, 2)
        DeltaVol30 = round((calcdict[j]["Volume"][0] - calcdict[j]["Volume"][6]) / calcdict[j]["Volume"][6] * 100, 2)
      else:
        DeltaPrice30 = 0.0
        DeltaVol30 = 0.0

      #print(f"{DeltaPrice5}, {DeltaVol5}")
      # if any price is greater than threshold send data to email
      if (DeltaPrice5 or DeltaPrice10 or DeltaPrice15 or DeltaPrice20 or DeltaPrice25 or DeltaPrice30) >= PercPriceDif:
        subject = f"{calcdict[j]["CryptoName"]+ " is trending"}"
        body = f"5 Min % Change Price: {DeltaPrice5}, Volume: {DeltaVol5}\n 10 Min % Change Price: {DeltaPrice10}, Volume: {DeltaVol10}\n 15 Min % Change Price: {DeltaPrice15}, Volume: {DeltaVol15}\n 20 Min % Change Price: {DeltaPrice20}, Volume: {DeltaVol20}\n 25 Min % Change Price: {DeltaPrice25}, Volume: {DeltaVol25}\n 30 Min % Change Price: {DeltaPrice30}, Volume: {DeltaVol30}"
        sender = EmailInfo.Sender
        recipients = EmailInfo.Recipients
        password = EmailInfo.Password
        print("Email Sent")
        send_email(subject, body, sender, recipients, password)

# Count down timer
def countdown_timer(seconds):
    while seconds > 0:
        time.sleep(1)
        seconds -= 1
    Crypto_data(CryptoArray, True)

# Accessing Cyrpto Data
def Crypto_data(StockArray, FinishedScan):
    Start = time.perf_counter()
    t1 = threading.Thread(target=countdown_timer, args=(Minutes * 60,))
    t1.start()
    for i in range(len(StockArray)):
      
      product = client.get_product(f"{StockArray[i]}-USD") #Getting Crypto info from Coinbase
      if FinishedScan == False:
        Crypto_id = str(product['product_id']) #getting the name of the Crypto currency
        Crypto_Info = {'CryptoName' : Crypto_id, 'Price': [0, 0, 0, 0, 0, 0, 0], 'Volume': [0, 0, 0, 0, 0, 0, 0]} #adding info into a dictionary
        dict.append(Crypto_Info) #adding dictionary to a list

      # choosing which items I want from Crpto Data
      CryptoPrice = float(product['price']) # convert string from json into float
      dict[i]["Price"].insert(0,CryptoPrice)

      CryptoVol = float(product['volume_24h']) # convert string from json into float
      dict[i]["Volume"].insert(0, CryptoVol)

      time.sleep(0.75)
      # After gone through entire Crypto list turn this bit on 
      if i == (len(CryptoArray) - 1):
        FinishedScan = True
      print(f'{dict[i]["CryptoName"]}')
    finish = time.perf_counter()
    print(f'Finished in {round(finish-Start, 2)} second(s)')  
    calc(dict) # calling calc function

#-------------------------------------- Main Code -----------------------------------------------
Crypto_data(CryptoArray, IdScanDone)
  
#print(f"{dict[i]["Volume"][6]}")
   

  
  
 
  

