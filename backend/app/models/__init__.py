"""
ORM модели для хранения изменений в нормативной базе
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class DocumentCategory(str, enum.Enum):
    """Категории электронных документов"""
    ETRN = "etrn"  # Электронная транспортная накладная
    EPL = "epl"    # Электронный путевой лист
    EED = "eed"    # Электронные экспедиторские документы
    ETD = "etd"    # Единый транспортный документ
    OTHER = "other"

class RoleType(str, enum.Enum):
    """Роли пользователей"""
    ACCOUNTANT = "accountant"      # Бухгалтер
    LOGIST = "logist"              # Логист
    DISPATCHER = "dispatcher"      # Диспетчер
    DEVELOPER = "developer"        # 1С-разработчик
    IT_SPECIALIST = "it_specialist"  # IT-специалист
    MANAGER = "manager"            # Руководитель

class NormativeChange(Base):
    """Модель для хранения изменений в нормативной базе"""
    __tablename__ = "normative_changes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text)
    content = Column(Text)  # Полный текст документа
    
    # Метаданные
    source = Column(String(100), nullable=False, index=True)  # fns, mintrans, gost и т.д.
    source_url = Column(String(1000), nullable=False)
    document_number = Column(String(100), index=True)  # Номер приказа, постановления и т.д.
    
    # Категория и влияние
    category = Column(Enum(DocumentCategory), default=DocumentCategory.OTHER, index=True)
    affected_roles = Column(String(500))  # JSON: ["accountant", "logist"]
    affected_documents = Column(String(500))  # JSON: ["etrn", "epl"]
    
    # Важность и статус
    importance_level = Column(Integer, default=5)  # 1-10 (1 = низкий, 10 = критичный)
    is_critical = Column(Boolean, default=False)
    
    # Анализ
    ai_summary = Column(Text)  # Краткое резюме от LLM
    implementation_deadline = Column(DateTime, nullable=True)
    
    # Временные метки
    discovered_at = Column(DateTime, default=datetime.utcnow, index=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Отношения
    notifications = relationship("Notification", back_populates="change")

class Notification(Base):
    """Модель для хранения уведомлений"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    change_id = Column(Integer, ForeignKey("normative_changes.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    
    # Статус отправки
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    delivery_channel = Column(String(50))  # email, telegram, web
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Отношения
    change = relationship("NormativeChange", back_populates="notifications")
    subscription = relationship("Subscription", back_populates="notifications")

class Subscription(Base):
    """Модель для подписок пользователей"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Контактная информация
    email = Column(String(255), unique=True, index=True, nullable=True)
    telegram_user_id = Column(String(100), unique=True, index=True, nullable=True)
    
    # Предпочтения
    roles = Column(String(500))  # JSON: ["accountant", "logist"]
    categories = Column(String(500))  # JSON: ["etrn", "epl"]
    min_importance_level = Column(Integer, default=3)  # Минимальный уровень важности
    
    # Настройки доставки
    enable_email = Column(Boolean, default=True)
    enable_telegram = Column(Boolean, default=False)
    enable_web = Column(Boolean, default=True)
    
    # Статус
    is_active = Column(Boolean, default=True)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Отношения
    notifications = relationship("Notification", back_populates="subscription")

class CrawlerRun(Base):
    """Модель для отслеживания запусков crawler'ов"""
    __tablename__ = "crawler_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    crawler_name = Column(String(100), nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Результаты
    changes_found = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    status = Column(String(50), default="running")  # running, success, failed
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
