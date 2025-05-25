# src/llm_interview_simulation/pdf_generator.py
import logging
import os
from io import BytesIO
from datetime import datetime
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

from src.models.interview_simulation_models import InterviewSimulation

logger = logging.getLogger("pdf_generator")

class InterviewSimulationPDFGenerator:
    """Генератор PDF документов для симуляций интервью."""
    
    def __init__(self):
        """Инициализация генератора PDF."""
        self.styles = getSampleStyleSheet()
        self._register_fonts()
        self._setup_custom_styles()
    
    def _register_fonts(self):
        """Регистрация русских шрифтов."""
        try:
            # Возможные пути к папке со шрифтами
            possible_font_paths = [
                os.getenv('FONTS_PATH'),            # Путь из переменной окружения
                "/Users/mask/Desktop/dejavu-sans",  # Текущий путь пользователя
                "./fonts/dejavu-sans",              # Относительный путь в проекте
                "/usr/share/fonts/truetype/dejavu", # Linux стандартный путь
                "/System/Library/Fonts",            # macOS системные шрифты
            ]
            
            font_path = None
            # Ищем существующий путь к шрифтам
            for path in possible_font_paths:
                if path and os.path.exists(path):
                    font_path = path
                    break
            
            if not font_path:
                raise FileNotFoundError("Не найден путь к шрифтам DejaVu")
            
            # Регистрируем шрифты DejaVu
            font_files = {
                'DejaVuSans': 'DejaVuSans.ttf',
                'DejaVuSans-Bold': 'DejaVuSans-Bold.ttf', 
                'DejaVuSans-Oblique': 'DejaVuSans-Oblique.ttf',
                'DejaVuSans-BoldOblique': 'DejaVuSans-BoldOblique.ttf'
            }
            
            fonts_registered = 0
            for font_name, font_file in font_files.items():
                font_file_path = os.path.join(font_path, font_file)
                if os.path.exists(font_file_path):
                    pdfmetrics.registerFont(TTFont(font_name, font_file_path))
                    fonts_registered += 1
                else:
                    logger.warning(f"Файл шрифта не найден: {font_file_path}")
            
            if fonts_registered == 0:
                raise FileNotFoundError("Не найдено ни одного файла шрифта DejaVu")
            
            # Регистрируем семейство шрифтов
            registerFontFamily('DejaVuSans',
                             normal='DejaVuSans',
                             bold='DejaVuSans-Bold',
                             italic='DejaVuSans-Oblique',
                             boldItalic='DejaVuSans-BoldOblique')
            
            self.font_family = 'DejaVuSans'
            logger.info(f"Русские шрифты DejaVu успешно зарегистрированы из {font_path} ({fonts_registered} файлов)")
            
        except Exception as e:
            logger.warning(f"Не удалось загрузить шрифты DejaVu: {e}. Будет использован стандартный шрифт.")
            self.font_family = 'Helvetica'
    
    def _setup_custom_styles(self):
        """Настройка пользовательских стилей для PDF."""
        # Заголовок документа
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontName=self.font_family,
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor='#2E4BC6'
        )
        
        # Заголовки разделов
        self.section_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading1'],
            fontName=f'{self.font_family}-Bold',
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor='#1F4E79'
        )
        
        # Заголовки подразделов
        self.subsection_style = ParagraphStyle(
            'SubsectionHeader',
            parent=self.styles['Heading2'],
            fontName=f'{self.font_family}-Bold',
            fontSize=12,
            spaceAfter=8,
            spaceBefore=15,
            textColor='#4472C4'
        )
        
        # Стиль для HR вопросов
        self.hr_style = ParagraphStyle(
            'HRStyle',
            parent=self.styles['Normal'],
            fontName=self.font_family,
            fontSize=11,
            spaceAfter=8,
            spaceBefore=8,
            leftIndent=20,
            textColor='#C55A5A',
            alignment=TA_JUSTIFY
        )
        
        # Стиль для ответов кандидата
        self.candidate_style = ParagraphStyle(
            'CandidateStyle',
            parent=self.styles['Normal'],
            fontName=self.font_family,
            fontSize=11,
            spaceAfter=8,
            spaceBefore=8,
            leftIndent=20,
            textColor='#548235',
            alignment=TA_JUSTIFY
        )
        
        # Стиль для аналитических блоков
        self.analysis_style = ParagraphStyle(
            'AnalysisStyle',
            parent=self.styles['Normal'],
            fontName=self.font_family,
            fontSize=10,
            spaceAfter=12,
            spaceBefore=12,
            leftIndent=15,
            rightIndent=15,
            alignment=TA_JUSTIFY,
            textColor='#404040'
        )
        
        # Стиль для метаданных
        self.metadata_style = ParagraphStyle(
            'MetadataStyle',
            parent=self.styles['Normal'],
            fontName=self.font_family,
            fontSize=9,
            spaceAfter=6,
            textColor='#666666',
            alignment=TA_LEFT
        )
    
    def _create_header_section(self, simulation: InterviewSimulation) -> list:
        """Создает заголовочную секцию документа."""
        elements = []
        
        # Заголовок документа
        title = f"Симуляция интервью: {simulation.position_title}"
        elements.append(Paragraph(title, self.title_style))
        elements.append(Spacer(1, 20))
        
        # Базовая информация
        info_text = f"""
        <b>Кандидат:</b> {simulation.candidate_name}<br/>
        <b>Дата симуляции:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}<br/>
        <b>Количество раундов:</b> {simulation.simulation_metadata.get('rounds_completed', 'N/A')}<br/>
        <b>Контекст:</b> {simulation.company_context}
        """
        elements.append(Paragraph(info_text, self.metadata_style))
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _create_dialog_section(self, simulation: InterviewSimulation) -> list:
        """Создает секцию с диалогом интервью."""
        elements = []
        
        # Заголовок секции
        elements.append(Paragraph("Ход интервью", self.section_style))
        elements.append(Spacer(1, 15))
        
        # Группируем сообщения по раундам
        rounds = {}
        for msg in simulation.dialog_messages:
            round_num = msg.round_number
            if round_num not in rounds:
                rounds[round_num] = []
            rounds[round_num].append(msg)
        
        # Выводим диалог по раундам
        for round_num in sorted(rounds.keys()):
            # Заголовок раунда
            round_title = f"Раунд {round_num}"
            elements.append(Paragraph(round_title, self.subsection_style))
            
            # Сообщения раунда
            round_messages = rounds[round_num]
            for msg in round_messages:
                if msg.speaker == "HR":
                    speaker_label = "🎯 <b>HR-менеджер:</b>"
                    style = self.hr_style
                else:
                    speaker_label = "💼 <b>Кандидат:</b>"
                    style = self.candidate_style
                
                message_text = f"{speaker_label} {msg.message}"
                elements.append(Paragraph(message_text, style))
            
            elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_analysis_section(self, simulation: InterviewSimulation) -> list:
        """Создает аналитическую секцию документа."""
        elements = []
        
        # Заголовок секции
        elements.append(Paragraph("Анализ результатов интервью", self.section_style))
        elements.append(Spacer(1, 15))
        
        # Оценка HR
        elements.append(Paragraph("Оценка HR-менеджера", self.subsection_style))
        hr_assessment_text = f"📋 {simulation.hr_assessment}"
        elements.append(Paragraph(hr_assessment_text, self.analysis_style))
        elements.append(Spacer(1, 15))
        
        # Анализ выступления
        elements.append(Paragraph("Анализ выступления кандидата", self.subsection_style))
        performance_text = f"📊 {simulation.candidate_performance_analysis}"
        elements.append(Paragraph(performance_text, self.analysis_style))
        elements.append(Spacer(1, 15))
        
        # Рекомендации по улучшению
        elements.append(Paragraph("Рекомендации для улучшения", self.subsection_style))
        recommendations_text = f"💡 {simulation.improvement_recommendations}"
        elements.append(Paragraph(recommendations_text, self.analysis_style))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_footer_section(self, simulation: InterviewSimulation) -> list:
        """Создает нижнюю секцию с метаданными."""
        elements = []
        
        # Разделитель
        elements.append(Spacer(1, 20))
        
        # Техническая информация
        tech_info = f"""
        <i>Документ создан автоматически системой симуляции интервью.<br/>
        Модель ИИ: {simulation.simulation_metadata.get('model_used', 'N/A')}<br/>
        Версия системы: 1.0<br/>
        Время создания: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</i>
        """
        elements.append(Paragraph(tech_info, self.metadata_style))
        
        return elements
    
    def generate_pdf(self, simulation: InterviewSimulation) -> Optional[BytesIO]:
        """
        Генерирует PDF документ симуляции интервью.
        
        Args:
            simulation: Объект симуляции интервью
            
        Returns:
            BytesIO: PDF документ в виде байтов или None в случае ошибки
        """
        try:
            # Создаем BytesIO объект для PDF
            buffer = BytesIO()
            
            # Создаем документ
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Создаем элементы документа
            story = []
            
            # Добавляем секции
            story.extend(self._create_header_section(simulation))
            story.extend(self._create_dialog_section(simulation))
            story.extend(self._create_analysis_section(simulation))
            story.extend(self._create_footer_section(simulation))
            
            # Генерируем PDF
            doc.build(story)
            
            # Возвращаем буфер в начало
            buffer.seek(0)
            
            logger.info("PDF документ симуляции интервью успешно создан")
            return buffer
            
        except Exception as e:
            logger.error(f"Ошибка при создании PDF: {e}")
            return None
    
    def generate_filename(self, simulation: InterviewSimulation) -> str:
        """Генерирует имя файла для PDF."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Очищаем название позиции для имени файла
        clean_title = "".join(c for c in simulation.position_title if c.isalnum() or c in (' ', '-', '_'))[:50]
        clean_title = clean_title.replace(' ', '_')
        
        return f"interview_simulation_{clean_title}_{timestamp}.pdf"