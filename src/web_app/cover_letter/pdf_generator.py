"""
PDF генератор для сопроводительных писем

Генерирует профессиональные PDF с сопроводительными письмами
на основе данных от LLMCoverLetterGenerator.
"""

import io
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import Any, Dict, List
import os


class CoverLetterPDFGenerator:
    """Генератор PDF для сопроводительных писем"""
    
    def __init__(self):
        # Цветовая схема (должна быть первой!)
        self.colors = {
            'primary': colors.HexColor('#2C5282'),      # Темно-синий
            'secondary': colors.HexColor('#3182CE'),    # Синий
            'accent': colors.HexColor('#38A169'),       # Зеленый
            'warning': colors.HexColor('#D69E2E'),      # Оранжевый
            'light_blue': colors.HexColor('#EBF8FF'),   # Светло-голубой
            'light_gray': colors.HexColor('#F7FAFC'),   # Светло-серый
            'dark_gray': colors.HexColor('#4A5568'),    # Темно-серый
            'text': colors.HexColor('#2D3748')          # Темный текст
        }
        
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()
        self.register_fonts()
        self.setup_custom_styles()
    
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
            name='CoverLetterTitle',
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
        
        # Основной текст письма
        self.styles.add(ParagraphStyle(
            name='LetterBody',
            parent=self.styles['Normal'],
            fontName='DejaVuSans',
            fontSize=11,
            textColor=self.colors['text'],
            spaceBefore=6,
            spaceAfter=6,
            leading=16,
            leftIndent=0,
            rightIndent=0
        ))
        
        # Текст анализа
        self.styles.add(ParagraphStyle(
            name='AnalysisText',
            parent=self.styles['Normal'],
            fontName='DejaVuSans',
            fontSize=10,
            textColor=self.colors['text'],
            spaceBefore=4,
            spaceAfter=4,
            leading=14
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
    
    def generate_pdf(self, cover_letter_result) -> io.BytesIO:
        """Генерация PDF сопроводительного письма"""
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
        story.append(Paragraph("Сопроводительное Письмо", self.styles['CoverLetterTitle']))
        story.append(Spacer(1, 12))
        
        # Основное письмо
        story.extend(self._create_letter_section(cover_letter_result))
        story.append(Spacer(1, 24))
        
        # Анализ письма
        story.extend(self._create_analysis_section(cover_letter_result))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _create_letter_section(self, cover_letter_result) -> List:
        """Создание секции с самим письмом"""
        elements = []
        
        elements.append(Paragraph("Текст Сопроводительного Письма", self.styles['SectionHeader']))
        elements.append(Spacer(1, 8))
        
        # Тема письма
        if hasattr(cover_letter_result, 'subject_line') and cover_letter_result.subject_line:
            elements.append(Paragraph(f"<b>Тема:</b> {cover_letter_result.subject_line}", self.styles['LetterBody']))
            elements.append(Spacer(1, 12))
        
        # Приветствие
        if hasattr(cover_letter_result, 'personalized_greeting') and cover_letter_result.personalized_greeting:
            elements.append(Paragraph(cover_letter_result.personalized_greeting, self.styles['LetterBody']))
            elements.append(Spacer(1, 8))
        
        # Основные части письма
        letter_parts = [
            ('opening_hook', 'Вступительный хук'),
            ('company_interest', 'Интерес к компании'),
            ('relevant_experience', 'Релевантный опыт'),
            ('value_demonstration', 'Демонстрация ценности'),
            ('growth_mindset', 'Настрой на развитие'),
            ('professional_closing', 'Профессиональное закрытие')
        ]
        
        for attr_name, section_name in letter_parts:
            if hasattr(cover_letter_result, attr_name):
                content = getattr(cover_letter_result, attr_name)
                if content and content.strip():
                    elements.append(Paragraph(content, self.styles['LetterBody']))
                    elements.append(Spacer(1, 8))
        
        # Подпись
        if hasattr(cover_letter_result, 'signature') and cover_letter_result.signature:
            elements.append(Spacer(1, 8))
            elements.append(Paragraph(cover_letter_result.signature, self.styles['LetterBody']))
        
        return elements
    
    def _create_analysis_section(self, cover_letter_result) -> List:
        """Создание секции с анализом письма"""
        elements = []
        
        elements.append(Paragraph("Анализ Сопроводительного Письма", self.styles['SectionHeader']))
        elements.append(Spacer(1, 8))
        
        # Контекст компании
        if hasattr(cover_letter_result, 'company_context'):
            elements.extend(self._create_company_context_table(cover_letter_result.company_context))
            elements.append(Spacer(1, 12))
        
        # Соответствие навыков
        if hasattr(cover_letter_result, 'skills_match'):
            elements.extend(self._create_skills_match_table(cover_letter_result.skills_match))
            elements.append(Spacer(1, 12))
        
        # Персонализация
        if hasattr(cover_letter_result, 'personalization'):
            elements.extend(self._create_personalization_table(cover_letter_result.personalization))
            elements.append(Spacer(1, 12))
        
        # Оценка качества
        elements.extend(self._create_quality_assessment_table(cover_letter_result))
        
        return elements
    
    def _create_company_context_table(self, company_context) -> List:
        """Создание таблицы контекста компании"""
        elements = []
        elements.append(Paragraph("Контекст Компании", self.styles['SubHeader']))
        
        data = [
            ['Параметр', 'Значение'],
            ['Название компании', getattr(company_context, 'company_name', 'Не указано')],
            ['Размер компании', getattr(company_context, 'company_size', 'Не указано')],
            ['Тип роли', getattr(company_context, 'role_type', 'Не указано')]
        ]
        
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
    
    def _create_skills_match_table(self, skills_match) -> List:
        """Создание таблицы соответствия навыков"""
        elements = []
        elements.append(Paragraph("Соответствие Навыков", self.styles['SubHeader']))
        
        # Преобразуем список навыков в строку, если это список
        matched_skills = getattr(skills_match, 'matched_skills', [])
        if isinstance(matched_skills, list):
            matched_skills_str = ', '.join(matched_skills)
        else:
            matched_skills_str = str(matched_skills)
        
        data = [
            ['Параметр', 'Значение'],
            ['Соответствующие навыки', matched_skills_str],
            ['Релевантный опыт', getattr(skills_match, 'relevant_experience', 'Не указано')],
            ['Количественные достижения', getattr(skills_match, 'quantified_achievement', 'Не указано')]
        ]
        
        table = Table(data, colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['secondary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(table)
        return elements
    
    def _create_personalization_table(self, personalization) -> List:
        """Создание таблицы персонализации"""
        elements = []
        elements.append(Paragraph("Персонализация", self.styles['SubHeader']))
        
        data = [
            ['Параметр', 'Значение'],
            ['Ценностное предложение', getattr(personalization, 'value_proposition', 'Не указано')],
            ['Мотивация роли', getattr(personalization, 'role_motivation', 'Не указано')],
            ['Знание компании', getattr(personalization, 'company_knowledge', 'Не указано')]
        ]
        
        table = Table(data, colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['accent']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(table)
        return elements
    
    def _create_quality_assessment_table(self, cover_letter_result) -> List:
        """Создание таблицы оценки качества"""
        elements = []
        elements.append(Paragraph("Оценка Качества", self.styles['SubHeader']))
        
        data = [
            ['Метрика', 'Оценка'],
            ['Оценка персонализации', f"{getattr(cover_letter_result, 'personalization_score', 'Н/Д')}/10"],
            ['Оценка релевантности', f"{getattr(cover_letter_result, 'relevance_score', 'Н/Д')}/10"],
            ['Оценка профессионального тона', f"{getattr(cover_letter_result, 'professional_tone_score', 'Н/Д')}/10"]
        ]
        
        # Добавляем предложения по улучшению, если есть
        if hasattr(cover_letter_result, 'improvement_suggestions') and cover_letter_result.improvement_suggestions:
            suggestions = cover_letter_result.improvement_suggestions
            if isinstance(suggestions, list):
                suggestions_str = '; '.join(suggestions)
            else:
                suggestions_str = str(suggestions)
            data.append(['Предложения по улучшению', suggestions_str])
        
        table = Table(data, colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['warning']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(table)
        return elements