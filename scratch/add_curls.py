import re

filepath = 'd:/doc/dev-guide/dev-guide/02.产品业务AI文档/TBS系统/TBS_接口文档.md'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add curl examples before the JSON request body examples
# We need to find the API path to construct the curl command.
# The API path is in the basic info table: | 接口地址 | `/scene/createScene` |
# Then we find the "**请求示例**" and the following ```json block.

def add_curl(match):
    path = match.group(1)
    before_req_example = match.group(2)
    req_example_title = match.group(3)
    json_body = match.group(4)
    
    curl_cmd = f"**请求示例 (cURL)**\\n\\n```bash\\ncurl -X POST 'https://cwork-web-test.xgjktech.com.cn/open-api/tbs-admin{path}' \\\\\\n  -H 'appKey: YOUR_APP_KEY' \\\\\\n  -H 'Content-Type: application/json' \\\\\\n  -d '{json_body.strip()}'\\n```\\n\\n**请求示例 (JSON Body)**\\n\\n```json\\n{json_body}\\n```"
    
    return f"| 接口地址 | `{path}` |{before_req_example}{req_example_title}\\n\\n```json\\n{json_body}\\n```"
    
# Actually it's easier to just find the URL and then replace the next 请求示例.
# Let's do a more robust regex or just manual replace.
blocks = content.split('**基本信息**')
new_blocks = [blocks[0]]

for block in blocks[1:]:
    # extract path
    path_match = re.search(r'\|\s*接口地址\s*\|\s*`([^`]+)`\s*\|', block)
    if path_match:
        path = path_match.group(1)
        # find the json request example
        # **请求示例**\n\n```json\n...\n```
        def replacer(m):
            json_body = m.group(1)
            curl_cmd = f"**请求示例**\\n\\n```bash\\ncurl -X POST 'https://cwork-web-test.xgjktech.com.cn/open-api/tbs-admin{path}' \\\\\\n  -H 'appKey: YOUR_APP_KEY' \\\\\\n  -H 'Content-Type: application/json' \\\\\\n  -d '{json_body.strip()}'\\n```\\n\\n**请求体示例**\\n\\n```json\\n{json_body}\\n```"
            return curl_cmd
            
        block = re.sub(r'\*\*请求示例\*\*\s*```json\s*(.*?)\s*```', replacer, block, flags=re.DOTALL)
    new_blocks.append(block)

final_content = '**基本信息**'.join(new_blocks)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(final_content)
print("Added curl examples.")
