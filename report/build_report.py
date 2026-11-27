from pathlib import Path
import json,re,hashlib
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

REPO=Path(__file__).resolve().parents[1]
OUT=REPO/'report';OUT.mkdir(exist_ok=True)
content=json.loads((OUT/'content.json').read_text())
expected=content['expected_evaluation_sha256']
actual=hashlib.sha256((REPO/'evaluation/comparison.json').read_bytes()).hexdigest()
if actual!=expected:raise ValueError('Evaluation changed; review the report text before rebuilding')
evaluation=json.loads((REPO/'evaluation/comparison.json').read_text())
manifest=json.loads((REPO/'papers/manifest.json').read_text())
refs=[b for b in content['pages'][-1]['blocks'] if 'ref' in b]
content['pages'][-1]['blocks']=[b for b in content['pages'][-1]['blocks'] if 'ref' not in b and b.get('heading')!='References']
content['pages'].append({'blocks':[{'heading':'Dataset results'},{'p':'Each dataset has four targeted definitions. The table reports fully supported targets; partial, omitted, incorrect, ambiguous, and abstained outcomes remain separate in the full evaluation. The documentation column is source consistency, because the table documentation was a generation input.'},{'table':'dataset_results'},{'heading':'References'}]+refs})
labels={
'inventors_college':'Inventors by college','inventors_childhood_cz':'Inventors by childhood CZ',
'atlas_county_covariates':'Atlas county characteristics','atlas_county_outcomes':'Atlas county outcomes',
'life_national_mortality':'National mortality rates','life_county_expectancy':'County life expectancy',
'race_national_statistics':'National outcomes by race','race_cz_income':'CZ income ranks by race',
'college_access_mobility':'College access and mobility','college_characteristics':'College characteristics'}
conditions=[['CSV baseline','CSV sample and profiles','gpt-4o-mini semantic analysis and description'],
['Strict paper support','Same CSV inputs and mapped paper','gpt-4.1 claims and two gpt-5.1 audits'],
['Documentation assisted','Same CSV, paper, and linked table PDF','Same claim and audit stages with table definitions']]
order=['supported','partial','omitted','incorrect','ambiguous','abstained']
tables={
'datasets':(['Dataset','Rows','Columns'],[[labels[d['dataset_id']],f"{d['conditions']['csv_baseline']['rows']:,}",str(d['conditions']['csv_baseline']['columns'])] for d in evaluation['datasets']],[4.5,1.05,1.15]),
'conditions':(['Condition','Evidence available','Generation stages'],conditions,[1.35,2.35,3.0]),
'results':(['Condition','Supported','Partial','Omitted','Incorrect','Ambiguous','Abstained'],[[label]+[str(evaluation['totals'][c].get(k,0)) for k in order] for c,label in [('csv_baseline','CSV baseline'),('strict_paper_only','Strict paper'),('documentation_assisted','Documented')]],[1.25,.89,.66,.84,.87,1.05,1.14]),
'dataset_results':(['Dataset','CSV baseline','Strict paper','Documented'],[[labels[d['dataset_id']]]+[str(d['conditions'][c]['labels'].get('supported',0)) for c in ['csv_baseline','strict_paper_only','documentation_assisted']] for d in evaluation['datasets']],[3.45,1.1,1.05,1.1])}

doc=Document();s=doc.sections[0];s.page_width=Inches(8.5);s.page_height=Inches(11)
s.left_margin=s.right_margin=Inches(.9);s.top_margin=s.bottom_margin=Inches(.7)
s.footer_distance=Inches(.3)
for st in doc.styles:
 if st.type in [1,2]:
  st.font.name='Calibri';st.font.color.rgb=RGBColor(0,0,0)
normal=doc.styles['Normal'];normal.font.size=Pt(11)
normal.paragraph_format.line_spacing=1.07;normal.paragraph_format.space_after=Pt(7)
for name,size in [('Title',22),('Heading 1',13),('Heading 2',11.5)]:
 st=doc.styles[name];st.font.size=Pt(size);st.font.bold=True
 st.paragraph_format.space_before=Pt(11 if name!='Title' else 0)
 st.paragraph_format.space_after=Pt(6);st.paragraph_format.keep_with_next=True
# No personal attribution or completion-date field.
doc.core_properties.author='';doc.core_properties.last_modified_by=''
doc.core_properties.title=content['title'];doc.core_properties.subject='Dataset description methods and development evaluation'
for xmlroot in [doc.styles.element,doc.element]:
 for border in list(xmlroot.iter(qn('w:pBdr'))):border.getparent().remove(border)

