jq -r '
  ["Shortname", "Controllerurl", "url"],
  (.Usages[] | .[].plugininfo.Shortname as $shortname |
               .[].Location.Controllerurl as $controllerurl |
               .[].Location.url as $url |
               [$shortname, $controllerurl, $url])
  | @csv
' data.json