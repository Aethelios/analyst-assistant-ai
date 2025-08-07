import json
import re
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def is_json(text):
    """Checks if a string is a valid JSON object, possibly enclosed in markdown."""
    # Regex to find JSON block within ```json ... ```
    match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        return True, match.group(1)
    
    # Fallback for raw JSON
    try:
        json.loads(text)
        return True, text
    except ValueError:
        return False, None

@st.cache_data
def create_chart(chart_data_str: str):
    """
    Parses the JSON string and creates a Matplotlib chart.
    Returns the figure object for display in Streamlit.
    """
    try:
        chart_data = json.loads(chart_data_str)

        chart_type = chart_data.get("chart_type")
        title = chart_data.get("title", "Chart")
        x_label = chart_data.get("x_axis", {}).get("label", "X-Axis")
        y_label = chart_data.get("y_axis", {}).get("label", "Y-Axis")
        x_data = chart_data.get("x_axis", {}).get("data", [])
        y_data = chart_data.get("y_axis", {}).get("data", [])

        if not all([chart_type, x_data, y_data]):
            return None, "Error: Incomplete chart data provided in JSON."

        # Create the plot
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(10, 6))

        if chart_type == "bar":
            sns.barplot(x=x_data, y=y_data, ax=ax, palette="viridis")
        elif chart_type == "line":
            sns.lineplot(x=x_data, y=y_data, ax=ax, marker='o', color='b')
        elif chart_type == "pie":
            # Pie charts don't have x/y axes in the same way
            ax.pie(y_data, labels=x_data, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("pastel"))
            ax.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
        else:
            return None, f"Error: Unsupported chart type '{chart_type}'."

        ax.set_title(title, fontsize=16)
        ax.set_xlabel(x_label, fontsize=12)
        ax.set_ylabel(y_label, fontsize=12)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        
        return fig, None

    except json.JSONDecodeError:
        return None, "Error: Invalid JSON format received from the model."
    except Exception as e:
        return None, f"An error occurred while generating the chart: {e}"