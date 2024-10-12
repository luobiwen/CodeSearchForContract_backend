from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import gpt_integration  # 将文件名改为符合Python规范的ASCII文件名
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# 配置数据库，使用SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contracts.db'
db = SQLAlchemy(app)


# 创建数据库模型
class SmartContract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(42), unique=True, nullable=False)
    contract_code = db.Column(db.Text, nullable=False)


# 初始化数据库
db.create_all()


# 定义获取最近添加的智能合约并分析的API
@app.route('/analyze_latest_contract', methods=['GET'])
def analyze_latest_contract():
    try:
        # 获取最近添加的智能合约
        latest_contract = SmartContract.query.order_by(SmartContract.id.desc()).first()
        if not latest_contract:
            return jsonify({"error": "No contract found"}), 404

        # 分析智能合约代码
        analysis_result = gpt_integration.analyze_smart_contract(latest_contract.contract_code)

        return jsonify({"address": latest_contract.address, "analysis": analysis_result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 定义上传智能合约的API
@app.route('/upload_contract', methods=['POST'])
def upload_contract():
    try:
        # 从请求中获取智能合约地址
        data = request.json
        contract_address = data.get('address')
        if not contract_address:
            return jsonify({"error": "No contract address provided"}), 400

        # 模拟通过 Etherscan API 下载智能合约代码
        response = requests.get(
            f'https://api.etherscan.io/api?module=contract&action=getsourcecode&address={contract_address}&apikey=YourApiKeyToken'
        )

        if response.status_code != 200:
            return jsonify({"error": "Failed to download contract"}), 500

        # 检查Etherscan API响应内容
        result = response.json().get('result')
        if not result or len(result) == 0:
            return jsonify({"error": "No contract code found in response"}), 404

        contract_code = result[0].get('SourceCode')
        if not contract_code:
            return jsonify({"error": "No contract source code available"}), 404

        # 将智能合约存储到数据库中
        new_contract = SmartContract(address=contract_address, contract_code=contract_code)
        db.session.add(new_contract)
        db.session.commit()

        return jsonify({"message": "Contract uploaded successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 新增一个与前端 Mock.js 接口对应的端点
@app.route('/code/send_code', methods=['POST'])
def send_code():
    try:
        data = request.json
        contract_code = data.get('code')
        if not contract_code:
            return jsonify({"error": "No contract code provided"}), 400

        # 分析智能合约代码
        analysis_result = gpt_integration.analyze_smart_contract(contract_code)

        return jsonify({
            "tags": ["error", "warning", "info"],
            "message": analysis_result
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 为了允许跨域请求，安装 Flask-CORS 并配置
    from flask_cors import CORS
    CORS(app)
    app.run(debug=True)