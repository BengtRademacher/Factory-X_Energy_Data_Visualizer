from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Any, Sequence, Tuple
import uuid
import zipfile

import matplotlib as mpl
from matplotlib.backends.backend_pdf import PdfPages
import streamlit as st


def set_font_for_export() -> None:
    """Configure Matplotlib export fonts for editable text output."""
    mpl.rcParams["pdf.fonttype"] = 42
    mpl.rcParams["ps.fonttype"] = 42
    mpl.rcParams["svg.fonttype"] = "none"


def reset_font_for_display() -> None:
    """Restore Matplotlib display defaults after an export."""
    mpl.rcParams["pdf.fonttype"] = 3
    mpl.rcParams["ps.fonttype"] = 3
    mpl.rcParams["svg.fonttype"] = "path"


def _generate_unique_key(prefix: str) -> str:
    """Generate a unique Streamlit key."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _is_plotly_figure(obj: Any) -> bool:
    try:
        import plotly.graph_objects as go

        return isinstance(obj, go.Figure)
    except Exception:
        return False


def create_zip_buffer(figures, base_filename, formats, savefig_options):
    """Create an in-memory ZIP archive for exported figures."""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
        for title, fig in figures:
            safe_title = "".join([char if char.isalnum() else "_" for char in title])
            for fmt in formats:
                fmt_lower = fmt.lower()
                if _is_plotly_figure(fig):
                    try:
                        import kaleido  # noqa: F401

                        image_bytes = fig.to_image(format=fmt_lower if fmt_lower != "pdf" else "pdf", scale=2)
                        zip_file.writestr(f"{safe_title}.{fmt_lower}", image_bytes)
                    except Exception as exc:
                        st.warning(
                            f"Plotly figure '{title}' could not be exported as {fmt.upper()} ({exc}). Falling back to HTML."
                        )
                        try:
                            html_bytes = fig.to_html(full_html=True, include_plotlyjs="cdn").encode("utf-8")
                            zip_file.writestr(f"{safe_title}.html", html_bytes)
                        except Exception:
                            pass
                else:
                    fig_buffer = BytesIO()
                    fig.savefig(fig_buffer, format=fmt_lower, **savefig_options)
                    fig_buffer.seek(0)
                    zip_file.writestr(f"{safe_title}.{fmt_lower}", fig_buffer.read())

    zip_buffer.seek(0)
    return zip_buffer


@dataclass(slots=True)
class ExportItem:
    title: str
    figure: Any


def export_plots(
    plots_to_export: Sequence[Tuple[str, Any]] | Sequence[ExportItem],
    base_filename: str,
    format_str: str,
) -> None:
    """Export one or more plots in a single selected format."""
    if not plots_to_export:
        st.warning("No plots are available for export.")
        return

    set_font_for_export()
    try:
        savefig_options = {
            "dpi": 600,
            "bbox_inches": "tight",
            "pad_inches": 0.1,
            "facecolor": "w",
            "edgecolor": "w",
        }
        fmt_lower = format_str.lower()

        if len(plots_to_export) > 1:
            if format_str == "PDF" and all(not _is_plotly_figure(fig) for _, fig in plots_to_export):
                pdf_bytes = BytesIO()
                with PdfPages(pdf_bytes, "w") as pdf:
                    for _, fig in plots_to_export:
                        pdf.savefig(fig, **savefig_options)

                st.download_button(
                    label=f"Download combined PDF ({len(plots_to_export)} plots)",
                    data=pdf_bytes.getvalue(),
                    file_name=f"{base_filename}.pdf",
                    mime="application/pdf",
                    type="primary",
                    key=_generate_unique_key("download_combined_pdf"),
                    icon=":material/download:",
                )
            else:
                for index, (title, fig) in enumerate(plots_to_export, start=1):
                    safe_title = "".join([char if char.isalnum() else "_" for char in title])
                    filename = f"{base_filename}_{index}_{safe_title}.{fmt_lower}"

                    if _is_plotly_figure(fig):
                        try:
                            import kaleido  # noqa: F401

                            image_bytes = fig.to_image(format=fmt_lower, scale=2)
                            st.download_button(
                                label=f"{title} as {format_str}",
                                data=image_bytes,
                                file_name=filename,
                                mime=f"image/{fmt_lower}" if fmt_lower != "pdf" else "application/pdf",
                                type="primary",
                                key=_generate_unique_key(f"download_{index}_{fmt_lower}"),
                                icon=":material/download:",
                            )
                        except Exception as exc:
                            st.warning(f"Plotly figure '{title}' could not be exported as {format_str}: {exc}")
                    else:
                        buf = BytesIO()
                        fig.savefig(buf, format=fmt_lower, **savefig_options)
                        st.download_button(
                            label=f"{title} as {format_str}",
                            data=buf.getvalue(),
                            file_name=filename,
                            mime=f"image/{fmt_lower}" if fmt_lower not in ["pdf", "eps"] else ("application/pdf" if fmt_lower == "pdf" else "application/postscript"),
                            type="primary",
                            key=_generate_unique_key(f"download_{index}_{fmt_lower}"),
                            icon=":material/download:",
                        )
        else:
            title, fig = plots_to_export[0]
            safe_title = "".join([char if char.isalnum() else "_" for char in title])
            filename = f"{base_filename}_{safe_title}.{fmt_lower}"

            if _is_plotly_figure(fig):
                try:
                    import kaleido  # noqa: F401

                    image_bytes = fig.to_image(format=fmt_lower, scale=2)
                    st.download_button(
                        label=f"Download {title} as {format_str}",
                        data=image_bytes,
                        file_name=filename,
                        mime=f"image/{fmt_lower}" if fmt_lower != "pdf" else "application/pdf",
                        type="primary",
                        key=_generate_unique_key(f"download_single_{fmt_lower}"),
                        icon=":material/download:",
                    )
                except Exception as exc:
                    st.warning(f"Plotly figure '{title}' could not be exported as {format_str}: {exc}")
                    html_bytes = fig.to_html(full_html=True, include_plotlyjs="cdn").encode("utf-8")
                    st.download_button(
                        label=f"Download {title} as HTML (fallback)",
                        data=html_bytes,
                        file_name=f"{safe_title}.html",
                        mime="text/html",
                        type="primary",
                        key=_generate_unique_key("download_html_fallback"),
                        icon=":material/download:",
                    )
            else:
                buf = BytesIO()
                fig.savefig(buf, format=fmt_lower, **savefig_options)
                st.download_button(
                    label=f"Download {title} as {format_str}",
                    data=buf.getvalue(),
                    file_name=filename,
                    mime=f"image/{fmt_lower}" if fmt_lower not in ["pdf", "eps"] else ("application/pdf" if fmt_lower == "pdf" else "application/postscript"),
                    type="primary",
                    key=_generate_unique_key(f"download_single_{fmt_lower}"),
                    icon=":material/download:",
                )

        if not st.session_state.get("export_toast_shown", False):
            st.toast("Export ready.", icon=":material/check_circle:")
            st.session_state["export_toast_shown"] = True
    finally:
        reset_font_for_display()
