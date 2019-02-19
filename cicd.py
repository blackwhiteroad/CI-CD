import hashlib
import wget
import os
import requests
import tarfile


#1、判断是否有最新版本
def has_new_version(live_url, live_fname):
    if not os.path.isfile(live_fname):
        return True

    with open(live_fname) as fobj:
        local_version = fobj.read()

    r = requests.get(live_url)
    if r.text != local_version:
        return True

    return False


#2、如果有新版本则下载
def md5sum(app_fname):
    m = hashlib.md5()
    with open(app_fname, 'rb') as fobj:
        while True:
            data = fobj.read(4096)
            if not data:
                break
            m.update(data)
    return m.hexdigest()


#3、判断下载的软件包是否是完整的
def deploy(app_fname, deploy_dir):
    os.chdir(deploy_dir)
    tar = tarfile.open(app_fname, 'r:gz')
    tar.extractall()
    tar.close()
    app_path = os.path.basename(app_fname)
    app_path = app_path.replace('.tar.gz', '')
    app_path = os.path.join(deploy_dir, app_path)
    mudi_path = '/var/www/html/gooc'
    if os.path.exists(mudi_path):
        os.unlink(mudi_path)
    os.symlink(app_path, mudi_path)


#4、如果软件包完整，则解压缩并部署
if __name__ == '__main__':
    live_url = 'http://192.168.5.7/deploy/live_version'
    live_fname = '/var/www/html/deploy/live_version'
    if not has_new_version(live_url, live_fname):
        print('no new version')
        exit()
    r = requests.get(live_url)
    download_dir = '/var/www/download'
    deploy_dir = '/var/www/deploy'
    app_url = 'http://192.168.5.7/deploy/packages/website_%s.tar.gz' % (r.text.strip())
    wget.download(app_url, download_dir)
    app_md5_url = app_url + '.md5'
    wget.download(app_md5_url, download_dir)
    if os.path.exists(live_fname):
        os.remove(live_fname)
    # wget.download(live_url, deploy_dir)
    app_fname = os.path.join(download_dir, app_url.split('/')[-1])
    local_md5 = md5sum(app_fname)
    r = requests.get(app_md5_url)
    if local_md5 != r.text.strip():
        print('check file failed')
        exit(1)
    deploy(app_fname, deploy_dir)