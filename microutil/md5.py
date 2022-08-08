# -*- coding:utf-8 -*-
import hashlib


class Md5:

    @staticmethod
    def get_md5_str(str):
        md5_str = hashlib.md5(str.encode(encoding='UTF-8')).hexdigest()
        return md5_str
