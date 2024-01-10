import asyncio
import nest_asyncio
from telegram.ext import Application, ConversationHandler
import handlers  # Импорт модуля обработчиков

nest_asyncio.apply()

async def main():
    application = Application.builder().token("6505265129:AAErEfKi8BeoPX3yZfIhTu-P3JNLetP6Txk").build()

    conv_handler = handlers.setup_conversation()
    application.add_handler(conv_handler)

    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())