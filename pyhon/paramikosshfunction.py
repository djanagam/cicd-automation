def ssh_and_manage_directories(csv_filename, privkey_path, pod, action):
    try:
        with open(csv_filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                fqdn = row['FQDN']
                url_string = row['URL String']
                executorsubDir = row['Executor SubDir']
                remote_workspace = f"/workerfs{pod}/workspace/{url_string}"
                symlink_target = f"/apps/jenkins/pipeline-worker/executors/{executorsubDir}/workspace/{url_string}"

                # Establish SSH connection
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(fqdn, username='ejen', key_filename=privkey_path)

                # Validate or execute based on the action argument
                if action == 'validate':
                    stdin, stdout, stderr = ssh.exec_command(f'''
                        if [ -L {symlink_target} ]; then 
                            echo "OK - Link exists: {symlink_target} -> $(readlink -f {symlink_target})"; 
                        elif [ -d {symlink_target} ]; then 
                            echo "DIR - Directory exists: {symlink_target}"; 
                        else 
                            echo "MISSING - {symlink_target} does not exist"; 
                        fi
                    ''')
                    result = stdout.read().decode().strip()
                    print(f"{fqdn}: {result}")
                elif action == 'execute':
                    stdin, stdout, stderr = ssh.exec_command(f'''
                        mkdir -p {remote_workspace};
                        if [ -L {symlink_target} ]; then 
                            echo "OK - Link exists: {symlink_target} -> $(readlink -f {symlink_target})"; 
                        elif [ -d {symlink_target} ]; then 
                            rm -rf {symlink_target}; 
                            ln -s {remote_workspace} {symlink_target}; 
                            echo "Created symlink: {symlink_target} -> {remote_workspace}"; 
                        elif [ ! -d {remote_workspace} ]; then 
                            ln -s {remote_workspace} {symlink_target}; 
                            echo "Created target and symlink: {symlink_target} -> {remote_workspace}"; 
                        else 
                            echo "MISSING - {symlink_target} does not exist"; 
                        fi
                    ''')
                    result = stdout.read().decode().strip()
                    print(f"{fqdn}: {result}")

                ssh.close()
    except Exception as e:
        print(f"An error occurred during SSH operations: {e}")