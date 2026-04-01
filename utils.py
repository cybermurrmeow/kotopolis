import pandas as pd
from datetime import date
from io import BytesIO
import os

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm


# Регистрация шрифта для кириллицы
try:
    pdfmetrics.registerFont(TTFont('Arial', 'C:\\Windows\\Fonts\\arial.ttf'))
    FONT_NAME = 'Arial'
except:
    try:
        pdfmetrics.registerFont(TTFont('DejaVu', 'C:\\Windows\\Fonts\\DejaVuSans.ttf'))
        FONT_NAME = 'DejaVu'
    except:
        FONT_NAME = 'Helvetica'


def get_days_in_shelter(cat):
    """Рассчитывает количество дней в приюте"""
    if cat.arrival_date:
        return (date.today() - cat.arrival_date).days
    return 0


def export_to_excel(cats):
    """Экспорт данных в Excel"""
    data = []
    for cat in cats:
        data.append({
            'ID': cat.id,
            'Имя': cat.name,
            'Кличка': cat.nickname or '-',
            'Возраст (мес)': cat.age if cat.age else '-',
            'Возраст (лет)': f"{cat.age/12:.1f}" if cat.age else '-',
            'Порода': cat.breed or '-',
            'Пол': cat.gender or '-',
            'Окрас': cat.color or '-',
            'Вес (кг)': cat.weight if cat.weight else '-',
            'Настроение': cat.mood or '-',
            'Любимая игрушка': cat.favorite_toy or '-',
            'Статус': cat.status,
            'Дней в приюте': get_days_in_shelter(cat),
            'Здоровье': cat.health or '-',
            'Последняя прививка': cat.last_vacc_date.strftime('%d.%m.%Y') if cat.last_vacc_date else '-',
            'Следующая прививка': cat.next_vacc_date.strftime('%d.%m.%Y') if cat.next_vacc_date else '-',
            'Вакцинирован': 'Да' if cat.is_vaccinated else 'Нет',
            'Стерилизован': 'Да' if cat.is_sterilized else 'Нет',
            'Дата поступления': cat.arrival_date.strftime('%d.%m.%Y') if cat.arrival_date else '-',
            'Характер': cat.personality or '-',
            'Уровень активности': cat.activity_level or '-',
            'С детьми': 'Да' if cat.kids_friendly else 'Нет',
            'С кошками': 'Да' if cat.cats_friendly else 'Нет',
            'С собаками': 'Да' if cat.dogs_friendly else 'Нет',
            'Любимое место': cat.favorite_place or '-',
            'Особенности питания': cat.food_preferences or '-',
            'Голос': cat.vocal or '-',
        })
    
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Коты', index=False)
        
        stats_data = {
            'Показатель': ['Всего котов', 'В приюте', 'Усыновлено', 'На лечении', 'В карантине', 'Вакцинировано', 'Стерилизовано'],
            'Количество': [
                len(cats),
                sum(1 for c in cats if c.status == 'В приюте'),
                sum(1 for c in cats if c.status == 'Усыновлён'),
                sum(1 for c in cats if c.status == 'На лечении'),
                sum(1 for c in cats if c.status == 'В карантине'),
                sum(1 for c in cats if c.is_vaccinated),
                sum(1 for c in cats if c.is_sterilized)
            ]
        }
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_excel(writer, sheet_name='Статистика', index=False)
    
    output.seek(0)
    return output


