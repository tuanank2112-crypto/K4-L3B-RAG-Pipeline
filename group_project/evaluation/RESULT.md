# RAG evaluation results

## Run information

Generated: 2026-09-26T03:22:09.496142+00:00

```json
{
  "run_id": "run_20260926_032209_492532",
  "status": "complete",
  "golden_size": 16,
  "corpus_sha256": "691e3c4dca6a4fdf5e6bd3b1c88ad142e7fc612a2daf1e83a1b0286a74edf529",
  "golden_sha256": "a049524fa373911088533d32aa9b354f879477fa48205a925d7fb0fda88efc84",
  "generation_sha256": "e213bba465c3486d2063b2629f146ce9e810f25a5a7932bfc9b702964d738f66",
  "prompt_sha256": "354138efc5de1ee96e76e17b26e7287138789afbfd8af26fc30acd960701e654",
  "evaluator_sha256": "7dd875e9676b4cf0ee3c0e5889182cd121f4d42ad7f34901ad6f82d85c96729e",
  "git_commit": "a23df34c17c930e95b755d250921f41969e25ee0",
  "embedding_provider": "jina",
  "embedding_model": "jina-embeddings-v3",
  "generator_provider": "gemini",
  "generator_model": "gemini-3.5-flash-lite",
  "temperature": 0.3,
  "seed": null,
  "top_k": 5,
  "fallback_enabled": false,
  "rrf_k": 60,
  "python": "3.13.15",
  "sdk_versions": {
    "openai": "3.13.0",
    "google-genai": "2.23.0",
    "anthropic": "1.5.0",
    "chromadb": "1.5.9",
    "rank-bm25": "0.2.2",
    "sentence-transformers": null
  },
  "source_count": 8,
  "evaluator": "token-overlap-v2 (not semantic RAGAS)"
}
```

## Configurations

A: dense-only. B: dense + BM25 + RRF k=60. Same corpus, top_k and shared generator; PageIndex fallback disabled.

## Overall scores

| Metric | Config A | Config B | Delta B−A |
| --- | ---: | ---: | ---: |
| faithfulness | 0.1351 | 0.1573 | +0.0222 |
| answer_relevance | 0.6643 | 0.7389 | +0.0746 |
| context_recall | 0.8181 | 0.9343 | +0.1161 |
| context_precision | 0.0625 | 0.0625 | +0.0000 |
| average | 0.4200 | 0.4732 | +0.0532 |
| avg_latency_sec | 4.0469 | 3.5430 | -0.5039 |

## A/B comparison

B cao hơn A trên trung bình heuristic: Delta B−A = +0.0532. Đây là số đo mô tả, chưa chứng minh ý nghĩa thống kê hay nguyên nhân.

## Worst performers

| Config | Case | Question | Mean heuristic | Observed weakest metric |
| --- | --- | --- | ---: | --- |
| A | 6 | Hướng dẫn đánh giá VUNI.39 ban hành ngày 12/06/2024 áp dụng cho các chương trình đào tạo đại học nào của VinUni? | 0.0000 | faithfulness=0.0000 |
| A | 5 | Sinh viên thuộc đối tượng nào được áp dụng khối lượng học tập ít nhất 10 tín chỉ và không quá 14 tín chỉ trong học kỳ chính? | 0.0100 | faithfulness=0.0000 |
| A | 8 | Sổ tay sinh viên VinUni (Student Handbook) phiên bản lịch sử năm 2020 đưa ra lưu ý gì về tính chính xác và thay đổi của thông tin? | 0.3440 | context_precision=0.0000 |
| B | 8 | Sổ tay sinh viên VinUni (Student Handbook) phiên bản lịch sử năm 2020 đưa ra lưu ý gì về tính chính xác và thay đổi của thông tin? | 0.4109 | context_precision=0.0000 |
| B | 13 | Các đồ vật bị bỏ quên (Lost and Found) có giá trị trên 500.000 VNĐ tại thư viện được quy định bảo quản như thế nào? | 0.4109 | context_precision=0.0000 |
| B | 11 | Tài liệu yêu cầu mượn trước (holds) sẽ được lưu giữ tại quầy lưu hành trong bao lâu để người mượn đến nhận? | 0.4179 | context_precision=0.0000 |

## Recommendations

Đối chiếu answer, sources và expected_context của các case thấp nhất trong results.json trước khi xác định nguyên nhân; metric thấp chỉ là dấu hiệu cần kiểm tra.
Nếu có lỗi pipeline, xử lý cấu hình/provider rồi chạy lại cả A/B. Tách tập calibration khỏi golden test trước khi điều chỉnh chunk hoặc retrieval; chưa có số đo mức cải thiện kỳ vọng.

## Metric definitions and limitations

Token = tập từ Unicode viết thường; citation labels được bỏ khỏi answer. Faithfulness = |answer tokens ∩ context tokens| / |answer tokens|. Answer relevance = |question tokens ∩ answer tokens| / |question tokens|. Context recall = |expected_context tokens ∩ context tokens| / |expected_context tokens|. Context precision = average precision theo thứ hạng, chunk liên quan khi bao phủ ≥25% expected_answer tokens. Mẫu số rỗng nhận 0; không có điểm nền hoặc thưởng refusal.
Đây là token heuristics, không phải semantic RAGAS: không xác minh mâu thuẫn, phủ định, entailment, từng khẳng định hay chất lượng citation. Aggregate chỉ có khi mọi case thành công. Latency gồm retrieval/generation; chi phí và seed chưa đo/không cố định. Golden provenance kiểm quote và URL, không tự xác nhận đáp án đúng về mặt chuyên môn.

## Bonus experiments

Chưa đo thí nghiệm bonus; không công bố điểm cộng.
