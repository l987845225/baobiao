import requests
import json
import pandas as pd

# 共享的标头
headers = {
    "Accept": "application/json, text/javascript, /; q=0.01",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": "PHPSESSID=lsesfedlc48089eou9ntka7v52",
    "Host": "yyxt.xmx023.com",
    "Origin": "http://yyxt.xmx023.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "X-Requested-With": "XMLHttpRequest",
}

def read_names_from_file(file_path):
    # 使用 os.path.join 和 os.environ 获取绝对路径
    absolute_path = os.path.join(os.environ["GITHUB_WORKSPACE"], file_path)
    
    with open(absolute_path, "r", encoding="utf-8") as user_file:
        return user_file.read().split(',')

def fetch_data(url, params):
    response = requests.post(url, headers=headers, data=params)
    try:
        return json.loads(response.text)
    except json.JSONDecodeError as e:
        print(f"错误: 在查询数据时发生解析错误: {e}")
        return None

def count_data_for_name(url, name, column_name, filter_condition=None):
    page_num = 0
    count = 0

    while True:
        params = {"key": "value", "pageNum": str(page_num)}
        json_data = fetch_data(url, params)

        if not json_data or "list" not in json_data or not json_data["list"]:
            break

        for item in json_data["list"]:
            if item.get("type_in") == name and (not filter_condition or filter_condition(item)):
                count += 1

        if page_num < json_data.get("totalPage", 1):
            page_num += 1
        else:
            break

    return {column_name: count}

def main():
    names = read_names_from_file("user.txt")

    df = pd.DataFrame(columns=["姓名", "有效客资", "预约互联网"])

    # 处理第一个链接 http://yyxt.xmx023.com/index.php/index/dengji_ajax.html
    url_dengji = "http://yyxt.xmx023.com/index.php/index/dengji_ajax.html"

    # 处理第二个链接 http://yyxt.xmx023.com/index.php/index/yuyue_ajax.html
    url_yuyue = "http://yyxt.xmx023.com/index.php/index/yuyue_ajax.html"

    for name in names:
        result_dengji = count_data_for_name(url_dengji, name, "有效客资", lambda item: item.get("huifang") != "无效")
        result_yuyue = count_data_for_name(url_yuyue, name, "预约互联网", lambda item: item.get("huifang") == "预约互联网医院")
        df = pd.concat([df, pd.DataFrame({"姓名": [name], **result_dengji, **result_yuyue})], ignore_index=True)

    # 保存结果到表格
    df.to_csv("baobiao.csv", index=False, encoding='utf-8-sig')

    print("查询结果已保存在 baobiao.csv 文件中。")

    # 生成HTML文件
    generate_html_from_csv("baobiao.csv", "index.html")

def generate_html_from_csv(csv_file, output_html):
    # 读取CSV文件
    df = pd.read_csv(csv_file)

    # 从DataFrame生成HTML
    html_content = df.to_html(index=False)

    # 创建HTML文件
    with open(output_html, "w", encoding="utf-8") as html_file:
        html_file.write(f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>统计结果</title>
</head>
<body>
  <h2>统计结果</h2>
  {html_content}
</body>
</html>
""")

if __name__ == "__main__":
    main()
