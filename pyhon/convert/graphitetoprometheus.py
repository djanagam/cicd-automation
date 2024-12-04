import json
import re

# Mapping of Graphite functions to Prometheus equivalents
FUNCTION_MAPPING = {
    "sumSeries": "sum",
    "averageSeries": "avg",
    "maxSeries": "max",
    "minSeries": "min",
    "divideSeries": "/",
    "movingAverage": "rate",
    "timeShift": "offset",
    "alias": "",  # Alias isn't directly used in Prometheus, may adjust manually
    "groupByNode": "sum by",  # Grouping by labels
    "derivative": "rate",
    "integral": "increase",
    "nonNegativeDerivative": "rate",
}

def convert_graphite_function(graphite_query):
    """
    Replace Graphite functions with Prometheus equivalents.
    """
    for graphite_func, prom_func in FUNCTION_MAPPING.items():
        graphite_query = re.sub(rf"{graphite_func}\((.*?)\)", rf"{prom_func}(\1)", graphite_query)
    return graphite_query

def convert_graphite_path_to_prometheus(graphite_path):
    """
    Convert Graphite metric paths to Prometheus-style metrics with labels.
    Example:
      Graphite: stats.gauges.myapp.requests.count
      Prometheus: myapp_requests_total{job="myapp", instance="requests"}
    """
    # Replace dots in metric paths with underscores for metric names
    metric_name = re.sub(r'[^\w]', '_', graphite_path)
    
    # Extract labels from the path dynamically
    labels = []
    parts = graphite_path.split('.')
    if len(parts) >= 2:
        labels.append(f'job="{parts[1]}"')
    if len(parts) >= 3:
        labels.append(f'instance="{parts[2]}"')

    # Combine metric name and labels
    prometheus_query = f"{metric_name}{{{', '.join(labels)}}}" if labels else metric_name
    return prometheus_query

def convert_graphite_to_prometheus(graphite_query):
    """
    Comprehensive conversion of a Graphite query to Prometheus.
    Handles functions, paths, and nested queries.
    """
    # First, convert functions
    prometheus_query = convert_graphite_function(graphite_query)
    
    # Then, convert metric paths
    prometheus_query = re.sub(r"[a-zA-Z0-9_.]+", lambda m: convert_graphite_path_to_prometheus(m.group(0)), prometheus_query)

    return prometheus_query

def convert_dashboard(file_path, output_path):
    """
    Convert a Grafana dashboard JSON file from Graphite to Prometheus queries.
    """
    with open(file_path, 'r') as f:
        dashboard = json.load(f)

    # Traverse panels and update queries
    for panel in dashboard.get("panels", []):
        targets = panel.get("targets", [])
        for target in targets:
            if "target" in target:  # Graphite query
                original_query = target["target"]
                try:
                    converted_query = convert_graphite_to_prometheus(original_query)
                    target["expr"] = converted_query  # Prometheus uses "expr"
                    del target["target"]  # Remove Graphite query field
                except Exception as e:
                    print(f"Error converting query '{original_query}': {e}")

    # Update data source
    for panel in dashboard.get("panels", []):
        if "datasource" in panel:
            panel["datasource"] = "Prometheus"  # Replace with your Prometheus datasource name

    # Save the updated dashboard
    with open(output_path, 'w') as f:
        json.dump(dashboard, f, indent=2)

    print(f"Dashboard converted and saved to {output_path}")

# Example Usage
if __name__ == "__main__":
    input_file = "graphite_dashboard.json"  # Path to the input JSON
    output_file = "prometheus_dashboard.json"  # Path to the output JSON
    convert_dashboard(input_file, output_file)