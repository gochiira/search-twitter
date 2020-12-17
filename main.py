from dotenv import load_dotenv
from time import sleep
import tweepy
import os
import requests

# .env読み出し
load_dotenv(verbose=True, override=True)


class ChinoDownloader():
    def __init__(self, keywords=["チノちゃん", "香風智乃"], filePath="imgs"):
        CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
        CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
        ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
        ACCESS_SECRET = os.environ.get("ACCESS_SECRET")
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        self.cl = tweepy.API(auth)
        if not os.path.exists(filePath):
            os.mkdir(filePath)
        self.filePath = filePath
        self.keywords = keywords

    def search(self, keyword, count):
        '''
        検索カーソルを得る
        '''
        keyword += " filter:images"
        # extendedにしないとテキストが省略される
        cursor = tweepy.Cursor(
            self.cl.search,
            q=keyword,
            tweet_mode='extended',
            include_entities=True
        ).items(count)
        return cursor

    def run(self, count=20, waitTime=10):
        '''
        巡回を開始する

        Rate limit:
        アプリとしての認証では 12req/分 = 0.2req/秒 = 5秒に1回まで
        ユーザーログイン済みでは 30req/分 = 0.5req/秒 = 2秒に1回まで
        だが実際そんなにツイートは増えないので負荷軽減のため10秒ほど待つ
        '''
        while True:
            for keyword in self.keywords:
                results = self.search(keyword, count)
                for r in results:
                    # 画像だけの場合テキストは存在しない
                    if hasattr(r, "full_text"):
                        print(
                            r.id, r.user.screen_name,
                            r.created_at, r.full_text
                        )
                    else:
                        print(r.id, r.user.screen_name, r.created_at)
                    # リツイートもしくはメディアURLをコピペした場合extendedは存在しない
                    if hasattr(r, "extended_entities"):
                        for i, media in enumerate(
                            r.extended_entities['media']
                        ):
                            path = os.path.join(
                                self.filePath,
                                f"{r.id}_{i}.jpg"
                            )
                            if not os.path.exists(path):
                                # 画像はjpgまたはpng
                                img_url = media["media_url"].replace(
                                    ".jpg", "?format=jpg"
                                ).replace(
                                    ".png", "?format=png"
                                ) + "&name=orig"
                                resp = requests.get(img_url)
                                with open(path, "wb") as f:
                                    f.write(resp.content)
            print("Wait...")
            sleep(waitTime)


if __name__ == '__main__':
    cl = ChinoDownloader(keywords=["チノちゃん", "香風智乃"])
    cl.run(waitTime=10)
