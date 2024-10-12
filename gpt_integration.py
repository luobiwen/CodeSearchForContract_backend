# 需要先有智能合约文件.sol
import openai
# GPT-4智能合约分析函数
def analyze_smart_contract(code):
    try:
        # 调用GPT模型分析智能合约
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一位智能合约安全专家，请帮忙分析智能合约的潜在漏洞。"},
                {"role": "user",
                 "content": f"请简要分析以下智能合约代码中的潜在漏洞，用最简短的方式给出关键漏洞描述，并使用以下格式返回结果："
                            "标签: [error, warning, info] 漏洞名称。"
                            "如果特别严重的漏洞用error，"
                            "不会造成过大损失但有隐藏风险的用warning，"
                            "没有漏洞用info。\n\n{code}"}
            ],
            max_tokens=500
        )

        # 获取GPT返回的内容
        analysis_result = response['choices'][0]['message']['content']

        # 提取标签和漏洞名称
        lines = analysis_result.strip().splitlines()
        results = []
        for line in lines:
            # 返回的格式是 "标签: 漏洞名称"
            if ":" in line:
                tag, name = map(str.strip, line.split(":", 1))
                if tag in ['error', 'warning', 'info']:
                    results.append({"tag": tag, "name": name})

        return results

    except Exception as e:
        return [{"tag": "error", "name": f"分析时出错: {str(e)}"}]
