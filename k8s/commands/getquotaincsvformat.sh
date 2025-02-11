kubectl describe quota | awk '
/Name:/ {name=$2}
/Resource / {
    getline
    while ($0 !~ /^$/) {
        if ($1 == "cpu") cpu=$2;
        else if ($1 == "memory") memory=$2;
        else if ($1 == "pods") pods=$2;
        else if ($1 == "requests.storage") storage=$2;
        getline
    }
    print name","cpu","memory","pods","storage
}' | sed '1i NAME,CPU,MEMORY,PODS,STORAGE'