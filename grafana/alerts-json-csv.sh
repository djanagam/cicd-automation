jq.exe -r '
[
  .[] 
  | .folder as $folder 
  | .dashboards[] 
  | .dashboard as $dashboard 
  | .alerts[] 
  | {
      folder: $folder,
      dashboard: $dashboard,
      id: .id,
      name: .name,
      condition: .condition,
      frequency: .frequency
    }
] 
| (first | keys_unsorted) as $keys 
| $keys, map([.[ $keys[] ]])[] 
| @csv
' alert_rules.json > alert_rules.csv