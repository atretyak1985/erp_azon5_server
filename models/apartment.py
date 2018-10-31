from db import db

class ApartamentModel(db.Model):
    __tablename__ = 'apartament'

    _id = db.Column(db.Integer, primary_key=True)

    add_id = db.Column(db.String(255))
    title = db.Column(db.String(255))
    price =db.Column(db.String(255))
    currency = db.Column(db.String(255))
    city = db.Column(db.String(255))
    district = db.Column(db.String(255))
    region = db.Column(db.String(255))
    gps = db.Column(db.String(255))
    description = db.Column(db.String(9000))
    poster_name = db.Column(db.String(255))
    url = db.Column(db.String(255))
    date_added = db.Column(db.String(9000))
    images = db.Column(db.String(9000))
    private_business = db.Column(db.String(255))
    total_area = db.Column(db.String(255))
    number_of_rooms = db.Column(db.String(255))


    def __init__(self):
        pass

    def json(self):
        return {
            'type': self.type,
            'data': self.data,
        }

    @classmethod
    def find_by_add_id(self, id):
        return self.query.filter_by(add_id=id).first()

    @classmethod
    def get_all(self):
        return self.query.all()

    def save_to_db(self):
        print('save')
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            'id':self._id,
            'add_id':self.add_id,
            'title':self.title,
            'price':self.price,
            'currency':self.currency,
            'city':self.city,
            'district':self.district,
            'region':self.region,
            'gps':self.gps,
            'description':self.description,
            'poster_name':self.poster_name,
            'url':self.url,
            'date_added':self.date_added,
            'images':self.images,
            'private_business':self.private_business,
            'total_area':self.total_area,
            'number_of_rooms':self.number_of_rooms,
        }
