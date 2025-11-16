from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

# --- 關鍵修改 ---
# 絕對不要將你的金鑰寫死在這裡！
# 程式碼會從你稍後在 Render 平台上設定的「環境變數」中讀取金鑰
ACCESS_TOKEN = os.environ.get('YOUR_CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.environ.get('YOUR_CHANNEL_SECRET')

# 檢查金鑰是否存在，如果 Render 平台上沒有設定，程式會在這裡印出錯誤日誌
if ACCESS_TOKEN is None or CHANNEL_SECRET is None:
    print("嚴重錯誤：環境變數 'YOUR_CHANNEL_ACCESS_TOKEN' 或 'YOUR_CHANNEL_SECRET' 尚未在 Render 上設定。")
    # 你可以選擇在這裡讓程式 crash，但通常印出日誌就足以讓 Render 部署失敗並顯示錯誤
    # abort(500, "Server configuration error") 
    
line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error("Invalid signature. 請檢查你的 Channel Secret 是否在 Render 上設定正確。")
        abort(400)
    except Exception as e:
        app.logger.error(f"處理訊息時發生錯誤: {e}")
        abort(500)

    return 'OK'

# 處理文字訊息 (Echo)
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text)) # 回應和用戶輸入一樣的訊息
    except Exception as e:
        app.logger.error(f"回覆訊息時發生錯誤: {e}")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
