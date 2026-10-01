from class_mother_personnel import BaseFile, BaseComplement
from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship


class UserComplements(BaseComplement):
    __tablename__ = 'user_complements'


class Users(BaseFile):
    __tablename__ = 'users'

    # Relacionamento com Complemento do usuário
    complement_id = Column(
        Integer, 
        ForeignKey(
            'user_complements.id', 
            ondelete="CASCADE"), 
        unique=True, 
        nullable=False
    )
    complement = relationship("UserComplements", lazy="joined")    
    last_date_login = Column(DateTime, default=func.current_timestamp(), nullable=False)
