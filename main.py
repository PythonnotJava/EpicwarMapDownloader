import requests
from bs4 import BeautifulSoup
import os
import time
from tqdm import tqdm  # 进度条模块

# 代理设置（你可以换成自己的代理）
proxies = {
    'http': 'socks5h://127.0.0.1:xxx',  # 使用混合端口
    'https': 'socks5h://127.0.0.1:xxx', # 使用混合端口
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

base_url = "https://www.epicwar.com"
save_dir = "warcraft_maps"
os.makedirs(save_dir, exist_ok=True)

# 设置要爬的页数
start_page = 8
end_page = 10

for page in range(start_page, end_page + 1):
    url = f"https://www.epicwar.com/maps/search/?go=1&n=&a=&c=2&p=8&pf=1&roc=1&tft=1&page={page}&sort=time&order=desc"
    print(f"正在解析第 {page} 页：{url}")

    res = requests.get(url, headers=headers, proxies=proxies)
    soup = BeautifulSoup(res.text, 'html.parser')

    # 找到所有下载链接
    entries = soup.select('td.listentry a[href^="/maps/download/"]')
    print(f"找到 {len(entries)} 个地图")

    for a in entries:
        map_name = a.text.strip().replace('/', '_')  # 防止文件名非法
        download_url = base_url + a['href']
        print(f"准备下载地图：{map_name} -> {download_url}")

        try:
            # 获取文件大小（不一定有，视具体页面而定）
            response = requests.head(download_url, headers=headers, proxies=proxies)
            file_size = int(response.headers.get('Content-Length', 0))  # 取得文件大小
            print(f"文件大小：{file_size / 1024 / 1024:.2f} MB")

            # 通过流式下载获取文件数据
            with requests.get(download_url, headers=headers, proxies=proxies, stream=True) as r:
                r.raise_for_status()  # 检查请求是否成功
                file_path = os.path.join(save_dir, f"{map_name}.w3x")

                # 使用 tqdm 显示进度条
                with open(file_path, 'wb') as f, tqdm(
                    total=file_size, unit='B', unit_scale=True, desc=map_name
                ) as bar:
                    for chunk in r.iter_content(chunk_size=8192):  # 每次下载 8KB
                        f.write(chunk)
                        bar.update(len(chunk))

            print(f"✅ 成功下载：{file_path}")
        except Exception as e:
            print(f"❌ 下载失败：{map_name}，原因：{e}")

        time.sleep(1)  # 给服务器留点时间，防止被封

print("🎉 全部下载完成！")
