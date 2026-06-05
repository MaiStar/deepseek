# mdtopdf.py
from markdown_pdf import MarkdownPdf, Section
from pathlib import Path


def convertMD(name, text):
    """Конвертирует текст из Markdown в PDF и сохраняет в папку pdf/."""
    # Убедимся, что папка для PDF существует
    Path("pdf/").mkdir(parents=True, exist_ok=True)

    pdf = MarkdownPdf(toc_level=2)
    pdf.add_section(Section(text, toc=False))

    # Извлекаем только имя файла из полного пути, если оно передано
    base_filename = Path(name).stem
    pdf.save(f"pdf/{base_filename}.pdf")
