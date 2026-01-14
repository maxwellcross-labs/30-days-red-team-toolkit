import os
from utils.helpers import run_command, check_file_permissions


def _check_task_privesc(task, reporter):
    user = task.get('user', '').upper()
    if 'SYSTEM' not in user and 'ADMINISTRATOR' not in user:
        return

    command = task.get('command', '')
    if not command:
        return

    if command.lower().endswith(('.bat', '.ps1', '.vbs', '.js')):
        script_path = command.strip('"')
        if os.path.exists(script_path):
            perm_result = check_file_permissions(script_path)
            if perm_result:
                print(f"[+] Found scheduled task with writable script: {task['name']}")
                reporter.add_finding('high', {
                    'category': 'Weak Scheduled Task',
                    'task': task['name'],
                    'script': script_path,
                    'user': task['user'],
                    'exploitation': 'Modify script to execute malicious payload',
                    'impact': 'High - Execute as SYSTEM'
                })


def enumerate_scheduled_tasks(reporter):
    print(f"\n" + "=" * 60)
    print(f"SCHEDULED TASK ENUMERATION")
    print(f"=" * 60)

    try:
        cmd = 'schtasks /query /fo LIST /v'
        result = run_command(cmd)

        print(f"[*] Checking for tasks running as SYSTEM with weak permissions...")

        current_task = {}
        for line in result.stdout.split('\n'):
            if 'TaskName:' in line:
                if current_task:
                    _check_task_privesc(current_task, reporter)
                current_task = {'name': line.split('TaskName:')[1].strip()}
            elif 'Task To Run:' in line:
                current_task['command'] = line.split('Task To Run:')[1].strip()
            elif 'Run As User:' in line:
                current_task['user'] = line.split('Run As User:')[1].strip()

        if current_task:
            _check_task_privesc(current_task, reporter)

        print(f"\n[*] Scheduled task enumeration complete")
    except Exception as e:
        print(f"[-] Scheduled task enumeration failed: {e}")