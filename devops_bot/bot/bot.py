import psycopg2
from psycopg2 import Error
import logging 
import re
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import paramiko
import os

from dotenv import load_dotenv
load_dotenv()

userDB=os.getenv('DB_USER')
passwordDB=os.getenv('DB_PASSWORD')
hostDB=os.getenv('DB_HOST')
portDB=os.getenv('DB_PORT')
databaseDB=os.getenv('DB_DATABASE')

connection = psycopg2.connect(        
    user=userDB,
    password=passwordDB,
    host=hostDB,
    port=portDB,
    database=databaseDB
)
cursor = connection.cursor()

def get_emails(update: Update, context):
    cursor.execute("SELECT * FROM email;")
    data = cursor.fetchall()
    for row in data:
        update.message.reply_text(row)

def get_phone_numbers(update: Update, context):
    cursor.execute("SELECT * FROM phone_number;")
    data = cursor.fetchall()
    for row in data:
        update.message.reply_text(row)

password1 = os.getenv('RM_PASSWORD')
client = paramiko.SSHClient()
def connect_vm():
    host = os.getenv('RM_HOST')
    port1 = os.getenv('RM_PORT')
    username1 = os.getenv('RM_USER')
    password1 = os.getenv('RM_PASSWORD')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username1, password=password1, port=port1)

TOKEN = os.getenv('TOKEN')

logging.basicConfig(
    filename='logfile.txt', format='% (asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def start (update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Пpивeт, {user.full_name}!')

def findEmail(update: Update, context):
    update.message.reply_text('Bведите текст для поиска еmail-адреса: ')
    return 'find_email'

def findPhoneNumber (update: Update, context):
    update.message.reply_text('Введите текст для поиска номеров: ')
    return 'find_phone_number'

def verifyPassword(update: Update, context): 
    update.message.reply_text('Bведите пароль: ')
    return 'verify_password'

def aptList(update: Update, context):
    update.message.reply_text('all - посмотреть все пaкеты,\
                              \n\'Название пакета\'  - посмотреть информацию о пакете')
    return 'get_apt_list'

def find_email(update: Update, context):
    user_input = update.message.text
    emailNumRegex = re.compile(r"\b[a-zA-Z0-9._%+-]+(?<!\.\.)@[a-zA-Z0-9.-]+(?<!\.)\.[a-zA-Z]{2,}\b")
    emailNumList = emailNumRegex.findall(user_input)
    context.user_data['email'] = emailNumList
    if not emailNumList:
        update.message.reply_text('Email-адреса не были найдены')
        return
    emailNum = ''
    for i in range(len(emailNumList)):
        emailNum += f'{i+1}. {emailNumList[i]}\n' 
    update.message.reply_text('найдены email: '\
                              +'\n'+ emailNum +'\n'\
                                +'записать в базу данных? (y\\n)')
    return 'save email'

def find_phone_number (update: Update, context):
    user_input = update.message.text
    phoneNumRegex = re.compile(r"\+?7[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}|\+?7[ -]?\d{10}|\+?7[ -]?\d{3}[ -]?\d{3}[ -]?\d{4}|8[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}|8[ -]?\d{10}|8[ -]?\d{3}[ -]?\d{3}[ -]?\d{4}")
    phoneNumberList = phoneNumRegex.findall (user_input)
    context.user_data['phone_number'] = phoneNumberList
    if not phoneNumberList:
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END
    phoneNumbers = ''
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n'
    update.message.reply_text('найдены номера: '\
                              +'\n'+ phoneNumbers +'\n'\
                                + 'записать в базу данных? (y\\n)')
    return 'save phone numbers'

def save_email(update: Update, context): 
    email = context.user_data['email'] 
    if update.message.text in ['y','n']: 
        if(update.message.text == 'y'):
            try:
                for x in email:
                    cursor.execute("INSERT INTO email(email) VALUES ('"+str(x)+"');")
                connection.commit()
                update.message.reply_text("Добавление выполнено успешно")
            except (Exception, Error) as error:
                update.message.reply_text("ERROR")
                return ConversationHandler.END
        else:
            return ConversationHandler.END
    else:
        update.message.reply_text("ERROR")
        return ConversationHandler.END
    return ConversationHandler.END


def save_phone_numbers (update: Update, context): 
    phoneNumberList = context.user_data['phone_number'] 
    if update.message.text in ['y','n']: 
        if(update.message.text == 'y'):
            try:
                for x in phoneNumberList:
                    cursor.execute("INSERT INTO phone_number(phone_number) VALUES ('"+str(x)+"');")
                connection.commit()
                update.message.reply_text("Добавление выполнено успешно")
            except (Exception, Error) as error:
                update.message.reply_text("ERROR")
                return ConversationHandler.END
        else:
            return ConversationHandler.END
    else:
        update.message.reply_text("ERROR")
        return ConversationHandler.END
    return ConversationHandler.END

def verify_password(update: Update, context): 
    user_input = update.message.text
    if (
        len(str(user_input))>=8 and
        re.search(r'[A-Z]', user_input)
        and re.search(r'[a-z]', user_input) 
        and re.search(r'\d', user_input) 
        and re.search(r'[!@#$%^&*()]', user_input)):
        update.message.reply_text('Пapоль сложный')
    else:
        update.message.reply_text('Пapоль простой')
        return ConversationHandler.END
    return ConversationHandler.END

