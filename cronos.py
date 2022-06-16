from asyncore import dispatcher
from telegram import *
from telegram.ext import *
from requests import *
from datetime import datetime
import gspread
import requests
import os
from oauth2client.service_account import ServiceAccountCredentials

credenciales = os.environ['CREDS']
updater = Updater(token=os.environ['TELEGRAM'])
alert_telegram_bot_id = os.environ['TELEGRAMBOTID']
alert_telegram_channel_id = os.environ['TELEGRAMCHANNELID']

dispatcher = updater.dispatcher
global_day_cell_row = "0"
sheet = "Liquidacion de Sueldos"

class horario:
    def __init__(self,user, dia, entrada, comida_entrada, comida_salida, salida ):
        self.user = user
        self.dia = dia
        self.entrada = entrada
        self.comida_entrada = comida_entrada
        self.comida_salida = comida_salida
        self.salida = salida
nuevo_dia = horario(1,1,1,1,1,1)


def telegram_message(message):
    headers_telegram = {"Content-Type": "application/x-www-form-urlencoded"}
    endpoint_telegram = "https://api.telegram.org/"+alert_telegram_bot_id+"/sendMessage"
    mensaje_telegram = {"chat_id": alert_telegram_channel_id, "text": "Problemas en RIG"}
    mensaje_telegram["text"] = message
    response = requests.post(endpoint_telegram, headers=headers_telegram, data=mensaje_telegram).json()
    return response


def login(user):
    if (user == "camilapalacin"):
        nuevo_dia.user = "Camila Palacin - 0720405488000037379704"
    if(user == "pupi_zanetti"):
        nuevo_dia.user = "Pagos Pupi - tomas.s.ghi"
    else:
        pass
        #Lo de pupi

def sanitize_string(string):
    a,b = 'áéíóúüñÁÉÍÓÚÜÑ','aeiouunAEIOUUN'
    trans = string.maketrans(a,b)
    return string.translate(trans)

def getCell(sheet, worksheet, string):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(credenciales, scope)
    client = gspread.authorize(creds)
    work_sheet = client.open(sheet)
    sheet_instance = work_sheet.worksheet(worksheet)
    cell = sheet_instance.find(string)
    return (cell.row, cell.col)

def updateCell(documento, hoja, cell, data):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(credenciales, scope)
    client = gspread.authorize(creds)
    sheet = client.open(documento)
    sheet_instance = sheet.worksheet(hoja)
    sheet_instance.update(cell, data,value_input_option="USER_ENTERED")



def getCellByRow(sheet, worksheet, row):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(credenciales, scope)
    client = gspread.authorize(creds)
    work_sheet = client.open(sheet)
    sheet_instance = work_sheet.worksheet(worksheet)
    val = sheet_instance.acell(row).value
    return (val)



def check_days(string, compare,day_cell_row):
    if(string == compare):
        return day_cell_row
    else:
        send_message("Error al leer!", update,context)
        return False


def get_day_cell_by_string(string, sheet, cbu):
    day_cell_row = 0
    cbu = nuevo_dia.user
    print(string)
    print(type(string))
    month_cell_row, month_cell_column = getCell(sheet, cbu ,string.lower().split(None,4)[4]) #BUSCO LA CELDA DEL MES DEL AÑO EL CUAL ESCRIBIO EN EL GRUPO DE TELEGRAM LO DEVUELVO EN 2 VARIABLES
    day_number = int(string.lower().split(None,4)[2])
    day_cell_row = int(day_number) + int(month_cell_row)
    day_name = str(string.lower().split(None,4)[1])
    excel_day_name = getCellByRow(sheet, cbu,"A"+str(day_cell_row)).lower().split(None,4)[0]
    return excel_day_name,day_name,day_cell_row



def startCommand(update: Update, context: CallbackContext):
    print(update.effective_chat)
    print(update.effective_chat["username"])
    login(update.effective_chat["username"])
    welcome_file = open('/app/welcome.txt','r')
    welcome_message = welcome_file.read()
    nuevo_dia.dia = 0
    context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)


