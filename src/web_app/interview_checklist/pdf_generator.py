"""
PDF генератор для чек-листов подготовки к интервью

Генерирует профессиональные PDF с чек-листами подготовки к интервью
на основе данных от LLMInterviewChecklistGenerator.
"""

import io
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import Any, Dict, List
import os


class InterviewChecklistPDFGenerator:
    """Генератор PDF для чек-листов подготовки к интервью"""
    
    def __init__(self):
        # Цветовая схема (должна быть первой!)
        self.colors = {
            # Основные цвета
            'primary': colors.HexColor('#2B6CB0'),      # Профессиональный синий для заголовков
            'secondary': colors.HexColor('#3182CE'),    # Светлый синий для подзаголовков
            'accent': colors.HexColor('#38A169'),       # Зеленый для успеха/исследования
            'text': colors.HexColor('#2D3748'),         # Темный текст
            
            # Приоритеты (интуитивные цвета)
            'priority_critical': colors.HexColor('#E53E3E'),  # Красный - критично
            'priority_important': colors.HexColor('#D69E2E'), # Желтый/оранжевый - важно
            'priority_medium': colors.HexColor('#3182CE'),    # Синий - средне
            'priority_low': colors.HexColor('#68D391'),       # Светло-зеленый - низко
            
            # Фоновые цвета
            'light_blue': colors.HexColor('#EBF8FF'),   # Светло-голубой
            'light_green': colors.HexColor('#F0FFF4'),  # Светло-зеленый
            'light_red': colors.HexColor('#FED7D7'),    # Светло-красный
            'light_yellow': colors.HexColor('#FEFCBF'), # Светло-желтый
            'light_gray': colors.HexColor('#F7FAFC'),   # Светло-серый
            'dark_gray': colors.HexColor('#4A5568'),    # Темно-серый
        }
        
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()
        self.register_fonts()
        self.setup_custom_styles()
    
    def get_priority_color(self, priority_text: str):
        """Определяет цвет для приоритета"""
        priority_lower = priority_text.lower()
        if 'критич' in priority_lower or 'critical' in priority_lower or 'высок' in priority_lower:
            return self.colors['priority_critical']
        elif 'важн' in priority_lower or 'important' in priority_lower:
            return self.colors['priority_important']
        elif 'средн' in priority_lower or 'medium' in priority_lower:
            return self.colors['priority_medium']
        elif 'низк' in priority_lower or 'low' in priority_lower:
            return self.colors['priority_low']
        else:
            return self.colors['secondary']  # По умолчанию
    
    def register_fonts(self):
        """Регистрация шрифтов с поддержкой кириллицы"""
        try:
            # Пробуем разные пути к шрифтам
            font_paths = [
                "fonts/dejavu-sans/DejaVuSans.ttf",
                "../fonts/dejavu-sans/DejaVuSans.ttf",
                "../../fonts/dejavu-sans/DejaVuSans.ttf",
                "/System/Library/Fonts/Arial.ttf",  # macOS
                "/Windows/Fonts/arial.ttf"  # Windows
            ]
            
            bold_font_paths = [
                "fonts/dejavu-sans/DejaVuSans-Bold.ttf",
                "../fonts/dejavu-sans/DejaVuSans-Bold.ttf",
                "../../fonts/dejavu-sans/DejaVuSans-Bold.ttf",
                "/System/Library/Fonts/Arial Bold.ttf",  # macOS
                "/Windows/Fonts/arialbd.ttf"  # Windows
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
                    break
            
            for font_path in bold_font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_path))
                    break
        except Exception as e:
            print(f"Font registration error: {e}")
    
    def setup_custom_styles(self):
        """Настройка пользовательских стилей"""
        # Заголовок документа
        self.styles.add(ParagraphStyle(
            name='ChecklistTitle',
            parent=self.styles['Title'],
            fontName='DejaVuSans-Bold',
            fontSize=18,
            textColor=self.colors['primary'],
            spaceAfter=20,
            alignment=1  # Center
        ))
        
        # Заголовок раздела
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontName='DejaVuSans-Bold',
            fontSize=14,
            textColor=self.colors['primary'],
            spaceBefore=16,
            spaceAfter=8,
            alignment=1  # Center
        ))
        
        # Подзаголовок
        self.styles.add(ParagraphStyle(
            name='SubHeader',
            parent=self.styles['Heading2'],
            fontName='DejaVuSans-Bold',
            fontSize=12,
            textColor=self.colors['secondary'],
            spaceBefore=12,
            spaceAfter=6
        ))
        
        # Основной текст
        self.styles.add(ParagraphStyle(
            name='ChecklistBody',
            parent=self.styles['Normal'],
            fontName='DejaVuSans',
            fontSize=10,
            textColor=self.colors['text'],
            spaceBefore=4,
            spaceAfter=4,
            leading=14
        ))
        
        # Текст задач
        self.styles.add(ParagraphStyle(
            name='TaskText',
            parent=self.styles['Normal'],
            fontName='DejaVuSans',
            fontSize=10,
            textColor=self.colors['text'],
            spaceBefore=2,
            spaceAfter=2,
            leading=13,
            leftIndent=20
        ))
        
        # Текст в таблице
        self.styles.add(ParagraphStyle(
            name='TableText',
            parent=self.styles['Normal'],
            fontName='DejaVuSans',
            fontSize=9,
            textColor=self.colors['text'],
            leading=12
        ))
    
    def generate_pdf(self, checklist_result) -> io.BytesIO:
        """Генерация PDF чек-листа"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # Заголовок
        story.append(Paragraph("Чек-лист Подготовки к Интервью", self.styles['ChecklistTitle']))
        story.append(Spacer(1, 12))
        
        # Определяем тип чек-листа и обрабатываем соответственно
        if hasattr(checklist_result, 'executive_summary'):
            # Профессиональная версия
            story.extend(self._create_professional_checklist(checklist_result))
        else:
            # Базовая версия
            story.extend(self._create_basic_checklist(checklist_result))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _create_professional_checklist(self, checklist_result) -> List:
        """Создание профессионального чек-листа"""
        elements = []
        
        # Резюме подготовки
        if hasattr(checklist_result, 'preparation_strategy'):
            elements.append(Paragraph("Стратегия Подготовки", self.styles['SectionHeader']))
            elements.append(Paragraph(checklist_result.preparation_strategy, self.styles['ChecklistBody']))
            elements.append(Spacer(1, 12))
        
        # Контекст персонализации
        if hasattr(checklist_result, 'personalization_context'):
            elements.extend(self._create_personalization_context_table(checklist_result.personalization_context))
            elements.append(Spacer(1, 16))
        
        # Техническая подготовка
        if hasattr(checklist_result, 'technical_preparation'):
            elements.extend(self._create_preparation_section(
                "Техническая Подготовка", 
                checklist_result.technical_preparation,
                self.colors['secondary']
            ))
            elements.append(Spacer(1, 12))
        
        # Поведенческая подготовка
        if hasattr(checklist_result, 'behavioral_preparation'):
            elements.extend(self._create_behavioral_section(checklist_result.behavioral_preparation))
            elements.append(Spacer(1, 12))
        
        # Исследование компании
        if hasattr(checklist_result, 'company_research'):
            elements.extend(self._create_preparation_section(
                "Исследование Компании", 
                checklist_result.company_research,
                self.colors['accent']
            ))
            elements.append(Spacer(1, 12))
        
        # Изучение технического стека
        if hasattr(checklist_result, 'technical_stack_study'):
            elements.extend(self._create_technical_stack_section(checklist_result.technical_stack_study))
            elements.append(Spacer(1, 12))
        
        # Практические упражнения
        if hasattr(checklist_result, 'practical_exercises'):
            elements.extend(self._create_practical_exercises_section(checklist_result.practical_exercises))
            elements.append(Spacer(1, 12))
        
        # Настройка интервью
        if hasattr(checklist_result, 'interview_setup'):
            elements.extend(self._create_preparation_section(
                "Настройка Интервью", 
                checklist_result.interview_setup,
                self.colors['priority_critical']  # Критично важная секция
            ))
            elements.append(Spacer(1, 12))
        
        # Критические факторы успеха
        if hasattr(checklist_result, 'critical_success_factors'):
            elements.extend(self._create_success_factors_section(checklist_result.critical_success_factors))
        
        return elements
    
    def _create_basic_checklist(self, checklist_result) -> List:
        """Создание базового чек-листа"""
        elements = []
        
        # Технические навыки
        if hasattr(checklist_result, 'technical_skills'):
            elements.extend(self._create_technical_skills_section(checklist_result.technical_skills))
            elements.append(Spacer(1, 16))
        
        # Поведенческие вопросы
        if hasattr(checklist_result, 'behavioral_questions'):
            elements.extend(self._create_behavioral_questions_section(checklist_result.behavioral_questions))
            elements.append(Spacer(1, 16))
        
        # Исследование компании
        if hasattr(checklist_result, 'company_research_tips'):
            elements.append(Paragraph("Исследование Компании", self.styles['SectionHeader']))
            elements.append(Paragraph(checklist_result.company_research_tips, self.styles['ChecklistBody']))
            elements.append(Spacer(1, 12))
        
        # Финальные рекомендации
        if hasattr(checklist_result, 'final_recommendations'):
            elements.append(Paragraph("Финальные Рекомендации", self.styles['SectionHeader']))
            elements.append(Paragraph(checklist_result.final_recommendations, self.styles['ChecklistBody']))
        
        return elements
    
    def _create_personalization_context_table(self, context) -> List:
        """Создание таблицы контекста персонализации"""
        elements = []
        elements.append(Paragraph("Контекст Кандидата", self.styles['SectionHeader']))
        
        # Обрабатываем enum значения, убирая префиксы
        candidate_level = getattr(context, 'candidate_level', 'Не указано')
        if hasattr(candidate_level, 'value'):
            candidate_level_text = candidate_level.value
        else:
            candidate_level_text = str(candidate_level) if candidate_level else 'Не указано'
            
        vacancy_type = getattr(context, 'vacancy_type', 'Не указано')
        if hasattr(vacancy_type, 'value'):
            vacancy_type_text = vacancy_type.value
        else:
            vacancy_type_text = str(vacancy_type) if vacancy_type else 'Не указано'
            
        company_format = getattr(context, 'company_format', 'Не указано')
        if hasattr(company_format, 'value'):
            company_format_text = company_format.value
        else:
            company_format_text = str(company_format) if company_format else 'Не указано'
        
        # Создаем данные с обёрнутыми в Paragraph элементами для переноса текста
        data = [
            [Paragraph('Параметр', self.styles['TableText']), Paragraph('Значение', self.styles['TableText'])],
            [Paragraph('Уровень кандидата', self.styles['TableText']), Paragraph(candidate_level_text, self.styles['TableText'])],
            [Paragraph('Тип вакансии', self.styles['TableText']), Paragraph(vacancy_type_text, self.styles['TableText'])],
            [Paragraph('Формат компании', self.styles['TableText']), Paragraph(company_format_text, self.styles['TableText'])]
        ]
        
        # Добавляем критические области фокуса
        if hasattr(context, 'critical_focus_areas') and context.critical_focus_areas:
            focus_areas = ', '.join(context.critical_focus_areas)
            data.append([Paragraph('Критические области фокуса', self.styles['TableText']), Paragraph(focus_areas, self.styles['TableText'])])
        
        table = Table(data, colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(table)
        return elements
    
    def _create_preparation_section(self, title: str, items: List, color) -> List:
        """Создание секции подготовки"""
        elements = []
        elements.append(Paragraph(title, self.styles['SectionHeader']))
        
        for item in items:
            # Заголовок задачи
            task_title = getattr(item, 'task_title', getattr(item, 'category', 'Задача'))
            elements.append(Paragraph(f"<b>{task_title}</b>", self.styles['SubHeader']))
            
            # Описание
            if hasattr(item, 'description'):
                elements.append(Paragraph(f"• {item.description}", self.styles['TaskText']))
            
            # Специфические действия или чек-лист
            if hasattr(item, 'specific_actions') and item.specific_actions:
                for action in item.specific_actions:
                    elements.append(Paragraph(f"• {action}", self.styles['TaskText']))
            
            if hasattr(item, 'checklist_items') and item.checklist_items:
                for check_item in item.checklist_items:
                    elements.append(Paragraph(f"☐ {check_item}", self.styles['TaskText']))
            
            # Время и приоритет
            time_info = []
            if hasattr(item, 'estimated_time'):
                time_info.append(f"Время: {item.estimated_time}")
            if hasattr(item, 'time_required'):
                time_info.append(f"Время: {item.time_required}")
            if hasattr(item, 'priority'):
                priority_val = item.priority
                if hasattr(priority_val, 'value'):
                    priority_text = priority_val.value
                else:
                    priority_text = str(priority_val)
                priority_color = self.get_priority_color(priority_text)
                time_info.append(f"<font color='{priority_color}'>Приоритет: {priority_text}</font>")
            if hasattr(item, 'urgency'):
                urgency_val = item.urgency
                if hasattr(urgency_val, 'value'):
                    urgency_text = urgency_val.value
                else:
                    urgency_text = str(urgency_val)
                urgency_color = self.get_priority_color(urgency_text)
                time_info.append(f"<font color='{urgency_color}'>Приоритет: {urgency_text}</font>")
            
            if time_info:
                elements.append(Paragraph(f"<i>{' | '.join(time_info)}</i>", self.styles['TaskText']))
            
            elements.append(Spacer(1, 8))
        
        return elements
    
    def _create_behavioral_section(self, behavioral_items: List) -> List:
        """Создание секции поведенческой подготовки"""
        elements = []
        elements.append(Paragraph("Поведенческая Подготовка", self.styles['SectionHeader']))
        
        for item in behavioral_items:
            # Категория
            category = getattr(item, 'category', 'Поведенческие навыки')
            elements.append(Paragraph(f"<b>{category}</b>", self.styles['SubHeader']))
            
            # Примеры вопросов
            if hasattr(item, 'example_questions') and item.example_questions:
                elements.append(Paragraph("Примеры вопросов:", self.styles['ChecklistBody']))
                for question in item.example_questions:
                    elements.append(Paragraph(f"• {question}", self.styles['TaskText']))
            
            # Советы по подготовке
            if hasattr(item, 'practice_tips'):
                elements.append(Paragraph("Советы по подготовке:", self.styles['ChecklistBody']))
                elements.append(Paragraph(f"• {item.practice_tips}", self.styles['TaskText']))
            
            elements.append(Spacer(1, 8))
        
        return elements
    
    def _create_technical_stack_section(self, tech_items: List) -> List:
        """Создание секции изучения технического стека"""
        elements = []
        elements.append(Paragraph("Изучение Технического Стека", self.styles['SectionHeader']))
        
        for item in tech_items:
            # Заголовок технологии
            task_title = getattr(item, 'task_title', getattr(item, 'category', 'Технология'))
            elements.append(Paragraph(f"<b>{task_title}</b>", self.styles['SubHeader']))
            
            # Описание и подход к изучению
            if hasattr(item, 'description'):
                elements.append(Paragraph(f"• {item.description}", self.styles['TaskText']))
            
            if hasattr(item, 'study_approach'):
                elements.append(Paragraph(f"• Подход к изучению: {item.study_approach}", self.styles['TaskText']))
            
            elements.append(Spacer(1, 8))
        
        return elements
    
    def _create_practical_exercises_section(self, exercises: List) -> List:
        """Создание секции практических упражнений"""
        elements = []
        elements.append(Paragraph("Практические Упражнения", self.styles['SectionHeader']))
        
        for exercise in exercises:
            # Заголовок упражнения
            title = getattr(exercise, 'exercise_title', getattr(exercise, 'category', 'Упражнение'))
            elements.append(Paragraph(f"<b>{title}</b>", self.styles['SubHeader']))
            
            # Описание
            if hasattr(exercise, 'description'):
                elements.append(Paragraph(f"• {exercise.description}", self.styles['TaskText']))
            
            # Уровень сложности
            if hasattr(exercise, 'difficulty_level'):
                elements.append(Paragraph(f"• Уровень сложности: {exercise.difficulty_level}", self.styles['TaskText']))
            
            # Ресурсы для практики
            if hasattr(exercise, 'practice_resources') and exercise.practice_resources:
                elements.append(Paragraph("Ресурсы для практики:", self.styles['ChecklistBody']))
                for resource in exercise.practice_resources:
                    elements.append(Paragraph(f"• {resource}", self.styles['TaskText']))
            
            elements.append(Spacer(1, 8))
        
        return elements
    
    def _create_success_factors_section(self, factors: List) -> List:
        """Создание секции критических факторов успеха"""
        elements = []
        elements.append(Paragraph("Критические Факторы Успеха", self.styles['SectionHeader']))
        
        for factor in factors:
            elements.append(Paragraph(f"• {factor}", self.styles['ChecklistBody']))
        
        return elements
    
    def _create_technical_skills_section(self, technical_skills: List) -> List:
        """Создание секции технических навыков (базовая версия)"""
        elements = []
        elements.append(Paragraph("Технические Навыки", self.styles['SectionHeader']))
        
        for skill in technical_skills:
            # Название навыка
            skill_name = getattr(skill, 'skill_name', 'Навык')
            elements.append(Paragraph(f"<b>{skill_name}</b>", self.styles['SubHeader']))
            
            # План изучения
            if hasattr(skill, 'study_plan'):
                elements.append(Paragraph(f"План изучения: {skill.study_plan}", self.styles['ChecklistBody']))
            
            # Текущий уровень
            if hasattr(skill, 'current_level_assessment'):
                elements.append(Paragraph(f"Текущий уровень: {skill.current_level_assessment}", self.styles['ChecklistBody']))
            
            # Приоритет
            if hasattr(skill, 'priority'):
                priority_val = skill.priority
                if hasattr(priority_val, 'value'):
                    priority_text = priority_val.value
                else:
                    priority_text = str(priority_val)
                priority_color = self.get_priority_color(priority_text)
                elements.append(Paragraph(f"<font color='{priority_color}'>Приоритет: {priority_text}</font>", self.styles['ChecklistBody']))
            
            # Ресурсы
            if hasattr(skill, 'resources') and skill.resources:
                elements.append(Paragraph("Ресурсы:", self.styles['ChecklistBody']))
                for resource in skill.resources:
                    resource_title = getattr(resource, 'title', str(resource))
                    elements.append(Paragraph(f"• {resource_title}", self.styles['TaskText']))
            
            elements.append(Spacer(1, 8))
        
        return elements
    
    def _create_behavioral_questions_section(self, behavioral_questions: List) -> List:
        """Создание секции поведенческих вопросов (базовая версия)"""
        elements = []
        elements.append(Paragraph("Поведенческие Вопросы", self.styles['SectionHeader']))
        
        for question_group in behavioral_questions:
            # Категория вопросов
            category = getattr(question_group, 'question_category', 'Вопросы')
            elements.append(Paragraph(f"<b>{category}</b>", self.styles['SubHeader']))
            
            # Примеры вопросов
            if hasattr(question_group, 'example_questions') and question_group.example_questions:
                elements.append(Paragraph("Примеры вопросов:", self.styles['ChecklistBody']))
                for question in question_group.example_questions:
                    elements.append(Paragraph(f"• {question}", self.styles['TaskText']))
            
            # Советы по подготовке
            if hasattr(question_group, 'preparation_tips'):
                elements.append(Paragraph("Советы по подготовке:", self.styles['ChecklistBody']))
                elements.append(Paragraph(question_group.preparation_tips, self.styles['TaskText']))
            
            # STAR метод примеры
            if hasattr(question_group, 'star_method_examples') and question_group.star_method_examples:
                elements.append(Paragraph("Примеры STAR метода:", self.styles['ChecklistBody']))
                elements.append(Paragraph(question_group.star_method_examples, self.styles['TaskText']))
            
            elements.append(Spacer(1, 8))
        
        return elements