def print_info(stdout, stderr):
    data = stdout.read().decode('utf-8') + stderr.read().decode('utf-8')
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1] 
    return(data)

def get_release(update: Update, context):
    connect_vm()
    stdin, stdout, stderr = client.exec_command('cat /etc/os-release')
    update.message.reply_text(print_info(stdout, stderr))

def get_uname(update: Update, context):
    connect_vm()
    stdin, stdout, stderr = client.exec_command('uname -a')
    update.message.reply_text(print_info(stdout, stderr))

def get_uptime(update: Update, context):
    connect_vm()
    stdin, stdout, stderr = client.exec_command('uptime') 
    update.message.reply_text(print_info(stdout,stderr))

def get_df(update: Update, context):
    connect_vm()
    stdin, stdout, stderr= client.exec_command('df')
    update.message.reply_text(print_info(stdout,stderr))

def get_free(update: Update, context):
    connect_vm()
    stdin, stdout, stderr = client.exec_command('free') 
    update.message.reply_text(print_info(stdout, stderr))

def get_mpstat(update: Update, context):
    connect_vm()
    stdin, stdout, stderr = client.exec_command('mpstat') 
    update.message.reply_text(print_info(stdout,stderr))

def get_w(update: Update, context):
    connect_vm()
    stdin, stdout, stderr = client.exec_command('w') 
    update.message.reply_text(print_info(stdout,stderr))

def get_auth(update: Update, context):
    connect_vm()
    stdin, stdout, stderr = client.exec_command('cat /var/log/auth.log | head -10')
    update.message.reply_text(print_info(stdout,stderr))

def get_critical(update: Update, context):
    connect_vm()
    stdin, stdout, stderr = client.exec_command('cat /var/log/syslog | head -5') 
    update.message.reply_text(print_info(stdout,stderr))

def get_ps(update: Update, context):
    connect_vm()
    stdin, stdout, stderr = client.exec_command('ps | head -10') 
    update.message.reply_text(print_info(stdout,stderr))

def get_ss(update: Update, context):
    connect_vm()
    stdin, stdout, stderr= client.exec_command('ss -tulpn | head -10')
    update.message.reply_text(print_info(stdout,stderr))

def get_apt_list(update: Update, context):
    connect_vm()
    user_input=str(update.message.text)
    if user_input=='all':
        stdin, stdout, stderr = client.exec_command('apt list | head -15')
        update.message.reply_text(print_info(stdout,stderr))
    else:
        user_input_apt=update.message.text
        stdin, stdout, stderr= client.exec_command('apt show '+str(user_input_apt))
        update.message.reply_text(print_info(stdout,stderr))
    return ConversationHandler.END

def get_services(update: Update, context):
    connect_vm()
    stdin, stdout, stderr = client.exec_command('service --status-all') 
    update.message.reply_text(print_info(stdout, stderr))

LOG_FILE_PATH = "/var/log/postgresql/postgresql.log"

def get_repl_logs(update: Update, context):
    connect_vm()
    stdin, stdout, stderr = client.exec_command(f'echo {password1} | sudo -S docker logs db_container 2>&1 | grep replication | tail -n 15')
    update.message.reply_text(print_info(stdout,stderr))

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def main():
    updater = Updater (TOKEN, use_context=True)
    dp = updater.dispatcher

    HandlerFindEmail = ConversationHandler( 
        entry_points=[CommandHandler('find_email',findEmail)],
        states={
            'find_email':[MessageHandler(Filters.text & ~Filters.command, find_email)],
            'save email':[MessageHandler(Filters.text & ~Filters.command, save_email)],
        },
        fallbacks=[]
    )    

    HandlerFindPhoneNumber = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumber)],
        states={
            'find_phone_number':[MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
            'save phone numbers':[MessageHandler(Filters.text & ~Filters.command, save_phone_numbers)],
        },
        fallbacks=[]
    )

    HandlerverifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPassword)],
        states={
            'verify_password':[MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )

    HandleraptList = ConversationHandler(
        entry_points = [CommandHandler('get_apt_list', aptList)],
        states={
            'get_apt_list':[MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(HandlerFindEmail)
    dp.add_handler(HandlerFindPhoneNumber)
    dp.add_handler(HandlerverifyPassword)
    dp.add_handler(HandleraptList)
    dp.add_handler(CommandHandler('get_release', get_release)) 
    dp.add_handler(CommandHandler('get_uname', get_uname)) 
    dp.add_handler(CommandHandler('get_uptime', get_uptime)) 
    dp.add_handler(CommandHandler('get_df', get_df))
    dp.add_handler(CommandHandler('get_free', get_free))
    dp.add_handler(CommandHandler('get_mpstat', get_mpstat))
    dp.add_handler(CommandHandler('get_w', get_w))
    dp.add_handler(CommandHandler('get_auth', get_auth))
    dp.add_handler(CommandHandler('get_critical', get_critical))
    dp.add_handler(CommandHandler('get_ps', get_ps))
    dp.add_handler(CommandHandler('get_ss', get_ss)) 
    dp.add_handler(CommandHandler('get_services', get_services))
    dp.add_handler(CommandHandler('get_repl_logs', get_repl_logs))
    dp.add_handler(CommandHandler('get_emails', get_emails))
    dp.add_handler(CommandHandler('get_phone_numbers', get_phone_numbers))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    
    updater.start_polling()
   
    updater.idle()
if __name__ == '__main__':
    main()
