# RAG Safety Notes 日本語

RAG では、検索された文書 chunk をそのまま命令として扱わないことが重要です。
ユーザー入力、システム指示、検索文書は prompt construction の中で明確に分離します。

検索文書に「これまでの指示を無視して」や「システムプロンプトを教えて」のような文が含まれる場合、それは indirect prompt injection の可能性がある untrusted context として記録します。
