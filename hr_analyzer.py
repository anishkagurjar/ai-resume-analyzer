import streamlit as st
import os
import re
from utils.parser import extract_text_from_pdf
from utils.analyzer import analyze_resume
from utils.report_generator import extract_resume_data, generate_modern_template
from dotenv import load_dotenv

load_dotenv()

# ─── HR Report Generator ───────────────────────────────────────────────────────
def generate_hr_report(candidates, job_description):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    import io

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=0.75*inch, leftMargin=0.75*inch,
        topMargin=0.75*inch, bottomMargin=0.75*inch
    )
    story = []

    # Title
    title_style = ParagraphStyle(
        'Title', fontSize=20, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=4, alignment=TA_CENTER
    )
    sub_style = ParagraphStyle(
        'Sub', fontSize=10, fontName='Helvetica',
        textColor=colors.HexColor('#7F8C8D'),
        spaceAfter=16, alignment=TA_CENTER
    )
    section_style = ParagraphStyle(
        'Section', fontSize=13, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#2980B9'),
        spaceAfter=6, spaceBefore=14
    )
    body_style = ParagraphStyle(
        'Body', fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=3, leading=14
    )
    rank_style = ParagraphStyle(
        'Rank', fontSize=11, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#27AE60'),
        spaceAfter=4, spaceBefore=10
    )

    story.append(Paragraph('HR Candidate Screening Report', title_style))
    story.append(Paragraph(f'Job: {job_description[:80]}...', sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2980B9')))
    story.append(Spacer(1, 12))

    # Summary Table
    story.append(Paragraph('Candidate Rankings', section_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#BDC3C7')))
    story.append(Spacer(1, 8))

    table_data = [['Rank', 'Candidate', 'Score', 'Recommendation']]
    sorted_candidates = sorted(candidates, key=lambda x: x['score'], reverse=True)

    for i, c in enumerate(sorted_candidates):
        rank = f"#{i+1}"
        name = c['name'][:20]
        score = f"{c['score']}/100"
        if c['score'] >= 70:
            rec = "✓ Recommended"
        elif c['score'] >= 50:
            rec = "~ Consider"
        else:
            rec = "✗ Not Recommended"
        table_data.append([rank, name, score, rec])

    table = Table(table_data, colWidths=[1*inch, 2.5*inch, 1.2*inch, 2.3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2980B9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#EBF5FB'), colors.white]),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 16))

    # Individual Reports
    story.append(Paragraph('Detailed Candidate Analysis', section_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#BDC3C7')))

    for i, c in enumerate(sorted_candidates):
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"#{i+1} — {c['name']} | Score: {c['score']}/100", rank_style))
        story.append(HRFlowable(width="100%", thickness=0.3, color=colors.HexColor('#BDC3C7')))
        story.append(Spacer(1, 4))

        # SWOT
        for line in c['analysis'].split('\n'):
            if line.strip():
                story.append(Paragraph(line.strip()[:200], body_style))

        story.append(Spacer(1, 8))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ─── Main App ─────────────────────────────────────────────────────────────────
def show_hr_mode(api_key, model_choice):

    st.markdown("""
        <div style='background: linear-gradient(135deg, #1a1a2e, #16213e);
        padding: 2rem; border-radius: 15px; text-align: center; margin-bottom: 2rem;'>
            <h1 style='color: white; margin:0;'>👔 HR Screening Mode</h1>
            <p style='color: #a0aec0; margin:0.5rem 0 0 0;'>
                Upload multiple resumes and find the best candidate!
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Job Description
    st.subheader("📋 Job Description")
    job_description = st.text_area(
        "Paste Job Description Here",
        height=150,
        placeholder="Paste the job description here...",
        key="hr_job_desc"
    )

    st.markdown("---")

    # Upload Multiple Resumes
    st.subheader("📤 Upload Resumes (Multiple)")
    uploaded_files = st.file_uploader(
        "Upload up to 10 resumes",
        type=["pdf"],
        accept_multiple_files=True,
        key="hr_resumes"
    )

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} resume(s) uploaded!")

        # Show uploaded files
        cols = st.columns(len(uploaded_files))
        for i, f in enumerate(uploaded_files):
            with cols[i]:
                st.markdown(f"""
                    <div style='background:#f0f4ff; padding:0.8rem;
                    border-radius:10px; text-align:center;'>
                        <b>📄 {f.name[:15]}...</b>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        if st.button("🔍 Analyze All Candidates", key="hr_analyze"):

            if not job_description:
                st.warning("⚠️ Please paste job description first!")
                return

            candidates = []
            os.makedirs("uploads", exist_ok=True)

            progress = st.progress(0)
            status = st.empty()

            for i, uploaded_file in enumerate(uploaded_files):
                status.info(f"🤖 Analyzing {uploaded_file.name}... ({i+1}/{len(uploaded_files)})")

                # Save file
                file_path = os.path.join("uploads", uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Extract text
                resume_text = extract_text_from_pdf(file_path)

                # AI Analysis
                analysis = analyze_resume(
                    resume_text,
                    job_description,
                    model_choice,
                    api_key
                )

                # Extract score
                match = re.search(r"(\d+)\s*/\s*100", analysis)
                score = int(match.group(1)) if match else 0

                # Extract name
                name = uploaded_file.name.replace('.pdf', '').replace('_', ' ')

                candidates.append({
                    'name': name,
                    'score': score,
                    'analysis': analysis,
                    'resume_text': resume_text
                })

                progress.progress((i + 1) / len(uploaded_files))

            status.success("✅ All candidates analyzed!")

            # Save to session
            st.session_state['hr_candidates'] = candidates
            st.session_state['hr_job'] = job_description

        # Show Results
        if 'hr_candidates' in st.session_state:
            candidates = st.session_state['hr_candidates']
            sorted_candidates = sorted(candidates, key=lambda x: x['score'], reverse=True)

            st.markdown("---")
            st.markdown("<h2 style='text-align:center;'>🏆 Candidate Rankings</h2>", unsafe_allow_html=True)

            # Rankings
            for i, c in enumerate(sorted_candidates):
                if i == 0:
                    color = "#27AE60"
                    badge = "🥇 Best Candidate"
                elif i == 1:
                    color = "#2980B9"
                    badge = "🥈 Second Best"
                elif i == 2:
                    color = "#E67E22"
                    badge = "🥉 Third Best"
                else:
                    color = "#7F8C8D"
                    badge = f"#{i+1}"

                with st.expander(f"{badge} — {c['name']} | Score: {c['score']}/100"):
                    st.progress(c['score'] / 100)
                    st.markdown(c['analysis'])

            st.markdown("---")

            # Best Candidate
            best = sorted_candidates[0]
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, #27AE60, #2ECC71);
                padding: 1.5rem; border-radius: 15px; text-align: center; color: white;'>
                    <h2>🏆 Best Candidate: {best['name']}</h2>
                    <h3>Score: {best['score']}/100</h3>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Download Report
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                report = generate_hr_report(
                    candidates,
                    st.session_state['hr_job']
                )
                st.download_button(
                    label="📥 Download HR Report PDF",
                    data=report,
                    file_name="hr_screening_report.pdf",
                    mime="application/pdf",
                    key="hr_report"
                )