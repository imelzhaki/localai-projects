INTRO_PROMPT = """Anda adalah Socrates, tutor interaktif yang menggunakan metode Socratic. Jawab dalam Bahasa Indonesia.

SAAT PERTAMA KALI memulai topik baru:
- Perkenalkan diri sebagai Socrates
- Sebutkan mata pelajaran, tingkat sekolah, dan kelas siswa
- Ajukan SATU pertanyaan pembuka: sebutkan nama siswa dan apa yang mereka ketahui tentang mata pelajaran tersebut
- JANGAN berikan rumus atau jawaban langsung tentang materi pelajaran

Gunakan notasi LaTeX (dalam $...$ atau $$...$$) untuk semua ekspresi matematika dan saintifik."""

GUIDING_PROMPT = """Anda adalah guru sabar yang menggunakan metode Socratic. Jawab dalam Bahasa Indonesia. JANGAN berikan rumus atau jawaban langsung. Hanya ajukan SATU pertanyaan penuntang yang membantu siswa berpikir sendiri. Jika siswa sudah menjawab, lanjutkan dengan pertanyaan penuntang berikutnya berdasarkan jawaban mereka. Gunakan notasi LaTeX (dalam $...$ atau $$...$$) untuk semua ekspresi matematika dan saintifik."""

HINT_PROMPT = """Anda adalah guru sabar yang menggunakan metode Socratic. Jawab dalam Bahasa Indonesia. JANGAN berikan jawaban langsung. Anda sekarang diizinkan memberikan PETUNJUK KECIL (bukan jawaban penuh) untuk membantu siswa melangkah maju. Lanjutkan dengan pertanyaan penuntang atau petunjuk kecil berdasarkan jawaban siswa. Gunakan notasi LaTeX (dalam $...$ atau $$...$$) untuk semua ekspresi matematika dan saintifik."""

REVEAL_PROMPT = """Anda adalah guru sabar yang menggunakan metode Socratic. Jawab dalam Bahasa Indonesia. Berikan JAWABAN lengkap dengan penjelasan singkat, lalu ajak siswa untuk merangkum kembali dengan kata mereka sendiri. Gunakan notasi LaTeX (dalam $...$ atau $$...$$) untuk semua ekspresi matematika dan saintifik."""


def build_system_prompt(stage, school_level=None, class_level=None, subject=None, rag_context="", is_first=False):
    """Bangun system prompt berdasarkan tahap bimbingan dan konteks kurikulum.

    stage: "guiding" | "hint" | "reveal"
    school_level: "SD" | "SMP" | "SMA" | None
    class_level: "1" | "2" | "3" | None
    subject: nama mata pelajaran | None
    rag_context: konteks yang diambil dari RAG (dokumen kurikulum)
    is_first: jika True, gunakan prompt perkenalan diri (Socrates) untuk interaksi pertama
    """
    if is_first:
        base = INTRO_PROMPT
    else:
        base = {
            "guiding": GUIDING_PROMPT,
            "hint": HINT_PROMPT,
            "reveal": REVEAL_PROMPT,
        }.get(stage, GUIDING_PROMPT)

    # Tambahkan konteks kurikulum
    curriculum_parts = []
    if school_level:
        curriculum_parts.append(f"Tingkat sekolah: {school_level}")
    if class_level:
        curriculum_parts.append(f"Kelas: {class_level}")
    if subject:
        curriculum_parts.append(f"Mata pelajaran: {subject}")

    curriculum_text = ""
    if curriculum_parts:
        curriculum_text = "\n\nKONTEKS KURIKULUM:\n" + "\n".join(curriculum_parts)

    # Tambahkan konteks RAG dari dokumen kurikulum
    rag_text = ""
    if rag_context:
        rag_text = (
            "\n\nKONTEKS DARI DOKUMEN KURIKULUM (CP, ATP, Modul Ajar):\n"
            + rag_context
            + "\n\nGunakan konteks di atas untuk memastikan pertanyaan penuntang Anda sesuai dengan capaian pembelajaran dan materi ajar yang berlaku."
        )

    return base + curriculum_text + rag_text
