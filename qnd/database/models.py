from datetime import datetime
import datetime

from database import db

class Setting(db.Model):
    """
    Application settings. Key value pair store.
    """
    __tablename__ = 'settings'
    key = db.Column(db.String, primary_key=True)                                # key
    value = db.Column(db.String)                                                # value

class Network(db.Model):
    """
    A network object
    The status can be
        - created 
        - updated
        - healthy
        - deleted
        - failed
    """
    __tablename__ = 'networks'
    id = db.Column(db.Integer, primary_key=True)                  
    name = db.Column(db.String) 
    password = db.Column(db.String) 
    port = db.Column(db.Integer)
    netmask = db.Column(db.Integer)
    ip = db.Column(db.String)
    status = db.Column(db.String())

class Client(db.Model):
    """
    A client object
    """
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)                       
    ip = db.Column(db.String)
    type = db.Column(db.String(3))   
    package = db.Column(db.String)
    key = db.Column(db.String)
    public = db.Column(db.String(1))

    network_id = db.Column(db.Integer, db.ForeignKey('networks.id'))                 
    network = db.relationship('Network', foreign_keys=[network_id], lazy='immediate')  
    status = db.Column(db.String())

class FirewallRule(db.Model):
    """
    An access control list object
    """
    __tablename__ = 'rules'
    id = db.Column(db.Integer, primary_key=True)    
    action = db.Column(db.String)  
    where = db.Column(db.String) 
    to = db.Column(db.String) 
    protocol = db.Column(db.String) 
    port = db.Column(db.String) 

class ACL(db.Model):
    """
    An access control list object
    """
    __tablename__ = 'acls'
    id = db.Column(db.Integer, primary_key=True)    
    
    network_id = db.Column(db.Integer, db.ForeignKey('networks.id'))                 
    network = db.relationship('Network', foreign_keys=[network_id], lazy='immediate')      

    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))                 
    client = db.relationship('Client', foreign_keys=[client_id], lazy='immediate')      

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))                 
    user = db.relationship('User', foreign_keys=[user_id], lazy='immediate')    
                                   
    role = db.Column(db.String)    
    
class Log(db.Model):
    """
    A log object
    """
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)                           
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)         

    title = db.Column(db.String)                                              
    description = db.Column(db.String)                                    
    stacktrace = db.Column(db.String)  
    
class User(db.Model):
    """
    Username in database; currently not used. Planned.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)                                    # id
    username = db.Column(db.String(32), index=True)                                 # the username
    password_hash = db.Column(db.String(64))                                        # hashed password
    type  = db.Column(db.String(1))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user
