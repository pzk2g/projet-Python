#!/usr/bin/python3

import math
import random
import subprocess

random.seed()


class RSA:
    cmd = "openssl prime {input}"
    expected_output = "is prime"

    msd_range = "12345679"  # Most significant digit range
    lsd_range = "1379"  # Less significant digit range
    isd_range = "0123456789"  # Other digits

    n_digits_range = (30, 30)

    e = 65537

    def __init__(self):
        p_digits = random.randint(*self.n_digits_range)
        q_digits = random.randint(*self.n_digits_range)
        p = self.__generate_prime_number(digits=p_digits)
        q = p
        while p == q:
            q = self.__generate_prime_number(digits=q_digits)
        self.n = p * q
        phi_n = (p - 1) * (q - 1)
        self.d = self.modinv(self.e, phi_n)
        self.max_len = int(math.log(self.n) / math.log(256))

    def is_prime(self, number: int):
        output = subprocess.run(
            self.cmd.format(input=number), shell=True, stdout=subprocess.PIPE, text=True
        )
        return self.expected_output in output.stdout

    def __generate_number(self, digits=7):

        number = ""
        for i in reversed(range(digits)):
            if i == digits - 1:
                number += random.choice(self.lsd_range)
            elif i == 0:
                number += random.choice(self.msd_range)
            else:
                number += random.choice(self.isd_range)
        return int(number)

    def __shift_number(self, number):
        number = str(number)[1:-1]
        if number[0] == "0":
            number = str(random.choice(self.msd_range)) + number[1::]
        number = (
            number
            + str(random.choice(self.isd_range))
            + str(random.choice(self.lsd_range))
        )
        return int(number)

    def __generate_prime_number(self, digits=7):
        number = self.__generate_number(digits=digits)
        while not self.is_prime(number):
            number = self.__shift_number(number)
        return number

    def encode(self, message, output_as_text=False, out_n=None):
        n = self.n
        if out_n is not None:
            n = out_n
        codes = list()
        for i in range(0, len(message), self.max_len):
            limit = min(len(message), i + self.max_len)
            sub_msg = message[i:limit]
            int_message = self.__convert_to_int(sub_msg)
            code = RSA.lpowmod(int_message, self.e, n)
            code = self.__convert_to_string(code) if output_as_text else str(code)
            codes.append(code)

        return " ".join(codes)

    def decode(self, c: str, input_as_text=False):
        codes = c.split(" ")
        if input_as_text:
            codes = list(map(lambda x: self.__convert_to_int(x), codes))
        else:
            codes = list(map(lambda x: int(x), codes))

        messages = list()
        for sub_code in codes:
            int_message_chunk = self.lpowmod(sub_code, self.d, self.n)
            message = self.__convert_to_string(int_message_chunk)
            messages.append(message)
        return "".join(messages)

    @staticmethod
    def __convert_to_int(message):  # TODO : More clean
        grd = 1
        num = 0
        message = message[::-1]
        for i in range(0, len(message), +1):
            num = num + ord(message[i]) * grd
            grd *= 256
        return num

    @staticmethod
    def __convert_to_string(code):
        st = ""
        while code != 0:
            temp = code % 256
            st += chr(temp)
            chr(temp)
            co = code - temp
            code = code // 256
        st = st[::-1]
        return st

    @staticmethod
    def egcd(a, b):
        x, y, u, v = 0, 1, 1, 0
        while a != 0:
            q, r = b // a, b % a
            m, n = x - u * q, y - v * q
            b, a, x, y, u, v = a, r, u, v, m, n
        gcd = b
        return gcd, x, y

    @staticmethod
    def modinv(a, m):
        gcd, x, y = RSA.egcd(a, m)
        if gcd != 1:
            return None
        return x % m

    @staticmethod
    def lpowmod(x, y, n):
        """puissance modulaire: (x**y)%n avec x, y et n entiers"""
        result = 1
        while y > 0:
            if y & 1 > 0:
                result = (result * x) % n
            y >>= 1
            x = (x * x) % n
        return result


if __name__ == "__main__":
    rsa = RSA()
    message = input("Message : ")
    while message != "quit":
        print("Encoding ....")
        print()
        code = rsa.encode(message)
        print(code)
        msg_code = rsa.encode(message, output_as_text=True)
        print(msg_code)
        print()

        print("Decoding ....")
        print()

        msg = rsa.decode(code)
        print(msg)
        msg = rsa.decode(msg_code, input_as_text=True)
        print(msg)
        print()
        message = input("Message : ")
