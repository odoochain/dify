import os
import ssl
import sys
import time
import urllib.request


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

def print_progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█'):
    """打印进度条"""
    percent = "{:.1f}".format(100 * (iteration / float(total)))  # 移除了显式位置索引 {0:.1f}
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
    # 如果完成则打印新行
    if iteration == total: 
        print()

def cache_tiktoken_models():
    """预缓存常用的tiktoken模型，提高首次使用性能"""
    # 导入tiktoken
    import tiktoken
    
    # 要缓存的模型和编码器
    model_encodings = [
        # 模型名称使用encoding_for_model
        {'type': 'model', 'name': 'gpt-3.5-turbo'},
        {'type': 'model', 'name': 'gpt-4'},
        {'type': 'model', 'name': 'gpt2'},
        {'type': 'model', 'name': 'text-davinci-003'},
        # 编码器名称使用get_encoding
        {'type': 'encoding', 'name': 'p50k_base'},
        {'type': 'encoding', 'name': 'cl100k_base'},
        {'type': 'encoding', 'name': 'r50k_base'}
    ]
    
    total = len(model_encodings)
    
    print(f"开始缓存 {total} 个tiktoken模型和编码器...")
    
    # 确保缓存目录存在
    cache_dir = os.environ.get('TIKTOKEN_CACHE_DIR', '/app/api/.tiktoken_cache')
    os.makedirs(cache_dir, exist_ok=True)
    print(f"tiktoken缓存目录: {cache_dir}")
    
    # 缓存每个模型或编码器
    for i, item in enumerate(model_encodings, 1):
        item_type = item['type']
        item_name = item['name']
        try:
            start_time = time.time()
            print(f"[{i}/{total}] 开始缓存{item_type}: {item_name}...")
            print_progress_bar(0, 3, prefix=f'{item_type} {item_name}:', suffix='初始化中', length=40)
            
            print_progress_bar(1, 3, prefix=f'{item_type} {item_name}:', suffix='加载编码器', length=40)
            
            # 根据类型选择不同的加载方法
            if item_type == 'model':
                encoding = tiktoken.encoding_for_model(item_name)
            else:  # encoding
                encoding = tiktoken.get_encoding(item_name)
                
            print_progress_bar(2, 3, prefix=f'{item_type} {item_name}:', suffix='测试编码', length=40)
            
            # 测试编码以确保缓存生效
            test_text = "Hello, world!"
            tokens = encoding.encode(test_text)
            
            print_progress_bar(3, 3, prefix=f'{item_type} {item_name}:', suffix='完成', length=40)
            
            elapsed = time.time() - start_time
            print(f"[{i}/{total}] 成功缓存{item_type} {item_name} "
                  f"(用时: {elapsed:.2f}秒, 测试文本编码为 {len(tokens)} 个token)")
        except Exception as e:
            print(f"\n[{i}/{total}] 缓存{item_type} {item_name} 时出错: {str(e)}", file=sys.stderr)
    
    print(f"tiktoken模型和编码器缓存完成，共 {total} 个")

# 在文件末尾的main()函数前添加以下代码
def cache_single_model(model_name):
    """只缓存单个指定的模型"""
    import tiktoken
    
    print(f"开始缓存模型: {model_name}...")
    
    # 确保缓存目录存在
    cache_dir = os.environ.get('TIKTOKEN_CACHE_DIR', '/app/api/.tiktoken_cache')
    os.makedirs(cache_dir, exist_ok=True)
    print(f"tiktoken缓存目录: {cache_dir}")
    
    try:
        start_time = time.time()
        # 加载模型编码器
        encoding = tiktoken.encoding_for_model(model_name)
        
        # 测试编码以确保缓存生效
        test_text = "Hello, world!"
        tokens = encoding.encode(test_text)
        
        elapsed = time.time() - start_time
        print(f"成功缓存模型 {model_name} "
              f"(用时: {elapsed:.2f}秒, 测试文本编码为 {len(tokens)} 个token)")
    except Exception as e:
        print(f"缓存模型 {model_name} 时出错: {str(e)}", file=sys.stderr)

# 修改main函数
def main():
    """主函数，可以直接运行或被导入使用"""
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == '--model':
        if len(sys.argv) > 2:
            model_name = sys.argv[2]
            setup_ssl_context()
            setup_proxy()
            cache_single_model(model_name)
            return
        else:
            print("请指定模型名称，例如: python cache_tiktoken_models.py --model gpt2")
            return
    
    # 原有的完整缓存逻辑
    setup_ssl_context()
    proxy_set = setup_proxy()
    if proxy_set:
        print("使用代理下载tiktoken模型")
    else:
        print("未设置代理，使用直接连接下载tiktoken模型")
    cache_tiktoken_models()

if __name__ == "__main__":
    main()