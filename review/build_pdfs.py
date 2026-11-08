"""Typeset the reviewed paper and claim audit. Uses the official section order.

Usage: python -m review.build_pdfs --out /absolute/output/directory
The review copy has a visible author-affiliation field to complete.
"""
import argparse
import html
import re
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT,TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,Table,TableStyle,PageBreak,KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
FONTDIR=Path('/usr/share/fonts/truetype/liberation')
for alias,filename in [('Paper','LiberationSerif-Regular.ttf'),('Paper-Bold','LiberationSerif-Bold.ttf'),('Audit','LiberationSans-Regular.ttf'),('Audit-Bold','LiberationSans-Bold.ttf'),('Code','LiberationMono-Regular.ttf')]:
    pdfmetrics.registerFont(TTFont(alias,str(FONTDIR/filename)))
pdfmetrics.registerFontFamily('Paper',normal='Paper',bold='Paper-Bold',italic='Paper',boldItalic='Paper-Bold')
pdfmetrics.registerFontFamily('Audit',normal='Audit',bold='Audit-Bold',italic='Audit',boldItalic='Audit-Bold')


def markup(text):
    text=html.escape(text)
    text=re.sub(r'`([^`]+)`',lambda m:'<font name="Code" size="8.5">'+m[1]+'</font>',text)
    text=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',text)
    text=re.sub(r'(?<!["=])(https?://[^\s<>]+)',lambda m:'<link href="'+m[1]+'" color="#1e5272">'+m[1]+'</link>',text)
    return text


def build(source,dest,paper=False):
    w,h=8.5*inch,11*inch
    margin=.77*inch;usable=w-2*margin
    styles=getSampleStyleSheet()
    base="Paper" if paper else "Audit"
    bold="Paper-Bold" if paper else "Audit-Bold"
    styles.add(ParagraphStyle(name="BodyX",fontName=base,fontSize=11 if paper else 10.3,leading=14.4 if paper else 14.2,spaceAfter=8.2,textColor=colors.HexColor("#17212b"),splitLongWords=True,allowWidows=0,allowOrphans=0))
    styles.add(ParagraphStyle(name="TitleX",fontName=bold,fontSize=24 if paper else 22,leading=27,spaceAfter=14,alignment=TA_CENTER if paper else TA_LEFT,textColor=colors.black))
    styles.add(ParagraphStyle(name="SubtitleX",fontName=base,fontSize=15,leading=19,spaceAfter=12,alignment=TA_CENTER,textColor=colors.black))
    styles.add(ParagraphStyle(name="H2X",fontName=bold,fontSize=14,leading=17,spaceBefore=13,spaceAfter=7,keepWithNext=True,textColor=colors.black))
    styles.add(ParagraphStyle(name="H3X",fontName=bold,fontSize=11.6,leading=15,spaceBefore=10,spaceAfter=6,keepWithNext=True,textColor=colors.black))
    styles.add(ParagraphStyle(name="MetaX",fontName=base,fontSize=10,leading=13,spaceAfter=5,alignment=TA_CENTER,textColor=colors.HexColor("#46525e")))
    styles.add(ParagraphStyle(name="AbstractX",parent=styles["BodyX"],leftIndent=18,rightIndent=18,spaceAfter=14))
    styles.add(ParagraphStyle(name="CaptionX",fontName=base,fontSize=9,leading=11.5,spaceBefore=5,spaceAfter=11,textColor=colors.HexColor("#46525e")))
    styles.add(ParagraphStyle(name="CellX",fontName=base,fontSize=9.2 if paper else 9.1,leading=12,spaceAfter=0,splitLongWords=True))
    styles.add(ParagraphStyle(name="CellHeadX",fontName=bold,fontSize=9.3,leading=12,textColor=colors.white))
    styles.add(ParagraphStyle(name="RefX",fontName=base,fontSize=9,leading=12,spaceAfter=7,splitLongWords=True))
    lines=source.read_text().splitlines();flow=[];i=0;section="";body_pages={}
    front=paper
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith("# "):
            flow.append(Paragraph(markup(line[2:]),styles["TitleX"]));i+=1;continue
        if line.startswith("## "):
            section=line[3:]
            if paper and section.startswith("Testing what"):
                flow.append(Paragraph(markup(section),styles["SubtitleX"]));i+=1;continue
            front=False
            if paper and (section=="References" or section.startswith("Appendix A") or section.startswith("Appendix C")):
                flow.append(PageBreak())
            flow.append(Paragraph(markup(section),styles["H2X"]));i+=1;continue
        if line.startswith("### "):
            flow.append(Paragraph(markup(line[4:]),styles["H3X"]));i+=1;continue
        if section=="References" and re.match(r'^\d+\.',line):
            flow.append(Paragraph(markup(line),styles["RefX"]));i+=1;continue
        image_match=re.match(r'!\[(.+)\]\((.+)\)',line)
        if image_match:
            from PIL import Image as PI
            imgpath=source.parent/image_match[2]
            with PI.open(imgpath) as im:iw,ih=im.size
            image=Image(str(imgpath),width=usable,height=usable*ih/iw)
            flow.append(KeepTogether([image,Paragraph(markup(image_match[1]),styles["CaptionX"])]));i+=1;continue
        if line.startswith("|"):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith("|"):
                cells=[c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.match(r'^[:\- ]+$',c) for c in cells):rows.append(cells)
                i+=1
            n=len(rows[0]);ratios={2:[.32,.68],3:[.25,.43,.32],5:[.15,.14,.12,.17,.42]}.get(n,[1/n]*n)
            if paper and n==3:ratios=[.20,.37,.43]
            data=[[Paragraph(markup(c),styles["CellHeadX"] if j==0 else styles["CellX"]) for c in row] for j,row in enumerate(rows)]
            table=Table(data,colWidths=[usable*x for x in ratios],repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#233b4c')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f2f5f7')]),('GRID',(0,0),(-1,-1),.45,colors.HexColor('#d9d9d9')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
            flow.extend([Spacer(1,4),table,Spacer(1,11)]);continue
        paragraph=[line];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(("#","|","![")):
            paragraph.append(lines[i].strip());i+=1
        style=styles["MetaX"] if front else styles["AbstractX"] if section=="Abstract" else styles["RefX"] if section=="References" else styles["BodyX"]
        flow.append(Paragraph(markup(" ".join(paragraph)),style))
    def footer(canvas,doc):
        canvas.saveState();canvas.setStrokeColor(colors.HexColor('#d9dfe3'));canvas.setLineWidth(.5)
        canvas.line(margin,.53*inch,w-margin,.53*inch)
        canvas.setFont('Audit',8);canvas.setFillColor(colors.HexColor('#586574'))
        canvas.drawString(margin,.35*inch,"Lock Before You Talk | Evidence review | 8 November 2026")
        canvas.drawRightString(w-margin,.35*inch,str(doc.page));canvas.restoreState()
    doc=SimpleDocTemplate(str(dest),pagesize=(w,h),rightMargin=margin,leftMargin=margin,topMargin=.70*inch,bottomMargin=.72*inch,title="Lock Before You Talk" if paper else "Evidence review of Lock Before You Talk",author="Vaughn DiMarco")
    doc.build(flow,onFirstPage=footer,onLaterPages=footer)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);args=ap.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    build(ROOT/'report/draft.md',out/'lock-before-you-talk-revised-report.pdf',True)
    build(ROOT/'report/audit/claim-audit.md',out/'lock-before-you-talk-claim-audit.pdf',False)
    print('Created reviewed report and full claim audit.')


if __name__=='__main__':main()
