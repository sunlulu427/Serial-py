# encoding:utf-8
import argparse
import configparser
import os
import platform
import re
import shutil
import sys

config_filename = 'pyproject.toml'
update_version_type = 'small'  # 升级时默认修改小的版本号
pattern = re.compile(r'version = "(\d+)\.(\d+)\.(\d+)"')
local_config: configparser.ConfigParser = configparser.ConfigParser()  # 本地配置文件，账号密码
py_command = 'py' if platform.system() == 'Windows' else 'python3'


def read_local_config(config: configparser.ConfigParser):
    local_filename = 'local.ini'
    if not os.path.exists(local_filename):
        return
    config.read(local_filename, encoding='utf-8')


def update_version_in_config_file() -> str:
    if not os.path.exists(config_filename):
        raise RuntimeError(f'File pyproject.toml is not found')
    with open(config_filename, 'r+') as f:
        origin_content = f.read()
        searched = re.search(pattern, origin_content)
        if not searched:
            raise RuntimeError(f'Field version is not found in {config_filename}')
        v1, v2, v3 = map(lambda it: int(it), searched.groups())
        print(f'origin version is: {v1}.{v2}.{v3}')
        # 版本号升级 检查版本号，并+1
        if update_version_type == 'big':
            v1 += 1
        elif update_version_type == 'middle':
            v2 += 1
        else:
            v3 += 1
        new_version = f'{v1}.{v2}.{v3}'
        print(f'new version is: {new_version}')
        new_content = re.sub(pattern, f'version = \"{new_version}\"', origin_content)
        f.seek(0)
        f.truncate()
        f.write(new_content)
        print(f'update version to {new_version} in {config_filename}.')
        return new_version


def clear():
    to_delete_dirs = [
        'build', 'dist',
        *[d for d in os.listdir('.') if d.endswith('egg-info')]
    ]
    for to_delete_dir in to_delete_dirs:
        if os.path.exists(to_delete_dir):
            print(f'删除{to_delete_dir}目录')
            shutil.rmtree(to_delete_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('')
    parser.add_argument('--v', type=str, required=False, default='small')
    parser.add_argument('--skip_build', type=bool, required=False, default=False)
    parser.add_argument('--git_push', type=bool, required=False, default=False)
    arguments, _ = parser.parse_known_args(sys.argv)
    update_version_type = arguments.v
    # 读取本地配置文件
    read_local_config(local_config)

    # 清理上次的产物
    clear()

    # 更新版本，会直接影响产物的名称
    version = update_version_in_config_file()

    # build
    if not arguments.skip_build:
        print('begin to build =>')
        os.system(f'{py_command} -m build')

    # upload
    username = local_config.get('pypi', 'username')
    password = local_config.get('pypi', 'password')
    if username is None or password is None:
        os.system(f'{py_command} -m twine upload dist/*')
    else:
        os.system(f'{py_command} -m twine upload -u {username} -p {password} dist/*')

    # git commit
    if arguments.git_push:
        os.system('git add .')
        os.system(f'git commit -m "[Auto]: publish version {version}"')
        os.system('git push')
