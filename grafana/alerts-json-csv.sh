jq -r '
[.[] | {id, name, condition, frequency}] | 
(first | keys_unsorted) as $keys | 
$keys, map([.[ $keys[] ]])[] | @csv
' alert_rules.json > alert_rules.csv