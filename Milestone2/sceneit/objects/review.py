class Review:
    @staticmethod
    def review_attrs_soft_check(review_attrs):
        return all(value for value in review_attrs.values())

    def __init__(self, review_attrs):
        self.review_id = int(review_attrs['review_id'])
        self.movie_id = int(review_attrs['movie_id'])
        self.user_id = int(review_attrs['user_id'])
        self.title = review_attrs['title']
        self.content = review_attrs['content']
        self.rating = float(review_attrs['rating'])
        self.created_at = review_attrs['created_at']
        self.updated_at = review_attrs['updated_at']

