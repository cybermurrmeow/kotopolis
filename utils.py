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
    
    elements = []
    
    elements.append(Paragraph("КОТОПОЛИС", title_style))
    elements.append(Paragraph(f"Отчёт сгенерирован: {date.today().strftime('%d.%m.%Y')}", subtitle_style))
    elements.append(Spacer(1, 0.5*cm))
    
    total = len(cats)
    in_shelter = sum(1 for c in cats if c.status == 'В приюте')
    adopted = sum(1 for c in cats if c.status == 'Усыновлён')
    treatment = sum(1 for c in cats if c.status == 'На лечении')
    quarantine = sum(1 for c in cats if c.status == 'В карантине')
    
    stats_data = [
        ['Показатель', 'Количество'],
        ['Всего котиков', str(total)],
        ['В приюте', str(in_shelter)],
        ['Усыновлены', str(adopted)],
        ['На лечении', str(treatment)],
        ['В карантине', str(quarantine)]
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
    
    # Возрастные группы (возраст в годах)
    elements.append(Paragraph("Возрастные группы", section_style))
    
    kittens = sum(1 for c in cats if c.age is not None and c.age < 12)  # <1 года = <12 месяцев
    young = sum(1 for c in cats if c.age is not None and 12 <= c.age <= 36)  # 1-3 года
    adult = sum(1 for c in cats if c.age is not None and 36 < c.age <= 84)  # 4-7 лет
    senior = sum(1 for c in cats if c.age is not None and c.age > 84)  # 8+ лет
    
    age_data = [
        ['Категория', 'Количество', 'Процент'],
        ['Котята (до 1 года)', str(kittens), f"{kittens/total*100:.1f}%" if total > 0 else '0%'],
        ['Молодые (1-3 года)', str(young), f"{young/total*100:.1f}%" if total > 0 else '0%'],
        ['Взрослые (4-7 лет)', str(adult), f"{adult/total*100:.1f}%" if total > 0 else '0%'],
        ['Пожилые (8+ лет)', str(senior), f"{senior/total*100:.1f}%" if total > 0 else '0%']
    ]
    
    age_table = Table(age_data, colWidths=[6*cm, 3*cm, 3*cm])
    age_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF69B4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#FFB6C1')),
        ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
    ]))
    
    elements.append(age_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Медицинская статистика
    elements.append(Paragraph("Медицинская статистика", section_style))
    
    vaccinated = sum(1 for c in cats if c.is_vaccinated)
    sterilized = sum(1 for c in cats if c.is_sterilized)
    need_vacc_count = sum(1 for c in cats if not c.is_vaccinated or (c.last_vacc_date and (date.today() - c.last_vacc_date).days > 365))
    
    medical_data = [
        ['Показатель', 'Количество', 'Процент'],
        ['Вакцинированы', str(vaccinated), f"{vaccinated/total*100:.1f}%" if total > 0 else '0%'],
        ['Стерилизованы', str(sterilized), f"{sterilized/total*100:.1f}%" if total > 0 else '0%'],
        ['Требуют прививки', str(need_vacc_count), f"{need_vacc_count/total*100:.1f}%" if total > 0 else '0%']
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
    elements.append(Paragraph("Список всех котиков", section_style))
    
    cats_data = [['Имя', 'Возраст', 'Порода', 'Статус', 'Дней в приюте']]
    for cat in cats[:20]:
        age_str = f"{cat.age} мес." if cat.age else '-'
        if cat.age and cat.age >= 12:
            age_str = f"{cat.age/12:.1f} лет"
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
