from fastapi import HTTPException, status


class SeeraError(HTTPException):
    code: str = "SEERA_ERROR"

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(
            status_code=status_code,
            detail={"code": self.code, "message": message},
        )


class InvalidSkinToneError(SeeraError):
    code = "INVALID_SKIN_TONE"


class InvalidUndertoneError(SeeraError):
    code = "INVALID_UNDERTONE"


class SessionNotFoundError(SeeraError):
    code = "SESSION_NOT_FOUND"

    def __init__(self, message: str = "Sesi percakapan tidak ditemukan."):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class InvalidConversationStateError(SeeraError):
    code = "INVALID_CONVERSATION_STATE"


class RecommendationNotFoundError(SeeraError):
    code = "RECOMMENDATION_NOT_FOUND"

    def __init__(self, message: str = "Rekomendasi belum tersedia untuk sesi ini."):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class EducationTopicNotFoundError(SeeraError):
    code = "EDUCATION_TOPIC_NOT_FOUND"

    def __init__(self, message: str = "Topik edukasi tidak tersedia."):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)
