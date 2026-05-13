from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, Float
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func
import enum


class Base(DeclarativeBase):
    pass


class UserRole(str, enum.Enum):
    admin = "admin"
    productor = "productor"
    supervisor_legal = "supervisor_legal"
    tecnico_audio = "tecnico_audio"
    traductor = "traductor"
    actor = "actor"
    cliente_viewer = "cliente_viewer"


class DubbingMode(str, enum.Enum):
    humano_asistido = "doblaje_humano_asistido"
    ia_autorizada = "voz_original_ia_autorizada"


class JobStatus(str, enum.Enum):
    uploaded = "uploaded"
    pending_legal_check = "pending_legal_check"
    blocked_legal = "blocked_legal"
    transcribing = "transcribing"
    translating = "translating"
    awaiting_translation_review = "awaiting_translation_review"
    generating_voice = "generating_voice"
    lipsyncing = "lipsyncing"
    mixing = "mixing"
    awaiting_approval = "awaiting_approval"
    approved = "approved"
    rejected = "rejected"
    exported = "exported"
    failed = "failed"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.cliente_viewer, nullable=False)
    is_active = Column(Boolean, default=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    tax_id = Column(String(50))
    country = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="organization")
    projects = relationship("Project", back_populates="organization")
    contracts = relationship("VoiceContract", back_populates="organization")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization", back_populates="projects")
    media_assets = relationship("MediaAsset", back_populates="project")
    dubbing_jobs = relationship("DubbingJob", back_populates="project")


class MediaAsset(Base):
    __tablename__ = "media_assets"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    media_type = Column(String(50))  # video, audio
    duration_seconds = Column(Float)
    file_size_bytes = Column(Integer)
    mime_type = Column(String(100))
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="media_assets")


class Actor(Base):
    __tablename__ = "actors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    voice_gender = Column(String(50))
    voice_language = Column(String(50))
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    contracts = relationship("VoiceContract", back_populates="actor")


class VoiceContract(Base):
    __tablename__ = "voice_contracts"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, ForeignKey("actors.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    contract_ref = Column(String(100), unique=True, nullable=False)
    signed_date = Column(DateTime(timezone=True), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    ia_consent = Column(Boolean, default=False)
    allowed_languages = Column(Text, default="[]")  # JSON array
    allowed_territories = Column(Text, default="[]")
    allowed_usage_types = Column(Text, default="[]")  # JSON array
    max_duration_seconds = Column(Float)
    compensation_terms = Column(Text)
    document_path = Column(String(1000))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    actor = relationship("Actor", back_populates="contracts")
    organization = relationship("Organization", back_populates="contracts")
    permissions = relationship("ContractPermission", back_populates="contract")


class ContractPermission(Base):
    __tablename__ = "contract_permissions"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("voice_contracts.id"), nullable=False)
    permission_type = Column(String(100), nullable=False)  # language, territory, usage
    permission_value = Column(String(255), nullable=False)
    is_allowed = Column(Boolean, default=True)

    contract = relationship("VoiceContract", back_populates="permissions")


class DubbingJob(Base):
    __tablename__ = "dubbing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    media_asset_id = Column(Integer, ForeignKey("media_assets.id"), nullable=True)
    actor_id = Column(Integer, ForeignKey("actors.id"), nullable=True)
    contract_id = Column(Integer, ForeignKey("voice_contracts.id"), nullable=True)
    status = Column(Enum(JobStatus), default=JobStatus.uploaded, nullable=False)
    mode = Column(Enum(DubbingMode), nullable=False)
    source_language = Column(String(50), nullable=False)
    target_language = Column(String(50), nullable=False)
    territory = Column(String(100))
    usage_type = Column(String(100))
    legal_blocked = Column(Boolean, default=False)
    legal_block_reason = Column(Text)
    tts_provider_used = Column(String(100))
    lipsync_provider_used = Column(String(100))
    model_version = Column(String(100))
    prompt_text = Column(Text)
    output_path = Column(String(1000))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="dubbing_jobs")
    steps = relationship("JobStep", back_populates="dubbing_job")
    approvals = relationship("Approval", back_populates="dubbing_job")


class JobStep(Base):
    __tablename__ = "job_steps"

    id = Column(Integer, primary_key=True, index=True)
    dubbing_job_id = Column(Integer, ForeignKey("dubbing_jobs.id"), nullable=False)
    step_name = Column(String(100), nullable=False)
    status = Column(String(50), default="pending")
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_ms = Column(Integer)
    output_data = Column(Text)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)

    dubbing_job = relationship("DubbingJob", back_populates="steps")


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    dubbing_job_id = Column(Integer, ForeignKey("dubbing_jobs.id"), nullable=False)
    language = Column(String(50), nullable=False)
    segments = Column(Text, nullable=False)  # JSON array of {start, end, text}
    raw_text = Column(Text)
    model_used = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Translation(Base):
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True, index=True)
    dubbing_job_id = Column(Integer, ForeignKey("dubbing_jobs.id"), nullable=False)
    source_language = Column(String(50), nullable=False)
    target_language = Column(String(50), nullable=False)
    segments = Column(Text, nullable=False)  # JSON
    raw_text = Column(Text)
    model_used = Column(String(100))
    reviewed = Column(Boolean, default=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GeneratedVoiceAsset(Base):
    __tablename__ = "generated_voice_assets"

    id = Column(Integer, primary_key=True, index=True)
    dubbing_job_id = Column(Integer, ForeignKey("dubbing_jobs.id"), nullable=False)
    file_path = Column(String(1000), nullable=False)
    duration_seconds = Column(Float)
    provider = Column(String(100))
    model_used = Column(String(100))
    prompt_hash = Column(String(64))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class LipsyncOutput(Base):
    __tablename__ = "lipsync_outputs"

    id = Column(Integer, primary_key=True, index=True)
    dubbing_job_id = Column(Integer, ForeignKey("dubbing_jobs.id"), nullable=False)
    file_path = Column(String(1000), nullable=False)
    provider = Column(String(100))
    model_used = Column(String(100))
    duration_seconds = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    dubbing_job_id = Column(Integer, ForeignKey("dubbing_jobs.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    decision = Column(String(50), nullable=False)  # approved, rejected
    comments = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    dubbing_job = relationship("DubbingJob", back_populates="approvals")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    organization_id = Column(Integer, nullable=True)
    project_id = Column(Integer, nullable=True)
    dubbing_job_id = Column(Integer, nullable=True)
    action = Column(String(255), nullable=False)
    entity_type = Column(String(100))
    entity_id = Column(Integer)
    details = Column(Text)
    ip_address = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="audit_logs")


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    provider = Column(String(100), nullable=False)
    model_type = Column(String(100), nullable=False)  # tts, asr, translate, lipsync
    version = Column(String(50))
    config = Column(Text)  # JSON
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ProviderCredential(Base):
    __tablename__ = "provider_credentials"

    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String(100), nullable=False)
    provider_type = Column(String(100), nullable=False)
    api_key_encrypted = Column(String(1000))
    endpoint_url = Column(String(500))
    config = Column(Text)  # JSON
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
