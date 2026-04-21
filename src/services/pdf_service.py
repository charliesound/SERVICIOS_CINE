from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from schemas.presentation_schema import PresentationFilmstripResponse


class PdfRenderError(RuntimeError):
    pass


class PdfService:
    def __init__(self) -> None:
        templates_root = Path(__file__).resolve().parents[2] / "templates"
        self.templates_root = templates_root
        self.environment = Environment(
            loader=FileSystemLoader(str(templates_root)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render_filmstrip_html(
        self,
        payload: PresentationFilmstripResponse | dict,
        *,
        render_mode: str = "html",
    ) -> str:
        template = self.environment.get_template("presentation/filmstrip.html")
        payload_data = (
            payload.model_dump(mode="json")
            if isinstance(payload, PresentationFilmstripResponse)
            else payload
        )
        return template.render(payload=payload_data, render_mode=render_mode)

    def export_filmstrip_pdf(self, payload: PresentationFilmstripResponse | dict) -> bytes:
        html = self.render_filmstrip_html(payload, render_mode="pdf")
        try:
            return HTML(string=html, base_url=str(self.templates_root.parent)).write_pdf()
        except Exception as exc:
            raise PdfRenderError(f"WeasyPrint failed to render the presentation PDF: {exc}") from exc


pdf_service = PdfService()
