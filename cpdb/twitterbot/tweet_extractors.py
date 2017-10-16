class RelatedTweetExtractor:
    def extract(self, tweet, context):
        tweets = self.get_tweets(tweet, context)
        try:
            context['first_non_retweet'] = [t for t in tweets if not t.is_retweet][0]
        except IndexError:
            context['first_non_retweet'] = None
        context['original_tweet'] = self.get_original_tweet(tweets)
        return tweets

    def is_self_tweet(self, tweet, context):
        return tweet.user_id == context['client'].get_current_user().id

    def get_tweets(self, tweet, context):
        if tweet is None or self.is_self_tweet(tweet, context):
            return []
        else:
            tweets = [tweet]
        tweets += self.get_related_tweets(tweet, context)
        return tweets

    def get_related_tweets(self, tweet, context):
        tweets = []
        tweets += self.get_tweets(tweet.in_reply_to_tweet, context)
        tweets += self.get_tweets(tweet.retweeted_tweet, context)
        tweets += self.get_tweets(tweet.quoted_tweet, context)
        return tweets

    def get_original_tweet(self, tweets):
        if len(tweets) > 0:
            return min(tweets, key=lambda tweet: tweet.created_at)