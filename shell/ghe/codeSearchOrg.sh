curl -s -H "Authorization: token ghp_xxxxxxx" \
    "https://api.github.com/search/code?q=%22com.gradle.enterprise%22+in:file+org:app-tst&per_page=100" | \
    jq -r '.items[] | [.repository.full_name, .name, .html_url] | @csv'
    
    
    
    curl -s -H "Authorization: token ghp_xxxxxxx" \
    "https://api.github.com/search/code?q=%22com.gradle.enterprise%22+in:file+org:app-tst&per_page=100" | \
    jq -r '.items[] | select(.text_matches[].fragment | contains("com.gradle.enterprise")) | [.repository.full_name, .name, .html_url] | @csv'