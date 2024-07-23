import pyotp
import time

totp = pyotp.TOTP('base32secret3232')
totp2 = pyotp.TOTP('base32secret323232')


# OTP verified for current time
x = totp.now()
y = totp2.now()
while 1:
    print(x)
    print(y)
    print(totp.now())
    print(totp2.now())
    print(totp.verify(x)) 
    print(totp2.verify(y)) 
    time.sleep(1)