def generate_pdf_report(cats, title="Отчёт Котополис"):
    """Генерация PDF отчёта"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    
    # Используем стандартный шрифт Helvetica (есть на Render)
    FONT_NAME = 'Helvetica'
    
    # Создаем стили с правильным шрифтом
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Normal'], fontSize=20,
        textColor=colors.HexColor('#FF69B4'), spaceAfter=20, alignment=1, fontName=FONT_NAME
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle', parent=styles['Normal'], fontSize=10,
        textColor=colors.grey, spaceAfter=30, alignment=1, fontName=FONT_NAME
    )
    
    section_style = ParagraphStyle(
        'Section', parent=styles['Normal'], fontSize=14,
        textColor=colors.HexColor('#FF69B4'), spaceAfter=12, spaceBefore=12,
        fontName=FONT_NAME, alignment=0
    )
    
    # Стиль для обычного текста
    normal_style = ParagraphStyle(
        'Normal', parent=styles['Normal'], fontName=FONT_NAME, fontSize=10
    )
    
    elements = []
    
    elements.append(Paragraph("KOTOPOLIS", title_style))  # Латинскими буквами
    elements.append(Paragraph(f"Report generated: {date.today().strftime('%d.%m.%Y')}", subtitle_style))
    elements.append(Spacer(1, 0.5*cm))
    
    total = len(cats)
    in_shelter = sum(1 for c in cats if c.status == 'В приюте')
    adopted = sum(1 for c in cats if c.status == 'Усыновлён')
    treatment = sum(1 for c in cats if c.status == 'На лечении')
    quarantine = sum(1 for c in cats if c.status == 'В карантине')
    
    stats_data = [
        ['Statistics', 'Count'],
        ['Total cats', str(total)],
        ['In shelter', str(in_shelter)],
        ['Adopted', str(adopted)],
        ['Treatment', str(treatment)],
        ['Quarantine', str(quarantine)]
    ]
    
    stats_table = Table(stats_data, colWidths=[8*cm, 4*cm])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF69B4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#FFB6C1')),
        ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Медицинская статистика
    elements.append(Paragraph("Medical Statistics", section_style))
    
    vaccinated = sum(1 for c in cats if c.is_vaccinated)
    sterilized = sum(1 for c in cats if c.is_sterilized)
    need_vacc_count = sum(1 for c in cats if not c.is_vaccinated or (c.last_vacc_date and (date.today() - c.last_vacc_date).days > 365))
    
    medical_data = [
        ['Indicator', 'Count', 'Percentage'],
        ['Vaccinated', str(vaccinated), f"{vaccinated/total*100:.1f}%" if total > 0 else '0%'],
        ['Sterilized', str(sterilized), f"{sterilized/total*100:.1f}%" if total > 0 else '0%'],
        ['Need vaccination', str(need_vacc_count), f"{need_vacc_count/total*100:.1f}%" if total > 0 else '0%']
    ]
    
    medical_table = Table(medical_data, colWidths=[6*cm, 3*cm, 3*cm])
    medical_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF69B4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_NAME),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#FFB6C1')),
        ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
    ]))
    
    elements.append(medical_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Список котов
    elements.append(Paragraph("Cats List", section_style))
    
    cats_data = [['Name', 'Age', 'Breed', 'Status', 'Days']]
    for cat in cats[:20]:
        age_str = f"{cat.age} months" if cat.age else '-'
        if cat.age and cat.age >= 12:
            age_str = f"{cat.age/12:.1f} years"
        cats_data.append([
            cat.name,
            age_str,
            cat.breed or '-',
            cat.status,
            str(get_days_in_shelter(cat))
        ])
    
    cats_table = Table(cats_data, colWidths=[4*cm, 2.5*cm, 4*cm, 3.5*cm, 2.5*cm])
    cats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF69B4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_NAME),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#FFB6C1')),
        ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
    ]))
    
    elements.append(cats_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def calculate_stats(cats):
    """Расчёт расширенной статистики"""
    total = len(cats)
    in_shelter = sum(1 for c in cats if c.status == 'В приюте')
    adopted = sum(1 for c in cats if c.status == 'Усыновлён')
    treatment = sum(1 for c in cats if c.status == 'На лечении')
    quarantine = sum(1 for c in cats if c.status == 'В карантине')
    
    # Возраст в месяцах
    kittens = sum(1 for c in cats if c.age is not None and c.age < 12)
    young = sum(1 for c in cats if c.age is not None and 12 <= c.age <= 36)
    adult = sum(1 for c in cats if c.age is not None and 36 < c.age <= 84)
    senior = sum(1 for c in cats if c.age is not None and c.age > 84)
    
    vaccinated = sum(1 for c in cats if c.is_vaccinated)
    sterilized = sum(1 for c in cats if c.is_sterilized)
    
    need_vacc = []
    today = date.today()
    for cat in cats:
        if cat.last_vacc_date and (today - cat.last_vacc_date).days > 365:
            need_vacc.append(cat)
        elif not cat.is_vaccinated:
            need_vacc.append(cat)
    
    moods = {}
    for cat in cats:
        if cat.mood:
            moods[cat.mood] = moods.get(cat.mood, 0) + 1
    
    # Средний возраст в годах
    ages_months = [c.age for c in cats if c.age is not None]
    avg_age_years = (sum(ages_months) / len(ages_months) / 12) if ages_months else 0
    
    return {
        'total': total,
        'in_shelter': in_shelter,
        'adopted': adopted,
        'treatment': treatment,
        'quarantine': quarantine,
        'kittens': kittens,
        'young': young,
        'adult': adult,
        'senior': senior,
        'vaccinated': vaccinated,
        'sterilized': sterilized,
        'need_vacc': need_vacc,
        'vaccination_rate': (vaccinated / total * 100) if total > 0 else 0,
        'sterilization_rate': (sterilized / total * 100) if total > 0 else 0,
        'moods': moods,
        'avg_age': avg_age_years
    }
# Force update Wed Apr  1 02:51:37 RTZ 2026
