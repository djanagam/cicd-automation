def create_pull_request(repository, new_branch, base_branch, api_token):
    url = f"https://github..com/api/v3/repos/org-eng/{repository}/pulls"
    headers = {
        'Authorization': f'token {api_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Dynamic PR body with table in Markdown
    body = f"""
### Automatic Migration Activity:
This PR contains the configuration changes which are picked from existing XLR templates and DB profiles configurations.

#### Template Details:
- **Template URL**: [https://cd.com/default/#/templates/Releasea67e1626b1ce40279f3cd71b4b844807](https://cd.aexp.com/default/#/templates/Releasea67e1626b1ce40279f3cd71b4b844807)
- **Template Alias Name**: `600000170-multidb_multi_phase_template-Release`
- For more information, review the [NGDM DB CICD Documentation](https://cd.aexp.com/docs).

---

#### Call for Action:
- Review the configuration files below, which include details of the repository and database:
  - **.github/workflows/db_migration.yml**:
    - This file contains the GitHub Actions workflow for schema migration.
    - Review the properties:

| Prop Name             | Description                                              |
|-----------------------|----------------------------------------------------------|
| `name`                | It's the same as the XLR template alias name             |
| `branch`              | Same as in the XLR build phase                           |
| `folder`              | Same as in the XLR build phase                           |
| `config_file`         | New configuration file name containing DB details        |
| `change_template_name`| Same as configured in XLR for SRFC                       |
| `assignment_workgroup`| Same as configured in XLR for SRFC                       |
| `car_id`              | As per the DTC                                           |
| `car_name`            | As per the DTC                                           |

  - **dbscripts/db_config.yml**:
    - This file contains the database host, port, and database name values picked from existing DB profiles used in the XLR template.
    - It also references the Liquibase properties file and HashiCorp Vault path.
    - For any modification, change the values after PR merge. For details, refer to the [documentation](link).

---

#### Post-Merge Activities:
1. Merge the PR.
2. Validate the new workflow listed in the "Action Tab" by name `600000170-multidb_multi_phase_template-Release`.
3. Review environment protection settings with existing deployment users. For details, refer to [link](link).
4. Execute the workflow with "Validate Configuration" to confirm the setup. For a quick video reference, check [link](link).
5. For deployment usage, refer to the documentation at [link](link).
"""

    data = {
        "title": f"Pull request from {new_branch} to {base_branch}",
        "head": new_branch,
        "base": base_branch,
        "body": body
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        pr_url = response.json().get('html_url')
        logger.info(f"Pull request created successfully: {pr_url}")
        return pr_url
    else:
        logger.error(f"Failed to create pull request: {response.status_code} {response.text}")
        return ""