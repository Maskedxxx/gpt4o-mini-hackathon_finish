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
        # Цветовая схема (должна быть первой!)
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
        # Безопасное получение атрибутов
        match_percentage = getattr(analysis_result, 'overall_match_percentage', 0) or 0
        hiring_rec = getattr(analysis_result, 'hiring_recommendation', 'Не указано') or 'Не указано'
        key_strengths = getattr(analysis_result, 'key_strengths', None) or []
        major_gaps = getattr(analysis_result, 'major_gaps', None) or []
        
        # Создаем данные с обёрнутыми в Paragraph элементами для переноса текста
        key_strengths_text = ', '.join(key_strengths[:3]) if key_strengths else 'Не указано'
        major_gaps_text = ', '.join(major_gaps[:3]) if major_gaps else 'Не указано'
        
        data = [
            [Paragraph('Показатель', self.styles['TableText']), Paragraph('Значение', self.styles['TableText'])],
            [Paragraph('Общий процент соответствия', self.styles['TableText']), Paragraph(f"{match_percentage}%", self.styles['TableText'])],
            [Paragraph('Рекомендация по найму', self.styles['TableText']), Paragraph(hiring_rec, self.styles['TableText'])],
            [Paragraph('Ключевые сильные стороны', self.styles['TableText']), Paragraph(key_strengths_text, self.styles['TableText'])],
            [Paragraph('Основные пробелы', self.styles['TableText']), Paragraph(major_gaps_text, self.styles['TableText'])]
        ]
        
        table = Table(data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['secondary']),  # Изменили на голубой
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
        
        screening = getattr(analysis_result, 'primary_screening', None)
        if not screening:
            elements.append(Paragraph("Нет данных по первичному скринингу", self.styles['CustomBody']))
            return elements
        
        # Таблица результатов скрининга с обёрнутым в Paragraph текстом
        data = [
            [Paragraph('Критерий', self.styles['TableText']), Paragraph('Результат', self.styles['TableText'])],
            [Paragraph('Общий результат', self.styles['TableText']), Paragraph(getattr(screening, 'overall_screening_result', 'Не указано') or 'Не указано', self.styles['TableText'])],
            [Paragraph('Соответствие должности', self.styles['TableText']), Paragraph(str(getattr(screening, 'job_title_match', 'Не указано')), self.styles['TableText'])],
            [Paragraph('Соответствие опыта', self.styles['TableText']), Paragraph(str(getattr(screening, 'experience_years_match', 'Не указано')), self.styles['TableText'])],
            [Paragraph('Видимость ключевых навыков', self.styles['TableText']), Paragraph(str(getattr(screening, 'key_skills_visible', 'Не указано')), self.styles['TableText'])],
            [Paragraph('Подходящая локация', self.styles['TableText']), Paragraph(str(getattr(screening, 'location_suitable', 'Не указано')), self.styles['TableText'])],
            [Paragraph('Соответствие зарплатных ожиданий', self.styles['TableText']), Paragraph(str(getattr(screening, 'salary_expectations_match', 'Не указано')), self.styles['TableText'])]
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
        screening_notes = getattr(screening, 'screening_notes', None)
        if screening_notes:
            elements.append(Spacer(1, 8))
            elements.append(Paragraph("Примечания:", self.styles['SubHeader']))
            elements.append(Paragraph(str(screening_notes), self.styles['CustomBody']))
        
        return elements
    
    def _create_requirements_section(self, analysis_result) -> List:
        """Создание секции анализа требований"""
        elements = []
        
        elements.append(Paragraph("Анализ Требований", self.styles['SectionHeader']))
        
        # Проверяем, что requirements_analysis не None
        requirements = getattr(analysis_result, 'requirements_analysis', None) or []
        
        for req in requirements[:10]:  # Ограничиваем до 10 требований
            req_text = getattr(req, 'requirement_text', 'Не указано') or 'Не указано'
            elements.append(Paragraph(f"<b>{req_text}</b>", self.styles['SubHeader']))
            
            # Безопасное получение атрибутов
            evidence = getattr(req, 'evidence_in_resume', '') or ''
            gap_desc = getattr(req, 'gap_description', '') or ''
            
            # Обрезаем длинные строки
            evidence_text = evidence[:200] + '...' if len(evidence) > 200 else evidence
            gap_text = gap_desc[:200] + '...' if len(gap_desc) > 200 else gap_desc
            
            # Получаем статус соответствия и извлекаем только значение enum
            compliance_status = getattr(req, 'compliance_status', 'Не указано')
            if hasattr(compliance_status, 'value'):
                compliance_status_text = compliance_status.value
            else:
                compliance_status_text = str(compliance_status) if compliance_status else 'Не указано'
            
            req_data = [
                [Paragraph('Тип требования', self.styles['TableText']), Paragraph(getattr(req, 'requirement_type', 'Не указано') or 'Не указано', self.styles['TableText'])],
                [Paragraph('Статус соответствия', self.styles['TableText']), Paragraph(compliance_status_text, self.styles['TableText'])],
                [Paragraph('Подтверждение в резюме', self.styles['TableText']), Paragraph(evidence_text, self.styles['TableText'])],
                [Paragraph('Описание пробела', self.styles['TableText']), Paragraph(gap_text, self.styles['TableText'])],
                [Paragraph('Влияние на решение', self.styles['TableText']), Paragraph(getattr(req, 'impact_on_decision', 'Не указано') or 'Не указано', self.styles['TableText'])]
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
        
        quality = getattr(analysis_result, 'quality_assessment', None)
        if not quality:
            elements.append(Paragraph("Нет данных по оценке качества", self.styles['CustomBody']))
            return elements
        
        # Таблица оценок качества с обёрнутым в Paragraph текстом
        data = [
            [Paragraph('Аспект', self.styles['TableText']), Paragraph('Оценка', self.styles['TableText'])],
            [Paragraph('Четкость структуры', self.styles['TableText']), Paragraph(str(getattr(quality, 'structure_clarity', 'Не указано')), self.styles['TableText'])],
            [Paragraph('Релевантность контента', self.styles['TableText']), Paragraph(str(getattr(quality, 'content_relevance', 'Не указано')), self.styles['TableText'])],
            [Paragraph('Фокус на достижения', self.styles['TableText']), Paragraph(str(getattr(quality, 'achievement_focus', 'Не указано')), self.styles['TableText'])],
            [Paragraph('Качество адаптации', self.styles['TableText']), Paragraph(str(getattr(quality, 'adaptation_quality', 'Не указано')), self.styles['TableText'])],
            [Paragraph('Общее впечатление', self.styles['TableText']), Paragraph(str(getattr(quality, 'overall_impression', 'Не указано')), self.styles['TableText'])]
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
        quality_notes = getattr(quality, 'quality_notes', None)
        if quality_notes:
            elements.append(Spacer(1, 8))
            elements.append(Paragraph("Примечания к качеству:", self.styles['SubHeader']))
            elements.append(Paragraph(str(quality_notes), self.styles['CustomBody']))
        
        return elements
    
    def _create_recommendations_section(self, analysis_result) -> List:
        """Создание секции рекомендаций"""
        elements = []
        
        elements.append(Paragraph("Рекомендации по Улучшению", self.styles['SectionHeader']))
        
        # Критичные рекомендации
        critical_recs = getattr(analysis_result, 'critical_recommendations', None) or []
        if critical_recs:
            elements.append(Paragraph("Критичные рекомендации:", self.styles['SubHeader']))
            for rec in critical_recs:
                section = getattr(rec, 'section', 'Не указано') or 'Не указано'
                issue = getattr(rec, 'issue_description', 'Не указано') or 'Не указано'
                actions = getattr(rec, 'specific_actions', 'Не указано') or 'Не указано'
                example_wording = getattr(rec, 'example_wording', '') or ''
                business_rationale = getattr(rec, 'business_rationale', '') or ''
                
                # Форматируем действия правильно (убираем квадратные скобки)
                if isinstance(actions, list):
                    actions_text = '; '.join(actions)
                else:
                    actions_text = str(actions)
                
                elements.append(Paragraph(f"<b>{section}</b> - {issue}", self.styles['CustomBody']))
                elements.append(Paragraph(f"Действия: {actions_text}", self.styles['CustomBody']))
                if example_wording:
                    elements.append(Paragraph(f"Пример формулировки: {example_wording}", self.styles['CustomBody']))
                if business_rationale:
                    elements.append(Paragraph(f"Бизнес-обоснование: {business_rationale}", self.styles['CustomBody']))
                elements.append(Spacer(1, 4))
        
        # Важные рекомендации
        important_recs = getattr(analysis_result, 'important_recommendations', None) or []
        if important_recs:
            elements.append(Paragraph("Важные рекомендации:", self.styles['SubHeader']))
            for rec in important_recs:
                section = getattr(rec, 'section', 'Не указано') or 'Не указано'
                issue = getattr(rec, 'issue_description', 'Не указано') or 'Не указано'
                actions = getattr(rec, 'specific_actions', 'Не указано') or 'Не указано'
                example_wording = getattr(rec, 'example_wording', '') or ''
                business_rationale = getattr(rec, 'business_rationale', '') or ''
                
                # Форматируем действия правильно (убираем квадратные скобки)
                if isinstance(actions, list):
                    actions_text = '; '.join(actions)
                else:
                    actions_text = str(actions)
                
                elements.append(Paragraph(f"<b>{section}</b> - {issue}", self.styles['CustomBody']))
                elements.append(Paragraph(f"Действия: {actions_text}", self.styles['CustomBody']))
                if example_wording:
                    elements.append(Paragraph(f"Пример формулировки: {example_wording}", self.styles['CustomBody']))
                if business_rationale:
                    elements.append(Paragraph(f"Бизнес-обоснование: {business_rationale}", self.styles['CustomBody']))
                elements.append(Spacer(1, 4))
        
        # Следующие шаги
        next_steps = getattr(analysis_result, 'next_steps', None)
        if next_steps:
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("Рекомендуемые Следующие Шаги:", self.styles['SubHeader']))
            
            # Проверяем тип next_steps - может быть строкой или списком
            if isinstance(next_steps, str):
                # Если это строка, выводим её как один элемент
                elements.append(Paragraph(f"• {next_steps}", self.styles['CustomBody']))
            elif isinstance(next_steps, list):
                # Если это список, выводим каждый элемент
                for step in next_steps:
                    step_text = str(step) if step else 'Не указано'
                    elements.append(Paragraph(f"• {step_text}", self.styles['CustomBody']))
            else:
                # В остальных случаях преобразуем в строку
                elements.append(Paragraph(f"• {str(next_steps)}", self.styles['CustomBody']))
        
        return elements