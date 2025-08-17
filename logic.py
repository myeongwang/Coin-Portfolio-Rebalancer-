import pyupbit

# df=pyupbit.get_ohlcv("KRW-BTC","minute5")
# print(df)

# 로그인
access = "74r0aaqEDgWbE8Qdn8OtTZCceOUGjoreIRnUCuIi"                         # Upbit API access 키
secret = "A7068XkF8bLx7fYMgB5FByfZJa2jlORHpm6fenpL"                          # Upbit API secret 키
try:
  upbit = pyupbit.Upbit(access, secret)
  print("Login COMPLETE")
  print("====================================")
except:
  print("!!Login ERROR!!")