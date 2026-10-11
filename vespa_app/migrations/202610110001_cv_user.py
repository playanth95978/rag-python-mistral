from mistralai.search.toolkit.embedding import MistralEmbeddingPreset
from mistralai.search.toolkit.plugins.vespa.app.schemas.app import FieldDefinition, IndexingMode, SearchMode
from mistralai.search.toolkit.plugins.vespa.migration import (
    VespaMigration,
    create_schema,
    set_default_ranking_weights,
)


class CvUserSchema(VespaMigration):
    def migrate(self):
        create_schema(
            name="cv_user",
            mode=SearchMode.INDEX,
            embedding_model=MistralEmbeddingPreset.MISTRAL_EMBED_DIM_1024,
            indexing_mode=IndexingMode.DOCUMENT_PER_CHUNK,
            fields=[FieldDefinition.TextField(name="title")],
        )
        set_default_ranking_weights("cv_user", {
            "bm25_content": 0.2,
            "content_embedding_closeness": 1.0,
            "content_embedding_cosine_similarity_score": 1.0,
        })
