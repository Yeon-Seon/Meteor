import os


class Util:
    def __init__(self, path):
        self.path = path

    # 폴더 생성 함수
    def mkdir(self, add_path):
        try:
            if not os.path.exists(self.path + add_path):
                os.makedirs(self.path + add_path)
        except OSError:
            pass
