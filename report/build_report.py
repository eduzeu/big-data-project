"""Build an editable, two-column scientific manuscript from the verified record."""
from pathlib import Path
import hashlib
import json
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION_START
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

REPO=Path(__file__).resolve().parents[1];OUT=REPO/'report'
content=json.loads((OUT/'content.json').read_text())
if hashlib.sha256((REPO/'evaluation/comparison.json').read_bytes()).hexdigest()!=content['expected_evaluation_sha256']:
    raise ValueError('Evaluation changed; review the report text before rebuilding')
evaluation=json.loads((REPO/'evaluation/comparison.json').read_text())
by_heading={};current=None;refs=[]
for page in content['pages']:
    for block in page['blocks']:
        if 'heading' in block:current=block['heading'];by_heading[current]=[]
        elif 'ref' in block:refs.append(block)
        else:by_heading[current].append(block)
labels={'inventors_college':'Inventors college','inventors_childhood_cz':'Inventors childhood CZ',
'atlas_county_covariates':'Atlas covariates','atlas_county_outcomes':'Atlas outcomes',
'life_national_mortality':'National mortality','life_county_expectancy':'County life expectancy',
'race_national_statistics':'Race national outcomes','race_cz_income':'Race CZ income',
'college_access_mobility':'College access and mobility','college_characteristics':'College characteristics'}
order=['supported','partial','omitted','incorrect','ambiguous','abstained']
tables={
'datasets':(['Dataset','Rows','Cols'],[[labels[d['dataset_id']],f"{d['conditions']['csv_baseline']['rows']:,}",str(d['conditions']['csv_baseline']['columns'])] for d in evaluation['datasets']],[2.12,.70,.54],
'Table 1  Dataset inventory'),
'results':(['Target outcome','CSV','Paper','Docs'],[[k.capitalize()]+[str(evaluation['totals'][c].get(k,0)) for c in ['csv_baseline','strict_paper_only','documentation_assisted']] for k in order],[1.55,.56,.60,.65],
'Table 2  Target check outcomes out of 40'),
'dataset_results':(['Dataset','CSV','Paper','Docs'],[[labels[d['dataset_id']]]+[str(d['conditions'][c]['labels'].get('supported',0)) for c in ['csv_baseline','strict_paper_only','documentation_assisted']] for d in evaluation['datasets']],[1.92,.46,.48,.50],
'Table 3  Fully supported targets out of four per dataset')}

doc=Document();first=doc.sections[0]
first.page_width=Inches(8.5);first.page_height=Inches(11)
first.left_margin=first.right_margin=Inches(.75)
first.top_margin=first.bottom_margin=Inches(.65);first.footer_distance=Inches(.30)
for st in doc.styles:
    if st.type in [1,2]:
        st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0)
        fonts=st.element.get_or_add_rPr().find(qn('w:rFonts'))
        if fonts is not None:
            for attr in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme']:
                fonts.attrib.pop(qn('w:'+attr),None)
normal=doc.styles['Normal'];normal.font.size=Pt(10.5)
normal.paragraph_format.line_spacing=1.0;normal.paragraph_format.space_after=Pt(4)
normal.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
normal.paragraph_format.widow_control=True
for name,size in [('Title',17),('Heading 1',11),('Heading 2',10.5)]:
    st=doc.styles[name];st.font.size=Pt(size);st.font.bold=True
    st.paragraph_format.space_before=Pt(9 if name!='Title' else 0)
    st.paragraph_format.space_after=Pt(4);st.paragraph_format.keep_with_next=True
    st.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER if name=='Title' else WD_ALIGN_PARAGRAPH.LEFT
for xmlroot in [doc.styles.element,doc.element]:
    for border in list(xmlroot.iter(qn('w:pBdr'))):border.getparent().remove(border)
doc.core_properties.author='';doc.core_properties.last_modified_by=''
doc.core_properties.title=content['title'];doc.core_properties.subject='Two-column scientific manuscript on dataset descriptions'
title=doc.add_paragraph(content['title'],style='Title');title.paragraph_format.space_after=Pt(9)
# A full-width title followed by a true Word section with flowing columns.
body=doc.add_section(WD_SECTION_START.CONTINUOUS)
cols=body._sectPr.find(qn('w:cols'));cols.set(qn('w:num'),'2');cols.set(qn('w:space'),'403');cols.set(qn('w:equalWidth'),'1')

md=['# '+content['title'],'']
def paragraph(text,prefix=None,small=False):
    p=doc.add_paragraph();p.paragraph_format.widow_control=True
    if prefix:
        r=p.add_run(prefix+' ');r.bold=True
    r=p.add_run(text)
    if small:
        for run in p.runs:run.font.size=Pt(9.5)
    return p

def heading(text):
    doc.add_paragraph(text,style='Heading 1');md.extend(['## '+text,''])

