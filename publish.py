# encoding:utf-8
import configparser
import os
import shutil

config_filename = 'pyproject.toml'
local_config: configparser.ConfigParser = configparser.ConfigParser()  # 本地配置文件，账号密码


def read_local_config(config: configparser.ConfigParser):
    local_filename = 'local.ini'
    if not os.path.exists(local_filename):
        return
    config.read(local_filename, encoding='utf-8')


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
    # 读取本地配置文件
    read_local_config(local_config)

    # 清理上次的产物
    clear()

    os.system('python3 -m hatchling build')

    # upload
    username = local_config.get('pypi', 'username')
    password = local_config.get('pypi', 'password')
    if username is None or password is None:
        os.system('python3 -m twine upload dist/*')
    else:
        os.system('python3 -m twine upload -u {username} -p {password} dist/*')
