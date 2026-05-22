"""
PDF_GENERATOR.PY
Professional PDF report generation with multi-language support
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, 
    TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

class PDFGenerator:
    def __init__(self):
        """Initialize PDF generator with styles"""
        print("📄 Initializing PDF generator...")
        
        self.styles = getSampleStyleSheet()
        
        # Custom title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=1,  # Center
            fontName='Helvetica-Bold'
        )
        
        # Heading style
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            fontName='Helvetica'
        )
        
        # Info style
        self.info_style = ParagraphStyle(
            'InfoStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7F8C8D'),
            fontName='Helvetica'
        )
        
        print("✅ PDF generator ready!")
    
    def generate_report(self, output_path, meeting_data):
        """
        Generate complete PDF report
        
        Parameters:
            output_path (str): Path where PDF will be saved
            meeting_data (dict): Meeting information
                {
                    'date': str,
                    'duration': str,
                    'language': str,
                    'summary': str,
                    'actions': list,
                    'decisions': list,
                    'full_text': str (optional)
                }
        """
        print(f"📄 Generating PDF report...")
        print(f"   Output: {output_path}")
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=50
        )
        
        # Story (content flow)
        story = []
        
        # === TITLE ===
        story.append(Paragraph("🎤 Meeting Notes", self.title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # === MEETING INFO ===
        meeting_info = f"""
        <b>Date:</b> {meeting_data.get('date', datetime.now().strftime('%B %d, %Y'))}<br/>
        <b>Duration:</b> {meeting_data.get('duration', 'N/A')}<br/>
        <b>Language:</b> {meeting_data.get('language', 'English')}<br/>
        <b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        """
        story.append(Paragraph(meeting_info, self.info_style))
        story.append(Spacer(1, 0.3*inch))
        
        # === EXECUTIVE SUMMARY ===
        story.append(Paragraph("📊 Executive Summary", self.heading_style))
        summary_text = meeting_data.get('summary', 'No summary available.')
        story.append(Paragraph(summary_text, self.normal_style))
        story.append(Spacer(1, 0.3*inch))
        
        # === ACTION ITEMS ===
        actions = meeting_data.get('actions', [])
        if actions:
            story.append(Paragraph("🎯 Action Items", self.heading_style))
            
            # Create table
            table_data = [['Priority', 'Task', 'Assignee']]
            
            for action in actions:
                priority = action.get('priority', 'Normal')
                
                # Priority with color
                if priority == 'High':
                    priority_cell = Paragraph(
                        f'<font color="red"><b>{priority}</b></font>',
                        self.normal_style
                    )
                elif priority == 'Medium':
                    priority_cell = Paragraph(
                        f'<font color="orange"><b>{priority}</b></font>',
                        self.normal_style
                    )
                else:
                    priority_cell = Paragraph(
                        f'<font color="green">{priority}</font>',
                        self.normal_style
                    )
                
                task_text = action.get('task', '')
                # Limit task length for table
                if len(task_text) > 100:
                    task_text = task_text[:100] + '...'
                
                table_data.append([
                    priority_cell,
                    Paragraph(task_text, self.normal_style),
                    action.get('assignee', 'Team')
                ])
            
            # Create and style table
            table = Table(
                table_data,
                colWidths=[1*inch, 4*inch, 1.3*inch]
            )
            
            table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                
                # Data rows
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.lightgrey]),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.3*inch))
        else:
            story.append(Paragraph("🎯 Action Items", self.heading_style))
            story.append(Paragraph("No action items identified.", self.normal_style))
            story.append(Spacer(1, 0.3*inch))
        
        # === KEY DECISIONS ===
        decisions = meeting_data.get('decisions', [])
        if decisions:
            story.append(Paragraph("💡 Key Decisions", self.heading_style))
            
            for i, decision in enumerate(decisions, 1):
                decision_text = f"{i}. {decision}"
                story.append(Paragraph(decision_text, self.normal_style))
                story.append(Spacer(1, 0.1*inch))
            
            story.append(Spacer(1, 0.2*inch))
        else:
            story.append(Paragraph("💡 Key Decisions", self.heading_style))
            story.append(Paragraph("No key decisions identified.", self.normal_style))
            story.append(Spacer(1, 0.3*inch))
        
        # === FULL TRANSCRIPT (Optional) ===
        full_text = meeting_data.get('full_text', '')
        if full_text and len(full_text) > 100:
            story.append(PageBreak())
            story.append(Paragraph("📝 Full Transcript", self.heading_style))
            
            # Split into paragraphs for better readability
            paragraphs = full_text.split('. ')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip() + '.', self.normal_style))
                    story.append(Spacer(1, 0.1*inch))
        
        # === FOOTER ===
        story.append(Spacer(1, 0.5*inch))
        footer_text = """
        <i>Generated by AI Meeting Notes Generator</i><br/>
        <i>Powered by OpenAI Whisper, Hugging Face Transformers, and Python</i>
        """
        story.append(Paragraph(footer_text, self.info_style))
        
        # Build PDF
        try:
            doc.build(story)
            print(f"✅ PDF saved successfully: {output_path}")
            print(f"   File size: {os.path.getsize(output_path) / 1024:.1f} KB")
            return True
        except Exception as e:
            print(f"❌ Error generating PDF: {e}")
            return False


# Test function
if __name__ == "__main__":
    print("\n" + "="*60)
    print("PDF GENERATOR MODULE TEST")
    print("="*60 + "\n")
    
    generator = PDFGenerator()
    
    # Sample data
    sample_data = {
        'date': 'December 20, 2024',
        'duration': '45 minutes',
        'language': 'English + Hindi',
        'summary': 'Team discussed Q4 roadmap and decided to prioritize dashboard redesign. Budget allocation was approved for hiring two developers.',
        'actions': [
            {
                'task': 'Complete dashboard redesign by end of week',
                'assignee': 'Sarah',
                'priority': 'High'
            },
            {
                'task': 'Fix API performance issues',
                'assignee': 'John',
                'priority': 'High'
            },
            {
                'task': 'Prepare marketing campaign materials',
                'assignee': 'Marketing Team',
                'priority': 'Medium'
            }
        ],
        'decisions': [
            'Approved budget for two new developer positions',
            'Marketing campaign launch scheduled for next Monday',
            'Database optimization to be completed within 2 weeks'
        ],
        'full_text': 'Full meeting transcript would go here. This is just a sample text to show how the PDF layout works with longer content.'
    }
    
    # Generate test PDF
    output_file = "test_meeting_notes.pdf"
    success = generator.generate_report(output_file, sample_data)
    
    if success:
        print(f"\n✅ Test PDF created: {output_file}")
        print("   Open the file to view the result!")