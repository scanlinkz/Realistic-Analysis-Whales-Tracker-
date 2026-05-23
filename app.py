from flask import Flask
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running"
if __name__ == '__main__':
    import threading
    def run_bot():
        import os
        os.system("python bot.py")
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