def table(name):
 headers,rows,widths=tables[name]
 t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
 for i,w in enumerate(widths):t.columns[i].width=Inches(w)
 for row,values in zip([t.rows[0]]+[t.add_row() for _ in rows],[headers]+rows):
  for i,(cell,text) in enumerate(zip(row.cells,values)):
   cell.width=Inches(widths[i]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   tcpr=cell._tc.get_or_add_tcPr();m=OxmlElement('w:tcMar')
   for side,val in [('top',60),('bottom',60),('left',95),('right',95)]:
    x=OxmlElement('w:'+side);x.set(qn('w:w'),str(val));x.set(qn('w:type'),'dxa');m.append(x)
   tcpr.append(m)
   if row==t.rows[0]:pass
   p=cell.paragraphs[0];p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=1.02
   p.alignment=WD_ALIGN_PARAGRAPH.LEFT if i==0 or name=='conditions' else WD_ALIGN_PARAGRAPH.CENTER
   r=p.add_run(text);r.font.size=Pt(9 if name=='results' else 9.5);r.font.color.rgb=RGBColor(0,0,0)
  trpr=row._tr.get_or_add_trPr();nosplit=OxmlElement('w:cantSplit');trpr.append(nosplit)
 for cell in t.rows[0].cells:
  shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'EDEDED');cell._tc.get_or_add_tcPr().append(shade)
  for r in cell.paragraphs[0].runs:r.bold=True
 repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
 borders=OxmlElement('w:tblBorders')
 for edge in ['top','left','bottom','right','insideH','insideV']:
  x=OxmlElement('w:'+edge);x.set(qn('w:val'),'single');x.set(qn('w:sz'),'4');x.set(qn('w:color'),'D9D9D9');borders.append(x)
 t._tbl.tblPr.append(borders)
 p=doc.add_paragraph();p.paragraph_format.space_after=Pt(0);p.paragraph_format.space_before=Pt(0);p.paragraph_format.line_spacing=Pt(5);p.paragraph_format.space_after=Pt(4);p.add_run().font.size=Pt(5)

def reference(b):
 p=doc.add_paragraph();p.paragraph_format.space_after=Pt(5)
 r=p.add_run(f"[{b['ref']}] ");r.font.size=Pt(9.5)
 rel=p.part.relate_to(b['url'],RT.HYPERLINK,is_external=True)
 h=OxmlElement('w:hyperlink');h.set(qn('r:id'),rel)
 r=OxmlElement('w:r');pr=OxmlElement('w:rPr')
 for tag,val in [('color','000000'),('sz','19'),('u','none')]:
  x=OxmlElement('w:'+tag);x.set(qn('w:val'),val);pr.append(x)
 r.append(pr);text=OxmlElement('w:t');text.text=b['text'];r.append(text);h.append(r);p._p.append(h)

md=['# '+content['title'],'']
for page_number,page in enumerate(content['pages']):
 if page_number==0:doc.add_paragraph(content['title'],style='Title')
 else:doc.add_page_break()
 for b in page['blocks']:
  if 'heading' in b:
   doc.add_paragraph(b['heading'],style='Heading 1');md+=['## '+b['heading'],'']
  elif 'p' in b:
   p=doc.add_paragraph(b['p']);p.paragraph_format.widow_control=True;md+=[b['p'],'']
  elif 'table' in b:
   table(b['table']);headers,rows,_=tables[b['table']]
   md+=['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']
   md+=['| '+' | '.join(row)+' |' for row in rows];md+=['']
  elif 'ref' in b:
   reference(b);md += [f"[{b['ref']}] [{b['text']}]({b['url']})",'']
footer=s.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE')
r=OxmlElement('w:r');pr=OxmlElement('w:rPr');sz=OxmlElement('w:sz');sz.set(qn('w:val'),'18');pr.append(sz);r.append(pr)
t=OxmlElement('w:t');t.text='1';r.append(t);fld.append(r);footer._p.append(fld)
path=OUT/'Dataset_Description_Project_Report.docx';doc.save(path)
(REPO/'report/PROJECT_REPORT.md').write_text('\n'.join(md)+'\n')
print(path);print('Narrative words',sum(len(b.get('p','').split()) for p in content['pages'] for b in p['blocks']))
