import asyncio, json, requests, websockets
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# --- CONFIG ---
TELEGRAM_TOKEN = "8704199257:AAHwaptImmaAvoxxiYMAv63lUE8E8BUUiNE"

# 1. Bot aur Dispatcher ko pehle define karein
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Active Trackers Storage
active_trackers = {} 

async def tracker_worker(symbol):
    print(f"🚀 Started tracking: {symbol}")
    uri = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@aggTrade"
    buy, sell, last_upd = 0.0, 0.0, 0.0
    msg_id = None
    
    try:
        async with websockets.connect(uri) as ws:
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                p, q, m = float(data['p']), float(data['q']), data['m']
                
                if not m: buy += q
                else: sell += q
                
                if (buy + sell) - last_upd >= 0.5:
                    last_upd = buy + sell
                    bias = "🟢 BULLISH" if buy > sell else "🔴 BEARISH"
                    text = f"🎯 *{symbol.upper()} LIVE*\n💰 Price: `${p}`\n🟢 Buy: {buy:.2f} | 🔴 Sell: {sell:.2f}\n⚖️ Bias: {bias}"
                    
                    if not msg_id:
                        msg = await bot.send_message(chat_id="7003795092", text=text, parse_mode="Markdown")
                        msg_id = msg.message_id
                    else:
                        await bot.edit_message_text(text=text, chat_id="7003795092", message_id=msg_id, parse_mode="Markdown")
    except Exception as e:
        print(f"⚠️ Error in {symbol}: {e}")

# 2. @dp.message wali line ab kaam karegi kyunke dp upar define ho chuka hai
@dp.message(Command("track"))
async def add_tracker(message: types.Message):
    args = message.text.split()
    if len(args) > 1:
        symbol = args[1].lower()
        if symbol not in active_trackers:
            task = asyncio.create_task(tracker_worker(symbol))
            active_trackers[symbol] = task
            await message.answer(f"✅ Now tracking {symbol.upper()}!")
        else:
            await message.answer(f"⚠️ Already tracking {symbol.upper()}!")
    else:
        await message.answer("⚠️ Please provide a pair, e.g., /track ethusdt")

async def main():
    print("🤖 Bot Ready! Use /track [pair] in Telegram.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())