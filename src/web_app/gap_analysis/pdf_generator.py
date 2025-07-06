"""
PDF генератор для отчетов гап-анализа резюме

Генерирует профессиональные PDF отчеты с результатами анализа соответствия
резюме требованиям вакансии на основе данных от LLMGapAnalyzer.
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


class GapAnalysisPDFGenerator:
    """Генератор PDF отчетов для гап-анализа резюме"""
    
    def __init__(self):
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()
        self.register_fonts()
        self.setup_custom_styles()
        
        # Цветовая схема
        self.colors = {
            'primary': colors.HexColor('#2E3A87'),      # Темно-синий
            'secondary': colors.HexColor('#4A90E2'),    # Светло-синий
            'success': colors.HexColor('#27AE60'),      # Зеленый
            'warning': colors.HexColor('#F39C12'),      # Оранжевый
            'danger': colors.HexColor('#E74C3C'),       # Красный
            'light_gray': colors.HexColor('#F8F9FA'),   # Светло-серый
            'dark_gray': colors.HexColor('#6C757D'),    # Темно-серый
            'text': colors.HexColor('#2C3E50')          # Темный текст
        }
    
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
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
                    break
            else:
                # Если шрифт не найден, используем стандартный
                print("Warning: DejaVu Sans font not found, using default font")
        except Exception as e:
            print(f"Font registration error: {e}")
    
    def setup_custom_styles(self):
        """Настройка пользовательских стилей"""
        # Заголовок документа
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontName='DejaVuSans',
            fontSize=20,
            textColor=self.colors['primary'],
            spaceAfter=24,
            alignment=1  # Center
        ))
        
        # Заголовок раздела
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontName='DejaVuSans',
            fontSize=14,
            textColor=self.colors['primary'],
            spaceBefore=16,
            spaceAfter=8,
            borderWidth=0,
            borderColor=self.colors['primary'],
            borderPadding=4
        ))
        
        # Подзаголовок
        self.styles.add(ParagraphStyle(
            name='SubHeader',
            parent=self.styles['Heading2'],
            fontName='DejaVuSans',
            fontSize=12,
            textColor=self.colors['secondary'],
            spaceBefore=12,
            spaceAfter=6
        ))
        
        # Основной текст
        self.styles.add(ParagraphStyle(
            name='CustomBody',
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
    
    def generate_pdf(self, analysis_result) -> io.BytesIO:
        """Генерация PDF отчета"""
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
        story.append(Paragraph("Отчет Гап-Анализа Резюме", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        # Основные результаты
        story.extend(self._create_summary_section(analysis_result))
        story.append(Spacer(1, 16))
        
        # Первичный скрининг
        story.extend(self._create_screening_section(analysis_result))
        story.append(Spacer(1, 16))
        
        # Анализ требований
        story.extend(self._create_requirements_section(analysis_result))
        story.append(Spacer(1, 16))
        
        # Оценка качества
        story.extend(self._create_quality_section(analysis_result))
        story.append(Spacer(1, 16))
        
        # Рекомендации
        story.extend(self._create_recommendations_section(analysis_result))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _create_summary_section(self, analysis_result) -> List:
        """Создание секции с основными результатами"""
        elements = []
        
        elements.append(Paragraph("Основные Результаты", self.styles['SectionHeader']))
        
        # Таблица с ключевыми метриками
        data = [
            ['Показатель', 'Значение'],
            ['Общий процент соответствия', f"{analysis_result.overall_match_percentage}%"],
            ['Рекомендация по найму', analysis_result.hiring_recommendation],
            ['Ключевые сильные стороны', ', '.join(analysis_result.key_strengths[:3])],
            ['Основные пробелы', ', '.join(analysis_result.major_gaps[:3])]
        ]
        
        table = Table(data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(table)
        return elements
    
    def _create_screening_section(self, analysis_result) -> List:
        """Создание секции первичного скрининга"""
        elements = []
        
        elements.append(Paragraph("Первичный Скрининг", self.styles['SectionHeader']))
        
        screening = analysis_result.primary_screening
        
        # Таблица результатов скрининга
        data = [
            ['Критерий', 'Результат'],
            ['Общий результат', screening.overall_screening_result],
            ['Соответствие должности', screening.job_title_match],
            ['Соответствие опыта', screening.experience_years_match],
            ['Видимость ключевых навыков', screening.key_skills_visible],
            ['Подходящая локация', screening.location_suitable],
            ['Соответствие зарплатных ожиданий', screening.salary_expectations_match]
        ]
        
        table = Table(data, colWidths=[3*inch, 3*inch])
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
        
        # Примечания к скринингу
        if screening.screening_notes:
            elements.append(Spacer(1, 8))
            elements.append(Paragraph("Примечания:", self.styles['SubHeader']))
            elements.append(Paragraph(screening.screening_notes, self.styles['CustomBody']))
        
        return elements
    
    def _create_requirements_section(self, analysis_result) -> List:
        """Создание секции анализа требований"""
        elements = []
        
        elements.append(Paragraph("Анализ Требований", self.styles['SectionHeader']))
        
        for req in analysis_result.requirements_analysis[:10]:  # Ограничиваем до 10 требований
            elements.append(Paragraph(f"<b>{req.requirement_text}</b>", self.styles['SubHeader']))
            
            req_data = [
                ['Тип требования', req.requirement_type],
                ['Статус соответствия', req.compliance_status],
                ['Подтверждение в резюме', req.evidence_in_resume[:200] + '...' if len(req.evidence_in_resume) > 200 else req.evidence_in_resume],
                ['Описание пробела', req.gap_description[:200] + '...' if len(req.gap_description) > 200 else req.gap_description],
                ['Влияние на решение', req.impact_on_decision]
            ]
            
            req_table = Table(req_data, colWidths=[2*inch, 4*inch])
            req_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), self.colors['light_gray']),
                ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ]))
            
            elements.append(req_table)
            elements.append(Spacer(1, 8))
        
        return elements
    
    def _create_quality_section(self, analysis_result) -> List:
        """Создание секции оценки качества"""
        elements = []
        
        elements.append(Paragraph("Оценка Качества Резюме", self.styles['SectionHeader']))
        
        quality = analysis_result.quality_assessment
        
        # Таблица оценок качества
        data = [
            ['Аспект', 'Оценка'],
            ['Четкость структуры', quality.structure_clarity],
            ['Релевантность контента', quality.content_relevance],
            ['Фокус на достижения', quality.achievement_focus],
            ['Качество адаптации', quality.adaptation_quality],
            ['Общее впечатление', quality.overall_impression]
        ]
        
        table = Table(data, colWidths=[3*inch, 3*inch])
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
        
        # Примечания к качеству
        if quality.quality_notes:
            elements.append(Spacer(1, 8))
            elements.append(Paragraph("Примечания к качеству:", self.styles['SubHeader']))
            elements.append(Paragraph(quality.quality_notes, self.styles['CustomBody']))
        
        return elements
    
    def _create_recommendations_section(self, analysis_result) -> List:
        """Создание секции рекомендаций"""
        elements = []
        
        elements.append(Paragraph("Рекомендации по Улучшению", self.styles['SectionHeader']))
        
        # Критичные рекомендации
        if analysis_result.critical_recommendations:
            elements.append(Paragraph("Критичные рекомендации:", self.styles['SubHeader']))
            for rec in analysis_result.critical_recommendations:
                elements.append(Paragraph(f"<b>{rec.section}</b> - {rec.issue_description}", self.styles['CustomBody']))
                elements.append(Paragraph(f"Действия: {rec.specific_actions}", self.styles['CustomBody']))
                elements.append(Spacer(1, 4))
        
        # Важные рекомендации
        if analysis_result.important_recommendations:
            elements.append(Paragraph("Важные рекомендации:", self.styles['SubHeader']))
            for rec in analysis_result.important_recommendations:
                elements.append(Paragraph(f"<b>{rec.section}</b> - {rec.issue_description}", self.styles['CustomBody']))
                elements.append(Paragraph(f"Действия: {rec.specific_actions}", self.styles['CustomBody']))
                elements.append(Spacer(1, 4))
        
        # Следующие шаги
        if analysis_result.next_steps:
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("Рекомендуемые Следующие Шаги:", self.styles['SubHeader']))
            for step in analysis_result.next_steps:
                elements.append(Paragraph(f"• {step}", self.styles['CustomBody']))
        
        return elements