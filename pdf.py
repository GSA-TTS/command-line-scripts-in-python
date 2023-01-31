import jinja2
import pdfkit
import re

def render_html(row):
    template_loader = jinja2.FileSystemLoader(searchpath="./")
    template_env = jinja2.Environment(loader=template_loader)
    template_file = "letter.html"
    template = template_env.get_template(template_file)
    output_text = template.render(
        fscs_id=row['fscs_id'],
        name=row['name'],
        address=row['address'],
        api_key=row['api_key']
    )
    base_path = "letters/{}-{}".format(
        row['fscs_id'], 
        re.sub(r'\W+', '', row['address']))
    html_path = base_path + ".html"
    html_file = open(html_path, 'w')
    html_file.write(output_text)
    html_file.close()
    return base_path

def html2pdf(html_path, pdf_path):
    options = {
        'page-size': 'Letter',
        'margin-top': '0.35in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None
    }
    with open(html_path) as f:
        pdfkit.from_file(f, pdf_path, options=options)