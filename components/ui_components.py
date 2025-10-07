"""
Återanvändbara UI-komponenter för dashboarden
"""

import streamlit as st
from typing import Optional, Dict, Any
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def show_metric_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    help_text: Optional[str] = None,
    status: str = "normal"
) -> None:
    """
    Visa en metric card med styling
    
    Args:
        label: Etikett för metric
        value: Huvudvärde att visa
        delta: Förändring (optional)
        help_text: Hjälptext (optional)
        status: 'normal', 'success', 'warning', 'error'
    """
    status_colors = {
        "normal": "#3b82f6",
        "success": "#10b981",
        "warning": "#ffc107",
        "error": "#ef4444"
    }
    
    color = status_colors.get(status, status_colors["normal"])
    
    st.markdown(f"""
    <div style="
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid {color};
    ">
        <p style="margin: 0; color: #666; font-size: 0.9rem;">{label}</p>
        <h2 style="margin: 0.5rem 0; color: #1a1a1a;">{value}</h2>
        {f'<p style="margin: 0; color: {color}; font-size: 0.9rem;">{delta}</p>' if delta else ''}
        {f'<p style="margin: 0.5rem 0 0 0; color: #999; font-size: 0.8rem;">{help_text}</p>' if help_text else ''}
    </div>
    """, unsafe_allow_html=True)

def create_population_line_chart(
    data: pd.DataFrame,
    x_col: str = "År",
    y_col: str = "Antal",
    color_col: str = "Kön",
    title: str = "Befolkningsutveckling"
) -> go.Figure:
    """
    Skapa linjediagram för befolkningsutveckling
    
    Args:
        data: DataFrame med data
        x_col: Kolumn för X-axel
        y_col: Kolumn för Y-axel
        color_col: Kolumn för färggruppering
        title: Titel på diagram
        
    Returns:
        Plotly Figure object
    """
    fig = px.line(
        data,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        markers=True
    )
    
    fig.update_layout(
        height=400,
        xaxis=dict(
            tickmode='array',
            tickvals=data[x_col].unique(),
            ticktext=[str(int(year)) for year in data[x_col].unique()],
            title=x_col
        ),
        hovermode='x unified'
    )
    
    return fig

def create_bar_chart(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    color_col: Optional[str] = None
) -> go.Figure:
    """
    Skapa stapeldiagram
    
    Args:
        data: DataFrame med data
        x_col: Kolumn för X-axel
        y_col: Kolumn för Y-axel
        title: Titel
        color_col: Kolumn för färg (optional)
        
    Returns:
        Plotly Figure object
    """
    fig = px.bar(
        data,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title
    )
    
    fig.update_layout(height=400)
    return fig

def show_data_source_status(sources: Dict[str, Dict[str, Any]]) -> None:
    """
    Visa status för datakällor
    
    Args:
        sources: Dict med datakällor och deras status
            Format: {
                "SCB": {"status": "ok", "last_updated": "2024-10-02", "message": ""},
                "Kolada": {"status": "error", "last_updated": None, "message": "Connection failed"}
            }
    """
    st.subheader("📊 Datakällor")
    
    status_icons = {
        "ok": "✅",
        "warning": "⚠️",
        "error": "❌",
        "loading": "🔄"
    }
    
    for source_name, source_info in sources.items():
        status = source_info.get("status", "unknown")
        icon = status_icons.get(status, "❓")
        last_updated = source_info.get("last_updated", "Okänd")
        message = source_info.get("message", "")
        
        with st.expander(f"{icon} {source_name}", expanded=(status == "error")):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Status:** {status.upper()}")
            with col2:
                st.write(f"**Senast uppdaterad:** {last_updated}")
            
            if message:
                if status == "error":
                    st.error(message)
                elif status == "warning":
                    st.warning(message)
                else:
                    st.info(message)

def show_loading_spinner(message: str = "Hämtar data..."):
    """Context manager för loading spinner"""
    return st.spinner(message)

def show_error_message(error: Exception, context: str = "") -> None:
    """
    Visa felmeddelande på ett användarvänligt sätt
    
    Args:
        error: Exception som kastades
        context: Kontext där felet uppstod
    """
    st.error(f"❌ Ett fel uppstod {context}")
    with st.expander("🔍 Teknisk information"):
        st.code(str(error))
        st.caption("Om problemet kvarstår, kontakta support.")

def create_comparison_table(
    data: pd.DataFrame,
    title: str = "Jämförelse"
) -> None:
    """
    Skapa en jämförelsetabell med styling
    
    Args:
        data: DataFrame med data
        title: Titel på tabellen
    """
    st.subheader(title)
    st.dataframe(
        data,
        use_container_width=True,
        hide_index=False
    )
