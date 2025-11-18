# Issue 15: Build Evaluation and Metrics Framework (Phase 5)

**Priority:** Low (Future)
**Estimated Effort:** 2-3 weeks
**Labels:** `evaluation`, `metrics`, `phase-5`, `quality`
**Phase:** 5 - Evaluation and Optimization

## Problem Statement

From project plan (docs/2_Ragnostic_Project_Plan.md):
- RAG system built but quality not measured
- No metrics for retrieval accuracy
- No evaluation of answer quality
- Cannot compare different configurations
- No performance tracking over time

## Scope

Build comprehensive evaluation framework:
1. **Retrieval Metrics** - Precision, recall, MRR, NDCG
2. **Answer Quality Metrics** - Faithfulness, relevance, completeness
3. **Test Dataset** - Curated Q&A pairs with ground truth
4. **Benchmarking** - Compare configurations and models
5. **Regression Testing** - Prevent quality degradation

## Proposed Metrics

### Retrieval Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Precision@K** | Relevant docs in top K | >0.8 |
| **Recall@K** | % of relevant docs retrieved | >0.7 |
| **MRR** | Mean Reciprocal Rank | >0.85 |
| **NDCG** | Normalized Discounted Cumulative Gain | >0.75 |
| **Hit Rate** | % queries with ≥1 relevant doc | >0.9 |

### Answer Quality Metrics

| Metric | Description | Method |
|--------|-------------|--------|
| **Faithfulness** | Answer grounded in context | LLM-as-judge |
| **Relevance** | Answers the question | LLM-as-judge |
| **Completeness** | Covers all aspects | Human eval |
| **Correctness** | Factually accurate | Human eval |
| **Latency** | Time to answer | Measurement |

## Proposed Solution

### Test Dataset Structure

```json
{
  "test_cases": [
    {
      "id": "test_001",
      "question": "What are the main components of a transformer architecture?",
      "relevant_documents": ["doc_123", "doc_456"],
      "relevant_chunks": ["chunk_789", "chunk_012"],
      "expected_answer_contains": [
        "self-attention",
        "feed-forward network",
        "positional encoding"
      ],
      "difficulty": "easy"
    }
  ]
}
```

### Evaluation Framework

```python
# src/ragnostic/evaluation/evaluator.py
from dataclasses import dataclass
from typing import List, Dict
import numpy as np

@dataclass
class EvaluationResult:
    """Results from evaluation run."""
    precision_at_5: float
    recall_at_5: float
    mrr: float
    ndcg: float
    hit_rate: float
    avg_latency: float
    faithfulness: float
    relevance: float
    test_cases_passed: int
    test_cases_total: int

class RAGEvaluator:
    """Evaluator for RAG system quality."""

    def __init__(self, rag_system, test_dataset):
        self.rag = rag_system
        self.test_dataset = test_dataset

    def evaluate(self) -> EvaluationResult:
        """Run full evaluation suite."""

        precision_scores = []
        recall_scores = []
        reciprocal_ranks = []
        ndcg_scores = []
        hits = []
        latencies = []
        faithfulness_scores = []
        relevance_scores = []

        for test_case in self.test_dataset:
            # Measure retrieval quality
            results = self.rag.query_pipeline.query(
                test_case['question'],
                top_k_docs=5
            )

            # Calculate retrieval metrics
            retrieved_doc_ids = [r.document_id for r in results]
            relevant_doc_ids = test_case['relevant_documents']

            precision_scores.append(
                self._precision_at_k(retrieved_doc_ids, relevant_doc_ids, k=5)
            )
            recall_scores.append(
                self._recall_at_k(retrieved_doc_ids, relevant_doc_ids, k=5)
            )
            reciprocal_ranks.append(
                self._reciprocal_rank(retrieved_doc_ids, relevant_doc_ids)
            )
            ndcg_scores.append(
                self._ndcg_at_k(retrieved_doc_ids, relevant_doc_ids, k=5)
            )
            hits.append(
                int(any(doc_id in relevant_doc_ids for doc_id in retrieved_doc_ids))
            )

            # Measure answer quality
            import time
            start = time.time()
            answer = self.rag.ask(test_case['question'])
            latencies.append(time.time() - start)

            # LLM-as-judge for faithfulness and relevance
            faithfulness_scores.append(
                self._evaluate_faithfulness(answer, results)
            )
            relevance_scores.append(
                self._evaluate_relevance(answer, test_case['question'])
            )

        return EvaluationResult(
            precision_at_5=np.mean(precision_scores),
            recall_at_5=np.mean(recall_scores),
            mrr=np.mean(reciprocal_ranks),
            ndcg=np.mean(ndcg_scores),
            hit_rate=np.mean(hits),
            avg_latency=np.mean(latencies),
            faithfulness=np.mean(faithfulness_scores),
            relevance=np.mean(relevance_scores),
            test_cases_passed=sum(1 for s in faithfulness_scores if s > 0.7),
            test_cases_total=len(self.test_dataset)
        )

    def _precision_at_k(self, retrieved: List[str], relevant: List[str], k: int) -> float:
        """Calculate Precision@K."""
        retrieved_k = retrieved[:k]
        relevant_retrieved = len(set(retrieved_k) & set(relevant))
        return relevant_retrieved / k if k > 0 else 0.0

    def _recall_at_k(self, retrieved: List[str], relevant: List[str], k: int) -> float:
        """Calculate Recall@K."""
        retrieved_k = retrieved[:k]
        relevant_retrieved = len(set(retrieved_k) & set(relevant))
        return relevant_retrieved / len(relevant) if relevant else 0.0

    def _reciprocal_rank(self, retrieved: List[str], relevant: List[str]) -> float:
        """Calculate reciprocal rank."""
        for i, doc_id in enumerate(retrieved, 1):
            if doc_id in relevant:
                return 1.0 / i
        return 0.0

    def _ndcg_at_k(self, retrieved: List[str], relevant: List[str], k: int) -> float:
        """Calculate NDCG@K."""
        retrieved_k = retrieved[:k]

        # DCG
        dcg = sum(
            (1 if doc_id in relevant else 0) / np.log2(i + 2)
            for i, doc_id in enumerate(retrieved_k)
        )

        # IDCG (ideal)
        ideal = sum(1 / np.log2(i + 2) for i in range(min(len(relevant), k)))

        return dcg / ideal if ideal > 0 else 0.0

    def _evaluate_faithfulness(self, answer: str, context: List) -> float:
        """Evaluate if answer is grounded in context using LLM."""
        prompt = f"""Evaluate if the following answer is faithful to the provided context.
Score from 0 to 1, where 1 means completely faithful and 0 means not faithful.

Context: {context}

Answer: {answer}

Faithfulness score (0-1):"""

        # Use LLM to judge
        # Implementation depends on LLM provider
        return 0.8  # Placeholder

    def _evaluate_relevance(self, answer: str, question: str) -> float:
        """Evaluate if answer is relevant to question using LLM."""
        prompt = f"""Evaluate if the following answer is relevant to the question.
Score from 0 to 1, where 1 means highly relevant and 0 means not relevant.

Question: {question}

Answer: {answer}

Relevance score (0-1):"""

        # Use LLM to judge
        return 0.8  # Placeholder
```