def table(name):
    headers,rows,widths,caption=tables[name]
    p=doc.add_paragraph(caption);p.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next=True;p.paragraph_format.space_before=Pt(5);p.paragraph_format.space_after=Pt(3)
    for r in p.runs:r.font.size=Pt(9);r.italic=True
    t=doc.add_table(rows=1,cols=len(headers));t.autofit=False;t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for i,w in enumerate(widths):t.columns[i].width=Inches(w)
    for row,values in zip([t.rows[0]]+[t.add_row() for _ in rows],[headers]+rows):
        trpr=row._tr.get_or_add_trPr();trpr.append(OxmlElement('w:cantSplit'))
        for i,(cell,text) in enumerate(zip(row.cells,values)):
            cell.width=Inches(widths[i]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            props=cell._tc.get_or_add_tcPr();m=OxmlElement('w:tcMar')
            for side,val in [('top',45),('bottom',45),('left',65),('right',65)]:
                x=OxmlElement('w:'+side);x.set(qn('w:w'),str(val));x.set(qn('w:type'),'dxa');m.append(x)
            props.append(m)
            p=cell.paragraphs[0];p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=1.0
            p.alignment=WD_ALIGN_PARAGRAPH.LEFT if i==0 else WD_ALIGN_PARAGRAPH.CENTER
            r=p.add_run(text);r.font.size=Pt(9);r.font.color.rgb=RGBColor(0,0,0)
    for cell in t.rows[0].cells:
        shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'EEEEEE');cell._tc.get_or_add_tcPr().append(shade)
        for r in cell.paragraphs[0].runs:r.bold=True
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    borders=OxmlElement('w:tblBorders')
    for edge in ['top','left','bottom','right','insideH','insideV']:
        x=OxmlElement('w:'+edge);x.set(qn('w:val'),'single');x.set(qn('w:sz'),'4');x.set(qn('w:color'),'D9D9D9');borders.append(x)
    t._tbl.tblPr.append(borders)
    p=doc.add_paragraph();p.paragraph_format.space_after=Pt(2);p.paragraph_format.line_spacing=Pt(2)
    md.extend(['*'+caption+'*','', '| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |'])
    md.extend('| '+' | '.join(row)+' |' for row in rows);md.append('')

def blocks(name):
    for b in by_heading[name]:
        if 'p' in b:
            text=b['p'].replace('Each row totals 40 target checks.', 'Each condition column totals 40 target checks.')
            paragraph(text);md.extend([text,''])
        elif b.get('table')=='conditions':
            # The three conditions are already described in the method prose;
            # keep their exact model/input summary as short scientific prose.
            text='The three conditions are CSV baseline (CSV sample and profiles; gpt-4o-mini), strict paper support (the same CSV with its mapped paper; gpt-4.1 claims and two gpt-5.1 audits), and documentation assistance (the same evidence plus the linked table PDF).'
            paragraph(text);md.extend([text,''])
        elif 'table' in b:table(b['table'])

abstract=by_heading['Project summary'][0]['p']
paragraph(abstract,prefix='Abstract:',small=True);md.extend(['## Abstract','',abstract,''])
keywords='Dataset descriptions; AutoDDG; retrieval; table documentation; factual evaluation.'
paragraph(keywords,prefix='Keywords:',small=True);md.extend(['**Keywords:** '+keywords,''])
for number,old,new in [(1,'Research question','Introduction'),(2,'Datasets and source material','Data and sources'),
(3,'Method','Method'),(4,'Evaluation design','Evaluation design'),(5,'Results','Results')]:
    heading(f'{number} {new}');blocks(old)
# Related findings remain within the Results section as compact subheadings.
for name in ['What the added evidence clarified','What remains unresolved']:
    doc.add_paragraph(name,style='Heading 2');md.extend(['### '+name,'']);blocks(name)
heading('6 Discussion and limitations');blocks('Interpretation and limitations')
heading('7 Conclusion');blocks('Conclusion')
heading('8 Reproducibility');blocks('Reproducibility and project artifacts')
paragraph('Table 3 reports fully supported targets out of four per dataset. CSV denotes the baseline, Paper the strict paper-only condition, and Docs the documentation-assisted condition. Partial credit and abstentions are not included in these fully supported counts.')
md.extend(['Table 3 reports fully supported targets out of four per dataset. CSV denotes the baseline, Paper the strict paper-only condition, and Docs the documentation-assisted condition. Partial credit and abstentions are not included in these fully supported counts.',''])
table('dataset_results')
heading('References')
for b in refs:
    p=doc.add_paragraph();p.paragraph_format.keep_together=True;p.paragraph_format.space_after=Pt(3);p.paragraph_format.left_indent=Inches(.16);p.paragraph_format.first_line_indent=Inches(-.16)
    r=p.add_run(f"[{b['ref']}] ");r.font.size=Pt(9)
    rel=p.part.relate_to(b['url'],RT.HYPERLINK,is_external=True)
    h=OxmlElement('w:hyperlink');h.set(qn('r:id'),rel);r=OxmlElement('w:r');pr=OxmlElement('w:rPr')
    for tag,val in [('color','000000'),('sz','18'),('u','none')]:
        x=OxmlElement('w:'+tag);x.set(qn('w:val'),val);pr.append(x)
    r.append(pr);text=OxmlElement('w:t');text.text=b['text'];r.append(text);h.append(r);p._p.append(h)
    md.extend([f"[{b['ref']}] [{b['text']}]({b['url']})",''])
# Ending the columns with a continuous section balances the last page.
end=doc.add_section(WD_SECTION_START.CONTINUOUS)
endcols=end._sectPr.find(qn('w:cols'));endcols.set(qn('w:num'),'1')
footer=first.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');r=OxmlElement('w:r')
pr=OxmlElement('w:rPr');sz=OxmlElement('w:sz');sz.set(qn('w:val'),'18');pr.append(sz);r.append(pr)
t=OxmlElement('w:t');t.text='1';r.append(t);fld.append(r);footer._p.append(fld)
p=OUT/'Dataset_Description_Project_Report.docx';doc.save(p)
(OUT/'PROJECT_REPORT.md').write_text('\n'.join(md)+'\n')
print(p)
