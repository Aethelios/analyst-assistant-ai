CHART_JSON_SCHEMA = """
{
    "chart_type": "bar | line | pie",
    "title": "A descriptive title for the chart",
    "x_axis": {
        "label": "Label for the X-axis",
        "data": ["category1", "category2", ...]
    },
    "y_axis": {
        "label": "Label for the Y-axis",
        "data": [value1, value2, ...]
    }
}
"""

EXAMPLE_JSON_OUTPUT = """
```json
{
    "chart_type": "bar",
    "title": "Sales by Region",
    "x_axis": {
        "label": "Region",
        "data": ["West", "East"]
    },
    "y_axis": {
        "label": "Total Sales",
        "data": [2300, 300]
    }
}"""