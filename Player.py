class Player():
    def __init__(self, id, rating):
        self.id = id
        self.rating = rating

    def show(self):
        print(f'id: {self.id}')
        print(f'rating: {self.rating}')
        return None