# src/llm_interview_simulation/pdf_generator.py
import logging
import os
from io import BytesIO
from datetime import datetime
from typing import Optional, List, Dict, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, NextPageTemplate, PageTemplate, Frame
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF

from src.models.interview_simulation_models import InterviewSimulation, CompetencyArea, QuestionType
from src.utils import get_logger

logger = get_logger()

class ProfessionalInterviewPDFGenerator:
    """Продвинутый генератор PDF отчетов с визуализацией и современным дизайном."""
    
    # Цветовая схема
    COLORS = {
        'primary': HexColor('#2E4BC6'),      # Синий основной
        'secondary': HexColor('#1F4E79'),    # Темно-синий
        'accent': HexColor('#4472C4'),       # Голубой акцент
        'success': HexColor('#548235'),      # Зеленый
        'warning': HexColor('#C5504B'),      # Красный
        'light_grey': HexColor('#F2F2F2'),   # Светло-серый
        'medium_grey': HexColor('#8C8C8C'),  # Серый
        'dark_grey': HexColor('#404040'),    # Темно-серый
        'hire': HexColor('#548235'),         # Зеленый для hire
        'conditional': HexColor('#D4A574'),  # Оранжевый для conditional
        'reject': HexColor('#C5504B')        # Красный для reject
    }
    
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
                os.getenv('FONTS_PATH'),            
                "/Users/mask/Desktop/dejavu-sans",  
                "./fonts/dejavu-sans",              
                "/usr/share/fonts/truetype/dejavu", 
                "/System/Library/Fonts",            
            ]
            
            font_path = None
            for path in possible_font_paths:
                if path and os.path.exists(path):
                    font_path = path
                    break
            
            if font_path:
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
                
                if fonts_registered > 0:
                    registerFontFamily('DejaVuSans',
                                     normal='DejaVuSans',
                                     bold='DejaVuSans-Bold',
                                     italic='DejaVuSans-Oblique',
                                     boldItalic='DejaVuSans-BoldOblique')
                    self.font_family = 'DejaVuSans'
                    logger.info(f"Русские шрифты DejaVu зарегистрированы ({fonts_registered} файлов)")
                else:
                    raise FileNotFoundError("Файлы шрифтов не найдены")
            else:
                raise FileNotFoundError("Папка со шрифтами не найдена")
                
        except Exception as e:
            logger.warning(f"Не удалось загрузить шрифты DejaVu: {e}. Используется стандартный шрифт.")
            self.font_family = 'Helvetica'
    
    def _setup_custom_styles(self):
        """Настройка пользовательских стилей."""
        
        # Заголовок документа
        self.title_style = ParagraphStyle(
            'ModernTitle',
            parent=self.styles['Title'],
            fontName=f'{self.font_family}-Bold',
            fontSize=24,
            spaceAfter=20,
            spaceBefore=10,
            alignment=TA_CENTER,
            textColor=self.COLORS['primary']
        )
        
        # Подзаголовок
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontName=self.font_family,
            fontSize=14,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=self.COLORS['medium_grey']
        )
        
        # Заголовки разделов
        self.section_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading1'],
            fontName=f'{self.font_family}-Bold',
            fontSize=16,
            spaceAfter=15,
            spaceBefore=25,
            textColor=self.COLORS['secondary'],
            borderWidth=0,
            borderColor=self.COLORS['primary'],
            borderPadding=5
        )
        
        # Подзаголовки
        self.subsection_style = ParagraphStyle(
            'SubsectionHeader',
            parent=self.styles['Heading2'],
            fontName=f'{self.font_family}-Bold',
            fontSize=13,
            spaceAfter=10,
            spaceBefore=15,
            textColor=self.COLORS['accent']
        )
        
        # Основной текст
        self.body_style = ParagraphStyle(
            'ModernBody',
            parent=self.styles['Normal'],
            fontName=self.font_family,
            fontSize=11,
            spaceAfter=8,
            spaceBefore=8,
            alignment=TA_JUSTIFY,
            textColor=self.COLORS['dark_grey']
        )
        
        # Стиль для важной информации
        self.highlight_style = ParagraphStyle(
            'Highlight',
            parent=self.body_style,
            backColor=self.COLORS['light_grey'],
            borderWidth=1,
            borderColor=self.COLORS['medium_grey'],
            borderPadding=10,
            borderRadius=5
        )
        
        # Стиль для HR вопросов
        self.hr_style = ParagraphStyle(
            'HRStyle',
            parent=self.body_style,
            leftIndent=15,
            rightIndent=15,
            textColor=self.COLORS['warning'],
            borderWidth=1,
            borderColor=self.COLORS['warning'],
            borderPadding=8,
            borderRadius=3
        )
        
        # Стиль для ответов кандидата
        self.candidate_style = ParagraphStyle(
            'CandidateStyle',
            parent=self.body_style,
            leftIndent=15,
            rightIndent=15,
            textColor=self.COLORS['success'],
            borderWidth=1,
            borderColor=self.COLORS['success'],
            borderPadding=8,
            borderRadius=3
        )
        
        # Стиль для метаданных
        self.metadata_style = ParagraphStyle(
            'MetadataStyle',
            parent=self.styles['Normal'],
            fontName=self.font_family,
            fontSize=9,
            textColor=self.COLORS['medium_grey'],
            alignment=TA_LEFT
        )
    
    def _create_header_section(self, simulation: InterviewSimulation) -> List:
        """Создает современную заголовочную секцию."""
        elements = []
        
        # Главный заголовок
        title = f"Отчет по симуляции интервью"
        elements.append(Paragraph(title, self.title_style))
        
        # Подзаголовок с позицией
        subtitle = f"{simulation.position_title}"
        elements.append(Paragraph(subtitle, self.subtitle_style))
        
        # Информационная таблица с обёрнутым в Paragraph содержимым
        info_data = [
            [Paragraph('Кандидат:', self.metadata_style), Paragraph(simulation.candidate_name, self.metadata_style)],
            [Paragraph('Дата симуляции:', self.metadata_style), Paragraph(datetime.now().strftime('%d.%m.%Y %H:%M'), self.metadata_style)],
            [Paragraph('Уровень кандидата:', self.metadata_style), Paragraph(simulation.candidate_profile.detected_level.value.title(), self.metadata_style)],
            [Paragraph('IT-роль:', self.metadata_style), Paragraph(simulation.candidate_profile.detected_role.value.replace('_', ' ').title(), self.metadata_style)],
            [Paragraph('Количество раундов:', self.metadata_style), Paragraph(str(simulation.total_rounds_completed), self.metadata_style)],
            [Paragraph('Общая рекомендация:', self.metadata_style), Paragraph(self._get_recommendation_text(simulation.assessment.overall_recommendation), self.metadata_style)]
        ]
        
        info_table = Table(info_data, colWidths=[5*cm, 7*cm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.font_family),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), self.COLORS['medium_grey']),
            ('TEXTCOLOR', (1, 0), (1, -1), self.COLORS['dark_grey']),
            ('FONTNAME', (0, 0), (0, -1), f'{self.font_family}-Bold'),
            ('FONTNAME', (1, 5), (1, 5), f'{self.font_family}-Bold'),
            ('TEXTCOLOR', (1, 5), (1, 5), self._get_recommendation_color(simulation.assessment.overall_recommendation)),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_competencies_visualization(self, simulation: InterviewSimulation) -> List:
        """Создает визуализацию оценок по компетенциям."""
        elements = []
        
        elements.append(Paragraph("Оценка компетенций", self.section_style))
        
        # Подготавливаем данные для таблицы
        competency_data = [['Компетенция', 'Оценка', 'Статус']]
        
        for comp_score in simulation.assessment.competency_scores:
            comp_name = self._translate_competency_name(comp_score.area)
            score_text = f"{comp_score.score}/5"
            status = self._get_score_status(comp_score.score)
            competency_data.append([comp_name, score_text, status])
        
        # Создаем таблицу с оценками
        comp_table = Table(competency_data, colWidths=[7*cm, 2*cm, 3*cm])
        comp_table.setStyle(TableStyle([
            # Заголовок
            ('FONTNAME', (0, 0), (-1, 0), f'{self.font_family}-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['primary']),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Данные
            ('FONTNAME', (0, 1), (-1, -1), self.font_family),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TEXTCOLOR', (0, 1), (0, -1), self.COLORS['dark_grey']),
            ('TEXTCOLOR', (1, 1), (1, -1), self.COLORS['secondary']),
            ('FONTNAME', (1, 1), (1, -1), f'{self.font_family}-Bold'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            
            # Границы и отступы
            ('GRID', (0, 0), (-1, -1), 1, self.COLORS['medium_grey']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        # Добавляем цвета для статусов
        for i, comp_score in enumerate(simulation.assessment.competency_scores, 1):
            color = self._get_score_color(comp_score.score)
            comp_table.setStyle(TableStyle([
                ('TEXTCOLOR', (2, i), (2, i), color),
                ('FONTNAME', (2, i), (2, i), f'{self.font_family}-Bold'),
            ]))
        
        elements.append(comp_table)
        elements.append(Spacer(1, 20))
        
        # Средний балл
        avg_score = sum(cs.score for cs in simulation.assessment.competency_scores) / len(simulation.assessment.competency_scores)
        avg_text = f"<b>Средний балл:</b> {avg_score:.1f}/5.0"
        elements.append(Paragraph(avg_text, self.highlight_style))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_strengths_weaknesses_section(self, simulation: InterviewSimulation) -> List:
        """Создает секцию с анализом сильных и слабых сторон."""
        elements = []
        
        elements.append(Paragraph("Анализ кандидата", self.section_style))
        
        # Сильные стороны
        elements.append(Paragraph("Сильные стороны", self.subsection_style))
        
        if simulation.assessment.strengths:
            # Создаем Paragraph элементы для каждой сильной стороны
            strengths_data = [[Paragraph(f"✓ {strength}", self.body_style)] for strength in simulation.assessment.strengths]
            strengths_table = Table(strengths_data, colWidths=[15*cm])
            strengths_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.font_family),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.COLORS['success']),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#F0F8F0')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(strengths_table)
        else:
            elements.append(Paragraph("Не выявлены", self.body_style))
        
        elements.append(Spacer(1, 15))
        
        # Слабые стороны
        elements.append(Paragraph("Области для развития", self.subsection_style))
        
        if simulation.assessment.weaknesses:
            # Создаем Paragraph элементы для каждой области развития
            weaknesses_data = [[Paragraph(f"⚠ {weakness}", self.body_style)] for weakness in simulation.assessment.weaknesses]
            weaknesses_table = Table(weaknesses_data, colWidths=[15*cm])
            weaknesses_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.font_family),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.COLORS['warning']),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#FFF8F0')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(weaknesses_table)
        else:
            elements.append(Paragraph("Не выявлены", self.body_style))
        
        elements.append(Spacer(1, 15))
        
        # Красные флаги
        if simulation.assessment.red_flags:
            elements.append(Paragraph("Красные флаги", self.subsection_style))
            # Создаем Paragraph элементы для каждого красного флага
            red_flags_data = [[Paragraph(f"🚩 {flag}", self.body_style)] for flag in simulation.assessment.red_flags]
            red_flags_table = Table(red_flags_data, colWidths=[15*cm])
            red_flags_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.font_family),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.COLORS['reject']),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#FFEBEE')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(red_flags_table)
            elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_dialog_section(self, simulation: InterviewSimulation) -> List:
        """Создает секцию с диалогом интервью."""
        elements = []
        
        elements.append(Paragraph("Ход интервью", self.section_style))
        
        # Группируем сообщения по раундам
        rounds = {}
        for msg in simulation.dialog_messages:
            round_num = msg.round_number
            if round_num not in rounds:
                rounds[round_num] = []
            rounds[round_num].append(msg)
        
        # Выводим диалог по раундам
        for round_num in sorted(rounds.keys()):
            round_messages = rounds[round_num]
            
            # Определяем тип вопроса для заголовка раунда
            hr_msg = next((msg for msg in round_messages if msg.speaker == "HR"), None)
            question_type_text = ""
            if hr_msg and hr_msg.question_type:
                question_type_text = f" ({self._translate_question_type(hr_msg.question_type)})"
            
            round_title = f"Раунд {round_num}{question_type_text}"
            elements.append(Paragraph(round_title, self.subsection_style))
            
            # Сообщения раунда
            for msg in round_messages:
                if msg.speaker == "HR":
                    speaker_label = f"<b>🎯 HR-менеджер:</b>"
                    message_text = f"{speaker_label} {msg.message}"
                    elements.append(Paragraph(message_text, self.hr_style))
                else:
                    quality_indicator = ""
                    if msg.response_quality:
                        stars = "★" * msg.response_quality + "☆" * (5 - msg.response_quality)
                        quality_indicator = f" <i>({stars})</i>"
                    
                    speaker_label = f"<b>💼 Кандидат:</b>"
                    message_text = f"{speaker_label} {msg.message}{quality_indicator}"
                    elements.append(Paragraph(message_text, self.candidate_style))
                
                elements.append(Spacer(1, 8))
            
            elements.append(Spacer(1, 10))
        
        return elements
    
    def _create_recommendations_section(self, simulation: InterviewSimulation) -> List:
        """Создает секцию с рекомендациями."""
        elements = []
        
        elements.append(Paragraph("Профессиональные рекомендации", self.section_style))
        
        # HR оценка
        elements.append(Paragraph("Заключение HR-специалиста", self.subsection_style))
        elements.append(Paragraph(simulation.hr_assessment, self.highlight_style))
        elements.append(Spacer(1, 15))
        
        # Анализ выступления
        elements.append(Paragraph("Анализ выступления", self.subsection_style))
        elements.append(Paragraph(simulation.candidate_performance_analysis, self.body_style))
        elements.append(Spacer(1, 15))
        
        # Рекомендации по улучшению
        elements.append(Paragraph("Рекомендации по развитию", self.subsection_style))
        elements.append(Paragraph(simulation.improvement_recommendations, self.body_style))
        elements.append(Spacer(1, 15))
        
        # Детальные рекомендации по компетенциям
        elements.append(Paragraph("Детальные рекомендации по компетенциям", self.subsection_style))
        
        for comp_score in simulation.assessment.competency_scores:
            comp_name = self._translate_competency_name(comp_score.area)
            elements.append(Paragraph(f"<b>{comp_name}:</b> {comp_score.improvement_notes}", self.body_style))
        
        return elements
    
    def _create_footer_section(self, simulation: InterviewSimulation) -> List:
        """Создает нижнюю секцию."""
        elements = []
        
        elements.append(Spacer(1, 30))
        
        # Техническая информация
        tech_info = f"""
        <i>Документ создан автоматически системой симуляции интервью.<br/>
        Модель ИИ: {simulation.simulation_metadata.get('model_used', 'N/A')}<br/>
        Время создания: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}<br/>
        Средняя оценка качества ответов: {simulation.average_response_quality:.1f}/5.0</i>
        """
        elements.append(Paragraph(tech_info, self.metadata_style))
        
        return elements
    
    def _translate_competency_name(self, competency: CompetencyArea) -> str:
        """Переводит название компетенции на русский."""
        translations = {
            CompetencyArea.TECHNICAL_EXPERTISE: "Техническая экспертиза",
            CompetencyArea.COMMUNICATION: "Коммуникативные навыки",
            CompetencyArea.PROBLEM_SOLVING: "Решение проблем",
            CompetencyArea.TEAMWORK: "Командная работа",
            CompetencyArea.LEADERSHIP: "Лидерские качества",
            CompetencyArea.ADAPTABILITY: "Адаптивность",
            CompetencyArea.LEARNING_ABILITY: "Способность к обучению",
            CompetencyArea.MOTIVATION: "Мотивация",
            CompetencyArea.CULTURAL_FIT: "Культурное соответствие"
        }
        return translations.get(competency, competency.value)
    
    def _translate_question_type(self, question_type: QuestionType) -> str:
        """Переводит тип вопроса на русский."""
        translations = {
            QuestionType.INTRODUCTION: "Знакомство",
            QuestionType.TECHNICAL_SKILLS: "Технические навыки",
            QuestionType.EXPERIENCE_DEEP_DIVE: "Глубокий анализ опыта",
            QuestionType.BEHAVIORAL_STAR: "Поведенческие вопросы",
            QuestionType.PROBLEM_SOLVING: "Решение проблем",
            QuestionType.MOTIVATION: "Мотивация",
            QuestionType.CULTURE_FIT: "Культурное соответствие",
            QuestionType.LEADERSHIP: "Лидерство",
            QuestionType.FINAL: "Финальные вопросы"
        }
        return translations.get(question_type, question_type.value)
    
    def _get_recommendation_text(self, recommendation: str) -> str:
        """Возвращает текст рекомендации."""
        texts = {
            'hire': '✅ Рекомендовать к найму',
            'conditional_hire': '⚡ Условно рекомендовать',
            'reject': '❌ Не рекомендовать'
        }
        return texts.get(recommendation, recommendation)
    
    def _get_recommendation_color(self, recommendation: str):
        """Возвращает цвет для рекомендации."""
        colors = {
            'hire': self.COLORS['hire'],
            'conditional_hire': self.COLORS['conditional'],
            'reject': self.COLORS['reject']
        }
        return colors.get(recommendation, self.COLORS['medium_grey'])
    
    def _get_score_status(self, score: int) -> str:
        """Возвращает статус оценки."""
        if score >= 4:
            return "Отлично"
        elif score >= 3:
            return "Хорошо"
        elif score >= 2:
            return "Удовлетворительно"
        else:
            return "Требует улучшения"
    
    def _get_score_color(self, score: int):
        """Возвращает цвет для оценки."""
        if score >= 4:
            return self.COLORS['success']
        elif score >= 3:
            return self.COLORS['accent']
        elif score >= 2:
            return self.COLORS['warning']
        else:
            return self.COLORS['reject']
    
    def generate_pdf(self, simulation: InterviewSimulation) -> Optional[BytesIO]:
        """
        Генерирует профессиональный PDF документ симуляции интервью.
        """
        try:
            # Создаем BytesIO объект для PDF
            buffer = BytesIO()
            
            # Создаем документ с отступами
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Создаем элементы документа
            story = []
            
            # Добавляем секции
            story.extend(self._create_header_section(simulation))
            story.extend(self._create_competencies_visualization(simulation))
            story.extend(self._create_strengths_weaknesses_section(simulation))
            
            # Разрыв страницы перед диалогом
            story.append(PageBreak())
            story.extend(self._create_dialog_section(simulation))
            
            # Разрыв страницы перед рекомендациями
            story.append(PageBreak()) 
            story.extend(self._create_recommendations_section(simulation))
            story.extend(self._create_footer_section(simulation))
            
            # Генерируем PDF
            doc.build(story)
            
            # Возвращаем буфер в начало
            buffer.seek(0)
            
            logger.info("Профессиональный PDF документ симуляции интервью создан")
            return buffer
            
        except Exception as e:
            logger.error(f"Ошибка при создании PDF: {e}")
            return None
    
    def generate_filename(self, simulation: InterviewSimulation) -> str:
        """Генерирует имя файла для PDF."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Очищаем название позиции
        clean_title = "".join(c for c in simulation.position_title if c.isalnum() or c in (' ', '-', '_'))[:50]
        clean_title = clean_title.replace(' ', '_')
        
        # Добавляем уровень кандидата
        level = simulation.candidate_profile.detected_level.value
        
        return f"interview_report_{clean_title}_{level}_{timestamp}.pdf"

# Для обратной совместимости
InterviewSimulationPDFGenerator = ProfessionalInterviewPDFGenerator