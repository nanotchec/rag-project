from rerankers.cross_encoder_reranker import CrossEncoderReranker


def test_reranker_scores_length():
    reranker = CrossEncoderReranker()
    scores = reranker.rerank("bonjour", ["salut", "au revoir"])
    assert len(scores) == 2