### Benchmarking Tool

```python
# src/ragnostic/evaluation/benchmark.py
class RAGBenchmark:
    """Benchmark different RAG configurations."""

    def __init__(self, test_dataset):
        self.test_dataset = test_dataset

    def compare_configurations(self, configs: Dict[str, Dict]) -> pd.DataFrame:
        """Compare multiple RAG configurations.

        Args:
            configs: Dict of {name: config_params}

        Returns:
            DataFrame with comparison results
        """
        results = []

        for name, config in configs.items():
            # Initialize RAG with config
            rag = RAGnostic(**config)

            # Evaluate
            evaluator = RAGEvaluator(rag, self.test_dataset)
            result = evaluator.evaluate()

            results.append({
                "Configuration": name,
                "Precision@5": result.precision_at_5,
                "Recall@5": result.recall_at_5,
                "MRR": result.mrr,
                "NDCG": result.ndcg,
                "Hit Rate": result.hit_rate,
                "Latency (s)": result.avg_latency,
                "Faithfulness": result.faithfulness,
                "Relevance": result.relevance,
            })

        return pd.DataFrame(results)
```

## Acceptance Criteria

- [ ] Test dataset created with ≥50 question-answer pairs
- [ ] Retrieval metrics implemented (Precision, Recall, MRR, NDCG)
- [ ] Answer quality metrics implemented
- [ ] LLM-as-judge evaluation implemented
- [ ] Benchmarking tool for comparing configurations
- [ ] Automated regression testing
- [ ] Performance tracking over time
- [ ] Visualization of metrics
- [ ] Documentation of evaluation methodology

## Implementation Steps

1. Create evaluation module
2. Implement retrieval metrics
3. Implement LLM-as-judge for answer quality
4. Create test dataset (manual curation)
5. Build benchmarking framework
6. Add visualization (plots, dashboards)
7. Integrate with CI/CD for regression testing
8. Document methodology and best practices

## Dependencies

**Required before:**
- Issue #14 (Query pipeline must exist)
- Full RAG system implemented

## Testing Strategy

- Validate metric implementations
- Test with known ground truth
- Compare with existing RAG benchmarks (e.g., BEIR)
- Human evaluation for subset of results

## Test Dataset Creation

### Sources for Questions
1. Create questions from existing document corpus
2. Use GPT to generate questions from document summaries
3. Manual curation by domain experts
4. Crowdsource questions from users

### Quality Criteria
- Questions should be answerable from corpus
- Mix of difficulty levels (easy, medium, hard)
- Different question types (factual, reasoning, summary)
- Clear ground truth annotations

## Benchmarking Scenarios

Compare:
- Different embedding models
- Different chunk sizes
- Different retrieval strategies (top-k values)
- Different reranking approaches
- Different LLM providers

## Regression Testing

Integrate into CI/CD:
```yaml
# .github/workflows/evaluation.yml
name: RAG Evaluation

on: [push]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run evaluation
        run: python -m ragnostic.evaluation.run
      - name: Check metrics
        run: |
          python -m ragnostic.evaluation.check_thresholds \
            --min-precision 0.7 \
            --min-recall 0.6 \
            --min-mrr 0.75
```

## Visualization

Use tools like:
- Matplotlib/Seaborn for metric plots
- Weights & Biases for experiment tracking
- Streamlit for interactive dashboards

## Notes

- Start with small test dataset (20-30 questions)
- Expand as system matures
- Consider domain-specific metrics
- Human evaluation needed for final validation
- Track metrics over time to detect regression
- Compare against baselines (BM25, simple vector search)