def diaCommand(update: Update, context: CallbackContext):
    print(update.effective_chat)
    login(update.effective_chat["username"])
    string = str(sanitize_string(update.message.text))
    excel_day_name,day_name,day_cell_row = get_day_cell_by_string(string, sheet,cbu="")
    day_cell_row = check_days(excel_day_name,day_name,day_cell_row)
    if(day_cell_row):
        nuevo_dia.dia = day_cell_row
        print("Dia cargado correctamente: "+str(day_cell_row))


def entradaCommand(update: Update, context: CallbackContext):
    print(update.effective_chat)
    string = update.message.text
    data = string.lower().split(None,4)[1]
    print(data)
    try:
        updateCell(sheet, nuevo_dia.user, "B"+str(nuevo_dia.dia), data)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Cargada entrada a las "+str(data))
        telegram_message("Comienzo del dia: "+str(data)+"   - "+str(update.effective_chat["username"]))
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No se registro correctamente el dia. Comunicarse con GUIDO !!!! ")
        telegram_message("Error cargando comienzo: "+str(data)+"   - "+str(update.effective_chat["username"]))


def comidaCommand(update: Update, context: CallbackContext):
    print(update.effective_chat)
    string = update.message.text
    data = string.lower().split(None,4)[1]
    print(data)
    try:
        updateCell(sheet, nuevo_dia.user, "C"+str(nuevo_dia.dia), data)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Cargada comida a las "+str(data))
        telegram_message("Comienzo Comida: "+str(data)+"   - "+str(update.effective_chat["username"]))
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No se registro correctamente el dia. Comunicarse con GUIDO !!!! ")
        telegram_message("Error cargando comida: "+str(data)+"   - "+str(update.effective_chat["username"]))

def finComidaCommand(update: Update, context: CallbackContext):
    print(update.effective_chat)
    string = update.message.text
    data = string.lower().split(None,4)[1]
    print(data)
    try:
        updateCell(sheet, nuevo_dia.user, "D"+str(nuevo_dia.dia), data)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Cargada fin comida a las "+str(data))
        telegram_message("Fin Comida: "+str(data)+"   - "+str(update.effective_chat["username"]))
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No se registro correctamente el dia. Comunicarse con GUIDO !!!! ")
        telegram_message("Error cargando: "+str(data)+"   - "+str(update.effective_chat["username"]))


def finCommand(update: Update, context: CallbackContext):
    print(update.effective_chat)
    string = update.message.text
    data = string.lower().split(None,4)[1]
    print(data)
    try:
        updateCell(sheet, nuevo_dia.user, "E"+str(nuevo_dia.dia), data)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Cargado fin del dia a las "+str(data)+"\n Fiuj! ")
        telegram_message("Fin dia: "+str(data)+"   - "+str(update.effective_chat["username"]))
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No se registro correctamente el dia. Comunicarse con GUIDO !!!! ")
        telegram_message("Error fin del dia: "+str(data)+"   - "+str(update.effective_chat["username"]))

def kilometrosCommand(update: Update, context: CallbackContext):
    print(update.effective_chat)
    string = update.message.text
    data = string.lower().split(None,4)[1]
    print(data)
    try:
        updateCell(sheet, nuevo_dia.user, "K"+str(nuevo_dia.dia), data)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Cargada entrada a las "+str(data))
        telegram_message("Cargados Kilometros: "+str(data)+"   - "+str(update.effective_chat["username"]))
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No se registro correctamente el dia. Comunicarse con GUIDO !!!! ")
        telegram_message("No se registro Kilometros: "+str(data)+"   - "+str(update.effective_chat["username"]))


def send_message(response, update,context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)

dispatcher.add_handler(CommandHandler("start", startCommand))
dispatcher.add_handler(CommandHandler("Dia", diaCommand))
dispatcher.add_handler(CommandHandler("Entrada", entradaCommand))
dispatcher.add_handler(CommandHandler("Comida", comidaCommand))
dispatcher.add_handler(CommandHandler("Fin_Comida", finComidaCommand))
dispatcher.add_handler(CommandHandler("Fin", finCommand))
dispatcher.add_handler(CommandHandler("Kilometros", kilometrosCommand))


updater.start_polling()
