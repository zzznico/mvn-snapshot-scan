import requests
import json
import subprocess
import os

def git_clone(repo_url,local_directory):
    try:
        subprocess.run(["git", "clone", repo_url, local_directory], check=True)
        print(f"Repository cloned to {local_directory}")
    except subprocess.CalledProcessError as e:
        print(f"Cloning failed: {e}")

def execute_mvn_command(directory,appcode):
    # command =f'mvn dependency:list {directory} | awk -F \'[,:]\' \'{if ($3 == "jar") print $2,$3,$4,$5,$6}\''
    command =f"/Library/apache-maven-3.5.4/bin/mvn dependency:list -f {directory}"
    command_append = """| awk -F '[,:]' '{if ($3 == "jar") print $2,$3,$4}'"""
    command = command + command_append
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    if error:
        print(f"Error occurred: {error.decode('utf-8')}")
    else:
        snapshot_found = 'SNAPSHOT'.lower()  in output.decode('utf-8').lower()
        if snapshot_found:
            print("Snapshot found! Writing error to /scan.txt")
            unique_snapshot_output = set(output.decode('utf-8').splitlines())
            file_path = f'/Downloads/snapshot/{appcode}/scan.txt'
            directory_structure = '/'.join(file_path.split('/')[:-1])
            os.makedirs(directory_structure, exist_ok=True)
            with open(directory + '/mvn-result.txt', 'w') as result_file:
                with open(file_path, 'a') as snapshot_file:
                    for line in unique_snapshot_output:
                        result_file.write(line + '\n')
                        if 'SNAPSHOT'.lower() in line.lower():
                            snapshot_file.write(line + '\n')
        else:
            unique_output = set(output.decode('utf-8').splitlines())
            with open(directory + '/mvn-result.txt', 'w') as file:
                for line in unique_output:
                    file.write(line + '\n')

        print(f"Results saved to mvn-result.txt")


def get_application_list():
    url = ""
    data = {"": "", "pageSize": 2}
    new_data_available = True
    page_num = 1
    while new_data_available:
        data["pageNum"] = page_num
        response = requests.post(url, json=data)
        if response.status_code != 200:
            print(f"请求失败，状态码：{response.status_code}")
            break
        result = response.json()
        # 如果结果为空，说明没有更多数据
        if not result.get("data") or len(result.get("data")) == 0:
            new_data_available = False
        else:
            for item in result['data']:
                if item['codeLanguage'] == 'Java' and item['gitlabProjectId'] is not None:
                    yield result
            page_num += 1



def get_project_info(project_id):
    url = f"https://gitexample.com/api/v4/projects/{project_id}"
    headers = {
        "Accept": "application/json",
        "Private-Token": ""
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        project_data = response.json()
        path_with_namespace = project_data['http_url_to_repo']
        return path_with_namespace
    else:
        print(f"请求失败，状态码：{response.status_code}")
        return None




for result in get_application_list():
    for item in result['data']:
        http_url=get_project_info(item['gitlabProjectId'])
        if http_url is not None:
            print(http_url+"开始下载代码")
            appcode=str(item['code'])
            code_dir="/Downloads/"+appcode
            git_clone(http_url, code_dir)
            print("代码下载完毕")
            execute_mvn_command(code_dir,appcode)
        else:
            print("未能获取项目信息")
print("脚本运行结束")





