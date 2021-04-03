#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]

#https://github.com/poolitzer/ReportBot bot report 
# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets
import logging

import traceback
import html
import json
import logging
import random

from telegram import ChatAction, InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity, ParseMode, Update, error, ReplyKeyboardMarkup, ReplyKeyboardRemove 
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from telegram.ext.dispatcher import run_async
from manager import strings, api
from typing import Dict
from functools import wraps

#loadenv
import os
from dotenv import load_dotenv
from pathlib import Path  # Python 3.6+ only
env_path = Path('./manager/.env') 
load_dotenv(dotenv_path=env_path)

SECRET_KEY = os.getenv("TELEGRAM_TOKEN")
ADMIN = os.getenv("ADM")
GRUP = os.getenv("CAC_BRASIL")

#change PORT TO HEROKU
PORT = int(os.environ.get('PORT', '443'))


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__) 

LOCATION, END, FIRST = range(3)

keyboard1 = [["DADOS DO BRASIL", "DADOS DE SUA CIDADE"], ["TUTORIAL"]]
markup = ReplyKeyboardMarkup(keyboard1, one_time_keyboard=True)

def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context,  *args, **kwargs)
        return command_func
    
    return decorator

send_typing_action = send_action(ChatAction.TYPING)

#Start options
def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    reply_markup=markup 
    update.message.reply_text("Olá " + update.message.from_user.first_name + strings.StartText, parse_mode= ParseMode.MARKDOWN) 
    update.message.reply_text('*DE QUAL REGIÃO VOCÊ DEDEJA OBTER INFORMAÇÕES, USE O TUTORIAL PARA USAR O BOT*' , parse_mode= ParseMode.MARKDOWN, reply_markup=markup ) 
    return FIRST


def brazil_data(update: Update, context: CallbackContext):
    #get randomize msg in trings.randon_suport_msg
    rand_msg = random.choice(strings.randon_suport_msg)

    text = update.message.text
    if text == "DADOS DO BRASIL":
        update.message.reply_text(api.get_from_brazil() +  rand_msg , parse_mode= ParseMode.MARKDOWN, reply_markup = ReplyKeyboardRemove())  
        return ConversationHandler.END
    elif text == "DADOS DE SUA CIDADE":
        update.message.reply_text(f' {update.message.from_user.first_name} me envie a sua localização para obter da sua região. caso não saiba fazer isso use a finção /start e selecione tutorial',parse_mode= ParseMode.MARKDOWN ,  reply_markup = ReplyKeyboardRemove())
        return LOCATION
    elif text == "TUTORIAL":
        update.message.reply_text('Tutorial https://youtu.be/KxJigCgTboQ',reply_markup = ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        return ConversationHandler.END



#enter location conversation
def location(update: Update, context: CallbackContext):
    user = update.message.from_user
    update.message.reply_text(f' {user.first_name} me envie a sua localização para obter da sua região. caso não saiba fazer isso use a finção /start e selecione tutorial')
    return LOCATION

def get_location(update:Update, context: CallbackContext):
    #get randomize msg in trings.randon_suport_msg
    rand_msg = random.choice(strings.randon_suport_msg)

    user = update.message.from_user
    user_location = update.message.location
    update.message.reply_text(api.city_retun(f'{ user_location.latitude}, { user_location.longitude}') + rand_msg, parse_mode = ParseMode.MARKDOWN)
    return ConversationHandler.END


#enter patterns
def donate(update: Update, context: CallbackContext):
     keyboard = [
        [
            InlineKeyboardButton("CONTATO", url="https://t.me/AngeloAbrita"),
            InlineKeyboardButton("DOAR PAYPAL", url ='https://www.paypal.com/donate/?cmd=_s-xclick&hosted_button_id=NTVK3A8XG54W2&source=url'),
        ]
       
    ]

     reply_markup = InlineKeyboardMarkup(keyboard)
     update.message.reply_text(strings.donate_text.format(update.message.from_user.first_name), parse_mode = ParseMode.MARKDOWN, reply_markup=reply_markup)

#enter about
def about(update: Update, context: CallbackContext):
     keyboard = [
        [
            InlineKeyboardButton("FACEBOOK", url="https://www.facebook.com/agtastudios/"),
            InlineKeyboardButton("TWITTER", url ='https://twitter.com/agtastudios'),
        ],
        [
            InlineKeyboardButton("CONTATO", url="https://t.me/AngeloAbrita"),
        ],
         [
            InlineKeyboardButton("DOAR", url="https://www.paypal.com/donate/?cmd=_s-xclick&hosted_button_id=NTVK3A8XG54W2&source=url"),
                   
        ]
       
    ]

     reply_markup = InlineKeyboardMarkup(keyboard)
     update.message.reply_text(strings.about_text.format(update.message.from_user.first_name), parse_mode = ParseMode.MARKDOWN, reply_markup=reply_markup)

def reply_mentions(update:Update, context: CallbackContext):
    text = update.message.text
    user = update.message.from_user
    update.message.reply_text(f'{user.first_name}  Minhas respostas são limitadas, use o comando /start para saber oque posso fazer' )


def cancel(update:Update, context: CallbackContext):
    update.message.reply_text("Okay caso queira mais info use o comando/start", reply_markup = ReplyKeyboardRemove())
    return ConversationHandler.END

################ERRO HANDLER##################
def error_handler(update: Update, context: CallbackContext):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    # Finally, send the message
    context.bot.send_message(chat_id=ADMIN, text=message, parse_mode=ParseMode.HTML)



def main():
    """Start the bot."""
   
   # Secretkey is the bot token in evn
    updater = Updater(SECRET_KEY, use_context=True)
 


    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_start = ConversationHandler(
        entry_points= [CommandHandler("start",start)],
        states={

            FIRST: [
                MessageHandler( Filters.text & ~(Filters.command ), brazil_data),
            ],    
            LOCATION: [ 
                
                MessageHandler(Filters.location, get_location),

            ],
            ConversationHandler.TIMEOUT: [MessageHandler(Filters.text | Filters.command, cancel)],


         },
          fallbacks=[CommandHandler('cancelar', cancel)],
          conversation_timeout=180
    )

    conv_localization= ConversationHandler(
        entry_points= [CommandHandler("situacao",location)],
        states={

            LOCATION: [ 
                
                MessageHandler(Filters.location, get_location),

            ],
             ConversationHandler.TIMEOUT: [MessageHandler(Filters.text | Filters.command, cancel)],


         },
          fallbacks=[CommandHandler('cancelar', cancel)],
          conversation_timeout=180
    )

    
  
    #conversation hendler
    dispatcher.add_handler(conv_localization)
    dispatcher.add_handler(conv_start)
    ##### handler##########
    #dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("doacao",donate))
    dispatcher.add_handler(CommandHandler("sobre",about))
     # ...and the error handler
    dispatcher.add_error_handler(error_handler)
    #filter mention @cacazinhobot
    dispatcher.add_handler( MessageHandler(Filters.entity(MessageEntity.MENTION) , reply_mentions))


    # Start the Bot
     #hook to heroku
    # updater.start_webhook(listen="0.0.0.0",
    #                       port=PORT,
    #                       url_path=SECRET_KEY)
 
    # updater.bot.set_webhook('https://<YOUR_HEROKU_APP_NAME>.herokuapp.com/' + SECRET_KEY)
    #use for localhost
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
