from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io
import re


def clean(text):
    if not text:
        return ''
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text.strip()


def extract_name(resume_text):
    # Common name patterns in resumes
    lines = [l.strip() for l in resume_text.split('\n') if l.strip()]

    # Try to find name - usually all caps or title case, no numbers
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if '@' in line or 'http' in line:
            continue
        if re.search(r'\d{4,}', line):
            continue
        if len(line.split()) > 5:
            continue
        cleaned = re.sub(r'[^a-zA-Z\s]', '', line).strip()
        cleaned = ' '.join(cleaned.split())
        if len(cleaned) > 3 and cleaned.replace(' ', '').isalpha():
            return cleaned

    # Try from end of document (some PDFs have name at bottom)
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        if '@' in line or 'http' in line:
            continue
        if re.search(r'\d{4,}', line):
            continue
        cleaned = re.sub(r'[^a-zA-Z\s]', '', line).strip()
        cleaned = ' '.join(cleaned.split())
        if len(cleaned) > 3 and len(cleaned.split()) <= 4:
            return cleaned

    return 'Your Name'


def extract_resume_data(resume_text, ai_result):
    lines = [l.strip() for l in resume_text.split('\n') if l.strip()]
    text_lower = resume_text.lower()

    # Name
    name = extract_name(resume_text)

    # Email
    email_match = re.search(r'[\w.\-]+@[\w.\-]+\.\w+', resume_text)
    email = email_match.group() if email_match else ''

    # Phone
    phone_match = re.search(r'[\+]?[\d][\d\s\-().]{8,15}', resume_text)
    phone = phone_match.group().strip() if phone_match else ''

    # Location
    location_match = re.search(
        r'([A-Z][a-z]+),?\s*(M\.?P\.?|Maharashtra|Delhi|Karnataka|Rajasthan|Gujarat|India)',
        resume_text
    )
    location = location_match.group() if location_match else 'India'

    def extract_section(text, start_keywords, end_keywords):
        start_idx = -1
        for kw in start_keywords:
            idx = text_lower.find(kw)
            if idx != -1:
                start_idx = idx
                break
        if start_idx == -1:
            return ''
        end_idx = len(text)
        for kw in end_keywords:
            idx = text_lower.find(kw, start_idx + 10)
            if idx != -1 and idx < end_idx:
                end_idx = idx
        section = text[start_idx:end_idx].strip()
        section_lines = section.split('\n')
        return '\n'.join(section_lines[1:]).strip()

    # Summary / Objective
    summary = extract_section(
        resume_text,
        ['career objective', 'objective', 'summary', 'profile', 'about me'],
        ['education', 'academic', 'experience', 'skills', 'project',
         'core competencies', 'competencies']
    )

    # Education
    education = extract_section(
        resume_text,
        ['education', 'academic record', 'qualification', 'academic background'],
        ['experience', 'skills', 'project', 'achievement', 'certificate',
         'core competencies', 'internship', 'training']
    )

    # Experience
    experience = extract_section(
        resume_text,
        ['experience', 'work experience', 'internship', 'training'],
        ['skills', 'project', 'achievement', 'education', 'certificate',
         'core competencies', 'strength', 'personal']
    )

    # Skills
    skills = extract_section(
        resume_text,
        ['skills', 'technical skills', 'key skills',
         'core competencies', 'competencies', 'technologies'],
        ['project', 'achievement', 'certificate', 'language',
         'hobby', 'strength', 'personal', 'declaration']
    )

    # Projects
    projects = extract_section(
        resume_text,
        ['project', 'projects'],
        ['achievement', 'certificate', 'language', 'hobby',
         'reference', 'strength', 'personal', 'declaration']
    )

    # Achievements
    achievements = extract_section(
        resume_text,
        ['achievement', 'accomplishment', 'community', 'extracurricular'],
        ['strength', 'personal', 'declaration', 'reference', 'language']
    )

    # Combine experience + projects
    exp_combined = ''
    if experience:
        exp_combined += experience
    if projects:
        exp_combined += '\n\nPROJECTS:\n' + projects
    if achievements:
        exp_combined += '\n\nACHIEVEMENTS & ACTIVITIES:\n' + achievements

    return {
        'name': name,
        'email': email,
        'phone': phone,
        'location': location,
        'summary': summary or '',
        'experience': exp_combined.strip(),
        'education': education,
        'skills': skills
    }


