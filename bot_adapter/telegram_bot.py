# bot_adapter/telegram_bot.py

"""Telegram бот адаптер"""
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import telegram_settings
from usecases.run_pipeline import PipelineOrchestrator
from domain.user_state import UserStateEnum
from loguru import logger


class UserStates(StatesGroup):
    """Состояния FSM для бота"""
    waiting_for_resume = State()
    waiting_for_vacancy = State()


class TelegramBotAdapter:
    """Адаптер для работы с Telegram"""
    
    def __init__(self, pipeline: PipelineOrchestrator):
        self.pipeline = pipeline
        self.bot = Bot(token=telegram_settings.bot_token)
        self.dp = Dispatcher(storage=MemoryStorage())
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Настроить обработчики команд"""
        
        @self.dp.message(Command("start"))
        async def start_handler(message: types.Message):
            """Обработка команды /start"""
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(
                    text="Редактировать резюме", 
                    callback_data="edit_resume"
                )]
            ])
            
            await message.answer(
                "Привет! Я помогу адаптировать ваше резюме под вакансию.\n\n"
                "Нажмите кнопку ниже, чтобы начать:",
                reply_markup=keyboard
            )
        
        @self.dp.callback_query(lambda c: c.data == "edit_resume")
        async def edit_resume_callback(callback: types.CallbackQuery):
            """Обработка нажатия кнопки редактирования"""
            user_id = callback.from_user.id
            
            try:
                # Генерируем ссылку для авторизации
                auth_url = await self.pipeline.start_oauth(user_id)
                
                await callback.message.answer(
                    f"Для доступа к вашему резюме необходима авторизация.\n\n"
                    f"Перейдите по ссылке и дайте согласие:\n"
                    f"{auth_url}"
                )
                
                await callback.answer()
                
            except Exception as e:
                logger.error(f"Failed to start OAuth: {e}")
                await callback.message.answer(
                    "Произошла ошибка. Попробуйте позже."
                )
        
        @self.dp.message(Command("resume"))
        async def resume_command(message: types.Message, state: FSMContext):
            """Команда для ввода резюме после авторизации"""
            user_id = message.from_user.id
            
            # Проверяем состояние пользователя
            user_state = await self.pipeline.state_storage.get_state(user_id)
            
            if not user_state or user_state.state not in [
                UserStateEnum.TOKEN_RECEIVED,
                UserStateEnum.RESUME_PARSING
            ]:
                await message.answer(
                    "Сначала необходимо авторизоваться. Используйте /start"
                )
                return
            
            await message.answer(
                "Пожалуйста, отправьте ссылку на ваше резюме:"
            )
            await state.set_state(UserStates.waiting_for_resume)
        
        @self.dp.message(UserStates.waiting_for_resume)
        async def process_resume(message: types.Message, state: FSMContext):
            """Обработка ссылки на резюме"""
            user_id = message.from_user.id
            resume_url = message.text
            
            try:
                # Парсим резюме
                resume = await self.pipeline.parse_resume(user_id, resume_url)
                
                await message.answer(
                    f"Резюме успешно получено!\n"
                    f"Имя: {resume.fullname}\n\n"
                    f"Теперь отправьте ссылку на вакансию:"
                )
                
                await state.set_state(UserStates.waiting_for_vacancy)
                await state.update_data(resume_url=resume_url)
                
            except Exception as e:
                logger.error(f"Failed to parse resume: {e}")
                await message.answer(
                    "Не удалось получить резюме. Проверьте ссылку и попробуйте снова."
                )
        
        @self.dp.message(UserStates.waiting_for_vacancy)
        async def process_vacancy(message: types.Message, state: FSMContext):
            """Обработка ссылки на вакансию"""
            user_id = message.from_user.id
            vacancy_url = message.text
            
            try:
                # Получаем сохраненную ссылку на резюме
                data = await state.get_data()
                resume_url = data.get('resume_url')
                
                if not resume_url:
                    await message.answer("Ошибка: потеряна ссылка на резюме")
                    await state.clear()
                    return
                
                await message.answer(
                    "Анализирую резюме и вакансию... Это может занять некоторое время."
                )
                
                # Запускаем полный pipeline
                result = await self.pipeline.run_full_pipeline(
                    user_id, resume_url, vacancy_url
                )
                
                if result['success']:
                    gap_report = result['gap_report']
                    
                    # Формируем отчет для пользователя
                    report_text = "✅ Анализ завершен!\n\n"
                    
                    if gap_report['missing_skills']:
                        report_text += "🔴 Недостающие навыки:\n"
                        for skill in gap_report['missing_skills']:
                            report_text += f"• {skill}\n"
                        report_text += "\n"
                    
                    if gap_report['recommendations']:
                        report_text += "💡 Рекомендации:\n"
                        for rec in gap_report['recommendations']:
                            report_text += f"• {rec}\n"
                        report_text += "\n"
                    
                    report_text += "Ваше резюме было обновлено с учетом рекомендаций!"
                    
                    await message.answer(report_text)
                    
                    # Если текст резюме не слишком длинный, отправим его
                    if len(result['new_resume_text']) < 4000:
                        await message.answer(
                            "Новый текст резюме:\n\n" + result['new_resume_text']
                        )
                else:
                    await message.answer(
                        "Не удалось обновить резюме. Попробуйте позже."
                    )
                
                await state.clear()
                
            except Exception as e:
                logger.error(f"Pipeline failed: {e}")
                await message.answer(
                    f"Произошла ошибка: {str(e)}\n"
                    f"Попробуйте начать заново с /start"
                )
                await state.clear()
    
    async def start(self):
        """Запустить бота"""
        logger.info("Starting Telegram bot...")
        await self.dp.start_polling(self.bot)