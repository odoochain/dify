import os
import ssl
import sys
import time
import urllib.request

import nltk


def setup_ssl_context():
    """设置SSL上下文以避免证书验证问题"""
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

def setup_proxy():
    """设置HTTP和HTTPS代理"""
    # 从环境变量获取代理设置
    http_proxy = os.environ.get('HTTP_PROXY_2') or os.environ.get('http_proxy')
    https_proxy = os.environ.get('HTTPS_PROXY_2') or os.environ.get('https_proxy')
    
    if http_proxy or https_proxy:
        proxy_handler = urllib.request.ProxyHandler({
            'http': http_proxy,
            'https': https_proxy or http_proxy  # 如果没有https代理，使用http代理
        })
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)
        print(f"已设置代理: HTTP={http_proxy}, HTTPS={https_proxy}")
        return True
    return False

def download_nltk_data():
    """下载所需的NLTK数据包并处理可能的错误"""
    # 设置NLTK数据目录（可选）
    nltk_data_dir = os.environ.get('NLTK_DATA')
    if nltk_data_dir:
        os.makedirs(nltk_data_dir, exist_ok=True)
    
    # 需要下载的NLTK数据包
    nltk_data_packages = [
        'punkt',
        'averaged_perceptron_tagger'
    ]
    
    total = len(nltk_data_packages)
    
    # 下载每个包并处理可能的错误
    for i, package in enumerate(nltk_data_packages, 1):
        try:
            start_time = time.time()
            print(f"[{i}/{total}] 开始下载 {package}...")
            nltk.download(package, quiet=False)
            elapsed = time.time() - start_time
            print(f"[{i}/{total}] 成功下载 {package} (用时: {elapsed:.2f}秒)")
        except Exception as e:
            print(f"[{i}/{total}] 下载 {package} 时出错: {str(e)}", file=sys.stderr)
            # 如果是关键包，可以选择在失败时退出
            # sys.exit(1)
    
    print(f"NLTK数据下载完成，共 {total} 个包")

if __name__ == "__main__":
    setup_ssl_context()
    proxy_set = setup_proxy()
    if proxy_set:
        print("使用代理下载NLTK数据")
    else:
        print("未设置代理，使用直接连接下载NLTK数据")
    download_nltk_data()