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


################

jq.exe -r '
[
  .[] 
  | .orgid as $orgid 
  | .e as $title 
  | .folder as $folder 
  | .interval as $interval
  | .groups[]
  | .rules[]
  | .uid as $uid
  | .title as $rule_title
  | .condition as $condition
  | .data[]
  | {
      orgid: $orgid,
      title: $title,
      folder: $folder,
      interval: $interval,
      uid: $uid,
      rule_title: $rule_title,
      condition: $condition,
      refid: .refid,
      from: .relativeTimeRange.from,
      to: .relativeTimeRange.to,
      datasourceUid: .datasourceUid,
      mod: .mod,
      nin_doc_count: ."nin doc count",
      order: .order,
      orderBy: .orderBy,
      size: .size,
      type: .type
    }
]
| (first | keys_unsorted) as $keys 
| $keys, map([.[ $keys[] ]])[] 
| @csv
' path\to\alert_rules.json > path\to\alert_rules.csv

###############################

jq.exe -r '
[
  .[] 
  | .orgid as $orgid 
  | .e as $title 
  | .folder as $folder 
  | .interval as $interval
  | .groups[]
  | .rules[]
  | .uid as $uid
  | .title as $rule_title
  | .condition as $condition
  | .data[]
  | {
      orgid: $orgid,
      title: $title,
      folder: $folder,
      interval: $interval,
      uid: $uid,
      rule_title: $rule_title,
      condition: $condition,
      refid: .refid,
      from: .relativeTimeRange.from,
      to: .relativeTimeRange.to,
      datasourceUid: .datasourceUid,
      mod: .mod,
      nin_doc_count: ."nin doc count",
      order: .order,
      orderBy: .orderBy,
      size: .size,
      type: .type
    }
]
| (first | keys_unsorted) as $keys 
| $keys, map([.[ $keys[] ]])[] 
| @csv
' alert_rules.json > alert_rules.csv

