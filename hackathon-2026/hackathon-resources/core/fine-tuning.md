# 🎯 Fine-Tuning LLMs (LoRA & QLoRA)

## 1. What is Fine-Tuning?
Training a pre-trained model further on a specific, smaller dataset to specialize its behavior.
- **Full Fine-Tuning**: Update all model weights. Very expensive.
- **LoRA** (Low-Rank Adaptation): Freeze most weights and inject small trainable adapters. **Used in 90% of hackathon projects.**
- **QLoRA**: LoRA + quantized (4-bit) base model. Runs on Google Colab's free GPU.

## 2. When to Fine-Tune (vs. Prompting)?
| Situation | Use |
|---|---|
| Model doesn't follow a specific format | Prompt Engineering first |
| Need domain-specific knowledge not in training data | RAG first |
| Consistent style/output over thousands of calls | Fine-Tuning |

> **Hackathon tip**: Almost always, RAG or prompting is faster and good enough. Only fine-tune if you have a specific structured output requirement.

## 3. Resources
- [Hugging Face PEFT (LoRA/QLoRA) Guide](https://huggingface.co/docs/peft/index)
- [QLoRA Paper in Plain English (Sebastian Raschka)](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms)
- [Fine-Tuning Llama 3 on Colab (YouTube)](https://www.youtube.com/watch?v=aQmoog_s8HE)
