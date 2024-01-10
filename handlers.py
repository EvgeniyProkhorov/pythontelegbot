from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler, ConversationHandler
from utils import get_available_cabins
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Определение этапов разговора
CHOOSE_ACTION, SELECT_CABIN, CONFIRM_SELECTION = range(3)

async def start(update: Update, context: CallbackContext) -> int:
    context.user_data['state'] = CHOOSE_ACTION
    logger.info("Функция start вызвана")
    
    keyboard = [[InlineKeyboardButton("🏠 Выбрать бытовку из наличия", callback_data='show_cabin')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите действие:', reply_markup=reply_markup)
    
    logger.info("Переход в состояние CHOOSE_ACTION")
    return CHOOSE_ACTION

# async def show_cabins(update: Update, context: CallbackContext) -> int:
#     current_state = context.user_data.get('state')
#     logger.info(f"Текущее состояние: {current_state}")
#     context.user_data['state'] = SELECT_CABIN

#     query = update.callback_query
#     await query.answer()

#     cabins = get_available_cabins()
#     for cabin in cabins:
#         keyboard = [[InlineKeyboardButton("Выбрать эту бытовку", callback_data=f'select_{cabin["id"]}')]]
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         await query.message.reply_photo(cabin['photo'], caption=cabin['description'], reply_markup=reply_markup)
    
#     logger.info("Переход в состояние SELECT_CABIN")
#     return SELECT_CABIN
async def show_cabins(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    context.user_data['state'] = SELECT_CABIN
    context.user_data['cabin_messages'] = []  # Инициализация списка для идентификаторов сообщений

    cabins = get_available_cabins()
    for cabin in cabins:
        keyboard = [[InlineKeyboardButton("Выбрать эту бытовку", callback_data=f'select_{cabin["id"]}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        sent_message = await context.bot.send_photo(chat_id=update.effective_chat.id, photo=cabin['photo'], caption=cabin['description'], reply_markup=reply_markup)

        # Сохраняем идентификаторы отправленных сообщений
        context.user_data['cabin_messages'].append(sent_message.message_id)

    logger.info("Переход в состояние SELECT_CABIN")
    return SELECT_CABIN


async def confirm_cabin_selection(update: Update, context: CallbackContext) -> int:
    current_state = context.user_data.get('state')
    logger.info(f"Текущее состояние: {current_state}")
    context.user_data['state'] = CONFIRM_SELECTION

    query = update.callback_query
    await query.answer()

    # Тут можно добавить логику для обработки выбора бытовки
    await query.edit_message_text(text="Вы выбрали бытовку. Тут можно предложить следующие шаги.")

    logger.info("Переход в состояние CONFIRM_SELECTION")
    return CONFIRM_SELECTION

# async def cabin_details(update: Update, context: CallbackContext) -> None:
#     query = update.callback_query
#     await query.answer()

#     # Получаем ID выбранной бытовки из callback_data
#     selected_cabin_id = query.data.split('_')[1]
#     cabins = get_available_cabins()
#     selected_cabin = next((c for c in cabins if str(c['id']) == selected_cabin_id), None)

#     if selected_cabin:
#         keyboard = [
#             [InlineKeyboardButton("📲 Связаться в Telegram", url="https://t.me/ivanov1111")],
#             [InlineKeyboardButton("💬 Связаться в WhatsApp", url="https://api.whatsapp.com/send?phone=79111781781")],
#             [InlineKeyboardButton("🌐 Посетить наш сайт", url="https://www.bytovki-1.ru/")],
#             [InlineKeyboardButton("🔵 Посетить наше сообщество в VK", url="https://vk.com/public210580591")],
#             [InlineKeyboardButton("📞 Заказать обратный звонок", callback_data='contact')]
#         ]
#         reply_markup = InlineKeyboardMarkup(keyboard)

#         caption = f"{selected_cabin['description']}\n\nЧтобы узнать более подробную информацию и цену на интересующее Вас изделие, выберите удобный для Вас способ связи:"
        
#         # Обновляем подпись к фото
#         await query.edit_message_caption(caption=caption, reply_markup=reply_markup)

#         context.user_data['state'] = 'CABIN_DETAILS'
#     else:
#         await context.bot.send_message(chat_id=update.effective_chat.id, text="Извините, произошла ошибка. Пожалуйста, выберите бытовку заново.")
#         context.user_data['state'] = 'CHOOSE_ACTION'

#     return
async def cabin_details(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    selected_cabin_id = query.data.split('_')[1]
    cabins = get_available_cabins()
    selected_cabin = next((c for c in cabins if str(c['id']) == selected_cabin_id), None)

    if selected_cabin:
        # Удаление предыдущих сообщений, кроме текущего
        for msg_id in context.user_data.get('cabin_messages', []):
            if msg_id != query.message.message_id:  # Не удаляем текущее сообщение
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_id)
        context.user_data['cabin_messages'] = []  # Очищаем список после удаления сообщений

        keyboard = [
            [InlineKeyboardButton("📲 Связаться в Telegram", url="https://t.me/ivanov1111")],
            [InlineKeyboardButton("💬 Связаться в WhatsApp", url="https://api.whatsapp.com/send?phone=79111781781")],
            [InlineKeyboardButton("🌐 Посетить наш сайт", url="https://www.bytovki-1.ru/")],
            [InlineKeyboardButton("🔵 Посетить наше сообщество в VK", url="https://vk.com/public210580591")],
            [InlineKeyboardButton("📞 Заказать обратный звонок", callback_data='contact')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        caption = f"{selected_cabin['description']}\n\nЧтобы узнать более подробную информацию и цену на интересующее Вас изделие, выберите удобный для Вас способ связи:"
        await query.edit_message_caption(caption=caption, reply_markup=reply_markup)

        context.user_data['state'] = 'CABIN_DETAILS'
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Извините, произошла ошибка. Пожалуйста, выберите бытовку заново.")
        context.user_data['state'] = 'CHOOSE_ACTION'

    return




def setup_conversation() -> ConversationHandler:
    logger.info("Функция setup_conversation вызвана")
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSE_ACTION: [CallbackQueryHandler(show_cabins, pattern='^show_cabin$')],
            SELECT_CABIN: [CallbackQueryHandler(cabin_details, pattern='^select_')],
            CONFIRM_SELECTION: [CallbackQueryHandler(confirm_cabin_selection, pattern='^confirm_')]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    return conv_handler

