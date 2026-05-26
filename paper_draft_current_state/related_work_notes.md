# Related Work Notes

These notes are for paper drafting. Citation metadata should be checked again before final submission.

## 1. Text-to-Image Faithfulness / Alignment Evaluation

TIFA: Accurate and Interpretable Text-to-Image Faithfulness Evaluation with Question Answering, ICCV 2023. TIFA evaluates whether a generated image is faithful to a text prompt by converting the prompt into question-answer pairs and applying VQA over the image. It is relevant because it makes image-text evaluation more interpretable than global similarity, but it does not directly distinguish whether a visible abnormality is required, permitted, violating, or ambiguous.

VQAScore / GenAI-Bench: Evaluating Text-to-Visual Generation with Image-to-Text Generation, 2024. This line of work uses VQA or image-to-text likelihood to evaluate text-to-visual generation, including complex prompt understanding. It is relevant to automated evaluation of generated images, but the present project focuses on permission status of a target anomaly rather than prompt satisfaction alone.

## 2. Compositional Text-to-Image Evaluation

GenEval: An Object-Focused Framework for Evaluating Text-to-Image Alignment, NeurIPS 2023. GenEval evaluates object-centric prompt alignment properties such as object co-occurrence, position, count, and color. It is useful as a benchmark precedent for fine-grained image-text alignment, while our work targets abnormality permission rather than object correctness alone.

T2I-CompBench: A Comprehensive Benchmark for Open-world Compositional Text-to-image Generation, NeurIPS 2023. T2I-CompBench evaluates compositional generation across attribute binding, spatial relationships, non-spatial relationships, and complex compositions. It motivates the need for targeted diagnostic evaluation. Our benchmark similarly isolates specific axes, but asks whether a target abnormality should be labeled hallucination under the prompt.

## 3. Image Hallucination / Visual Factuality

Visual hallucination work often defines errors as visual content that conflicts with an instruction, caption, or source image. This is close to our `prompt_violating` category. The difference is that our benchmark treats the same visible abnormality as non-hallucinatory when the prompt requires or permits it, and as uncertain when the prompt boundary is underdetermined.

For the paper, frame this as a refinement rather than a rejection of hallucination evaluation. The contribution is not "visual hallucination is wrong as a concept"; it is that hallucination labels need a permission-aware boundary when creative prompts intentionally license abnormal visual features.

## 4. Annotator Disagreement and Majority-Vote Limitations

Davani et al., Dealing with Disagreements: Looking Beyond the Majority Vote in Subjective Annotations, TACL 2022. Davani et al. argue that annotator disagreement can reflect systematic perspectives and uncertainty, not merely noise. This directly supports our caution against majority-vote final gold for ambiguous and no_issue/control categories.

Connection to this project: the v1 human pilot shows high agreement on clear boundaries but 0/40 three-rater exact agreement for ambiguous and 0/24 for no_issue/control. Majority vote would erase the uncertainty-sensitive categories the benchmark is designed to test.

## Positioning Sentence

Existing text-to-image evaluation asks whether generated content matches a prompt. This project asks a narrower but important question: when a visible abnormality exists, does the prompt require it, permit it, forbid it, leave it ambiguous, or contain no issue at all?

## Source Links Checked During Drafting

- TIFA arXiv: https://arxiv.org/abs/2303.11897
- GenEval arXiv: https://arxiv.org/abs/2310.11513
- T2I-CompBench arXiv: https://arxiv.org/abs/2307.06350
- Evaluating Text-to-Visual Generation with Image-to-Text Generation arXiv: https://arxiv.org/abs/2404.01291
- Davani et al. TACL page: https://transacl.org/index.php/tacl/article/view/3173