# ─── Template 1: Modern Professional ──────────────────────────────────────────
def generate_modern_template(resume_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=0.75*inch, leftMargin=0.75*inch,
        topMargin=0.75*inch, bottomMargin=0.75*inch
    )
    story = []

    name_style = ParagraphStyle(
        'Name', fontSize=24, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=4, alignment=TA_CENTER
    )
    story.append(Paragraph(clean(resume_data.get('name', 'Your Name')), name_style))

    contact_style = ParagraphStyle(
        'Contact', fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#7F8C8D'),
        spaceAfter=10, alignment=TA_CENTER
    )
    contact_parts = []
    if resume_data.get('email'): contact_parts.append(resume_data['email'])
    if resume_data.get('phone'): contact_parts.append(resume_data['phone'])
    if resume_data.get('location'): contact_parts.append(resume_data['location'])
    story.append(Paragraph(' | '.join(contact_parts), contact_style))

    story.append(HRFlowable(
        width="100%", thickness=2,
        color=colors.HexColor('#3498DB')
    ))
    story.append(Spacer(1, 10))

    section_style = ParagraphStyle(
        'Section', fontSize=11, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#3498DB'),
        spaceAfter=4, spaceBefore=10
    )
    body_style = ParagraphStyle(
        'Body', fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=3, leading=14
    )

    sections = [
        ('PROFESSIONAL SUMMARY', 'summary'),
        ('EXPERIENCE & PROJECTS', 'experience'),
        ('EDUCATION', 'education'),
        ('SKILLS', 'skills'),
    ]

    for title, key in sections:
        content = resume_data.get(key, '')
        if content:
            story.append(Paragraph(title, section_style))
            story.append(HRFlowable(
                width="100%", thickness=0.5,
                color=colors.HexColor('#BDC3C7')
            ))
            story.append(Spacer(1, 4))
            for line in content.split('\n'):
                if line.strip():
                    story.append(Paragraph(clean(line), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ─── Template 2: Creative Bold ────────────────────────────────────────────────
def generate_creative_template(resume_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=0.75*inch, leftMargin=0.75*inch,
        topMargin=0.75*inch, bottomMargin=0.75*inch
    )
    story = []

    name_style = ParagraphStyle(
        'Name', fontSize=26, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#6C3483'),
        spaceAfter=2, alignment=TA_LEFT
    )
    story.append(Paragraph(clean(resume_data.get('name', 'Your Name')), name_style))

    story.append(HRFlowable(
        width="100%", thickness=3,
        color=colors.HexColor('#6C3483')
    ))
    story.append(Spacer(1, 6))

    contact_style = ParagraphStyle(
        'Contact', fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#6C3483'), spaceAfter=12
    )
    contact_parts = []
    if resume_data.get('email'): contact_parts.append(resume_data['email'])
    if resume_data.get('phone'): contact_parts.append(resume_data['phone'])
    if resume_data.get('location'): contact_parts.append(resume_data['location'])
    story.append(Paragraph(' | '.join(contact_parts), contact_style))

    section_style = ParagraphStyle(
        'Section', fontSize=10, fontName='Helvetica-Bold',
        textColor=colors.white,
        spaceAfter=6, spaceBefore=10,
        backColor=colors.HexColor('#6C3483'),
        borderPadding=(4, 6, 4, 6)
    )
    body_style = ParagraphStyle(
        'Body', fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=3, leading=14
    )

    sections = [
        ('  PROFESSIONAL SUMMARY', 'summary'),
        ('  EXPERIENCE & PROJECTS', 'experience'),
        ('  EDUCATION', 'education'),
        ('  SKILLS', 'skills'),
    ]

    for title, key in sections:
        content = resume_data.get(key, '')
        if content:
            story.append(Paragraph(title, section_style))
            story.append(Spacer(1, 4))
            for line in content.split('\n'):
                if line.strip():
                    story.append(Paragraph(clean(line), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ─── Template 3: Minimal Clean ────────────────────────────────────────────────
def generate_minimal_template(resume_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=inch, leftMargin=inch,
        topMargin=inch, bottomMargin=inch
    )
    story = []

    name_style = ParagraphStyle(
        'Name', fontSize=22, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1A1A1A'),
        spaceAfter=4, alignment=TA_CENTER
    )
    story.append(Paragraph(clean(resume_data.get('name', 'Your Name')), name_style))

    contact_style = ParagraphStyle(
        'Contact', fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#666666'),
        spaceAfter=12, alignment=TA_CENTER
    )
    contact_parts = []
    if resume_data.get('email'): contact_parts.append(resume_data['email'])
    if resume_data.get('phone'): contact_parts.append(resume_data['phone'])
    if resume_data.get('location'): contact_parts.append(resume_data['location'])
    story.append(Paragraph(' | '.join(contact_parts), contact_style))

    story.append(HRFlowable(
        width="100%", thickness=1,
        color=colors.HexColor('#1A1A1A')
    ))
    story.append(Spacer(1, 10))

    section_style = ParagraphStyle(
        'Section', fontSize=10, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1A1A1A'),
        spaceAfter=4, spaceBefore=10
    )
    body_style = ParagraphStyle(
        'Body', fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#333333'),
        spaceAfter=3, leading=14
    )

    sections = [
        ('SUMMARY', 'summary'),
        ('EXPERIENCE & PROJECTS', 'experience'),
        ('EDUCATION', 'education'),
        ('SKILLS', 'skills'),
    ]

    for title, key in sections:
        content = resume_data.get(key, '')
        if content:
            story.append(Paragraph(title, section_style))
            story.append(HRFlowable(
                width="100%", thickness=0.3,
                color=colors.HexColor('#999999')
            ))
            story.append(Spacer(1, 4))
            for line in content.split('\n'):
                if line.strip():
                    story.append(Paragraph(clean(line), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer