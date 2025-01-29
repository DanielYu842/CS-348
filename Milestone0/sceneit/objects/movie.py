class Movie:
   def movie_attrs_soft_check(movie_attrs):
      return all([value for value in movie_attrs.values()])

   def __init__(self, movie_attrs):
      self.movie_title = movie_attrs['movie_title']
      self.movie_info = movie_attrs['movie_info']
      self.critics_consensus = movie_attrs['critics_consensus']
      self.rating = movie_attrs['rating']
      self.in_theaters_date = movie_attrs['in_theaters_date']
      self.on_streaming_date = movie_attrs['on_streaming_date']
      self.runtime_in_minutes = int(movie_attrs['runtime_in_minutes'])
      self.tomatometer_status = movie_attrs['tomatometer_status']
      self.tomatometer_rating = float(movie_attrs['tomatometer_rating'])
      self.tomatometer_count = int(movie_attrs['tomatometer_count'])
      self.audience_rating = float(movie_attrs['audience_rating'])
      self.audience_count = int(movie_attrs['audience_count'])
      
      