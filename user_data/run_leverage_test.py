import os
import re
import subprocess
import json

strategy_file = "/Users/hoangkien/Youtube/trade/user_data/strategies/SmartMoneyConcepts.py"

def set_leverage(lev):
    with open(strategy_file, 'r') as f:
        content = f.read()
    
    new_content = re.sub(
        r'def leverage\(.*?\n.*?return \d+\.\d+',
        f'def leverage(self, pair, current_time, current_rate, proposed_leverage,\n                 max_leverage, entry_tag, side, **kwargs):\n        return {float(lev)}',
        content,
        flags=re.DOTALL | re.MULTILINE
    )
    
    with open(strategy_file, 'w') as f:
        f.write(new_content)

print("🚀 Starting Leverage Sweep (x2 to x10) for SMC Monster...")
results = []

for lev in range(2, 11):
    print(f"\n⏳ Testing Leverage x{lev}...")
    set_leverage(lev)
    
    cmd = "rtk docker-compose run --rm freqtrade backtesting --strategy SmartMoneyConcepts -c user_data/config-futures.json --timerange 20250101-20260514"
    process = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd="/Users/hoangkien/Youtube/trade")
    
    output = process.stdout + process.stderr
    
    # Extract profit
    profit_match = re.search(r'│\s*SmartM[^\s│]*\s*│\s*\d+\s*│\s*[\d\.\-]+\s*│\s*[\d\.\-]+\s*│\s*([\d\.\-]+)\s*│', output)
    profit = profit_match.group(1) if profit_match else "0"
    
    # Extract drawdown
    dd_match = re.search(r'Absolute drawdown \(wallet balance\)\s*│\s*[\d\.\-]+\s*USDT\s*\(\s*([\d\.\-]+)%\s*\)', output)
    dd = dd_match.group(1) if dd_match else "100"
    
    # Extract sharpe
    sharpe_match = re.search(r'Sharpe \(daily wallet balance\)\s*│\s*([\d\.\-]+)', output)
    sharpe = sharpe_match.group(1) if sharpe_match else "0"
    
    print(f"✅ Result x{lev} -> Profit: {profit}%, Drawdown: {dd}%, Sharpe: {sharpe}")
    results.append({
        "leverage": lev, 
        "profit": float(profit), 
        "drawdown": float(dd), 
        "sharpe": float(sharpe)
    })

print("\n" + "="*50)
print("📊 LEVERAGE SWEEP RESULTS SUMMARY")
print("="*50)
print(f"{'Leverage':<10} | {'Profit (%)':<15} | {'Drawdown (%)':<15} | {'Sharpe':<10}")
print("-" * 55)
for r in results:
    print(f"x{r['leverage']:<9} | {r['profit']:<15} | {r['drawdown']:<15} | {r['sharpe']:<10}")

# Determine the best leverage (Highest profit with Drawdown <= 20%)
valid_results = [r for r in results if r['drawdown'] <= 20.0]
if not valid_results:
    print("\n⚠️ No leverage kept Drawdown under 20%. Picking the least bad one.")
    best = min(results, key=lambda x: x['drawdown'])
else:
    # Among valid, pick the highest profit
    best = max(valid_results, key=lambda x: x['profit'])

print("\n🏆 BEST LEVERAGE FOR THE MONSTER:")
print(f"-> Leverage: x{best['leverage']}")
print(f"-> Profit:   {best['profit']}%")
print(f"-> Drawdown: {best['drawdown']}%")
print(f"-> Sharpe:   {best['sharpe']}")

print(f"\n🔧 Automatically setting strategy to optimal leverage (x{best['leverage']})...")
set_leverage(best['leverage'])
print("🎉 Done!")
