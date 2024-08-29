def ssh_and_manage_directories(csv_filename, privkey_path, pod, action):
    try:
        with open(csv_filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                fqdn = row['FQDN']
                url_string = row['URL String']
                executorsubDir = row['Executor SubDir']

                # Skip processing if executorsubDir is empty
                if not executorsubDir:
                    print(f"{fqdn}: Skipping row because Executor SubDir is empty")
                    continue

                remote_workspace = f"/workerfs{pod}/workspace/{url_string}"
                symlink_target = f"/apps/jenkins/pipeline-worker/executors/{executorsubDir}/workspace/{url_string}"
                parent_directory = os.path.dirname(symlink_target)

                # Establish SSH connection
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(fqdn, username='ejen', key_filename=privkey_path)

                # Validate or execute based on the action argument
                if action == 'validate':
                    stdin, stdout, stderr = ssh.exec_command(f'''
                        if [ -L {symlink_target} ]; then 
                            if [ -e $(readlink -f {symlink_target}) ]; then 
                                echo "OK - Link exists and target is valid: {symlink_target} -> $(readlink -f {symlink_target})"; 
                            else 
                                echo "Invalid target for symlink: {symlink_target}";
                            fi
                        elif [ -d {symlink_target} ]; then 
                            echo "DIR - Directory exists: {symlink_target}"; 
                        elif [ ! -e {symlink_target} ]; then 
                            echo "MISSING - {symlink_target} does not exist and is not a directory"; 
                        fi
                    ''')
                    result = stdout.read().decode().strip()
                    print(f"{fqdn}: {result}")

                elif action == 'execute':
                    stdin, stdout, stderr = ssh.exec_command(f'''
                        if [ -L {symlink_target} ]; then 
                            if [ -e $(readlink -f {symlink_target}) ]; then 
                                echo "OK - Link exists and target is valid: {symlink_target} -> $(readlink -f {symlink_target})"; 
                            else 
                                echo "Invalid target, unlinking symlink: {symlink_target}";
                                unlink {symlink_target};
                            fi
                        elif [ -d {symlink_target} ]; then 
                            echo "DIR - Directory exists: {symlink_target}"; 
                        elif [ ! -e {symlink_target} ]; then 
                            if [ -d {remote_workspace} ]; then 
                                mkdir -p {parent_directory};
                                ln -s {remote_workspace} {symlink_target};
                                echo "Created symlink: {symlink_target} -> {remote_workspace} after creating parent directory";
                            else 
                                echo "MISSING - Target directory {remote_workspace} does not exist; no symlink created for {symlink_target}";
                            fi
                        fi
                    ''')
                    result = stdout.read().decode().strip()
                    print(f"{fqdn}: {result}")

                ssh.close()
    except Exception as e:
        print(f"An error occurred during SSH operations: {e}")