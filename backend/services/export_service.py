"""
Export Service - экспорт документов в .docx, .pdf, .txt, .md.
"""
from pathlib import Path
from backend.config import settings


class DocumentExporter:
    """Экспорт документов в различные форматы."""

    FORMATS = ["docx", "pdf", "txt", "md"]

    def export(self, doc_id: int, content: str, title: str, format: str) -> dict:
        """Экспорт документа."""
        export_dir = Path(settings.export_dir)
        export_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{title}_{doc_id}.{format}"
        # Санитайзим имя файла
        filename = "".join(
            c if c.isalnum() or c in "._- " else "_" for c in filename
        )
        filepath = export_dir / filename

        if format == "docx":
            filepath = filepath.with_suffix(".docx")
            self._export_docx(content, title, str(filepath))
        elif format == "pdf":
            filepath = filepath.with_suffix(".pdf")
            self._export_pdf(content, title, str(filepath))
        elif format == "txt":
            filepath = filepath.with_suffix(".txt")
            filepath.write_text(content, encoding="utf-8")
        elif format == "md":
            filepath = filepath.with_suffix(".md")
            filepath.write_text(content, encoding="utf-8")
        else:
            raise ValueError(f"Неподдерживаемый формат: {format}")

        return {
            "file_path": str(filepath),
            "format": format,
            "filename": filepath.name,
            "size_bytes": filepath.stat().st_size,
        }

    def _export_docx(self, content: str, title: str, filepath: str):
        """Экспорт в .docx через python-docx."""
        try:
            from docx import Document

            doc = Document()
            doc.add_heading(title, level=1)
            for paragraph in content.split("\n\n"):
                doc.add_paragraph(paragraph.strip())
            doc.save(filepath)
        except ImportError:
            # Fallback: plain text
            Path(filepath).write_text(content, encoding="utf-8")

    def _export_pdf(self, content: str, title: str, filepath: str):
        """Экспорт в PDF (через weasyprint или html fallback)."""
        html = (
            f"<html><body><h1>{title}</h1><pre>{content}</pre></body></html>"
        )
        try:
            from weasyprint import HTML

            HTML(string=html).write_pdf(filepath)
        except ImportError:
            # Fallback: пишем plain text в тот же filepath (с расширением .pdf)
            Path(filepath).write_text(content, encoding="utf-8")
