from pydantic import BaseModel, Field, validator


class ZiswafEntry(BaseModel):
    donor_name: str | None = Field(default=None, description="Nama pemberi dana")
    category: str | None = Field(default=None, description="kategori: zakat, infaq, shadaqah, wakaf")
    amount_raw: str | None = Field(default=None, description="Salinan teks nominal asli dari input")
    payment_method: str | None = Field(default=None, description="tunai, transfer, qris")
    note: str | None = Field(default=None, description="Catatan tambahan")

    @validator("category")
    def validate_category(cls, v):
        if v is not None and v not in {"zakat", "infaq", "shadaqah", "wakaf"}:
            raise ValueError(f"Kategori tidak valid: {v}")
        return v

    @validator("payment_method")
    def validate_payment_method(cls, v):
        if v is not None and v not in {"tunai", "transfer", "qris"}:
            raise ValueError(f"Metode pembayaran tidak valid: {v}")
        return v