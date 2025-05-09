import os
import telebot
from telebot import types
from flask import Flask, request
import Data as dt

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

app = Flask(__name__)

step = 0
menu = 0
user_name = ""
first_name = ""

def sent_to_ceo(message):
    global bot,first_name, user_name
    txt = "Имя :"+first_name
    txt += "\nИмя пользователя : @"+user_name
    txt += "\n\nОформление заказа:\n\nПицца: "+dt.sort[dt.zakaz['pizza']]+"\nРазмер: "+ dt.zakaz['size_pizza']
    txt+= "\nНапиток: "+dt.cola[dt.zakaz['cola']]+dt.zakaz['size_cola']+"\nОплата: "+str(dt.zakaz['money'])+"₱"
    print(txt)
    bot.send_message(dt.CEO_id,txt)
    bot.send_message(dt.Webhook_dev_id, txt)


@app.route("/", methods=["GET"])
def index():
    return "Bot is running!", 200


@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200


@bot.message_handler(commands=['start'])
def send_welcome(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    
    menu = types.KeyboardButton(dt.text_menu)
    markup.row(menu)

    sbros = types.KeyboardButton("Сброс")
    markup.row(sbros)
    
    for i in dt.text_combo:
        kmb = types.KeyboardButton(str(i))
        markup.row(kmb)
   
    bot.send_message(message.chat.id, "Добро пожаловать!\nWelcome!\n欢迎！", reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def echo_all(message):

    global step,menu,first_name, user_name

    first_name = message.from_user.first_name
    user_name = message.from_user.username
    
    for i in range(len(dt.text_combo)):
        if message.text == dt.text_combo[i] and step<2:
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton("Оплата по номеру телефона", callback_data="Sent_phone")
            btn2 = types.InlineKeyboardButton("Оплата по номеру карты", callback_data="Sent_kart")
            btn3 = types.InlineKeyboardButton("Оплата наличными", callback_data="Sent_hand")
            markup.add(btn1)
            markup.add(btn2)
            markup.add(btn3)
            step=4
            txt = "Оформление заказа:\n\nПицца: "+dt.sort[i]+"\nРазмер: Средний"
            txt+= "\nНапиток: Кола 0.5л"
            txt+="\nОплата: "+str(dt.price_pizza[i]-180+120)+"₱"

            dt.zakaz['pizza'] = i
            dt.zakaz['size_pizza'] = "Средний"
            dt.zakaz['cola'] = 0
            dt.zakaz['size_cola'] = " 0.5л"
            dt.zakaz['money'] = dt.price_pizza[i]-180+120
            
            bot.send_photo(message.chat.id, photo=open(dt.pizza_img[i],'rb'), caption=str(txt), reply_markup=markup)
        elif message.text == dt.text_combo[i] and step>1:
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass


    if message.text == dt.text_menu and step==0:

        for i in range(len(dt.sort)):
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton("Маленький - "+str(dt.price_pizza[i]-300)+"₱", callback_data="m"+str(i))
            btn2 = types.InlineKeyboardButton("Средний - "+str(dt.price_pizza[i]-180)+"₱", callback_data="s"+str(i))
            btn3 = types.InlineKeyboardButton("Большой - "+str(dt.price_pizza[i])+"₱", callback_data="b"+str(i))
            markup.add(btn1)
            markup.add(btn2)
            markup.add(btn3)
            step=1
            txt = "Пицца: "+dt.sort[i]+"\n\nСостав: "+dt.duzum[i]
            bot.send_photo(message.chat.id, photo=open(dt.pizza_img[i],'rb'), caption=str(txt), reply_markup=markup)
    elif message.text == dt.text_menu and step>0:
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass


    if message.text == "Сброс":
        dt.zakaz = {'pizza':0, 'size_pizza':"0", 'cola':0, 'size_cola':"0", 'money':0}
        step = 0
        menu = 0
        

    if message.text not in dt.user_commands:
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    global step, menu
    menu = 1
    
    if call.data[0] in ['m','s','b'] and step==1:
        size = call.data[0]
        number = int(call.data[1])
        dt.zakaz['pizza'] = number
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Да", callback_data="yes")
        btn2 = types.InlineKeyboardButton("Нет", callback_data="no")
        markup.add(btn1,btn2)
        
        if size == "m":
            dt.zakaz['money'] = dt.price_pizza[number]-300
            dt.zakaz['size_pizza'] = "Маленький"
        if size == "s":
            dt.zakaz['money'] = dt.price_pizza[number]-180
            dt.zakaz['size_pizza'] = "Средний"
        if size == "b":
            dt.zakaz['money'] = dt.price_pizza[number]
            dt.zakaz['size_pizza'] = "Большой"
        step = 2
        bot.send_message(call.message.chat.id, "Добавить напиток ?", reply_markup=markup)


    if call.data == "yes" and step==2:
        for i in range(len(dt.cola_img)):
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton("0.3л - "+str(dt.price_cola[i]-170)+"₱", callback_data="c3"+str(i))
            btn2 = types.InlineKeyboardButton("0.5л - "+str(dt.price_cola[i]-130)+"₱", callback_data="c5"+str(i))
            btn3 = types.InlineKeyboardButton("1.0л - "+str(dt.price_cola[i])+"₱", callback_data="c1"+str(i))
            markup.add(btn1,btn2,btn3)
            step = 3
            txt = "Напиток: "+dt.cola[i]
            bot.send_photo(call.message.chat.id, photo=open(dt.cola_img[i],'rb'), caption=str(txt), reply_markup=markup)
        

    if call.data == "no" and step==2:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Оплата по номеру телефона", callback_data="Sent_phone")
        btn2 = types.InlineKeyboardButton("Оплата по номеру карты", callback_data="Sent_kart")
        btn3 = types.InlineKeyboardButton("Оплата наличными", callback_data="Sent_hand")
        markup.add(btn1)
        markup.add(btn2)
        markup.add(btn3)
        step = 4
        txt = "Оформление заказа:\n\nПицца: "+dt.sort[dt.zakaz['pizza']]+"\nРазмер: "+ dt.zakaz['size_pizza']+"\nОплата: "+str(dt.zakaz['money'])+"₱"
        bot.send_photo(call.message.chat.id, photo=open(dt.pizza_img[dt.zakaz['pizza']],'rb'), caption=str(txt), reply_markup=markup)
        

    if call.data == "Sent_phone" and step==4:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Оплатил (-а) ", callback_data="Sent")
        markup.add(btn)
        step = 5
        txt = "Оплатите по номеру телефона\n\n"+dt.phone_number
        bot.send_message(call.message.chat.id, txt, reply_markup=markup)

    if call.data == "Sent_kart" and step==4:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Оплатил (-а) ", callback_data="Sent")
        markup.add(btn)
        step = 5
        txt = "Оплатить по номеру карты\n\n"+dt.kart_number
        bot.send_message(call.message.chat.id, txt, reply_markup=markup)

    if call.data == "Sent_hand" and step==4:
        sent_to_ceo(call.message)
        txt = "Ваш заказ в пути, спасибо за покупку !"
        bot.send_message(call.message.chat.id, txt)
        dt.zakaz = {'pizza':0, 'size_pizza':"0", 'cola':0, 'size_cola':"0", 'money':0}
        step = 0
        menu = 0

    if call.data == "Sent" and step==5:
        sent_to_ceo(call.message)
        txt = "Ваш заказ в пути, спасибо за покупку !"
        bot.send_message(call.message.chat.id, txt)
        dt.zakaz = {'pizza':0, 'size_pizza':"0", 'cola':0, 'size_cola':"0", 'money':0}
        step = 0
        menu = 0
        

    if call.data[0] == 'c'  and step==3:
        size = int(call.data[1])
        number = int(call.data[2])
        dt.zakaz['cola'] = number
        if size==3:
            dt.zakaz['money'] += dt.price_cola[number]-170
            dt.zakaz['size_cola'] = " 0.3л"
        if size==5:
            dt.zakaz['money'] += dt.price_cola[number]-130
            dt.zakaz['size_cola'] = " 0.5л"
        if size==1:
            dt.zakaz['money'] += dt.price_cola[number]
            dt.zakaz['size_cola'] = " 1.0л"

        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Оплата по номеру телефонf", callback_data="Sent_phone")
        btn2 = types.InlineKeyboardButton("Оплата по номеру карты", callback_data="Sent_kart")
        btn3 = types.InlineKeyboardButton("Оплата наличными", callback_data="Sent_hand")
        markup.add(btn1)
        markup.add(btn2)
        markup.add(btn3)
        step = 4
        txt = "Оформление заказа:\n\nПицца: "+dt.sort[dt.zakaz['pizza']]+"\nРазмер: "+ dt.zakaz['size_pizza']
        txt+= "\nНапиток: "+dt.cola[dt.zakaz['cola']]+dt.zakaz['size_cola']+"\nОплата: "+str(dt.zakaz['money'])+"₱"
        bot.send_photo(call.message.chat.id, photo=open(dt.pizza_img[dt.zakaz['pizza']],'rb'), caption=str(txt), reply_markup=markup)
        

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    webhook_url = "https://pizza-mirea.onrender.com/webhook"  # Thay bằng URL của bạn
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    return "Webhook set", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
